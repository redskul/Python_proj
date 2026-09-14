# 08 — Automation: Launch Wizard & Infrastructure as Code

Repeatability is a support and cost requirement for SAP landscapes (DEV/QAS/PRD should
be built the same way). Three automation levels:

## 1. AWS Launch Wizard for SAP (guided, SAP-aware)

**AWS Launch Wizard for SAP** is a console/API guided deployment that:

- Asks about your SAP workload (product, HANA/NetWeaver, sizing, HA yes/no).
- Provisions **SAP-certified** infra per AWS/SAP best practice: EC2 (right family/size),
  EBS volumes with the correct HANA layout, subnets/SGs, IAM roles, and optionally the
  **HA cluster** scaffolding.
- Can install/prepare the OS and lay the ground for the SAP software install.
- Generates a **CloudFormation** stack under the hood (so it's reproducible/inspectable).

Best for: learning the "golden" layout, and for teams that want a validated starting
point without hand-rolling everything. Great study aid — deploy once and read the
generated CloudFormation to see how AWS models a certified SAP host.

## 2. Infrastructure as Code (Terraform / CloudFormation)

For full control and GitOps-style landscapes, use IaC:

- **Terraform** (this repo's labs) — declarative, multi-cloud, huge module ecosystem.
- **CloudFormation** / **CDK** — AWS-native; Launch Wizard emits CloudFormation.
- **AWS SAP automation content** — AWS publishes reference automation
  (CloudFormation/Ansible/Terraform patterns) for SAP; use them as blueprints.

Typical split:
```
IaC (Terraform)          → VPC, subnets, SGs, IAM, EC2, EBS (with HANA layout), EFS, endpoints
Config mgmt (Ansible)    → OS tuning (SLES/RHEL SAP notes), install SAP host agent,
                           mount volumes, Backint agent, cluster config
SAP tooling (SWPM/HDBLCM)→ actual SAP/HANA software install
```

> IaC provisions **infrastructure**; it does **not** install SAP itself — that's SWPM /
> HDBLCM (SAP's installers), often driven by Ansible. Keep the two layers separate.

## 3. Config management & post-provision

- **Ansible** (or SSM Automation) applies SAP OS prerequisites (kernel params, packages,
  `saptune`), mounts the LVM/EBS volumes, installs the **AWS Data Provider for SAP** and
  **Backint agent**, and configures **Pacemaker**.
- **saptune** (SUSE) / RHEL "system roles for SAP" apply SAP Note-mandated OS tuning.

## What the labs in this repo demonstrate

| Lab | Automates |
|-----|-----------|
| `lab01-vpc-foundation` | The multi-AZ VPC, subnets, route tables, IGW/NAT, S3 endpoint |
| `lab02-ec2-bastion` | Secure admin access (SSM-enabled host, IAM role) + an app-tier EC2 |
| `lab03-hana-host` | A HANA-shaped EC2 with the **correct EBS volume layout** (data/log/shared) — architecture-accurate, deploy optional (cost!) |
| `lab04-ha-overview` | A written walkthrough + snippets of the Pacemaker/overlay-IP design |

## The IaC + certification tie-in

Because SAP support depends on **certified instances + KPI-passing storage**, encoding
those choices in **version-controlled IaC** means every environment is provably built to
spec — and you can re-create PRD's exact shape for a DR test or a QAS refresh.

## Self-check

1. What does **Launch Wizard for SAP** produce under the hood, and why is that useful for
   reproducibility?
2. Which layer installs the actual SAP/HANA software — Terraform or SWPM/HDBLCM?
3. Name two things **Ansible / SSM** typically do after the infrastructure exists.

<details><summary>Answers</summary>

1. A **CloudFormation** stack — reproducible and inspectable, so you can re-deploy and
   learn the certified layout.
2. **SWPM / HDBLCM** (SAP installers). Terraform only builds the infrastructure.
3. Apply SAP OS tuning (`saptune`/system roles), mount LVM/EBS volumes, install the Data
   Provider + Backint agent, and configure Pacemaker.
</details>
