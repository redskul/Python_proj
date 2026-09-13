# SAP on AWS — A Hands-On Learning Project

A self-paced curriculum that takes you from **zero AWS knowledge** to being able to
**design, deploy, and operate SAP workloads on AWS**. It covers the AWS fundamentals
first (the same ground as the *AWS Certified Solutions Architect – Associate*), then
SAP fundamentals, and finally the specialised knowledge that maps to the
**AWS Certified: SAP on AWS – Specialty (PAS-C01)** exam.

> This is a **learning** repo. It mixes reading material, quizzes, runnable Python
> (boto3) automation, and Infrastructure-as-Code (Terraform) labs. Everything is
> designed to be run in a *personal* AWS account inside the Free Tier where possible.
> **Never run the SAP HANA labs against production and always destroy resources when
> you finish** — SAP-certified instances are large and expensive.

---

## Who this is for

- Developers / basis admins who know SAP but are new to AWS.
- Cloud engineers who know AWS but are new to SAP.
- Anyone preparing for the **SAP on AWS Specialty** certification.

No prior AWS or SAP experience is strictly required, but comfort with the Linux
command line and basic networking (IP, subnet, DNS) will help.

---

## How the repo is organised

```
sap-on-aws-learning/
├── 00-getting-started/     Set up your AWS account, IAM user, CLI, and tooling
├── 01-aws-fundamentals/    Core AWS: IAM, VPC, EC2, storage, DBs, security, HA, cost
├── 02-sap-fundamentals/    What SAP actually is: NetWeaver, HANA, S/4HANA, landscapes
├── 03-sap-on-aws/          The specialty: sizing, storage KPIs, HA, backup, migration
├── labs/                   Terraform labs you actually deploy
├── automation/             Runnable boto3 scripts (sizing calc, pre-flight checks…)
├── exercises/              A study plan + self-assessment quizzes
└── glossary.md             Every acronym in one place (there are a LOT)
```

Read the modules in order. Each module folder has its own `README.md` acting as a
table of contents.

---

## The learning path

| Phase | Folder | You will be able to… | Time |
|------:|--------|----------------------|------|
| 0 | `00-getting-started` | Log into AWS safely, use the CLI, run Terraform & boto3 | ~2h |
| 1 | `01-aws-fundamentals` | Explain and use IAM, VPC, EC2, EBS/S3/EFS/FSx, RDS, CloudWatch, HA & cost basics | ~15–20h |
| 2 | `02-sap-fundamentals` | Explain the SAP stack: ABAP/Java, HANA, S/4HANA, system landscapes | ~8h |
| 3 | `03-sap-on-aws` | Size, store, protect, migrate and operate SAP on AWS to SAP's KPIs | ~20h |
| ★ | `labs/` + `automation/` | Deploy a VPC, a bastion, and a HANA-ready host; automate sizing | ongoing |

---

## Quick start

```bash
# 1. Read the setup guide and create your AWS account + IAM admin user
open 00-getting-started/README.md

# 2. Install tooling (AWS CLI v2, Terraform >= 1.5, Python 3.10+)
#    Then verify:
aws sts get-caller-identity
terraform version
python3 --version

# 3. Set up the Python automation environment
cd automation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python list_sap_certified_instances.py --help

# 4. Deploy your first lab (a VPC foundation)
cd ../labs/lab01-vpc-foundation
terraform init && terraform plan
```

---

## Cost & safety warning ⚠️

- The **AWS fundamentals** labs are designed for the **Free Tier** (`t3.micro`, small
  EBS, no NAT gateway left running). They cost cents if you clean up.
- The **SAP HANA** labs describe instances like `r5.8xlarge` / `x2idn.16xlarge` and
  large `gp3`/`io2` volumes. These cost **many dollars per hour**. The HANA labs are
  written so you understand the architecture **without** necessarily launching the
  full instance. If you do launch one, **`terraform destroy` the same day.**
- Set a **billing budget + alarm** (see `01-aws-fundamentals/10-cost-and-billing.md`)
  *before* you deploy anything.

---

## Certifications this maps to

1. **AWS Certified Cloud Practitioner (CLF-C02)** — covered by phase 1.
2. **AWS Certified Solutions Architect – Associate (SAA-C03)** — covered by phase 1 + labs.
3. **AWS Certified: SAP on AWS – Specialty (PAS-C01)** — covered by phases 2 & 3.

See `exercises/study-plan.md` for a week-by-week schedule.

---

## License / disclaimer

Educational material. SAP, HANA, S/4HANA, NetWeaver are trademarks of SAP SE.
AWS and service names are trademarks of Amazon.com, Inc. This project is not
affiliated with or endorsed by either company. Always cross-check sizing and
support statements against the official **SAP Notes** and the **AWS documentation**
before using them for a real project — cloud services and SAP support matrices change.
