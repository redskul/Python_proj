# 04 — S/4HANA & the Product Families

## S/4HANA in one paragraph

**SAP S/4HANA** is SAP's current-generation ERP suite, **rebuilt to run only on the
HANA database**. Compared with the older ECC, it has a simplified data model (e.g. the
"Universal Journal" merges many finance tables), real-time analytics on live
transactional data, and the **Fiori** web UX by default. It's the target most companies
are migrating to before legacy ECC support ends.

## Deployment options (this affects who runs the infrastructure)

| Option | Who runs infra | Where |
|--------|----------------|-------|
| **S/4HANA (on-prem / self-managed)** | You | Your data centre **or your AWS account** (IaaS on EC2) |
| **S/4HANA Cloud, private edition** (part of **RISE with SAP**) | SAP-managed | Hyperscaler incl. **AWS** |
| **S/4HANA Cloud, public edition** | SAP (SaaS) | SAP-run multi-tenant |

> For this course, "**SAP on AWS**" mostly means **self-managed S/4HANA (or ECC/BW) on
> EC2 in your own AWS account** — you're the Basis/cloud team. **RISE** is worth knowing
> as the SAP-managed alternative that can still land on AWS infrastructure.

## Migration paths to S/4HANA (you'll hear these words)

- **Greenfield** — brand-new implementation, re-engineer processes, migrate master/some
  transactional data.
- **Brownfield** — technical **system conversion** of an existing ECC to S/4HANA (keep
  history & customisation). Uses **SUM/DMO** (Software Update Manager / Database
  Migration Option).
- **Bluefield / selective data transition** — hybrid; move selected data into a fresh
  shell.

Any of these is frequently combined with **migrating to AWS at the same time** (lift
the workload to EC2 as part of the project). That "convert + move to cloud" combo is
the bread and butter of SAP-on-AWS projects.

## The wider SAP product map (so acronyms don't surprise you)

| Product | What it does |
|---------|--------------|
| **S/4HANA** | ERP (finance, logistics, manufacturing, …) |
| **BW/4HANA** | Data warehouse / analytics (often scale-out HANA) |
| **SAP BTP** | Platform-as-a-service: extensions, integration (CPI), analytics, AI |
| **SuccessFactors** | Human capital management (SaaS, SAP-run) |
| **Ariba / Fieldglass** | Procurement / external workforce (SaaS) |
| **Concur** | Travel & expense (SaaS) |
| **SAP Datasphere / Analytics Cloud** | Modern data & analytics |
| **PI/PO, Integration Suite** | System-to-system integration middleware |

The ones you typically **run on AWS EC2 yourself**: **S/4HANA, ECC, BW/4HANA, Solution
Manager, PI/PO**, and the HANA databases beneath them.

## RISE with SAP (know the concept)

**RISE with SAP** is a **subscription bundle**: S/4HANA Cloud (private edition) +
technical managed services + tools, with the underlying infrastructure on a hyperscaler
(**AWS** among them). SAP manages the technical operations; the customer consumes ERP.
It changes the operating model (SAP-managed vs self-managed) but AWS can still be the
data-centre underneath.

## Self-check

1. What's the one hard requirement that distinguishes S/4HANA from ECC?
2. Contrast **greenfield** vs **brownfield** migration in one line each.
3. In "self-managed S/4HANA on AWS," who is responsible for the OS, HANA, and HA — SAP
   or you? How does that differ under **RISE**?

<details><summary>Answers</summary>

1. S/4HANA runs **only on the HANA database**.
2. Greenfield = fresh reimplementation; brownfield = in-place **system conversion** of an
   existing ECC (SUM/DMO), keeping history/customisation.
3. Self-managed on AWS: **you** own OS/HANA/HA (AWS owns the infra beneath). Under
   **RISE**, SAP manages the technical operations even when AWS is the underlying infra.
</details>
