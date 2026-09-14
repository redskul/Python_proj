# 03 — SAP HANA

HANA is the centre of gravity for modern SAP, and the component that most shapes your
AWS design. Understand it and the rest of SAP-on-AWS falls into place.

## What HANA is

**SAP HANA** = **H**igh-performance **AN**alytic **A**ppliance. It is:

- An **in-memory** database: the primary copy of the data lives in **RAM**, not on
  disk. Disk is only for persistence/recovery.
- A **column store** (primarily): great for analytics and, combined with in-memory,
  fast enough to also handle transactions — **HTAP** (do OLTP + OLAP in one system, no
  separate data warehouse copy needed for many cases).
- More than a DB: an **application platform** (calc views, stored procedures, ML,
  spatial, graph, XSA apps).

## Why "in-memory" dictates your AWS instance

Because the working data set sits in RAM, **you size a HANA host mostly by memory**:

```
required RAM ≈ (compressed data footprint) + working/temp space + OS/services headroom
```

That's why HANA runs on **memory-optimised (R/X) and High-Memory (U) EC2 instances**,
and only **SAP-certified** ones (SAP publishes exact certified types & max memory per
type). See `03-sap-on-aws/02-compute-and-sizing.md`.

## Persistence: data & log volumes

Even though it's in-memory, HANA must survive restarts and crashes:

- **Data volume** (`/hana/data`): periodic **savepoints** flush the in-memory image to
  disk. Needs high **throughput**.
- **Log volume** (`/hana/log`): every committed transaction writes a **redo log** entry
  synchronously. Needs very low **latency** (commits wait on it).
- On restart, HANA loads the last savepoint + replays the log → back in memory.

This is exactly why on AWS you use **gp3/io2** volumes tuned to SAP's **storage KPIs**
(latency and throughput at defined block sizes), validated with **HCMT**.

## Scale-up vs scale-out

- **Scale-up** (default, preferred): one big server, add RAM/CPU → bigger EC2 instance.
  Simpler; most S/4HANA runs scale-up on a single large instance.
- **Scale-out**: multiple HANA nodes sharing a dataset (used for very large **BW/BW4HANA**
  or huge datasets). On AWS this uses multiple EC2 nodes + a shared `/hana/shared`
  (EFS/FSx) + cluster placement.

## HANA System Replication (HSR) — the HA/DR engine

HANA replicates to a secondary system. Three modes matter:

| Mode | RPO | Use |
|------|-----|-----|
| **sync** | 0 (commit waits for secondary) | **HA across two AZs** (low latency) |
| **syncmem** | ~0 | secondary acks in memory |
| **async** | > 0 | **DR across Regions** (latency too high for sync) |

Combined with **Pacemaker** + an **overlay IP**, HSR-sync across two AZs gives
automatic multi-AZ HANA failover — the standard SAP-on-AWS HA pattern.

## MDC / tenant databases

Modern HANA is **multitenant (MDC)**: one `SystemDB` plus one or more **tenant DBs**.
Lets several SAP systems share a HANA instance while staying isolated.

## Backups

- **File/Backint backups**: HANA's native backup, streamed via **AWS Backint Agent**
  straight to **S3**.
- **Storage snapshots**: coordinate HANA + **EBS snapshots** for fast point-in-time.
- Log backups run frequently to bound RPO. See `03-sap-on-aws/06-backup-and-recovery.md`.

## Key tools/terms

- **hdbsql** — SQL client. **HANA Studio / Cockpit / DBACOCKPIT** — admin UIs.
- **hdbnsutil** — replication/topology tool.
- **HCMT** — HANA Hardware Configuration/Migration Tool (validates the AWS storage/CPU
  meets SAP KPIs). Run it after building a HANA host on AWS.
- **Quick Sizer / SAP Note sizing** — figure out how much RAM you need.

## Self-check

1. What single attribute of HANA most drives the choice of EC2 instance family?
2. Why does `/hana/log` care about **latency** while `/hana/data` cares about
   **throughput**?
3. Which HSR mode do you use **across AZs** for HA, and which **across Regions** for DR,
   and why?
4. What does **HCMT** verify and when do you run it on AWS?

<details><summary>Answers</summary>

1. **Memory** — it's in-memory, so RAM sizing picks the (memory-optimised/high-memory)
   instance.
2. Commits block on synchronous **redo-log** writes (latency-sensitive), while savepoints
   flush large data images (throughput-sensitive).
3. **sync** across AZs (low latency → RPO 0); **async** across Regions (latency too high
   for sync, accept some data loss for DR).
4. It validates the host's storage/CPU against SAP **KPIs**; run it after provisioning a
   HANA host on AWS, before go-live.
</details>
