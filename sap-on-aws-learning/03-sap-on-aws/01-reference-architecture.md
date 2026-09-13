# 01 — SAP on AWS Reference Architecture

The canonical, SAP-supported production layout for an S/4HANA (or NetWeaver) system on
AWS. Everything in the other phase-3 modules is a detail of this picture.

## The full picture (highly available, single Region)

```
                              Internet / Corporate DC
                                     │
                    ┌────────────────┴─────────────────┐
              Direct Connect / VPN               Route 53 (DNS)
                    │
        ┌───────────▼───────────────────────────────────────────────┐
        │  VPC 10.0.0.0/16   (Region eu-central-1)                    │
        │                                                             │
        │   AZ-a                          AZ-b                        │
        │  ┌───────────────┐            ┌───────────────┐             │
        │  │ public-a      │            │ public-b      │             │
        │  │  NAT GW, ALB, │            │  NAT GW, ALB, │             │
        │  │  bastion      │            │  bastion(std) │             │
        │  ├───────────────┤            ├───────────────┤             │
        │  │ app-a         │            │ app-b         │             │
        │  │  PAS + Web    │            │  AAS          │             │
        │  │  Disp (EC2)   │            │  (EC2)        │             │
        │  │  ASCS ◀───────┼── ENSA2 ───┼──▶ ERS        │  Pacemaker  │
        │  ├───────────────┤   cluster  ├───────────────┤  + overlay  │
        │  │ db-a          │            │ db-b          │  IPs        │
        │  │  HANA primary ┼── HSR sync ┼──▶ HANA sec.  │             │
        │  └───────────────┘            └───────────────┘             │
        │        shared FS: EFS/FSx  (/sapmnt, /usr/sap/trans)        │
        │        VPC endpoints: S3, KMS, SSM                          │
        └───────────────────────────┬────────────────────────────────┘
                                     │
                              S3 (HANA backups via Backint)
                              └─ lifecycle → Glacier; cross-Region copy → DR
```

## Layer by layer

| Layer | Component | AWS resource | Notes |
|-------|-----------|--------------|-------|
| Edge | User access | Route 53, ALB, DX/VPN | Low-latency access to Fiori/GUI |
| Network | Isolation | VPC, subnets (public/app/db) across 2 AZs | SAP in **private** subnets |
| Central services | (A)SCS + ERS | 2× EC2, Pacemaker, **overlay IP** | ENSA2 for clean failover |
| App tier | PAS + AAS + Web Disp | EC2 (M/R family), across AZs | Scale out; behind ALB |
| DB tier | HANA primary + secondary | 2× **certified EC2** (R/X/U) | **HSR sync** across AZs |
| Shared FS | /sapmnt, /usr/sap/trans | **EFS** or **FSx (ONTAP)** | Multi-AZ shared |
| Storage | HANA data/log volumes | **gp3/io2** per KPIs | See storage module |
| Backup | HANA backups | **Backint → S3** | Lifecycle + cross-Region |
| DR | Second Region | HSR **async**, AMIs, pilot light | See HA/DR module |
| Ops | Monitoring/patching | CloudWatch, **Data Provider for SAP**, SSM | + SolMan |
| Security | Identity/keys/secrets | IAM roles, KMS (CMK), Secrets Manager | IMDSv2, private subnets |

## Design principles specific to SAP on AWS

1. **Two AZs minimum** for any production SAP HA (primary + standby DB and ASCS).
2. **Only SAP-certified instances & OS.** Verify against SAP Notes each time.
3. **Storage must pass SAP KPIs** — validate with HCMT, don't assume.
4. **Overlay IPs** (outside the VPC CIDR) let the cluster float service addresses across
   AZs via route-table updates or an NLB.
5. **Keep AWS API traffic private** with VPC endpoints (S3/KMS/SSM) — backups and
   management shouldn't traverse the internet.
6. **Automate the build** (Launch Wizard / Terraform / CloudFormation) for repeatability
   across DEV/QAS/PRD.
7. **Right-size per environment**; only PRD needs full HA/DR.

## How the labs build toward this

- `labs/lab01-vpc-foundation` → the VPC/subnets/route tables/endpoints skeleton above.
- `labs/lab02-ec2-bastion` → secure admin access (bastion + SSM), an app-tier host.
- `labs/lab03-hana-host` → a single HANA-ready host with the correct volume layout
  (architecture + optional deploy).
- `labs/lab04-ha-overview` → walkthrough of the Pacemaker/HSR/overlay-IP HA design.

## Self-check

1. Why do the DB and central-services tiers each need a component in **both** AZs?
2. Which two AWS-native tricks keep backup and management traffic off the public
   internet?
3. In this diagram, what makes client connections survive a HANA node failover across
   AZs?

<details><summary>Answers</summary>

1. For **HA** — HSR sync keeps a live standby DB in AZ-b and an ENSA2/ERS partner for
   ASCS, so an AZ failure doesn't take the system down.
2. **VPC endpoints** (S3/KMS/SSM) and putting SAP hosts in **private subnets**
   (outbound via NAT only when needed).
3. The **overlay IP** managed by Pacemaker: on failover the route/NLB re-points the
   virtual address to the surviving node, so clients keep using the same address.
</details>
