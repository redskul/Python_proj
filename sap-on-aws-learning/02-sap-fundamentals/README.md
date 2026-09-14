# Phase 2 — SAP Fundamentals

Now the other half. If you come from an AWS background, this is where SAP stops being a
black box. If you're a SAP person, skim and jump to phase 3.

Read in order:

| # | Topic |
|--:|-------|
| 01 | [What is SAP?](01-what-is-sap.md) — the company, the products, the jargon |
| 02 | [SAP architecture](02-sap-architecture.md) — NetWeaver, ABAP/Java, the 3 tiers |
| 03 | [SAP HANA](03-sap-hana.md) — the in-memory database that changes everything |
| 04 | [S/4HANA & the product families](04-s4hana-and-products.md) |
| 05 | [SAP system landscapes & lifecycle](05-sap-landscape-and-lifecycle.md) |

## The 4-sentence SAP mental model

1. **SAP** makes enterprise software that runs a company's core processes (finance,
   logistics, HR, procurement) on one integrated data model.
2. The classic technical platform is **SAP NetWeaver**, a 3-tier app running **ABAP**
   (and/or Java) programs against a database.
3. **SAP HANA** is SAP's **in-memory column-store database** — fast enough to combine
   transactions and analytics; it's the mandatory DB for the flagship **S/4HANA** ERP.
4. Companies run **multiple copies** (Dev → QA → Prod) of each system — a **landscape** —
   and move changes between them via **transports**.

Everything in phase 3 is about running that landscape well on AWS.
