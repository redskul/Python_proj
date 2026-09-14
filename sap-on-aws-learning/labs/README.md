# Labs — deploy it yourself with Terraform

Hands-on beats reading. These labs build the SAP-on-AWS reference architecture piece by
piece using **Terraform**.

## Before you start — read this

- **Set a Billing budget alarm first** (`../01-aws-fundamentals/10-cost-and-billing.md`).
- The labs default to the **cheapest** viable resources (small instances, no idle NAT
  where avoidable). Even so, **NAT Gateways, and any large instance in lab03, cost real
  money.**
- **Always `terraform destroy` when you finish a session.**
- Never run these against a production account.

## Prerequisites

```bash
terraform version      # >= 1.5
aws sts get-caller-identity   # you're authenticated
```

## The labs

| Lab | Builds | Deployable? | Rough cost if left running |
|-----|--------|-------------|----------------------------|
| [lab01-vpc-foundation](lab01-vpc-foundation/) | Multi-AZ VPC: public/app/db subnets, IGW, (optional) NAT, route tables, S3 endpoint | **Yes** (Free-Tier-ish; NAT optional) | ~$0 without NAT; ~$0.05/hr per NAT |
| [lab02-ec2-bastion](lab02-ec2-bastion/) | SSM-managed host (no SSH keys) + an "app-tier" `t3.micro` in a private subnet | **Yes** (Free Tier) | ~free (t3.micro) |
| [lab03-hana-host](lab03-hana-host/) | An EC2 with the **correct HANA EBS volume layout** (data/log/shared/usr-sap) | **Yes but $$$** — reads a `hana_instance_type` var; defaults to a *small* type for learning the layout | depends on instance |
| [lab04-ha-overview](lab04-ha-overview/) | **Reading + snippets**: Pacemaker / HSR / overlay-IP design (no deploy) | No (walkthrough) | $0 |

## Recommended order

1. `lab01` — get the network right; inspect the route tables and subnets in the console.
2. `lab02` — connect to a private instance via **SSM Session Manager** (no keys!).
3. `lab03` — see how HANA storage is modelled; deploy with a tiny instance to keep cost
   near zero, or just read the plan.
4. `lab04` — understand HA before you'd ever build it for real.

## The Terraform workflow (same for every lab)

```bash
cd lab01-vpc-foundation
terraform init          # download the AWS provider
terraform plan          # preview what will be created
terraform apply         # create it (type 'yes')
# ... explore in the AWS console / with the AWS CLI ...
terraform destroy       # tear it ALL down (type 'yes')  <-- don't skip
```

Each lab has its own `README.md`, `variables.tf` (knobs), `main.tf`, and `outputs.tf`.
