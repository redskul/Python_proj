# 01 — Cloud Concepts & Global Infrastructure

## What is cloud computing?

On-demand delivery of IT resources (compute, storage, database, networking) over the
internet with **pay-as-you-go** pricing. Instead of buying servers, you rent them.

Three service models:

| Model | You manage | AWS manages | SAP example |
|-------|------------|-------------|-------------|
| **IaaS** (Infrastructure) | OS, app, data | Hardware, virtualisation | **SAP on EC2** (you install HANA) |
| **PaaS** (Platform) | App, data | OS, runtime | RDS, Elastic Beanstalk |
| **SaaS** (Software) | Just use it | Everything | SAP SuccessFactors, Ariba (SAP-run) |

> Nearly all "SAP on AWS" (S/4HANA, ECC, BW) is **IaaS on EC2** — because SAP
> certifies specific OS + instance combinations and you run the SAP kernel yourself.
> **RISE with SAP** is closer to a managed/SaaS-ish model, but the underlying compute
> can still be AWS.

## The 6 advantages of cloud (AWS's own list)

1. Trade **capital expense for variable expense** (rent vs buy).
2. Benefit from **massive economies of scale**.
3. Stop **guessing capacity** — scale up/down on demand.
4. Increase **speed and agility** — minutes not months.
5. Stop spending on **running data centres**.
6. Go **global in minutes**.

## Global infrastructure

### Regions
A **Region** is a physical location in the world (e.g. `eu-central-1` = Frankfurt,
`us-east-1` = N. Virginia). Regions are **isolated** from each other by design. You
choose a Region based on:

- **Latency** to your users.
- **Data sovereignty / compliance** (GDPR → keep EU data in EU).
- **Service & instance availability** (not all SAP-certified instances exist everywhere).
- **Cost** (prices vary by Region).

### Availability Zones (AZs)
Each Region has **≥ 3 AZs** (named `eu-central-1a`, `-1b`, `-1c`). An AZ is one or
more discrete data centres with independent power, cooling, and networking, but
connected to sibling AZs by **low-latency (<~1–2 ms), high-bandwidth** links.

> **This is the single most important concept for SAP HA.** You put the primary SAP
> DB in AZ-a and the standby in AZ-b. If a whole data centre fails, the other AZ keeps
> running. Synchronous HANA System Replication across two AZs is the standard HA pattern.

### Edge locations & Local Zones
- **Edge locations**: 400+ sites for CloudFront (CDN), Route 53 DNS, low-latency delivery.
- **Local Zones / Wavelength**: place compute physically closer to end users/5G.
- **Outposts**: AWS hardware in *your* data centre (used for SAP when latency to
  on-prem factory floor matters, or for data-residency).

## Availability math you must know

| "Nines" | Uptime | Downtime/year |
|---------|--------|---------------|
| 99% (two nines) | | ~3.65 days |
| 99.9% (three nines) | | ~8.76 hours |
| 99.95% | | ~4.38 hours |
| 99.99% (four nines) | | ~52 minutes |

Single-AZ EC2 alone will not give you four nines for SAP — you need multi-AZ HA
(covered in module 09 and `03-sap-on-aws/05-high-availability-and-dr.md`).

## Key terms

- **Fault tolerance**: keep running with *no* interruption when a component fails.
- **High availability (HA)**: recover *quickly* (seconds/minutes) after a failure.
- **Disaster recovery (DR)**: recover after a *Region-wide* event, measured by:
  - **RPO** (Recovery Point Objective) — how much *data* you can afford to lose (time).
  - **RTO** (Recovery Time Objective) — how *long* recovery may take.
- **Elasticity**: scale resources with demand.
- **Scalability**: **vertical** (bigger instance) vs **horizontal** (more instances).
  - SAP HANA scales **up** (vertical) primarily; SAP app servers scale **out** (horizontal).

## Self-check

1. Why can't two servers in the same AZ protect you from a data-centre fire?
2. Your SAP users are in Germany but the system is in `us-east-1`. Name two problems.
3. What's the difference between RPO and RTO? Which one does HANA System Replication
   in **sync** mode drive toward zero?

<details><summary>Answers</summary>

1. One AZ can be a single data centre; a fire takes both down. Spread across AZs.
2. Latency (slow SAP GUI/Fiori) and potential GDPR/data-residency compliance issues.
3. RPO = data loss, RTO = time to recover. **Sync** HANA System Replication drives
   **RPO → 0** (every committed transaction is on the secondary before commit).
</details>
