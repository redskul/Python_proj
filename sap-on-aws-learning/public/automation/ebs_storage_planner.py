#!/usr/bin/env python3
"""Propose a HANA EBS volume layout from a target RAM size (educational).

Applies common SAP-on-AWS storage rules of thumb to suggest sizes for /hana/data,
/hana/log, /hana/shared, /usr/sap and root, plus gp3 vs io2 hints. It then reminds you
to validate against SAP's KPIs with HCMT.

No AWS account required; pure arithmetic. Sizes are ILLUSTRATIVE -- confirm with the
current AWS SAP HANA storage guidance and SAP sizing.

Example
-------
    python ebs_storage_planner.py --ram-gb 1024
"""
from __future__ import annotations

import argparse
import math
import sys


def plan(ram_gb: float) -> list[dict]:
    """Return a list of proposed volumes.

    Common rules of thumb (see AWS SAP HANA storage docs -- verify current values):
      /hana/data   ~= 1.2 x RAM   (savepoints; some guidance uses ~1.0-1.5x)
      /hana/log    ~= min(512 GB, 0.5 x RAM)  for RAM > 512 GB log is capped-ish
      /hana/shared ~= min(1 x RAM, 1024 GB)
      /usr/sap     ~= 50 GB
      root         ~= 50 GB
    Throughput for /hana/data is aggregated by striping multiple gp3 volumes with LVM.
    """
    data_gb = math.ceil(ram_gb * 1.2)
    log_gb = math.ceil(min(512, max(64, ram_gb * 0.5)))
    shared_gb = math.ceil(min(ram_gb, 1024))

    # For big data volumes, stripe several gp3 volumes to add throughput. Keep each
    # member volume to a sensible size.
    data_stripes = max(1, math.ceil(data_gb / 400))
    per_stripe = math.ceil(data_gb / data_stripes)

    # Use io2 for very large / most demanding databases.
    log_type = "io2" if ram_gb >= 2048 else "gp3"
    data_type = "io2 or gp3 (striped)" if ram_gb >= 2048 else "gp3 (LVM-striped)"

    return [
        {"mount": "/hana/data", "size_gb": data_gb, "type": data_type,
         "layout": f"{data_stripes} x {per_stripe} GB volume(s), LVM striped",
         "kpi": "throughput"},
        {"mount": "/hana/log", "size_gb": log_gb, "type": log_type,
         "layout": "1 volume (add IOPS/throughput for low latency)",
         "kpi": "latency"},
        {"mount": "/hana/shared", "size_gb": shared_gb, "type": "gp3",
         "layout": "1 volume (EFS/FSx in scale-out)", "kpi": "moderate"},
        {"mount": "/usr/sap", "size_gb": 50, "type": "gp3",
         "layout": "1 volume", "kpi": "moderate"},
        {"mount": "/ (root)", "size_gb": 50, "type": "gp3",
         "layout": "1 volume", "kpi": "low"},
    ]


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ram-gb", type=float, required=True,
                   help="Target HANA instance RAM in GB (e.g. 1024).")
    args = p.parse_args(argv)

    volumes = plan(args.ram_gb)
    total = sum(v["size_gb"] for v in volumes)

    print("=" * 78)
    print(f"Proposed HANA EBS layout for a {args.ram_gb:,.0f} GB RAM instance "
          f"(EDUCATIONAL)")
    print("=" * 78)
    header = f"{'mount':<14}{'size':>9}  {'type':<22}{'KPI':<11}layout"
    print(header)
    print("-" * len(header))
    for v in volumes:
        print(f"{v['mount']:<14}{v['size_gb']:>7} GB  {v['type']:<22}"
              f"{v['kpi']:<11}{v['layout']}")
    print("-" * len(header))
    print(f"{'TOTAL':<14}{total:>7} GB")

    print("\nReminders:")
    print("  * /hana/log is LATENCY-critical; /hana/data is THROUGHPUT-critical.")
    print("  * gp3 lets you set IOPS/throughput independently of size; stripe multiple")
    print("    gp3 volumes with LVM to exceed a single volume's throughput ceiling.")
    print("  * VALIDATE the result against SAP KPIs using HCMT before go-live.")
    print("  * Enable EBS encryption (KMS CMK). See ../03-sap-on-aws/03-storage.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
