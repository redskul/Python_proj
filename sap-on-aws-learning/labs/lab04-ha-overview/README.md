# Lab 04 — HA design walkthrough (Pacemaker · HSR · overlay IP)

A full multi-AZ SAP HA cluster is **not** something you should spin up casually — it
needs certified instances, a SAP-supported OS, real HANA installed, and it costs a lot.
So this lab is a **guided walkthrough** of the design with the key configuration
snippets, so you understand *how* it works and could build it later with confidence.

Pair it with `../../03-sap-on-aws/05-high-availability-and-dr.md`.

## The design (recap)

```
        AZ-a                                   AZ-b
  ┌────────────────┐                     ┌────────────────┐
  │ HANA primary   │── HSR (sync) ──────▶│ HANA secondary │
  │ 10.0.2.10      │                     │ 10.0.12.10     │
  └───────┬────────┘                     └───────┬────────┘
          │      Pacemaker / corosync cluster     │
          └──────────  overlay IP 192.168.10.5 ───┘
                (NOT in the VPC CIDR 10.0.0.0/16)
                        │
              clients connect here; route table points
              overlay-IP/32 -> the ACTIVE node's ENI
```

## Step-by-step (what a build looks like)

1. **Two HANA hosts**, one per AZ, on a **certified instance** + **SLES/RHEL for SAP**.
2. **Install HANA** on both; configure **HANA System Replication (sync)** from primary
   to secondary (`hdbnsutil -sr_enable` / `-sr_register`).
3. **Install the cluster stack** (`pacemaker`, `corosync`, and the SAP resource agents —
   e.g. `SAPHanaSR`/`SAPHanaSR-angi`, plus the AWS-specific agents).
4. **Choose an overlay IP outside the VPC CIDR** (here `192.168.10.5`).
5. **Configure the cluster resource** that, on failover, calls the EC2 API to update the
   VPC **route table** entry `192.168.10.5/32 → active node's ENI` (the AWS
   `aws-vpc-move-ip` / route resource agent). Alternatively, front the two nodes with an
   internal **NLB**.
6. **IAM role** on both nodes permitting the needed EC2 actions (describe/replace route,
   describe instances) — this is how the cluster reconfigures routing.
7. **Fencing (STONITH)** via the EC2 API so a failed node can be reliably isolated
   (`external/ec2` agent).
8. **Clients** (app servers) connect to the **overlay IP**, unaffected by which AZ is
   active.

### Illustrative cluster resource (conceptual — verify against SUSE/RHEL + AWS docs)

```
# Overlay IP managed via the AWS route table (SUSE 'aws-vpc-move-ip' style)
primitive rsc_ip_HDB ocf:suse:aws-vpc-move-ip \
    params ip=192.168.10.5 routing_table=rtb-0abc123 interface=eth0 \
           profile=cluster \
    op monitor interval=60s timeout=60s

# HANA topology + replication resources
primitive rsc_SAPHana_HDB ocf:suse:SAPHana \
    params SID=HDB InstanceNumber=00 \
           PREFER_SITE_TAKEOVER=true AUTOMATED_REGISTER=true ...
```

### Minimal IAM the cluster nodes need (illustrative)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeInstances",
      "ec2:DescribeRouteTables",
      "ec2:ReplaceRoute",
      "ec2:CreateRoute",
      "ec2:DescribeNetworkInterfaces"
    ],
    "Resource": "*"
  }]
}
```
(Scope the `Resource`/conditions down in production; this is the shape, not a
copy-paste policy.)

## Failover, step by step

1. Primary HANA (AZ-a) fails.
2. Pacemaker detects the failure (monitor op) and **fences** the old primary (STONITH).
3. It **promotes** the AZ-b secondary to primary (HANA takeover).
4. The overlay-IP resource **updates the route table** so `192.168.10.5/32 → AZ-b ENI`.
5. Clients reconnect to the same overlay IP — now served from AZ-b. **RPO ≈ 0** (sync),
   **RTO** = seconds to a few minutes.

## The ASCS/ERS cluster (same idea, different resource)

A parallel Pacemaker cluster protects the **(A)SCS** using **ENSA2**, with `/sapmnt` on
**EFS/FSx** and its own overlay IP. See the HA module.

## Why no `apply` here

Building this safely needs licensed HANA media, certified instances, a supported OS, and
careful cluster testing — well beyond a cost-safe sandbox. Understand it here; build it
with the official **SUSE/RHEL SAP HA guides** and **AWS SAP HA documentation** when you
have a real project.

## Learning questions

1. What exactly does the cluster change on AWS to move the overlay IP between AZs?
2. Why do the cluster nodes need an IAM role with `ec2:ReplaceRoute`?
3. What is STONITH/fencing protecting against, and how is it done on AWS?
4. Which HSR mode is used here and what RPO does it deliver?

<details><summary>Answers</summary>

1. It updates a **VPC route-table** entry so `overlayIP/32` points at the active node's
   **ENI** (or shifts an NLB target).
2. So the failover resource agent can **reprogram the route** to the surviving node.
3. Split-brain (two nodes both thinking they're primary); on AWS, fencing calls the
   **EC2 API** to stop/verify the failed node.
4. **sync** — RPO ≈ 0 (every commit is on the secondary before it's acknowledged).
</details>
