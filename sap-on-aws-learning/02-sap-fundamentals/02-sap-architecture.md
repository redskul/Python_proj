# 02 — SAP Architecture (NetWeaver & the 3 tiers)

To run SAP on AWS you must know what the pieces *are*, because each maps to specific
EC2 instances, storage, and network rules.

## The classic 3-tier architecture

```
   Presentation tier      →   Application tier        →   Database tier
   (SAP GUI / Fiori /          (SAP kernel: ABAP           (HANA or AnyDB)
    browser)                    &/or Java work
                                processes)
```

1. **Presentation tier** — the user's client: **SAP GUI** (thick client) or **Fiori**
   (browser). Lives on user laptops; on AWS you mainly worry about *reaching* it with
   low latency (Direct Connect / VPN).
2. **Application tier** — the **SAP kernel** running work processes that execute
   business logic (ABAP programs, or Java). Scales **horizontally**: multiple
   application server instances. On AWS = multiple EC2 instances.
3. **Database tier** — persists everything. **HANA** (strategic) or an AnyDB. On AWS =
   EC2 (self-managed).

## Key components of a NetWeaver ABAP system

| Component | Role | AWS/HA note |
|-----------|------|-------------|
| **(A)SCS** — ABAP SAP Central Services | Holds the **Message Server** (load balancing/logon) and **Enqueue Server** (lock management). | **Single point of failure** → must be clustered (ENSA2 + Pacemaker across AZs). |
| **PAS** — Primary Application Server | The first/central app server instance. | EC2 in a private subnet. |
| **AAS** — Additional Application Server(s) | Extra dialog instances for scale/HA. | More EC2, across AZs. |
| **Database** | HANA / AnyDB. | Its own EC2 + storage + HA. |
| **SAP Web Dispatcher** | Reverse proxy / load balancer for HTTP(S)/Fiori. | Behind an AWS ALB. |
| **`/sapmnt`** | Shared SAP directory (profiles, kernel, global data). | Shared FS: **EFS** or **FSx**. |
| **`/usr/sap/trans`** | Transport directory shared across the landscape. | Shared FS. |

### Work processes (what the app tier actually does)
The kernel runs typed work processes: **Dialog** (interactive), **Background** (batch
jobs), **Update**, **Enqueue**, **Spool**, **Message**. Sizing (how many of each) drives
the CPU/memory you need — which drives the EC2 instance type.

## ENSA1 vs ENSA2 (matters for AWS HA)

The **Enqueue Server** guards SAP locks. Old **ENSA1** required the enqueue replication
server on the *same* node, constraining failover. **ENSA2 (Standalone Enqueue Server
2)** decouples this so the enqueue can fail over to **any** node — which is what makes
clean **multi-AZ Pacemaker clusters on AWS** possible. Modern S/4HANA uses ENSA2.

## ABAP vs Java stacks

- **ABAP stack**: the traditional and most common (ECC, S/4HANA, BW).
- **Java stack** (AS Java): used by some products (older Portal, PI/PO). Different
  central-services naming (**SCS** vs **ASCS**), but the same architectural ideas.
- Some older systems were **dual-stack**; SAP has since split them.

## SAPS — the unit of SAP compute

**SAPS (SAP Application Performance Standard)** is a hardware-independent measure of
throughput (derived from a standard SD benchmark; 100 SAPS ≈ 2,000 order line items/hr).
You size a system in **SAPS**, then pick an EC2 instance certified to deliver that many
SAPS. This is the bridge between "business load" and "AWS instance choice" — see
`03-sap-on-aws/02-compute-and-sizing.md` and the calculator in `automation/`.

## How this maps onto an AWS deployment (preview)

```
ALB (443) ─▶ Web Dispatcher (EC2)
                 │
     ┌───────────┴───────────┐
   PAS (EC2, AZ-a)        AAS (EC2, AZ-b)          ← app tier, private subnets
     └───────────┬───────────┘
        ASCS cluster (EC2 AZ-a ⇄ AZ-b, Pacemaker, overlay IP)   ← central services
                 │
        HANA primary (EC2, AZ-a)  ⇄  HANA secondary (EC2, AZ-b)  ← DB tier, HSR sync
        shared /sapmnt, /usr/sap/trans  → EFS/FSx
        backups → S3 (Backint)
```

## Self-check

1. Name the three tiers and which one scales horizontally.
2. Why is the **(A)SCS** the single point of failure, and what modern feature makes
   multi-AZ failover clean?
3. What is **SAPS** and why do you care about it on AWS?
4. Which shared directories typically live on **EFS/FSx** rather than EBS, and why?

<details><summary>Answers</summary>

1. Presentation, application, database. The **application** tier scales horizontally.
2. It hosts the single **enqueue** (lock) and message servers; **ENSA2** lets the
   enqueue fail over to any node, enabling clean multi-AZ Pacemaker clusters.
3. A hardware-independent throughput unit; you size in SAPS and pick an EC2 instance
   certified for that many SAPS.
4. **`/sapmnt`** and **`/usr/sap/trans`** — they must be shared by many app servers
   across AZs, which needs a multi-attach file system (EFS/FSx), not single-AZ EBS.
</details>
