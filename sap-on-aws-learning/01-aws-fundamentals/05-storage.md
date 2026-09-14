# 05 — Storage: EBS, EFS, FSx, S3

SAP has very specific storage needs (fast log volumes, big data volumes, a shared
`/sapmnt`, and cheap durable backup storage). Learn the four families and where each
fits.

## The four you must know

| Service | Type | Attaches how | SAP use |
|---------|------|--------------|---------|
| **EBS** | Block | One AZ, to one instance (io2 can be multi-attach) | HANA `/hana/data`, `/hana/log`, `/usr/sap`, root |
| **EFS** | File (NFS, Linux) | Multi-AZ, many instances | Shared `/sapmnt`, transport directory `/usr/sap/trans` |
| **FSx** | File | Managed | FSx for NetApp ONTAP / Windows for shared FS; NetWeaver on Windows |
| **S3** | Object | Over HTTPS/API | **Backups** (Backint), archives, software downloads, data lake |

## EBS — the workhorse for HANA

Elastic Block Store = network disks that behave like local drives. **Persist
independently** of the instance (unless you set delete-on-termination).

### Volume types

| Type | Class | Max IOPS | Max throughput | SAP use |
|------|-------|----------|----------------|---------|
| **gp3** | SSD general purpose | 16,000 | 1,000 MB/s | **Default for most HANA volumes** (decouples IOPS/throughput from size) |
| **io2 / io2 Block Express** | SSD provisioned IOPS | 256,000 | 4,000 MB/s | Highest-performance HANA log/data, large DBs |
| **st1** | HDD throughput | 500 | 500 MB/s | Big sequential (logs archive), *not* HANA data/log |
| **sc1** | HDD cold | 250 | 250 MB/s | Rarely accessed |

> **Why gp3 changed the game for SAP:** with gp2, IOPS were tied to volume size (3
> IOPS/GB), so you over-provisioned capacity just to get performance. **gp3** lets you
> set **IOPS and throughput independently** of size — cheaper HANA volumes that still
> meet SAP's storage KPIs.

### HANA volume layout (typical)
```
/hana/data     large,  high throughput   (gp3/io2, often striped across volumes via LVM)
/hana/log      smaller, low latency       (gp3/io2 — latency is critical for commits)
/hana/shared   medium                     (gp3, or EFS in scale-out)
/usr/sap       small                      (gp3)
/ (root)       small                      (gp3)
```
SAP publishes **storage KPIs** (latency & throughput at specific block sizes) the
volumes must pass — validated with SAP's **HCMT** (HANA Hardware Configuration Check
Tool). See `03-sap-on-aws/03-storage.md`.

### Snapshots
EBS **snapshots** are incremental backups stored in S3 (managed by AWS). Basis for
point-in-time recovery and cloning. **EBS Snapshot-based backup of HANA** (with
`hdbnsutil`/storage snapshots) is a supported HANA backup method alongside Backint.

### Encryption
EBS encryption uses **KMS**; enable **encryption by default** in the account. HANA
also has its own data/log volume encryption — you can use both.

## EFS — shared Linux file system
- Fully managed **NFS**, scales automatically, mountable from many instances across
  AZs simultaneously.
- Classic SAP use: **`/sapmnt`** and the **transport directory** shared by all app
  servers. Also `/hana/shared` in some scale-out designs.

## FSx
- **FSx for NetApp ONTAP**: enterprise NAS features (snapshots, dedup, SnapMirror) —
  popular for shared SAP file systems and even some HANA scenarios.
- **FSx for Windows File Server**: SMB shares for **SAP on Windows** (NetWeaver/ASCS
  on Windows uses an SMB share for the SAP global directory).

## S3 — object storage (backups & archives)
- **11 nines of durability** (`99.999999999%`), effectively unlimited.
- Organised into **buckets** → **objects** (key + data).
- **Storage classes** trade cost vs retrieval time:
  - `Standard` → hot.
  - `Standard-IA` / `One Zone-IA` → infrequent access.
  - `Glacier Instant / Flexible / Deep Archive` → cheap, cold, slow retrieval.
  - **Lifecycle policies** move backups from Standard → Glacier automatically.
- **SAP tie-in:** the **AWS Backint Agent for SAP HANA** streams HANA backups directly
  to S3. You then lifecycle them to Glacier for long retention. Cheap, durable,
  off-instance.
- **Versioning**, **Object Lock** (WORM/ransomware protection for backups), **cross-Region
  replication** (DR of backups).

## Durability vs availability (don't confuse them)
- **Durability** = will my data survive? (S3: 11 nines — practically never lost.)
- **Availability** = can I reach it right now? (S3 Standard: ~99.99%.)

## Self-check

1. Which EBS type do you pick for `/hana/log` and why is latency the deciding factor?
2. Why did gp3 reduce SAP storage cost vs gp2?
3. You need a file system shared by six SAP app servers across two AZs — EBS, EFS, or
   S3?
4. Where do HANA backups land when using the AWS Backint Agent, and how do you keep
   long-term copies cheap?

<details><summary>Answers</summary>

1. `gp3` (or `io2` for the largest DBs). Commits wait on log writes, so **low latency**
   dominates over raw capacity.
2. gp3 decouples IOPS/throughput from capacity, so you no longer over-provision GB just
   to hit SAP's performance KPIs.
3. **EFS** — multi-AZ, multi-attach NFS. EBS is single-AZ/single-instance; S3 isn't a
   POSIX file system.
4. In **S3**; use **lifecycle policies** to transition older backups to Glacier /
   Deep Archive.
</details>
