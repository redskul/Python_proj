# 07 — Monitoring & Management

You can't operate SAP on AWS blind. This module covers the AWS observability and
management services, and the special **AWS Data Provider for SAP** that bridges AWS
metrics into SAP's own monitoring.

## CloudWatch — metrics, logs, alarms

- **Metrics**: CPU, network, EBS IOPS/throughput/latency, status checks — per instance.
  (Note: **memory** and **disk usage** need the **CloudWatch Agent** installed, since
  they're inside the OS.)
- **Logs**: ship OS logs, SAP work-process traces, HANA trace files to CloudWatch Logs.
- **Alarms**: e.g. "alert if `/hana/log` volume latency > X" or "app-server CPU > 85%
  for 10 min" → SNS notification / auto-remediation.
- **Dashboards**: single pane for the landscape.

## AWS Data Provider for SAP (know this one)

SAP's OS-level monitoring (transaction **ST06**, the OS collector `saposcol`) expects
detailed metrics about the underlying host. On physical hardware it reads them
directly; on AWS the hypervisor abstracts them away. The **AWS Data Provider for SAP**
is a small daemon you install on each SAP host that collects EC2/EBS/CloudWatch data
and exposes it so **SAP ST06 shows correct CPU, disk, and network metrics**. SAP
support may **require** it for SAP-on-AWS systems.

## Systems Manager (SSM) — the ops swiss-army knife

| SSM capability | Use for SAP |
|----------------|-------------|
| **Session Manager** | Shell into instances **without SSH keys or a bastion** (audited) |
| **Patch Manager** | OS patching of SAP hosts on a schedule |
| **Run Command** | Run a script across many app servers at once |
| **Parameter Store** | Store config (non-secret) |
| **Inventory / State Manager** | Track installed software, enforce config |
| **Automation** | Runbooks (e.g. "start the whole SAP system in order") |

## CloudTrail vs CloudWatch vs Config (don't mix them up)

| Service | Answers |
|---------|---------|
| **CloudWatch** | "How is it performing?" (metrics/logs/alarms) |
| **CloudTrail** | "**Who** did **what** API call, **when**?" (audit trail) |
| **AWS Config** | "Is my config **compliant**, and how did it **change** over time?" |

For SAP compliance you typically enable **all three** across the landscape.

## AWS Backup

Centralised, policy-driven backup across EBS, EFS, RDS, FSx, etc. Complements SAP's own
Backint/HANA backups for the *infrastructure* layer (e.g. non-DB volumes).

## SAP-specific: AWS Systems Manager for SAP & Launch Wizard

- **AWS Launch Wizard for SAP**: guided deployment that provisions SAP-certified infra
  (EC2, EBS, networking) per SAP best practice. Great learning aid (see
  `03-sap-on-aws/08-automation-launch-wizard.md`).
- **AWS Systems Manager for SAP**: register SAP applications for start/stop, Backint
  registration, and integration with **AWS Backup** for HANA.

## Self-check

1. Why doesn't CloudWatch show EC2 **memory** usage out of the box, and how do you fix
   it?
2. What does the **AWS Data Provider for SAP** do, and which SAP transaction depends on
   it?
3. You need "who ran `TerminateInstances` on the HANA host last night?" — which
   service?
4. How can an admin get a shell on a private SAP app server with **no** SSH key and
   **no** bastion?

<details><summary>Answers</summary>

1. Memory lives inside the guest OS, invisible to the hypervisor; install the
   **CloudWatch Agent** to publish it.
2. It feeds EC2/EBS/CloudWatch metrics into SAP OS monitoring so **ST06/saposcol** are
   accurate; SAP support may require it.
3. **CloudTrail**.
4. **SSM Session Manager** (with the SSM agent + an instance role).
</details>
