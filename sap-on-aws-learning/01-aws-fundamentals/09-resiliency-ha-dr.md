# 09 — Resiliency: High Availability & Disaster Recovery

SAP is business-critical, so this module and its SAP-specific companion
(`03-sap-on-aws/05-high-availability-and-dr.md`) are the heart of the curriculum.

## The vocabulary (nail these)

- **RPO (Recovery Point Objective)**: max acceptable **data loss**, expressed as time
  ("we can lose at most 5 minutes of data").
- **RTO (Recovery Time Objective)**: max acceptable **downtime** ("back up within 1
  hour").
- **HA**: survive component/AZ failure automatically, small RTO, within a Region.
- **DR**: survive a whole-Region failure, using a second Region.

Lower RPO/RTO = higher cost. Match the objective to the business criticality.

## Design principles

1. **Eliminate single points of failure** — spread across **≥ 2 AZs**.
2. **Automate recovery** — Auto Scaling, health checks, cluster software.
3. **Test failover regularly** — a DR plan you've never tested is a hope, not a plan.
4. **Back up and test restores** — a backup you can't restore is worthless.

## HA building blocks on AWS

- **Multi-AZ deployment**: primary in AZ-a, standby in AZ-b.
- **Elastic Load Balancer + health checks**: route only to healthy targets.
- **Auto Scaling Group**: replace failed instances, scale with load (app tier).
- **Cluster software** (Pacemaker/corosync on SLES/RHEL) for the DB & ASCS tiers,
  moving an **overlay IP** between AZs (SAP-specific — see phase 3).

## The four DR strategies (increasing cost & decreasing RTO)

| Strategy | What's running in DR Region | RTO | RPO | Cost |
|----------|-----------------------------|-----|-----|------|
| **Backup & Restore** | Nothing; just backups in S3 | Hours | Hours | $ |
| **Pilot Light** | Core (DB replicating), minimal compute off | 10s of min | Minutes | $$ |
| **Warm Standby** | Scaled-down full stack running | Minutes | Seconds–min | $$$ |
| **Multi-Site Active/Active** | Full stack live in both | ~0 | ~0 | $$$$ |

For SAP, **Pilot Light** (HANA System Replication async to the DR Region, app servers
pre-baked as AMIs and started on failover) is the common cost/RTO sweet spot.

## Backups (recap + SAP angle)

- **EBS snapshots**: point-in-time volume backups (incremental, in S3).
- **S3 + lifecycle → Glacier**: long-term retention.
- **Cross-Region replication / copy snapshots**: get backups *out of the primary Region*
  so a regional event doesn't take the backups with it.
- **SAP:** HANA backups via **Backint → S3**, optionally copied cross-Region for DR.

## Worked example — SAP tiers mapped to AWS HA

| SAP tier | Failure protection |
|----------|--------------------|
| **HANA DB** | Sync **HANA System Replication** across AZ-a/AZ-b + Pacemaker + overlay IP |
| **(A)SCS** (central services, single point of failure in SAP) | **ENSA2** + Pacemaker cluster across AZs, EFS/FSx for shared FS |
| **App servers (PAS/AAS)** | Multiple dialog instances across AZs (+ optional ASG) |
| **Web Dispatcher / Fiori** | Behind an ALB across AZs |

## Self-check

1. Your business says "we can lose at most 15 minutes of SAP data but must be back in
   30 minutes." Which DR strategy roughly fits, and what replicates the DB?
2. What is the classic **single point of failure** in a SAP NetWeaver system, and how
   is it protected on AWS?
3. Why copy EBS snapshots / HANA backups to a **second Region**?

<details><summary>Answers</summary>

1. **Warm Standby** (or aggressive Pilot Light); **HANA System Replication** (async to
   the DR Region) replicates the DB.
2. The **(A)SCS** (enqueue + message server); protected by an **ENSA2 Pacemaker cluster**
   across two AZs with shared storage and an overlay IP.
3. So a whole-Region outage doesn't also destroy your only backups — DR needs backups
   outside the failed Region.
</details>
