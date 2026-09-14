# 04 — EC2: Elastic Compute Cloud

EC2 is virtual servers you rent. **Every SAP application server and every SAP HANA /
AnyDB database server on AWS is an EC2 instance**, so this is core knowledge.

## Anatomy of an instance

- **AMI (Amazon Machine Image)**: the template (OS + preinstalled software) you boot
  from. For SAP you use SUSE (SLES for SAP) or RHEL for SAP images from the
  Marketplace — they include SAP-required kernel tuning and support.
- **Instance type**: the hardware profile — vCPU, memory, network, storage. Named
  `<family><generation><attributes>.<size>` e.g. `r5.8xlarge`, `x2idn.16xlarge`.
- **EBS volumes**: network-attached disks (module 05).
- **Key pair**: SSH login (or use SSM Session Manager and skip keys entirely).
- **Security group**: the instance firewall.
- **User data**: a bootstrap script that runs on first boot.

## Instance families (what the letters mean)

| Family | Optimised for | SAP relevance |
|--------|---------------|---------------|
| **T** (t3, t4g) | Burstable, cheap | Dev/test, bastion, small tools — **not** production HANA |
| **M** (m5, m6i, m7i) | Balanced | SAP app servers, small NetWeaver |
| **C** (c5, c6i) | Compute | Batch, app servers |
| **R** (r5, r6i, r7i) | **Memory-optimised** | **HANA** (memory ≈ data), app servers |
| **X** (x1e, **x2idn, x2iedn**) | **High memory** | **Large HANA** (up to multi-TB RAM) |
| **U / High Memory** (u-6tb1, u-24tb1…) | **Extreme memory** | **Very large HANA / S/4HANA** (3–24+ TB RAM) |

> SAP HANA is an **in-memory** database: the whole dataset lives in RAM. So HANA
> instances are chosen mostly by **memory**, and only **SAP-certified** instance types
> are supported. See `03-sap-on-aws/02-compute-and-sizing.md` and run
> `automation/list_sap_certified_instances.py`.

## Purchasing options (drives your SAP bill)

| Option | Discount | Commitment | SAP use |
|--------|----------|------------|---------|
| **On-Demand** | 0% (baseline) | None | Dev/test, spikes, learning |
| **Savings Plans** | up to ~72% | 1 or 3 yr $/hr commit | **Steady-state production SAP** |
| **Reserved Instances (RI)** | up to ~72% | 1 or 3 yr, specific type | Older equivalent to Savings Plans |
| **Spot** | up to ~90% | Can be reclaimed | Batch/non-critical only — **never** the DB |
| **Dedicated Hosts** | — | Physical server | BYOL licensing, compliance |

Production SAP runs 24/7, so **Savings Plans / RIs** are essential to control cost.

## Placement & tenancy

- **Placement groups**: `cluster` (low-latency, same AZ), `spread` (separate
  hardware), `partition`. HANA scale-out uses cluster placement for node-to-node speed.
- **Tenancy**: shared (default), dedicated instance, dedicated host (BYOL SAP/OS).

## Lifecycle & metadata

```bash
# Launch (illustrative — the labs do this via Terraform)
aws ec2 run-instances --image-id ami-xxxx --instance-type t3.micro \
  --key-name my-key --security-group-ids sg-xxxx --subnet-id subnet-xxxx

# From inside an instance — IMDSv2 (token-based, enforce this)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-type
```

## Auto Scaling & load balancing (for the app tier)

- **SAP application servers** can scale **horizontally**: add more dialog instances
  behind an SAP logon group; the AWS pattern is an **Auto Scaling Group** of app
  servers. (The **database** tier does not auto-scale horizontally — HANA scales up.)
- **Elastic Load Balancers**:
  - **ALB** (Application, layer 7, HTTP/HTTPS) — Fiori/Web Dispatcher front end.
  - **NLB** (Network, layer 4, TCP) — used in some **SAP HA overlay-IP** designs.

## Cost hygiene for the labs

- Use **`t3.micro`** for anything in phase 1 (Free-Tier-eligible).
- **Stop** (not just idle) instances you're not using — you still pay for running
  instances and attached EBS.
- `terraform destroy` when the lab is done.

## Self-check

1. Why are HANA instances almost always from the **R / X / U** families?
2. Which purchase option should you *never* use for a production SAP database, and why?
3. What's the difference between **stopping** and **terminating** an instance for cost?
4. Which scales horizontally in SAP — the app tier or the DB tier?

<details><summary>Answers</summary>

1. HANA is in-memory; you pick instances by RAM, and those families offer the highest
   memory-to-vCPU ratios (and are SAP-certified).
2. **Spot** — it can be reclaimed with ~2 minutes' notice; losing the DB is catastrophic.
3. **Stopped**: no compute charge, but you still pay for EBS; can restart. **Terminated**:
   gone, EBS (unless "delete on termination" off) released.
4. The **app tier** scales out (more dialog instances). The HANA DB scales **up**.
</details>
