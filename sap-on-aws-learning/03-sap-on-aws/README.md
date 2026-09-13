# Phase 3 — SAP on AWS (the specialty)

This is where the two halves meet. You know AWS (phase 1) and SAP (phase 2); now learn
how to run SAP on AWS **to SAP's support requirements and KPIs**. This phase maps to the
**AWS Certified: SAP on AWS – Specialty (PAS-C01)** exam.

Read in order:

| # | Topic |
|--:|-------|
| 01 | [Reference architecture](01-reference-architecture.md) — the whole picture |
| 02 | [Compute & sizing](02-compute-and-sizing.md) — SAPS, certified instances |
| 03 | [Storage](03-storage.md) — HANA volume layout & KPIs |
| 04 | [Networking](04-networking.md) — subnets, overlay IP, endpoints, hybrid |
| 05 | [High availability & DR](05-high-availability-and-dr.md) — Pacemaker, HSR, multi-AZ |
| 06 | [Backup & recovery](06-backup-and-recovery.md) — Backint, snapshots, AWS Backup |
| 07 | [Migration to AWS](07-migration.md) — approaches & tools |
| 08 | [Automation: Launch Wizard & IaC](08-automation-launch-wizard.md) |
| 09 | [Operations & security](09-operations-and-security.md) — patching, monitoring, cost |

## The golden rule of SAP on AWS

> **SAP support is defined by SAP Notes + the AWS certification.** Before you choose an
> instance, an OS, or an HA design, check that the combination is **SAP-certified** and
> **AWS-supported**. Key references you should bookmark:
> - **SAP Note 1656099** — SAP on AWS: supported products & instance types.
> - **SAP Note 1656250** — SAP on AWS: support prerequisites.
> - **SAP Note 2718982** — SAP HANA on AWS.
> - **SAP on AWS documentation** — <https://docs.aws.amazon.com/sap/>.
> - The **SAP Certified and Supported SAP HANA Hardware Directory** (certified IaaS).
>
> (Note numbers/policies change over time — always verify the current version.)

## Certified building blocks at a glance

| Layer | SAP-on-AWS choice |
|-------|-------------------|
| Compute | **SAP-certified EC2** (R/X/U families for HANA; M/R for app) |
| OS | **SLES for SAP** or **RHEL for SAP** (from Marketplace, includes support) |
| Storage | **gp3 / io2** tuned to SAP KPIs; **EFS/FSx** for shared FS |
| DB | **HANA on EC2** (self-managed); AnyDB on EC2; RDS for Db2 (supported cases) |
| HA | **HSR sync across AZs** + **Pacemaker** + **overlay IP** |
| DR | **HSR async cross-Region** (pilot light) |
| Backup | **AWS Backint Agent → S3**, EBS snapshots, AWS Backup |
| Deploy | **AWS Launch Wizard for SAP**, Terraform/CloudFormation |
| Monitor | **CloudWatch** + **AWS Data Provider for SAP** + SolMan |
