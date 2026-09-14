# Phase 1 — AWS Fundamentals

Everything you need to understand AWS before layering SAP on top. If you can explain
each of these to a colleague, you're ready for phase 2.

Read in order:

| # | Topic | Why it matters for SAP later |
|--:|-------|------------------------------|
| 01 | [Cloud concepts & global infrastructure](01-cloud-concepts.md) | Regions/AZs decide where SAP HA can live |
| 02 | [IAM — identity & access](02-iam.md) | Least-privilege for basis admins, Backint roles |
| 03 | [VPC & networking](03-vpc-networking.md) | SAP needs private subnets, overlay IPs, DNS |
| 04 | [EC2 — compute](04-ec2-compute.md) | SAP app & DB servers are EC2 instances |
| 05 | [Storage — EBS, EFS, FSx, S3](05-storage.md) | HANA data/log volumes, /sapmnt, backups |
| 06 | [Databases — RDS, Aurora, and where HANA fits](06-databases.md) | AnyDB vs HANA on EC2 |
| 07 | [Monitoring & management](07-monitoring-and-management.md) | CloudWatch, Systems Manager, Data Provider for SAP |
| 08 | [Security](08-security.md) | Encryption, KMS, Secrets Manager, network security |
| 09 | [Resiliency — HA & DR](09-resiliency-ha-dr.md) | Multi-AZ SAP clusters, pilot light DR |
| 10 | [Cost & billing](10-cost-and-billing.md) | SAP is expensive; RIs/Savings Plans matter |

---

## The 5-sentence AWS mental model

1. **AWS is a set of on-demand services** you rent by the second/hour/GB, grouped
   into **Regions** (geographic) made of isolated **Availability Zones** (data centres).
2. **IAM** decides *who* can do *what*; nothing happens without permission.
3. **Compute** (EC2, Lambda, containers) runs your code; **storage** (EBS, S3, EFS,
   FSx) holds your data; **networking** (VPC) connects it privately.
4. The **shared responsibility model**: AWS secures the cloud *infrastructure*; **you**
   secure what you put *in* it (OS patching, SAP config, data, IAM).
5. You design for **failure**: spread across AZs, automate with Infrastructure as
   Code, monitor everything, and pay only for what you use.

Keep this model in mind — every SAP-on-AWS decision is an application of it.
