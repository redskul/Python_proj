#!/usr/bin/env python3
"""List EC2 instance types in a Region, annotated for SAP relevance (educational).

Queries EC2 for instance types available in a Region and filters by memory and family,
marking which are commonly used for SAP HANA vs the SAP application tier.

IMPORTANT: the "SAP relevance" flags here are HEURISTICS based on instance family and
memory (memory-optimised R/X and High-Memory U families for HANA). They are a learning
aid ONLY. The authoritative source is the SAP Certified and Supported SAP HANA Hardware
Directory plus SAP Notes 1656099 / 2718982 -- always confirm there before deploying.

Requires AWS credentials (read-only: ec2:DescribeInstanceTypes /
DescribeInstanceTypeOfferings).

Examples
--------
    python list_sap_certified_instances.py --region eu-central-1
    python list_sap_certified_instances.py --region us-east-1 --min-memory-gb 512 --hana-only
"""
from __future__ import annotations

import argparse
import sys

# Families commonly used for the HANA database tier (memory-optimised / high memory).
HANA_FAMILIES = ("r5", "r5b", "r6i", "r6id", "r7i", "r7iz",
                 "x1", "x1e", "x2idn", "x2iedn", "x2iezn",
                 "u-", "hpc")  # 'u-' covers High Memory (u-6tb1 etc.)

# Families commonly used for the SAP application tier.
APP_FAMILIES = ("m5", "m5d", "m6i", "m6id", "m7i", "c5", "c6i", "c7i") + HANA_FAMILIES


def family_of(instance_type: str) -> str:
    """'r6i.8xlarge' -> 'r6i';  'u-6tb1.112xlarge' -> 'u-'."""
    if instance_type.startswith("u-"):
        return "u-"
    return instance_type.split(".", 1)[0]


def sap_role(instance_type: str) -> str:
    fam = family_of(instance_type)
    is_hana = fam.startswith(HANA_FAMILIES)
    if is_hana:
        return "HANA+app"
    if fam.startswith(APP_FAMILIES):
        return "app"
    return "-"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--region", help="AWS Region (defaults to your configured Region).")
    p.add_argument("--min-memory-gb", type=float, default=0.0,
                   help="Only show types with at least this much RAM.")
    p.add_argument("--max-memory-gb", type=float, default=float("inf"),
                   help="Only show types with at most this much RAM.")
    p.add_argument("--hana-only", action="store_true",
                   help="Only show HANA-relevant (memory-optimised / high-memory) types.")
    p.add_argument("--limit", type=int, default=60,
                   help="Max rows to print (default 60).")
    args = p.parse_args(argv)

    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        print("boto3 not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        return 1

    session = boto3.session.Session(region_name=args.region)
    region = session.region_name
    if not region:
        print("No Region set. Pass --region or run 'aws configure'.", file=sys.stderr)
        return 2
    ec2 = session.client("ec2")

    # 1. Which instance types are actually offered in this Region?
    try:
        offered: set[str] = set()
        paginator = ec2.get_paginator("describe_instance_type_offerings")
        for page in paginator.paginate(LocationType="region"):
            for off in page["InstanceTypeOfferings"]:
                offered.add(off["InstanceType"])
    except (NoCredentialsError, ClientError, BotoCoreError) as exc:
        print(f"Failed to list offerings in {region}: {exc}", file=sys.stderr)
        return 1

    # 2. Get details (memory, vCPU) for the ones we care about.
    candidates = sorted(t for t in offered
                        if family_of(t).startswith(APP_FAMILIES))
    rows = []
    try:
        # DescribeInstanceTypes accepts up to 100 names per call.
        for i in range(0, len(candidates), 100):
            chunk = candidates[i:i + 100]
            resp = ec2.describe_instance_types(InstanceTypes=chunk)
            for it in resp["InstanceTypes"]:
                mem_gb = it["MemoryInfo"]["SizeInMiB"] / 1024.0
                vcpu = it["VCpuInfo"]["DefaultVCpus"]
                itype = it["InstanceType"]
                role = sap_role(itype)
                if args.hana_only and role != "HANA+app":
                    continue
                if not (args.min_memory_gb <= mem_gb <= args.max_memory_gb):
                    continue
                rows.append((itype, vcpu, mem_gb, role))
    except (ClientError, BotoCoreError) as exc:
        print(f"Failed to describe instance types: {exc}", file=sys.stderr)
        return 1

    rows.sort(key=lambda r: (r[2], r[0]))  # by memory, then name

    print(f"# SAP-relevant EC2 instance types offered in {region}")
    print(f"# filters: min_mem={args.min_memory_gb} GB, max_mem={args.max_memory_gb} GB, "
          f"hana_only={args.hana_only}")
    print(f"# {'instance type':<20}{'vCPU':>6}{'memory (GB)':>14}   SAP role (heuristic)")
    print("# " + "-" * 62)
    for itype, vcpu, mem_gb, role in rows[:args.limit]:
        print(f"  {itype:<20}{vcpu:>6}{mem_gb:>14,.0f}   {role}")
    if len(rows) > args.limit:
        print(f"  ... {len(rows) - args.limit} more (raise --limit to see them)")

    print()
    print("!! Heuristic only. Confirm certification + max supported memory in the")
    print("!! SAP HANA Hardware Directory and SAP Note 1656099 / 2718982 before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
