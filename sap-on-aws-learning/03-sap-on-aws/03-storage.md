# 03 — Storage for SAP on AWS

HANA has published **storage performance KPIs**. Meeting them on AWS is a design task,
not luck. This module is the practical heart of building a HANA host.

## The volumes and what they need

| Mount | Contents | Dominant KPI | Typical AWS choice |
|-------|----------|--------------|--------------------|
| `/hana/data` | Savepoints (in-memory image on disk) | **Throughput** | gp3 (multiple, striped) or io2 |
| `/hana/log` | Redo log (commit path) | **Low latency** | gp3 or **io2** for large DBs |
| `/hana/shared` | Binaries, config; shared in scale-out | Moderate | gp3 (EFS/FSx in scale-out) |
| `/usr/sap` | Local SAP instance dirs | Moderate | gp3 |
| `/ (root)`, swap | OS | Low | gp3 |
| `/sapmnt`, `/usr/sap/trans` | Shared across app servers | NFS | **EFS / FSx** |

## Meeting the KPIs with gp3

**gp3** decouples IOPS and throughput from capacity, so you provision performance
directly:

- gp3 baseline: 3,000 IOPS + 125 MB/s free; provision **up to 16,000 IOPS** and
  **1,000 MB/s** per volume.
- For higher throughput than one gp3 volume gives, **stripe multiple gp3 volumes** with
  **LVM** (Logical Volume Manager) so throughput adds up. `/hana/data` is commonly a
  striped LVM volume group.
- For the very largest DBs / most demanding logs, use **io2 / io2 Block Express**
  (up to 256,000 IOPS, 4,000 MB/s, single-volume).

### Example gp3 layout for a ~1 TB-RAM HANA
```
/hana/data   : 3–4 × gp3, LVM-striped, each ~400 GB @ high MB/s  → aggregate throughput
/hana/log    : 1–2 × gp3 (or io2), low latency, ~size per SAP guidance
/hana/shared : 1 × gp3 (~1× RAM)
/usr/sap     : 1 × gp3 (~50 GB)
root         : 1 × gp3 (~50 GB)
```
Exact sizes/counts come from SAP sizing + AWS's SAP storage guidance — treat the above
as illustrative and **validate with HCMT**.

## Validate, don't assume: HCMT

After you build the host, run SAP's **HCMT (HANA Hardware Configuration/Migration
Tool)**. It measures latency and throughput at defined block sizes and tells you
whether the storage passes SAP's KPIs. If it fails, add IOPS/throughput or more striped
volumes. **This is the objective proof your AWS storage is HANA-supported.**

## Encryption

- Turn on **EBS encryption by default** (KMS CMK).
- Optionally enable **HANA data & log volume encryption** on top (defence in depth).
- The same CMK strategy extends to S3 backup encryption.

## Shared file systems

- **EFS**: managed NFS, multi-AZ, elastic — great for `/sapmnt`, `/usr/sap/trans`, and
  `/hana/shared` in scale-out.
- **FSx for NetApp ONTAP**: enterprise NAS (snapshots, dedup, SnapMirror) when you want
  those features; supported for several SAP shared-FS and even some HANA scenarios.

## Snapshots & data protection

- **EBS snapshots** = incremental point-in-time volume backups (stored in S3, managed).
- **HANA storage-snapshot backups**: quiesce HANA (`hdbnsutil`/backup catalog) then
  snapshot the volumes for fast PIT recovery — complements Backint (next module).
- Copy snapshots **cross-Region** for DR.

## Cost angles

- Provision only the IOPS/throughput the KPIs need (gp3 lets you dial it).
- Don't leave orphaned volumes/snapshots; lifecycle old snapshots.
- Remember **cross-AZ replication traffic** cost for HSR.

## Self-check

1. Why is `/hana/log` latency-critical and `/hana/data` throughput-critical?
2. How do you exceed a single gp3 volume's throughput ceiling for `/hana/data`?
3. What tool proves your AWS storage meets SAP's HANA KPIs, and when do you run it?
4. Which mounts belong on EFS/FSx rather than EBS, and why?

<details><summary>Answers</summary>

1. Commits block on synchronous redo-log writes (latency); savepoints flush large data
   images (throughput).
2. **Stripe multiple gp3 volumes with LVM** (or move to io2 Block Express).
3. **HCMT** — run it after provisioning, before go-live.
4. `/sapmnt`, `/usr/sap/trans` (and `/hana/shared` in scale-out) — they must be shared
   across multiple hosts/AZs, which EBS can't do but EFS/FSx can.
</details>
