#!/usr/bin/env python3
"""Rough SAP sizing helper (educational).

Converts simple business inputs into a ballpark SAPS requirement and a HANA memory
estimate, then suggests candidate EC2 instance families. This is a *learning* tool that
uses simplified rules of thumb -- NOT a substitute for SAP Quick Sizer, an EarlyWatch
report, or the SAP HANA Hardware Directory.

No AWS account required; pure arithmetic.

Examples
--------
    python saps_sizing_calculator.py --users 800 --activity medium --hana-data-gb 500
    python saps_sizing_calculator.py --measured-saps 25000 --hana-data-gb 1200
"""
from __future__ import annotations

import argparse
import sys

# Very rough SAPS-per-active-user by activity profile. Real numbers come from SAP
# Quick Sizer / measurement; these are illustrative teaching values only.
SAPS_PER_USER = {"low": 8, "medium": 25, "high": 55}

# A tiny, illustrative table of instance "buckets" by memory. Real certification is per
# exact type in the SAP HANA Hardware Directory -- always verify.
HANA_INSTANCE_HINTS = [
    (256, "r6i.4xlarge / r7i.4xlarge class (~128-256 GB)"),
    (512, "r6i.8xlarge class (~256-512 GB)"),
    (1024, "r6i.16xlarge / r6i.24xlarge class (~512 GB-1 TB)"),
    (2048, "x2idn.16xlarge / x2iedn.16xlarge class (~1-2 TB)"),
    (4096, "x2idn.32xlarge / x2iedn.32xlarge class (~2-4 TB)"),
    (6144, "u-6tb1 High Memory (~6 TB)"),
    (12288, "u-12tb1 High Memory (~12 TB)"),
    (24576, "u-24tb1 High Memory (~24 TB)"),
]


def estimate_saps(users: int | None, activity: str, measured_saps: int | None) -> int:
    if measured_saps is not None:
        return measured_saps
    if users is None:
        raise ValueError("Provide either --measured-saps or --users.")
    per_user = SAPS_PER_USER[activity]
    return users * per_user


def estimate_hana_ram_gb(hana_data_gb: float, compression: float, working_factor: float,
                         os_headroom_gb: float) -> float:
    """Very rough HANA RAM estimate.

    in-memory footprint ~= raw data / compression ratio
    total RAM           ~= in-memory footprint * working_factor + OS/services headroom

    SAP's real sizing (e.g. /SDF/HDB_SIZING) is far more nuanced. Teaching approximation.
    """
    in_memory = hana_data_gb / compression
    return in_memory * working_factor + os_headroom_gb


def suggest_instance(ram_gb: float) -> str:
    for ceiling, hint in HANA_INSTANCE_HINTS:
        if ram_gb <= ceiling:
            return hint
    return "Multiple High Memory instances / HANA scale-out -- engage AWS + SAP sizing."


def suggest_app_tier(saps: int) -> str:
    # Illustrative: assume a modern app-tier instance delivers ~10k-25k SAPS.
    per_instance = 20000
    n = max(1, -(-saps // per_instance))  # ceil division
    return (f"~{n} application-server instance(s) (m6i/r6i class), spread across >=2 AZs "
            f"for HA (assuming ~{per_instance:,} SAPS/instance -- verify per type).")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--users", type=int, help="Number of concurrently active SAP users.")
    p.add_argument("--activity", choices=SAPS_PER_USER, default="medium",
                   help="User activity profile (default: medium).")
    p.add_argument("--measured-saps", type=int,
                   help="Known SAPS requirement (overrides --users).")
    p.add_argument("--hana-data-gb", type=float, default=0.0,
                   help="Raw (uncompressed) DB data size in GB for HANA RAM sizing.")
    p.add_argument("--compression", type=float, default=3.0,
                   help="Assumed HANA compression ratio (default 3.0x).")
    p.add_argument("--working-factor", type=float, default=2.0,
                   help="Multiplier for work/temp space over the in-memory footprint "
                        "(default 2.0 -- SAP often uses ~2x column store).")
    p.add_argument("--os-headroom-gb", type=float, default=64.0,
                   help="RAM reserved for OS + HANA services (default 64 GB).")
    args = p.parse_args(argv)

    print("=" * 68)
    print("SAP sizing estimate (EDUCATIONAL rule-of-thumb -- verify with SAP tools)")
    print("=" * 68)

    try:
        saps = estimate_saps(args.users, args.activity, args.measured_saps)
    except ValueError as exc:
        p.error(str(exc))
        return 2

    print(f"\nApplication tier")
    print(f"  Estimated SAPS requirement : {saps:,}")
    print(f"  Suggestion                 : {suggest_app_tier(saps)}")

    if args.hana_data_gb > 0:
        ram = estimate_hana_ram_gb(args.hana_data_gb, args.compression,
                                   args.working_factor, args.os_headroom_gb)
        print(f"\nDatabase tier (HANA)")
        print(f"  Raw data size              : {args.hana_data_gb:,.0f} GB")
        print(f"  Assumed compression        : {args.compression:.1f}x")
        print(f"  Est. in-memory footprint   : {args.hana_data_gb / args.compression:,.0f} GB")
        print(f"  Est. required RAM          : {ram:,.0f} GB "
              f"(x{args.working_factor:.1f} + {args.os_headroom_gb:.0f} GB headroom)")
        print(f"  Candidate instance         : {suggest_instance(ram)}")
    else:
        print("\n(Provide --hana-data-gb to also estimate the HANA database tier.)")

    print("\nNext steps:")
    print("  * Confirm the exact certified type in the SAP HANA Hardware Directory")
    print("    and SAP Note 1656099 / 2718982.")
    print("  * See ../03-sap-on-aws/02-compute-and-sizing.md and 03-storage.md.")
    print("  * Plan the EBS layout with:  python ebs_storage_planner.py --ram-gb <RAM>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
