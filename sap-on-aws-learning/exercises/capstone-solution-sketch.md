# Capstone — worked solution sketch

For the retailer brief in `study-plan.md`. This is **one reasonable answer**, not the
only one. Verify every instance/OS/support claim against current SAP Notes + the SAP
HANA Hardware Directory before real use.

**Brief recap:** S/4HANA, HANA working set ≈ 800 GB, ~600 medium-activity users,
**RPO ≤ 5 min / RTO ≤ 30 min** for a Region failure, automatic single-AZ survival, EU
data residency, plus non-HA Dev & QA.

## 1. Region & network
- **Primary Region:** an EU Region (e.g. `eu-central-1`) for data residency.
- **DR Region:** a second EU Region (e.g. `eu-west-1`).
- **VPC** `10.0.0.0/16`, subnets across **2 AZs**: public / app / db per AZ (as lab01).
- **Direct Connect** (or VPN) to the corporate network; **VPC endpoints** for S3/KMS/SSM.

## 2. Sizing (use the calculators, then verify)
- **HANA RAM:** ~800 GB working set. Using `saps_sizing_calculator.py` with a 3x
  compression assumption gives a smaller in-memory figure, but you size for the **actual
  working set + working/temp + headroom** → target a certified instance with **~1 TB
  RAM** (e.g. an `r6i.24xlarge`/`r6i.32xlarge`-class or `x2idn.16xlarge`-class certified
  type). Confirm max supported memory in the Hardware Directory.
- **App tier:** 600 medium users → ~15,000 SAPS (calculator). Two app-server instances
  (e.g. `m6i`/`r6i`) across the two AZs for HA + capacity.
- **OS:** SLES for SAP or RHEL for SAP.

## 3. HA (within the primary Region)
- **HANA:** primary in AZ-a, secondary in AZ-b, **HSR sync**, **Pacemaker** + **overlay
  IP** → automatic AZ failover, RPO ≈ 0, RTO minutes. (Satisfies "survive single-AZ
  automatically.")
- **(A)SCS/ERS:** ENSA2 Pacemaker cluster across AZs, `/sapmnt` on **EFS/FSx**, overlay
  IP.
- **App servers:** multiple dialog instances across both AZs behind SAP logon groups;
  Fiori/Web Dispatcher behind an **ALB**.

## 4. DR (Region failure — RPO ≤ 5 min, RTO ≤ 30 min)
- **Pilot Light** in the DR Region:
  - **HANA System Replication async** to a running DR-Region secondary → RPO within
    minutes (meets ≤ 5 min with frequent log shipping).
  - App/ASCS servers pre-baked as **AMIs / IaC**, kept **stopped**; started on failover
    (meets ≤ 30 min RTO).
  - **Route 53** to redirect clients on failover.
- **Backups copied cross-Region** as a floor.
- **Test the failover** on a schedule.

## 5. Storage (HANA, from ebs_storage_planner.py for ~1 TB RAM)
- `/hana/data`: ~1.2 TB, several **gp3** volumes LVM-striped for throughput.
- `/hana/log`: gp3/io2, IOPS-tuned for low latency.
- `/hana/shared`, `/usr/sap`, root: gp3.
- **EBS encryption (KMS CMK)**; validate with **HCMT** before go-live.

## 6. Backup
- **AWS Backint Agent → S3**; log backups every ≤ 5 min (drives RPO).
- Lifecycle old backups → Glacier Deep Archive; **Object Lock (WORM)** + **cross-Region
  copy** for ransomware/DR resilience; consider a separate backup account.

## 7. Cost
- **Savings Plans / RIs** for the 24/7 PRD HANA + app instances.
- **Dev & QA:** smaller (right-sized) instances, single-AZ, **scheduled start/stop**
  off-hours (big saving; they don't need HA).
- Tag everything (`SID`, `Environment`, `Component`, `CostCenter`); watch Cost Explorer.

## 8. Security baseline
- Private subnets for all SAP hosts; **SSM Session Manager** (no SSH keys); **IMDSv2**.
- **IAM roles** on hosts (Backint→S3, CloudWatch, SSM); **Secrets Manager** for DB creds.
- Least-privilege SGs between tiers; **KMS CMKs** for EBS/S3/HANA encryption.
- **CloudTrail + Config + GuardDuty + Security Hub + Inspector** landscape-wide.
- Review against the **Well-Architected SAP Lens**.

## Sanity check against the brief
| Requirement | Met by |
|-------------|--------|
| Survive single AZ automatically | HSR sync + Pacemaker + overlay IP (HANA & ASCS) |
| RPO ≤ 5 min (Region DR) | HSR async + ≤ 5-min log backups cross-Region |
| RTO ≤ 30 min (Region DR) | Pilot light: pre-baked AMIs/IaC started on failover + Route 53 |
| EU data residency | Primary + DR both EU Regions |
| Dev/QA without HA, cheaper | Right-sized, single-AZ, start/stop schedule |
