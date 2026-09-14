# Lab 01 — VPC Foundation for SAP

Build the network the whole SAP landscape sits in: a **two-AZ VPC** with `public`,
`app`, and `db` subnets, an Internet Gateway, optional NAT Gateway(s), route tables, and
an **S3 gateway VPC endpoint** (for Backint backups without internet).

This is the skeleton from `../../03-sap-on-aws/01-reference-architecture.md`.

## What it creates

```
VPC (default 10.0.0.0/16) across 2 AZs
├── public-a / public-b   → route 0.0.0.0/0 to IGW
├── app-a    / app-b      → route 0.0.0.0/0 to NAT (if enabled)
├── db-a     / db-b       → private, no default internet route
├── Internet Gateway
├── NAT Gateway(s)        → optional (var.enable_nat), COSTS MONEY
├── Route tables (public, app, db) wired per AZ
└── S3 Gateway VPC Endpoint (free) attached to the app/db route tables
```

## Cost note

- The VPC, subnets, route tables, IGW, and **S3 gateway endpoint are free**.
- **NAT Gateways cost ~$0.045/hr each + data.** They're **off by default**
  (`enable_nat = false`). Turn them on only when you actually need private-subnet
  outbound internet, and destroy afterward.

## Run

```bash
terraform init
terraform plan  -var 'aws_region=eu-central-1'
terraform apply -var 'aws_region=eu-central-1'
# inspect:
terraform output
# tear down:
terraform destroy -var 'aws_region=eu-central-1'
```

Set `-var 'enable_nat=true'` to add NAT Gateways (remember the cost).

## Things to explore after `apply`

- In the console: **VPC → Subnets** — note each subnet's AZ.
- **VPC → Route tables** — see how `db-*` has no `0.0.0.0/0` route (truly private) while
  `public-*` routes to the IGW.
- **VPC → Endpoints** — the S3 gateway endpoint and which route tables it's on.
- Map each piece back to the reference architecture diagram.

## Learning questions

1. Which subnets are public and how can you tell from the route tables?
2. Why is the S3 gateway endpoint valuable for a HANA host doing Backint backups?
3. What would you pay for if you set `enable_nat=true` and forgot to destroy?
