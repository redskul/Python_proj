# 02 — Compute & Sizing for SAP on AWS

The most common real-world question: *"Which EC2 instance do I put SAP on?"* Getting
this right (and certified) is central to the specialty.

## Step 1 — size the workload in SAPS / memory

- **SAPS** (SAP Application Performance Standard) measures throughput. You derive the
  required SAPS from:
  - **SAP Quick Sizer** (for new systems, based on business volumes), or
  - **measured load** of an existing system (e.g. ST03 workload, EarlyWatch reports).
- **HANA memory**: from SAP sizing reports (e.g. `/SDF/HDB_SIZING`, Note-based sizing) —
  driven by the compressed in-memory data footprint + working space.

Output of this step: "I need ~X SAPS for the app tier and ~Y GB RAM for HANA."

## Step 2 — map to a **SAP-certified** EC2 instance

Only certain EC2 types are certified for SAP, and there are **two certification
contexts**:

- **SAP NetWeaver / application servers** — a broad set of general/compute/memory
  instances are supported (M, R, C, …).
- **SAP HANA (database)** — a **narrower, explicitly certified** list, because HANA has
  strict CPU/RAM ratio and performance requirements. These live in the **SAP Certified
  and Supported SAP HANA Hardware Directory**.

Typical HANA-certified families:

| Family | Example | Rough RAM range | Use |
|--------|---------|-----------------|-----|
| **R** (r5, r6i, r7i) | `r6i.4xlarge`…`r6i.32xlarge` | ~128 GB–1 TB | Small/medium HANA, app tier |
| **X** (x1e, **x2idn, x2iedn**) | `x2idn.16xlarge`, `x2iedn.32xlarge` | ~1–4 TB | Large HANA |
| **U / High Memory** | `u-6tb1.112xlarge` … `u-24tb1` | 3–24+ TB | Very large S/4HANA / BW |

> **Always confirm the exact certified type + max memory in the current SAP HANA
> Hardware Directory and SAP Note 1656099 / 2718982.** Certifications are added/changed
> frequently (newer generations, higher memory).

Use the helper: `automation/list_sap_certified_instances.py` filters EC2 offerings by
family/memory in your Region so you can see what's actually available.

## Step 3 — pick the OS (also certified)

- **SLES for SAP Applications** or **RHEL for SAP Solutions** (BYOS or on-demand from
  the AWS Marketplace). These images include the SAP-required kernel tuning and vendor
  support that SAP mandates. Plain SLES/RHEL/Amazon Linux are **not** supported for
  HANA.

## Step 4 — scale strategy

- **HANA**: scale **up** (bigger certified instance). Scale-out only for specific large
  BW/dataset cases.
- **App tier**: scale **out** (more dialog instances / EC2), optionally in an Auto
  Scaling Group, across AZs.

## Step 5 — purchasing

- Production runs 24/7 → **Savings Plans / Reserved Instances** (up to ~72% off).
- Non-prod → On-Demand + **scheduled start/stop**.
- **Never Spot** for the SAP DB or ASCS.

## Right-sizing per environment

| Env | Instance strategy |
|-----|-------------------|
| PRD | Certified, sized for peak + headroom, RI/Savings Plan |
| QAS | Smaller certified instance; often less RAM than PRD |
| DEV/SBX | Smallest workable certified instance; stop off-hours |

## Worked mini-example

*"HANA needs 900 GB RAM; app tier needs 12,000 SAPS."*

- HANA → an `r6i.24xlarge`/`r6i.32xlarge`-class certified instance (~768 GB–1 TB) — pick
  the certified type whose **max supported memory ≥ 900 GB** with headroom; verify in
  the Hardware Directory.
- App tier → one or two `m6i`/`r6i` instances across AZs delivering ≥ 12,000 SAPS
  combined (check each instance's published SAPS rating).
- Use `automation/saps_sizing_calculator.py` to sanity-check the arithmetic.

## Self-check

1. Why is the certified instance list for **HANA** narrower than for **app servers**?
2. Which OS images are supported for HANA and why not plain Amazon Linux?
3. You measured 30,000 SAPS of app load. How do you decide instance count/size?
4. Which purchasing option is off-limits for the DB tier?

<details><summary>Answers</summary>

1. HANA has strict CPU/RAM ratios and performance requirements, so SAP certifies a
   specific subset (the HANA Hardware Directory).
2. **SLES for SAP** / **RHEL for SAP** — they carry SAP-required tuning and vendor
   support; plain distros aren't in SAP's support matrix for HANA.
3. Pick certified instances whose combined published **SAPS ≥ 30,000** (plus headroom),
   spread across ≥ 2 AZs for HA.
4. **Spot** — the DB must not be interruptible.
</details>
