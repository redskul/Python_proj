# Study Plan

A suggested schedule. Adjust to your pace. Each "week" is ~5–8 hours; compress or expand
as needed.

## 6-week plan

### Week 0 — Setup
- [ ] Read `00-getting-started/README.md`; create AWS account + IAM admin + **budget alarm**.
- [ ] Install AWS CLI, Terraform, Python; run `automation/preflight_check.py`.

### Week 1 — AWS core I
- [ ] `01-aws-fundamentals/01-cloud-concepts.md`
- [ ] `02-iam.md`, `03-vpc-networking.md`
- [ ] **Lab 01** — deploy the VPC foundation; explore route tables.
- [ ] Answer all self-checks.

### Week 2 — AWS core II
- [ ] `04-ec2-compute.md`, `05-storage.md`, `06-databases.md`
- [ ] **Lab 02** — connect to an instance via SSM (no keys).
- [ ] Run `automation/list_sap_certified_instances.py` for your Region.

### Week 3 — AWS ops, security, resiliency, cost
- [ ] `07-monitoring-and-management.md`, `08-security.md`
- [ ] `09-resiliency-ha-dr.md`, `10-cost-and-billing.md`
- [ ] Quiz: `exercises/quiz-aws-fundamentals.md`.

### Week 4 — SAP fundamentals
- [ ] All of `02-sap-fundamentals/` (what is SAP, architecture, HANA, S/4HANA, landscape).
- [ ] Quiz: `exercises/quiz-sap-fundamentals.md`.

### Week 5 — SAP on AWS I
- [ ] `03-sap-on-aws/01-reference-architecture.md` … `04-networking.md`
- [ ] `automation/saps_sizing_calculator.py` + `ebs_storage_planner.py` on a made-up system.
- [ ] **Lab 03** — HANA storage layout (small instance).

### Week 6 — SAP on AWS II + wrap
- [ ] `03-sap-on-aws/05` … `09` (HA/DR, backup, migration, automation, ops).
- [ ] **Lab 04** — HA design walkthrough.
- [ ] Quiz: `exercises/quiz-sap-on-aws.md`.
- [ ] Design exercise (below).

## Capstone design exercise

Design (on paper / in a diagram) a production S/4HANA landscape on AWS for this brief:

> A retailer needs S/4HANA. HANA DB working set ≈ 800 GB. ~600 concurrent users,
> medium activity. Business requires **RPO ≤ 5 min, RTO ≤ 30 min** for a Region
> failure, and must survive a single-AZ outage automatically. Data must stay in the EU.
> Dev and QA systems are also needed but don't need HA.

Produce:
1. A **VPC diagram** (Region, AZs, subnets, tiers).
2. **Instance choices** for HANA and app tiers (use the sizing calculator; verify against
   the certified list).
3. The **HA design** (HANA + ASCS) and the **DR design** (which Region, which strategy,
   what replicates and how).
4. The **storage layout** for HANA (use the EBS planner).
5. **Backup** approach + retention + ransomware protection.
6. **Cost optimisations** (which systems get RIs/Savings Plans, which get start/stop).
7. **Security** baseline (IAM, encryption, network, secrets, audit).

Check your answer against the reference architecture and the relevant modules. There's a
worked sketch in `exercises/capstone-solution-sketch.md`.
