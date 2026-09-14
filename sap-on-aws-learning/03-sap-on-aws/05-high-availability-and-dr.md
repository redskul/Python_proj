# 05 — High Availability & Disaster Recovery for SAP on AWS

The most exam-heavy and job-critical topic. Builds on
`01-aws-fundamentals/09-resiliency-ha-dr.md`.

## HA vs DR for SAP (scope reminder)

- **HA** = survive an **AZ / component** failure automatically, within one Region
  (RTO minutes, RPO ~0). Achieved with **two AZs + clustering**.
- **DR** = survive a **Region** failure, using a **second Region** (RTO/RPO per business
  choice). Achieved with **async replication + pilot light**.

## HA for the database tier: HSR + Pacemaker + overlay IP

```
        AZ-a                                AZ-b
   ┌───────────────┐   HANA System      ┌───────────────┐
   │ HANA primary  │   Replication      │ HANA secondary│
   │ (indexserver) │ ── SYNC ─────────▶ │ (in-memory or │
   │               │                    │  preload)     │
   └──────┬────────┘                    └──────┬────────┘
          │        Pacemaker/corosync cluster   │
          └───────────────  overlay IP  ─────────┘
                     (route table / NLB repoint on failover)
```

- **HANA System Replication (HSR) in `sync` mode** across the two AZs keeps a live
  secondary with **RPO = 0** (every commit is on the secondary first). AZ-to-AZ latency
  is low enough for sync.
- **Pacemaker + corosync** (the SLES/RHEL HA cluster stack, with SAP resource agents)
  monitors HANA and, on primary failure, **promotes** the secondary and moves the
  **overlay IP** to it.
- Clients connect to the **overlay IP**, so they're unaffected by which AZ is active.
- SAP/AWS provide the resource agents (e.g. `SAPHanaSR`, AWS-specific agents that call
  the EC2 API to update the route/ENI).

### The fencing/STONITH detail
Clusters must avoid "split brain." On AWS, fencing is done via the EC2 API (a resource
agent can stop/verify the other node). Ensure the cluster's IAM role permits the needed
EC2 actions.

## HA for the central-services tier: ASCS/ERS with ENSA2

- The **(A)SCS** (enqueue + message server) is SAP's classic single point of failure.
- Deploy **ASCS in AZ-a** and its **ERS (Enqueue Replication Server) in AZ-b**, in a
  **Pacemaker cluster** with an **overlay IP**.
- **ENSA2** lets the enqueue lock table fail over to any node, so recovery across AZs is
  clean.
- Shared SAP files (`/sapmnt`) on **EFS/FSx** so both nodes see them.

## HA for the application tier

- Run **multiple app-server instances (PAS + AAS) across both AZs**.
- SAP **logon groups** / Web Dispatcher distribute users; losing one app server just
  reduces capacity, not availability.
- Optionally front Fiori/Web Dispatcher with an **ALB** across AZs.

## Putting HA together (production S/4HANA)

| Tier | HA mechanism | Spans |
|------|--------------|-------|
| HANA DB | HSR **sync** + Pacemaker + overlay IP | AZ-a ⇄ AZ-b |
| ASCS/ERS | ENSA2 + Pacemaker + overlay IP + EFS | AZ-a ⇄ AZ-b |
| App servers | Multiple instances + logon groups | both AZs |
| Web/Fiori | ALB | both AZs |

Result: no single AZ or component failure takes the system down; RPO ≈ 0, RTO minutes.

## Disaster Recovery (second Region)

Cross-AZ HA won't save you from a Region-wide event. For DR:

1. **HANA System Replication in `async` mode to the DR Region** (latency too high for
   sync; accept a small RPO).
2. **App/ASCS servers as AMIs** (or IaC) in the DR Region, kept **stopped** (pilot
   light) and started on failover.
3. **Backups copied cross-Region** (Backint S3 objects / snapshot copies) as a floor.
4. **Route 53** to redirect clients to the DR Region on failover.
5. Optionally **AWS Elastic Disaster Recovery (DRS)** for the non-DB servers.

DR strategy choice (recap):

| Strategy | RTO | RPO | Cost | SAP fit |
|----------|-----|-----|------|---------|
| Backup & Restore | hours | hours | $ | non-critical |
| **Pilot Light** | 10s min | minutes | $$ | **common for SAP** |
| Warm Standby | minutes | sec–min | $$$ | high-criticality |
| Active/Active | ~0 | ~0 | $$$$ | rare for SAP DB |

## Test it

- Do **failover drills** (kill the primary HANA node; confirm the overlay IP moves and
  clients reconnect).
- Do **DR drills** (promote the DR-Region HANA, start app servers, repoint Route 53).
- Untested DR is not DR.

## Self-check

1. What three things combine to give automatic multi-AZ HANA failover on AWS?
2. Why is HSR **sync** used across AZs but **async** across Regions?
3. What is the SAP single point of failure other than the DB, and how is it made HA?
4. Sketch a **pilot light** DR for SAP: what runs in the DR Region normally, and what
   happens on failover?

<details><summary>Answers</summary>

1. **HSR sync** + **Pacemaker/corosync cluster** + **overlay IP** (repointed via route
   table/NLB).
2. AZ latency is low enough for sync (RPO 0); cross-Region latency is too high for sync
   without hurting commits, so async (small RPO) is used for DR.
3. The **(A)SCS** (enqueue/message server); made HA with an **ENSA2 ASCS/ERS Pacemaker
   cluster** across AZs + overlay IP + shared `/sapmnt` on EFS/FSx.
4. Normally: HANA async replica running + app/ASCS AMIs present but **stopped** +
   backups copied over. On failover: promote HANA, start the app/ASCS instances,
   repoint **Route 53** to the DR Region.
</details>
