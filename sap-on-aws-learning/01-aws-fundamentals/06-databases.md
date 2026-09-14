# 06 — Databases on AWS (and where SAP HANA fits)

AWS offers managed databases, but **SAP HANA is *not* one of them** — this is a key
distinction. Understanding the managed options tells you *why* HANA is run differently.

## AWS managed databases (PaaS)

| Service | Kind | Notes |
|---------|------|-------|
| **RDS** | Managed relational | MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, **Db2** |
| **Aurora** | Cloud-native relational | MySQL/PostgreSQL-compatible, auto-scaling storage |
| **DynamoDB** | NoSQL key-value | Serverless, single-digit-ms |
| **ElastiCache** | In-memory cache | Redis/Memcached |
| **Redshift** | Data warehouse | Analytics (SAP data often lands here via extraction) |

With RDS/Aurora, AWS manages patching, backups, failover, and replicas — you just use
the endpoint.

## So where does SAP run its database?

SAP supports several databases ("**AnyDB**" = SAP's term for the non-HANA ones):

| SAP database | On AWS runs as… |
|--------------|-----------------|
| **SAP HANA** | **Self-managed on EC2** (SUSE/RHEL). Not a managed service. |
| **Oracle** (AnyDB) | On EC2 (self-managed) — RDS for Oracle is **not** SAP-certified for the SAP DB tier in most cases; SAP wants full control |
| **IBM Db2** (AnyDB) | **RDS for Db2** is certified for some SAP NetWeaver workloads; also EC2 |
| **Microsoft SQL Server** (AnyDB) | On EC2 (self-managed) for SAP |
| **SAP ASE (Sybase)** | On EC2 |

> **The takeaway:** the strategic SAP database is **HANA**, and on AWS **HANA is
> installed by you on EC2** using SAP-certified instances and SAP-published storage.
> AWS gives you the *infrastructure*; SAP support and certification govern the rest.

### Why not "just use RDS" for HANA?
- HANA is an **in-memory column store** with tight coupling to certified hardware,
  specific OS tuning, and SAP's own HA (System Replication). SAP certifies exact
  instance types and storage KPIs. A generic managed service can't meet the SAP
  support matrix, so HANA is run on EC2 where you control everything SAP requires.

## Concepts that transfer to the HANA world

- **Read replicas** (RDS/Aurora) ↔ **HANA System Replication** secondaries.
- **Multi-AZ** (RDS synchronous standby) ↔ **sync HANA System Replication across AZs**.
- **Automated backups / snapshots** ↔ **Backint to S3** + EBS snapshots for HANA.
- **Parameter groups** (RDS tuning) ↔ HANA `global.ini`/`indexserver.ini` tuning.

## When you *would* use RDS/Aurora alongside SAP

- **Side-car / satellite apps**: custom apps, integration middleware, reporting stores.
- **Analytics**: extract SAP data into **Redshift** for BI.
- **Db2 workloads**: **RDS for Db2** for supported NetWeaver stacks to offload DB admin.

## Self-check

1. Is SAP HANA a managed AWS database service? If not, how is it run?
2. What RDS feature is conceptually the same as **synchronous HANA System Replication
   across two AZs**?
3. Name one legitimate use of RDS/Redshift *around* an SAP system.

<details><summary>Answers</summary>

1. No. HANA is **self-managed on EC2** using SAP-certified instances + SAP-defined storage.
2. **Multi-AZ RDS** (a synchronous standby in another AZ).
3. Extracting SAP data into **Redshift** for analytics, or a side-car app on RDS/Aurora.
</details>
