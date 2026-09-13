# 07 — Migrating SAP to AWS

Most SAP-on-AWS work starts as a **migration** from on-prem (or another cloud). Know the
approaches, the tools, and how the choice interacts with an S/4HANA conversion.

## The two dimensions of an SAP migration

1. **Where** (infrastructure): on-prem → AWS.
2. **What** (software): stay on ECC/AnyDB, or move to **S/4HANA/HANA** at the same time.

Combining them (convert to S/4HANA *and* move to AWS) is common but riskier; many
projects **decouple** — lift to AWS first, convert later, or vice versa.

## The "6 Rs" of migration (AWS framing)

| R | Meaning | SAP example |
|---|---------|-------------|
| **Rehost** | Lift & shift, no change | Move ECC-on-Oracle VMs to EC2 as-is |
| **Replatform** | Lift & optimise | Move ECC and switch DB to HANA (DB migration) |
| **Repurchase** | Move to a different product | Adopt **RISE with SAP** / S/4HANA Cloud |
| **Refactor** | Re-architect | Re-implement processes greenfield on S/4HANA |
| **Retire** | Decommission | Sunset unused SAP add-ons |
| **Retain** | Keep as-is (for now) | Leave a system on-prem temporarily |

## SAP-specific migration techniques

- **Homogeneous system copy** — same OS/DB on both sides → backup/restore or storage
  copy. Simplest (rehost).
- **Heterogeneous system copy / OS-DB migration** — change OS or DB → **SWPM** +
  **R3load/Migration Monitor** (export/import). Used when switching to HANA.
- **DMO (Database Migration Option) of SUM** — **upgrade + migrate to HANA in one run**;
  the standard for **ECC → S/4HANA** conversions. "**DMO with System Move**" migrates to
  a target host **on AWS** in the same step.
- **HANA System Replication** — can be used to move a HANA DB to AWS with minimal
  downtime (replicate to an AWS secondary, then take over).
- **Backup/restore to AWS** — Backint/native backup on-prem → restore on EC2.

## Moving the data to AWS

- **AWS Direct Connect** — dedicated bandwidth for large migration transfers.
- **AWS DataSync** — move file data (e.g. exports, `/sapmnt`) efficiently.
- **AWS Snowball** — offline device for very large datasets where the network is too
  slow.
- **S3** — staging area for exports/backups being restored on EC2.

## Minimising downtime

- **HSR takeover** (near-zero downtime for the DB move).
- **DMO with System Move** (combines conversion + relocation).
- **Downtime-optimized DMO** for large systems.
- Do trial runs; measure the migration window against the business's allowed downtime.

## AWS tools that help

- **AWS Launch Wizard for SAP** — pre-provision the SAP-certified **target** infra on
  AWS to migrate into (next module).
- **AWS Application Migration Service (MGN)** / **Elastic DR (DRS)** — block-level rehost
  of servers (useful for app servers / AnyDB rehost).
- **CloudEndure**-style continuous replication (now MGN/DRS).

## A typical migration project shape

1. **Assess & size** — inventory systems, size the AWS target (SAPS/RAM), pick certified
   instances.
2. **Design** — VPC, subnets, HA/DR, storage, security, connectivity (DX).
3. **Build target** — Launch Wizard / Terraform provisions the certified landscape.
4. **Migrate** — pick technique (rehost / replatform / DMO), transfer data (DX/DataSync/
   Snowball).
5. **Validate** — HCMT, functional & performance tests, SAP EarlyWatch.
6. **Cut over** — final sync, switch users (Route 53 / DNS), decommission source.
7. **Optimise** — Savings Plans, right-size, start/stop non-prod.

## Self-check

1. What's the difference between **rehost** and **replatform** for an ECC-on-Oracle
   system?
2. Which SAP tool performs an **ECC → S/4HANA conversion and HANA migration in one run**,
   and what variant relocates to AWS at the same time?
3. Your dataset is 80 TB and the network link is slow — which AWS service moves it?
4. Which technique gives **near-zero downtime** for moving a HANA DB to AWS?

<details><summary>Answers</summary>

1. Rehost = lift the VMs to EC2 unchanged (still Oracle). Replatform = also switch the
   DB (e.g. to HANA) during the move.
2. **SUM with DMO**; **DMO with System Move** relocates the target to AWS in the same
   procedure.
3. **AWS Snowball** (offline bulk transfer).
4. **HANA System Replication** takeover (replicate to an AWS secondary, then switch).
</details>
