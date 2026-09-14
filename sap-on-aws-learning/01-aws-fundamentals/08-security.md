# 08 — Security on AWS

Security is job zero, especially for business-critical SAP data (finance, HR, IP).

## The Shared Responsibility Model

- **AWS secures the cloud**: physical data centres, hardware, hypervisor, managed
  service software.
- **You secure what's in the cloud**: OS patching, SAP kernel patching, IAM,
  network config, encryption choices, and your data.

For **SAP on EC2 (IaaS)** you own a *lot*: the OS, HANA, network rules, and access.

## Data protection: encryption everywhere

- **At rest**:
  - **EBS encryption** (KMS) — enable **encryption by default** for the account.
  - **S3** default encryption (SSE-S3 or SSE-KMS) for HANA backups.
  - HANA **data & log volume encryption** (SAP feature) can layer on top.
- **In transit**:
  - **TLS** for Fiori/Web Dispatcher (443).
  - **SNC (Secure Network Communications)** for SAP GUI/RFC.
  - IPsec for VPN / private DX for the transport itself.

## KMS (Key Management Service)

- Central place to create and control **encryption keys**.
- **AWS-managed keys** (easy) vs **customer-managed keys** (CMK — you control rotation,
  policy, who can use them). Production SAP usually uses **CMKs** so key access is
  auditable and separable from data access.
- Key policies + IAM decide who can `Encrypt`/`Decrypt`. Combine with grants for the
  HANA Backint role.
- **CloudHSM** for dedicated hardware key custody (regulatory needs).

## Secrets Manager & Parameter Store

- **Secrets Manager**: store & **auto-rotate** DB passwords, HANA `SYSTEM` user creds,
  service accounts. The SAP host fetches them at runtime via its IAM role — no
  passwords in scripts.
- **SSM Parameter Store**: config values (and SecureString secrets, cheaper, no auto-rotation).

## Network security recap (see module 03)

- SAP servers in **private subnets**.
- **Security groups** scoped to specific source SGs (app-tier SG → db-tier SG on the
  HANA SQL port), never `0.0.0.0/0`.
- **VPC endpoints** so backup/monitoring traffic to S3/KMS/SSM stays on the AWS backbone.
- **NACLs** as a coarse subnet-level backstop.

## Detection & governance

| Service | Purpose |
|---------|---------|
| **GuardDuty** | Threat detection from logs (crypto-mining, anomalous API calls) |
| **Security Hub** | Aggregates findings, checks against CIS/AWS best-practice standards |
| **AWS Config** | Compliance rules ("EBS must be encrypted", "no public SG on port 22") |
| **CloudTrail** | Immutable audit log of API calls (turn on log-file validation) |
| **IAM Access Analyzer** | Finds overly broad resource sharing |
| **Inspector** | Scans EC2/containers for CVEs — patch your SAP OS |
| **Macie** | Finds sensitive data (PII) in S3 |

## Practical SAP security checklist

- [ ] Root user locked, MFA on all humans.
- [ ] IAM roles (not keys) on every SAP EC2 host; **IMDSv2 enforced**.
- [ ] EBS + S3 encrypted with **CMKs**; HANA volume encryption considered.
- [ ] SAP hosts in **private subnets**; SSH via **SSM Session Manager**.
- [ ] Security groups least-privilege between tiers.
- [ ] Secrets in **Secrets Manager**, not in files.
- [ ] CloudTrail + Config + GuardDuty enabled org-wide.
- [ ] OS/kernel patched via **SSM Patch Manager**; SAP Notes applied.

## Self-check

1. Under the shared responsibility model, who patches the SLES/RHEL OS of a HANA
   EC2 host?
2. Why prefer a **customer-managed KMS key (CMK)** over an AWS-managed key for SAP
   backups?
3. Where should the HANA `SYSTEM` password live, and how does the host get it safely?
4. Name the AWS service that would flag "an EC2 instance is talking to a known
   crypto-mining domain."

<details><summary>Answers</summary>

1. **You** — the OS is your responsibility on IaaS (use SSM Patch Manager + SAP Notes).
2. You control rotation, policy, and auditing, and can separate key-use permission from
   data-access permission.
3. In **Secrets Manager**; the host retrieves it at runtime via its **IAM role**, so no
   plaintext secret sits on disk.
4. **GuardDuty**.
</details>
