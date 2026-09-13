#!/usr/bin/env python3
"""Pre-flight check for the SAP-on-AWS learning environment.

Verifies that boto3 is installed, AWS credentials resolve, and prints who you are and
which Region you're in -- a friendly first script for phase 0. Read-only: it only calls
sts:GetCallerIdentity and ec2:DescribeRegions.

Usage
-----
    python preflight_check.py
    python preflight_check.py --region eu-central-1
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--region", help="Region to test against (defaults to your config).")
    args = p.parse_args(argv)

    print("SAP-on-AWS learning -- pre-flight check")
    print("-" * 45)

    # 1. boto3 present?
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
    except ImportError:
        print("[FAIL] boto3 is not installed.")
        print("       Run:  pip install -r requirements.txt")
        return 1
    print(f"[ OK ] boto3 imported (version {boto3.__version__})")

    session = boto3.session.Session(region_name=args.region)
    region = session.region_name
    if region:
        print(f"[ OK ] Region resolved: {region}")
    else:
        print("[WARN] No default Region set. Pass --region or run 'aws configure'.")

    # 2. Credentials + identity
    try:
        sts = session.client("sts")
        ident = sts.get_caller_identity()
    except (NoCredentialsError, ClientError, BotoCoreError) as exc:
        print(f"[FAIL] Could not get caller identity: {exc}")
        print("       Configure credentials with 'aws configure' (see")
        print("       ../00-getting-started/README.md).")
        return 1
    print(f"[ OK ] Authenticated as: {ident.get('Arn')}")
    print(f"       Account: {ident.get('Account')}")

    # 3. A harmless read to prove API access
    if region:
        try:
            ec2 = session.client("ec2")
            regions = ec2.describe_regions()["Regions"]
            print(f"[ OK ] EC2 API reachable ({len(regions)} regions visible).")
        except (ClientError, BotoCoreError) as exc:
            print(f"[WARN] EC2 DescribeRegions failed: {exc}")

    print("\nYou're ready. Next:")
    print("  python list_sap_certified_instances.py --region", region or "<region>")
    print("  Then head to ../01-aws-fundamentals/README.md")
    print("\nReminder: set a Billing budget alarm BEFORE deploying any labs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
