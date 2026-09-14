# Glossary — SAP on AWS

SAP and AWS both love acronyms. Here they all are.

## AWS

| Term | Meaning |
|------|---------|
| **AZ** | Availability Zone — isolated data centre(s) within a Region |
| **Region** | Geographic collection of AZs |
| **EC2** | Elastic Compute Cloud — virtual servers |
| **AMI** | Amazon Machine Image — boot template |
| **EBS** | Elastic Block Store — network block disks (gp3/io2/st1/sc1) |
| **EFS** | Elastic File System — managed NFS (multi-AZ) |
| **FSx** | Managed file systems (NetApp ONTAP, Windows) |
| **S3** | Simple Storage Service — object storage |
| **VPC** | Virtual Private Cloud — your isolated network |
| **IGW / NAT GW** | Internet Gateway / NAT Gateway |
| **SG / NACL** | Security Group (stateful) / Network ACL (stateless) |
| **ENI** | Elastic Network Interface — virtual NIC |
| **IAM** | Identity & Access Management |
| **KMS** | Key Management Service (encryption keys) |
| **IMDS(v2)** | Instance Metadata Service (v2 = token-based) |
| **ALB / NLB** | Application / Network Load Balancer |
| **ASG** | Auto Scaling Group |
| **RI / Savings Plan** | Reserved Instance / commitment-based discount |
| **DX** | Direct Connect — dedicated private link to AWS |
| **TGW** | Transit Gateway — network hub |
| **SSM** | AWS Systems Manager (Session Manager, Patch, Run Command…) |
| **RDS / Aurora** | Managed relational databases |
| **CloudWatch / CloudTrail / Config** | Metrics&logs / API audit / config compliance |
| **GuardDuty / Security Hub / Inspector** | Threat detection / findings hub / CVE scan |
| **MGN / DRS** | Application Migration Service / Elastic Disaster Recovery |
| **RPO / RTO** | Recovery Point / Time Objective |
| **CMK** | Customer-Managed Key (in KMS) |

## SAP

| Term | Meaning |
|------|---------|
| **ERP** | Enterprise Resource Planning |
| **ECC** | ERP Central Component (classic pre-S/4 ERP) |
| **S/4HANA** | Current-gen ERP, requires HANA |
| **HANA** | High-performance ANalytic Appliance — in-memory column DB & platform |
| **NetWeaver** | Classic SAP technical application platform (ABAP/Java) |
| **ABAP** | SAP's business-logic programming language |
| **Fiori** | Modern SAP web UI |
| **SAP GUI** | Classic thick-client UI |
| **SID** | System ID (3 chars, e.g. PRD) |
| **(A)SCS** | (ABAP) SAP Central Services — message + enqueue server |
| **ERS** | Enqueue Replication Server |
| **ENSA1 / ENSA2** | (Standalone) Enqueue Server v1/v2 |
| **PAS / AAS** | Primary / Additional Application Server |
| **Web Dispatcher** | SAP reverse proxy / HTTP load balancer |
| **HSR** | HANA System Replication (sync/syncmem/async) |
| **SAPS** | SAP Application Performance Standard (throughput unit) |
| **AnyDB** | SAP's term for non-HANA DBs (Oracle, Db2, SQL Server, ASE) |
| **Basis** | SAP system-administration discipline |
| **SAP Note** | Official SAP KB article/fix (by number) |
| **SWPM** | Software Provisioning Manager (installer) |
| **HDBLCM** | HANA Database Lifecycle Manager (HANA installer) |
| **SUM / DMO** | Software Update Manager / Database Migration Option |
| **HCMT** | HANA Hardware Configuration/Migration Tool (KPI validation) |
| **saptune** | SUSE tool applying SAP-Note OS tuning |
| **SolMan** | SAP Solution Manager (landscape management) |
| **BW/4HANA** | SAP data warehouse |
| **BTP** | Business Technology Platform (SAP PaaS) |
| **RISE with SAP** | SAP-managed S/4HANA Cloud subscription (can run on AWS) |
| **`/sapmnt`, `/usr/sap/trans`** | Shared SAP directories (on EFS/FSx) |

## SAP-on-AWS bridges

| Term | Meaning |
|------|---------|
| **Overlay IP** | Virtual service IP outside the VPC CIDR, moved across AZs by the HA cluster (route table / NLB) |
| **AWS Data Provider for SAP** | Daemon feeding EC2/EBS metrics into SAP ST06/saposcol |
| **AWS Backint Agent** | Implements SAP Backint API to stream HANA backups to S3 |
| **AWS Launch Wizard for SAP** | Guided, SAP-certified infra deployment (emits CloudFormation) |
| **AWS Systems Manager for SAP** | Register SAP apps for start/stop + Backint/AWS Backup |
| **SAP Certified Hardware Directory** | SAP's list of certified IaaS (incl. certified EC2 types) |
| **SLES for SAP / RHEL for SAP** | SAP-supported OS images (Marketplace, include tuning + support) |
