# 10 — Cost & Billing

SAP on AWS can be one of the largest line items in an IT budget (24/7 large-memory
instances). Understanding cost is a core skill, not an afterthought.

## How AWS charges (the mental model)

You pay for three things, roughly:

1. **Compute** — per second/hour that instances run (biggest SAP cost).
2. **Storage** — per GB-month of EBS/S3/EFS + IOPS/throughput provisioned (gp3/io2).
3. **Data transfer** — **out** to the internet and **between AZs/Regions** costs money;
   inbound is usually free. (Cross-AZ HANA replication traffic has a cost — budget it.)

## Cutting the compute bill

| Lever | Saving | For SAP |
|-------|--------|---------|
| **Savings Plans** (1/3-yr commit) | up to ~72% | The main lever for steady-state prod SAP |
| **Reserved Instances** | up to ~72% | Same idea, instance-scoped |
| **Right-sizing** | varies | Match instance to real SAPS/memory need (don't over-buy) |
| **Start/stop non-prod** | ~65%+ | Shut down dev/test/sandbox nights & weekends (SSM Automation) |
| **Spot** | up to ~90% | Only batch/stateless — **never** the SAP DB |

> **Non-prod start/stop is huge for SAP.** Dev/QA systems don't need to run 24/7. A
> scheduled SSM Automation runbook that stops them at night can cut their bill by
> more than half.

## Storage & data-transfer tips

- Use **gp3** and provision only the IOPS/throughput HANA actually needs (per KPIs).
- **Lifecycle** old HANA backups from S3 Standard → Glacier Deep Archive.
- Keep chatty tiers **in the same AZ** where HA allows, to reduce cross-AZ transfer
  (but never at the expense of the required multi-AZ HA).
- Delete unattached EBS volumes and stale snapshots.

## The cost tools

| Tool | Use |
|------|-----|
| **AWS Budgets** | Set spend/usage limits + email/SNS alerts (do this **first**) |
| **Cost Explorer** | Visualise & forecast spend, filter by tag/service |
| **Cost & Usage Report (CUR)** | Line-item detail into S3 for deep analysis |
| **Cost Allocation Tags** | Tag by `Environment=prod`, `SID=PRD`, `CostCenter=...` |
| **Compute Optimizer** | Right-sizing recommendations |
| **Pricing Calculator** | Estimate a design *before* building it |

## Tagging discipline (do it from day one)

Tag every SAP resource, e.g.:
```
SID          = PRD
Environment  = production
Component    = hana-db | ascs | app | webdisp
CostCenter   = 4711
Owner        = basis-team
```
Then Cost Explorer can answer "what does the PRD landscape cost per month?" instantly.

## Set your learning-account guardrail NOW

```bash
# Create a $10 monthly budget with an alert at 80% (illustrative CLI shape).
# Easiest via console: Billing → Budgets → Create budget → Cost budget.
```
Also enable **free-tier usage alerts** in Billing preferences.

## Self-check

1. What are the three broad things AWS bills you for?
2. Which cost lever is the single biggest for *steady-state production* SAP, and which
   for *non-production*?
3. Why should you tag every SAP resource with `SID` and `Environment` on day one?
4. Which data-transfer cost is easy to forget in a multi-AZ HANA HA design?

<details><summary>Answers</summary>

1. **Compute** (instance-hours), **storage** (GB-month + provisioned IOPS/throughput),
   and **data transfer** (egress + cross-AZ/Region).
2. Production: **Savings Plans/RIs**. Non-prod: **scheduled start/stop**.
3. So Cost Explorer / cost-allocation reports can attribute spend per landscape and
   environment.
4. **Cross-AZ** transfer for synchronous HANA System Replication between the primary
   and standby AZ.
</details>
