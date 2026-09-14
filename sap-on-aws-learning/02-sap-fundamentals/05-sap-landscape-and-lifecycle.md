# 05 — SAP System Landscapes & Lifecycle

A single SAP "system" is never alone. Companies run a **landscape** of copies and move
changes through them in a controlled way. This shapes how many EC2 instances you build
and how you automate.

## The classic 3-system landscape

```
   DEV  ──transport──▶  QAS  ──transport──▶  PRD
  (build)              (test)              (production)
   SID: DEV             SID: QAS            SID: PRD
```

- **DEV (Development)** — developers write/customise (ABAP, config). Small, can be
  stopped nights/weekends on AWS to save money.
- **QAS (Quality Assurance / Test)** — changes are tested against near-prod data. Medium.
- **PRD (Production)** — the live business system. Full HA/DR, never experimental.

Some landscapes add **Sandbox (SBX)** and **Pre-Prod / Training** systems.

## Transports — how change flows

A **transport request** packages configuration/code changes. They're released in DEV and
**imported** into QAS, then PRD, in order, via the shared **`/usr/sap/trans`** directory
(on AWS: **EFS/FSx** shared across the landscape). This is SAP's change-management
backbone; on AWS you keep the transport directory available across systems and back it up.

## Sizing the landscape for AWS (cost implications)

| System | Availability need | AWS pattern |
|--------|-------------------|-------------|
| PRD | High (HA multi-AZ + DR) | Big certified instance, HSR sync, Pacemaker, cross-Region DR |
| QAS | Business hours-ish | Medium instance, maybe single-AZ, **start/stop schedule** |
| DEV | Business hours | Smaller instance, **stopped off-hours** |
| SBX | Ad hoc | Smallest, spin up/down on demand |

> **Non-prod start/stop** and **right-sizing** (QAS/DEV don't need PRD-sized RAM) are
> the biggest SAP-on-AWS cost savings. See `01-aws-fundamentals/10-cost-and-billing.md`.

## The lifecycle activities (Basis on AWS)

- **Provision / install**: build the OS + SAP + HANA (AWS Launch Wizard helps).
- **Copy / refresh**: periodically copy PRD data down to QAS/DEV ("system refresh") —
  on AWS, EBS snapshots and HANA backup/restore make this fast.
- **Patch**: OS (SSM Patch Manager), HANA revisions, SAP kernel, SAP Notes.
- **Upgrade / convert**: SUM/DMO (e.g. ECC → S/4HANA).
- **Monitor**: CloudWatch + SAP Solution Manager + Data Provider for SAP.
- **Back up / DR test**: Backint to S3, cross-Region copies, restore drills.
- **Decommission**: snapshot, archive to S3/Glacier, terminate.

## SAP Solution Manager (SolMan)

SAP's central management system for the landscape (monitoring, change control, root
cause analysis). Often itself an EC2-hosted SAP system in the landscape.

## Naming & tagging tie-in

Because you'll have many systems, **tag every AWS resource** with its `SID` and
`Environment` (see the cost module). It's the only sane way to answer "which instances
belong to QAS?" and "what does PRD cost?".

## Self-check

1. Draw the flow of a change from a developer's keyboard to production, naming the
   systems and the mechanism between them.
2. Which non-prod cost optimisation is uniquely easy in a landscape, and why is it safe?
3. What shared directory must be reachable across the whole landscape, and what AWS
   service provides it?

<details><summary>Answers</summary>

1. DEV → (transport request) → QAS → (transport) → PRD, moved via `/usr/sap/trans`.
2. **Scheduled start/stop** of DEV/QAS — they're not needed 24/7, so stopping them
   off-hours cuts cost with no business impact.
3. **`/usr/sap/trans`** (the transport directory) — provided by **EFS** or **FSx**.
</details>
