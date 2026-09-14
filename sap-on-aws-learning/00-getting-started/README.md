# Phase 0 — Getting Started

Goal: have a safe AWS account, the CLI configured, and Terraform + Python working
before you touch any of the learning content.

---

## 1. Create an AWS account

1. Go to <https://aws.amazon.com> → **Create an AWS Account**.
2. Use a **strong unique password** on the root account and immediately enable
   **MFA** (multi-factor auth) on the root user.
3. **Never use the root user for day-to-day work.** You will create an IAM admin
   user in step 3.

## 2. Set a budget FIRST (do not skip)

Before deploying anything:

- **Billing → Budgets → Create budget → Zero-spend / Monthly cost budget.**
- Set a threshold (e.g. **$10**) and an email alert at 80% and 100%.
- Full walkthrough: `../01-aws-fundamentals/10-cost-and-billing.md`.

SAP-certified instances are large. A single forgotten `x2idn.16xlarge` can cost
**hundreds of dollars per day.** The budget alarm is your safety net.

## 3. Create an IAM admin user

Root account → **IAM → Users → Create user**:

- Name: `admin` (or your name).
- Attach policy: `AdministratorAccess` (fine for a personal learning account; in
  production you'd scope this down — see `../01-aws-fundamentals/02-iam.md`).
- Enable **console access** and **MFA** for this user too.
- Create an **access key** (for CLI). Store it in a password manager — you'll paste
  it into `aws configure` next.

## 4. Install the tooling

| Tool | Version | Purpose |
|------|---------|---------|
| AWS CLI | v2 | Talk to AWS from the terminal |
| Terraform | ≥ 1.5 | Deploy the labs (Infrastructure as Code) |
| Python | ≥ 3.10 | Run the boto3 automation scripts |
| git | any | You already have it |

Install (examples):

```bash
# macOS (Homebrew)
brew install awscli terraform python@3.11

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y python3 python3-venv unzip
# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
# Terraform: follow https://developer.hashicorp.com/terraform/install
```

## 5. Configure the CLI

```bash
aws configure
# AWS Access Key ID:     <from step 3>
# AWS Secret Access Key: <from step 3>
# Default region name:   eu-central-1        # pick one close to you
# Default output format: json
```

Verify:

```bash
aws sts get-caller-identity
# Should print your Account, UserId, and Arn (the admin user).
```

## 6. Set up the Python automation environment

```bash
cd ../automation
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python preflight_check.py          # sanity-checks your AWS + boto3 setup
```

## 7. Region choice matters for SAP

Not every AWS Region offers every **SAP-certified instance type** (especially the
large memory-optimised `x2idn`, `x2iedn`, `u-*` High Memory instances). For general
learning, any major Region works (`us-east-1`, `eu-central-1`, `ap-southeast-1`).
For the SAP labs, check availability with:

```bash
cd ../automation && python list_sap_certified_instances.py --region eu-central-1
```

---

## Checklist before moving on

- [ ] Root user has MFA and is locked away.
- [ ] IAM admin user created, with MFA + access key.
- [ ] **Budget alarm set.**
- [ ] `aws sts get-caller-identity` works.
- [ ] `terraform version` ≥ 1.5.
- [ ] `python preflight_check.py` passes.

Next: **`../01-aws-fundamentals/README.md`**
