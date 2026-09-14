# 09 — Operations & Security for SAP on AWS

Day-2: keeping the landscape healthy, secure, patched, and cost-efficient. Combines the
AWS ops tools (module 07 of phase 1) with SAP specifics.

## Monitoring

- **CloudWatch**: instance/EBS metrics, custom metrics (memory/disk via CloudWatch
  Agent), alarms → SNS. Watch `/hana/log` latency, `/hana/data` throughput, CPU, memory,
  swap.
- **AWS Data Provider for SAP**: install on every SAP host so **ST06/saposcol** shows
  correct virtualised metrics (may be **required** for SAP support).
- **SAP Solution Manager**: SAP-side monitoring, alerting, EarlyWatch, root-cause.
- **HANA Cockpit / DBACOCKPIT**: DB health, replication status, backups.

## Patching & OS management

- **SSM Patch Manager**: schedule OS patch cycles per environment (patch DEV first,
  PRD last).
- Apply **SAP Notes** (kernel, HANA revisions) via SAP tooling on a maintenance schedule.
- Keep **SLES for SAP / RHEL for SAP** subscriptions current (support requirement).
- Use **saptune** / RHEL SAP system roles to keep OS tuning compliant after patches.

## Access & administration

- **SSM Session Manager** for shell access (no bastion/keys, fully audited) — preferred
  over SSH.
- **IAM roles** on hosts (no static keys); **IMDSv2 enforced**.
- **Secrets Manager** for HANA/DB credentials with rotation.
- Least-privilege SGs between tiers; SAP hosts in private subnets.

## Security operations

- **CloudTrail** (with log validation) + **AWS Config** rules + **GuardDuty** +
  **Security Hub** across the landscape.
- **Inspector** to catch OS CVEs — feed into the patch cycle.
- **KMS CMKs** for EBS/S3/HANA encryption; audit key usage.
- **Backups**: Object Lock (WORM), cross-Region copies, isolated backup account.

## Start/stop & lifecycle automation

- **SSM Automation runbooks** to start/stop whole SAP systems **in the correct order**
  (DB up → ASCS → app servers; reverse for shutdown). SAP has start/stop dependencies —
  don't just stop the EC2 instances blindly on a running system; use `sapcontrol` to
  stop SAP gracefully first.
- Schedule non-prod stop nights/weekends (big cost saving).
- **AWS Systems Manager for SAP** to register apps for coordinated start/stop & backup.

## Cost operations

- **Savings Plans/RIs** for 24/7 prod; **right-size** with Compute Optimizer.
- **Tag** everything (`SID`, `Environment`, `Component`, `CostCenter`); watch **Cost
  Explorer** per landscape.
- Clean up orphaned EBS volumes/snapshots; lifecycle S3 backups to Glacier.
- Mind **cross-AZ HSR** and egress transfer costs.

## The Well-Architected lens for SAP

AWS publishes an **SAP Lens** for the Well-Architected Framework. Evaluate the landscape
against the six pillars:

| Pillar | SAP question |
|--------|--------------|
| Operational Excellence | Is start/stop, patching, monitoring automated? |
| Security | Encryption, least privilege, private subnets, audit? |
| Reliability | Multi-AZ HA, tested DR, backups restorable? |
| Performance Efficiency | Certified instances, KPI-passing storage (HCMT)? |
| Cost Optimization | RIs/Savings Plans, right-sized, non-prod stopped? |
| Sustainability | Efficient sizing, decommission unused systems? |

## Self-check

1. Why must you use `sapcontrol` (not just "stop the EC2 instance") to shut down a
   running SAP system for the night?
2. Which agent may be **required** for SAP support and what does it fix?
3. List the security services you'd enable landscape-wide for audit and threat
   detection.
4. What framework/lens does AWS provide to review an SAP deployment holistically?

<details><summary>Answers</summary>

1. SAP has ordered start/stop dependencies and in-flight work; `sapcontrol` stops the
   SAP application gracefully (app → ASCS → DB) so you don't corrupt state — then you can
   stop the instances.
2. The **AWS Data Provider for SAP** — feeds correct virtualised metrics to
   ST06/saposcol.
3. **CloudTrail, AWS Config, GuardDuty, Security Hub, Inspector** (plus KMS, IAM
   hygiene).
4. The **AWS Well-Architected Framework — SAP Lens**.
</details>
