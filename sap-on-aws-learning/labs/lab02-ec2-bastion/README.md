# Lab 02 — Secure access with SSM (no SSH keys)

Launch an "app-tier" EC2 instance and connect to it with **AWS Systems Manager Session
Manager** — **no SSH key, no open port 22, no bastion host**. This is the pattern you
should use for real SAP hosts (see `../../03-sap-on-aws/09-operations-and-security.md`).

## What it creates

- An **IAM role + instance profile** with the AWS-managed `AmazonSSMManagedInstanceCore`
  policy (lets the instance register with Systems Manager).
- A **security group** with **no inbound rules** (Session Manager needs none) and
  outbound allowed.
- One **`t3.micro`** (Free-Tier-eligible) running Amazon Linux 2023 (AMI resolved from
  the public SSM parameter, so it's always current).
- Optionally, **SSM interface VPC endpoints** (`ssm`, `ssmmessages`, `ec2messages`) so a
  truly **private** instance can reach Session Manager without NAT/internet
  (`var.create_ssm_endpoints = true`; small hourly cost per endpoint).

## Prerequisites — get IDs from lab01

```bash
cd ../lab01-vpc-foundation && terraform output   # note vpc_id and a subnet id
```

- For the **cheapest, no-endpoint** run: pass a **public** subnet id (the instance gets
  a public IP and reaches SSM over the internet — free).
- For the **SAP-realistic private** pattern: pass an **app/db** subnet id **and** set
  `-var 'create_ssm_endpoints=true'` (costs a little).

## Run

```bash
terraform init
terraform apply \
  -var 'aws_region=eu-central-1' \
  -var 'vpc_id=vpc-xxxxxxxx' \
  -var 'subnet_id=subnet-xxxxxxxx'      # a PUBLIC subnet for the free path

# Connect (needs the Session Manager plugin, or use the console):
aws ssm start-session --target "$(terraform output -raw instance_id)"

# Tear down:
terraform destroy -var 'vpc_id=vpc-xxxxxxxx' -var 'subnet_id=subnet-xxxxxxxx'
```

If `start-session` says the target isn't connected, wait ~1–2 min for the SSM agent to
register, and confirm the instance has an outbound path to SSM (public IP, NAT, or the
interface endpoints).

## Why this matters for SAP

- No SSH keys to manage or leak; access is **IAM-controlled and CloudTrail-audited**.
- SAP hosts stay in **private subnets** with **no inbound 22** — a big attack-surface
  reduction.
- The same role can later carry the Backint (S3) and CloudWatch permissions.

## Learning questions

1. How does the instance get admin access with **zero inbound** security-group rules?
2. What three interface endpoints let a fully private instance use Session Manager
   without a NAT Gateway?
3. Why is this safer than a traditional bastion + SSH key?
