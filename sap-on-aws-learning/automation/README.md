# Automation — boto3 & sizing helpers

Runnable Python that reinforces the theory. Two kinds of script:

- **Pure calculators** (no AWS account needed): `saps_sizing_calculator.py`,
  `ebs_storage_planner.py`.
- **AWS-connected** (need credentials): `preflight_check.py`,
  `list_sap_certified_instances.py`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

AWS-connected scripts use your normal credential chain (env vars, `~/.aws/credentials`,
or an instance role). Configure with `aws configure` first (see
`../00-getting-started/README.md`).

## Scripts

| Script | Needs AWS? | What it does |
|--------|-----------|--------------|
| `preflight_check.py` | Yes | Verifies boto3 + credentials + identity + region; a friendly first run |
| `list_sap_certified_instances.py` | Yes | Lists EC2 instance types in a Region, filtered by memory/family, annotated with which are commonly SAP/HANA-relevant |
| `saps_sizing_calculator.py` | No | Turns business inputs into a rough SAPS + memory estimate and suggests instance families |
| `ebs_storage_planner.py` | No | Proposes a HANA EBS volume layout (data/log/shared) from a target RAM size |

> ⚠️ The "certified" annotations are **heuristics for learning** (family + memory
> thresholds). **Always confirm against the SAP HANA Hardware Directory and SAP Note
> 1656099 / 2718982** before using anything for a real deployment.

## Examples

```bash
python preflight_check.py
python list_sap_certified_instances.py --region eu-central-1 --min-memory-gb 128 --hana-only
python saps_sizing_calculator.py --users 800 --activity medium --hana-data-gb 500
python ebs_storage_planner.py --ram-gb 1024
```

Every script supports `--help`.
