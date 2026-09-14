# 01 — What is SAP?

## The company and the idea

**SAP SE** (founded 1972, Germany) makes **enterprise application software**. The core
idea: run *all* of a company's business processes — finance, sales, procurement,
manufacturing, HR — on **one integrated system with one shared data model**, so that,
for example, a sales order automatically flows into inventory, production, accounting,
and shipping without re-keying.

This category is called **ERP (Enterprise Resource Planning)**. SAP is the market
leader; a huge share of the world's large enterprises run SAP.

## The product timeline (so the names make sense)

| Era | Product | Notes |
|-----|---------|-------|
| 1970s–90s | R/2, **R/3** | Client-server ERP; "R/3" = 3-tier |
| 2000s | **SAP ERP / ECC** (ERP Central Component) | The classic ERP most people mean by "SAP" |
| 2010s+ | **SAP Business Suite on HANA**, then **S/4HANA** | Rewritten to require the HANA database |
| Now | **S/4HANA** (on-prem, private cloud, public cloud) + **RISE with SAP** | The strategic ERP; SAP is pushing everyone here |

> **Key deadline:** SAP has announced **end of mainstream maintenance for legacy
> SAP ECC (Business Suite 7) around 2027** (extended to 2030 with paid options).
> This is *the* reason so many companies are migrating to **S/4HANA** — and often to
> AWS at the same time. That migration wave is why "SAP on AWS" skills are in demand.

## The vocabulary you'll hear constantly

| Term | Meaning |
|------|---------|
| **ERP** | The core business-process suite |
| **ECC** | The classic pre-S/4 ERP (ERP Central Component) |
| **S/4HANA** | The current-gen ERP, requires HANA DB |
| **HANA** | SAP's in-memory database (also an app platform) |
| **NetWeaver** | The classic technical application platform (ABAP/Java) |
| **ABAP** | SAP's proprietary programming language for business logic |
| **Fiori** | SAP's modern web UI (tiles/apps), replaces SAP GUI screens |
| **SAP GUI** | The classic thick-client UI |
| **SID** | System ID — a 3-char name for a system, e.g. `PRD`, `DEV`, `S4H` |
| **Instance** | A running SAP server process set (confusingly, not an EC2 instance) |
| **Transport** | A packaged change moved between systems (Dev→QA→Prod) |
| **Basis** | The SAP "sysadmin" discipline (installs, patches, tuning, HA) |
| **SAP Note** | An official SAP knowledge-base article / fix (often referenced by number) |
| **BW / BW4HANA** | SAP's data warehouse product |
| **RISE with SAP** | SAP's bundled subscription (S/4HANA Cloud + services), can run on AWS |

## Product families beyond ERP (you'll meet these)

- **SAP BW / BW4HANA** — data warehousing / analytics.
- **SAP SCM, SRM, CRM** — supply chain, supplier, customer (older suite pieces).
- **SuccessFactors** (HR), **Ariba** (procurement), **Concur** (travel) — **SaaS**,
  run by SAP.
- **SAP BTP (Business Technology Platform)** — SAP's PaaS for extensions/integration.

## Why "SAP on AWS" is a discipline of its own

SAP has **strict support requirements**: certified instance types, certified OS
(SLES for SAP / RHEL for SAP), storage performance KPIs, and documented HA/DR
patterns. AWS provides SAP-certified infrastructure and tools (Launch Wizard, Data
Provider, Backint). Knowing *both* worlds — and the SAP Notes that bless specific AWS
configs — is exactly what the **SAP on AWS Specialty** certification tests.

## Self-check

1. What does ERP stand for and what's the core idea?
2. What's the difference between **ECC** and **S/4HANA**, and why is 2027 relevant?
3. What is **Basis**, and what is a **transport**?

<details><summary>Answers</summary>

1. Enterprise Resource Planning — run all business processes on one integrated system
   and data model.
2. ECC is the classic ERP (runs on many DBs); S/4HANA is the rewritten current ERP that
   **requires HANA**. Legacy ECC mainstream support ends ~2027, driving mass migration.
3. Basis = the SAP system-administration discipline. A transport is a packaged change
   promoted from Dev → QA → Prod.
</details>
