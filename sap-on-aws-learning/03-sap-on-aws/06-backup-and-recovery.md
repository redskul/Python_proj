# 06 — Backup & Recovery for SAP on AWS

HA protects against failure; **backups protect against corruption, mistakes, and
ransomware** — and are the floor of your DR plan. HANA has its own backup framework;
AWS integrates with it.

## HANA backup concepts (recap)

- **Complete data backup**: full copy of the HANA data.
- **Delta backups**: incremental/differential since the last full.
- **Log backups**: frequent, bound your **RPO** (e.g. every 5–15 min). Without log
  backups you can only recover to the last data backup.
- **Backup catalog**: HANA's index of what backups exist (needed for recovery).

## Option A — AWS Backint Agent for SAP HANA (the AWS-native path)

**Backint** is SAP's backup API. The **AWS Backint Agent for SAP HANA** implements it so
HANA writes backups **directly to S3**:

```
HANA (backup command / scheduled) ──Backint──▶ AWS Backint Agent ──▶ S3 bucket
                                                        │
                                              IAM role + KMS (CMK)
```

- Configure once; then HANA `BACKUP DATA USING BACKINT` and log backups stream to S3.
- **No large local backup volume needed** — backups go straight to durable, cheap S3.
- Secured by the host's **IAM role** (write to the bucket) + **KMS CMK** (encryption).
- **Lifecycle** the bucket: S3 Standard → Glacier / Deep Archive for long retention.
- **Cross-Region replication** of the bucket for DR of the backups themselves.

## Option B — EBS / storage snapshots

- Quiesce HANA to create a **storage snapshot** (`hdbnsutil -createStorageSnapshot` /
  backup catalog entry), then take **EBS snapshots** of the data volumes.
- Very fast for **large** databases (snapshot vs streaming a multi-TB backup).
- Snapshots are incremental and stored in S3; copy **cross-Region** for DR.

## Option C — AWS Backup + Systems Manager for SAP

- **AWS Systems Manager for SAP** can register HANA databases and integrate with **AWS
  Backup** to orchestrate HANA (Backint) backups centrally with policies, retention, and
  cross-Region copy — a managed, auditable backup workflow across the landscape.
- **AWS Backup** also protects the *infrastructure* layer (non-DB EBS, EFS, FSx).

## AnyDB backups

For Oracle/Db2/SQL Server/ASE under SAP, use the DB's native backup tool writing to
S3 (via agents/S3 mounts) or AWS Backup where supported — same principles: off-instance,
encrypted, lifecycle, cross-Region.

## Designing to an RPO/RTO

| Business need | Backup design |
|---------------|---------------|
| RPO 15 min | Log backups every ≤ 15 min to S3 (Backint) |
| Fast restore of huge DB | Storage/EBS snapshots + log backups |
| Long retention (7 yr) | S3 lifecycle → Glacier Deep Archive, Object Lock (WORM) |
| Ransomware resilience | Object Lock + separate account + cross-Region copy |
| Regional DR | Cross-Region backup copy **and** HSR async |

## Recovery — practise it

1. Provision/identify target host.
2. Recover the **data backup** (Backint from S3 or snapshot restore).
3. Replay **log backups** to the desired point in time.
4. Validate the backup **catalog** and consistency.
5. **Test regularly** — a backup you've never restored is a guess.

## Self-check

1. Without **log backups**, what's the best recovery point you can achieve?
2. How does the **AWS Backint Agent** change where HANA backups are stored, and how is
   that access secured?
3. When are **storage/EBS snapshots** preferable to a streamed Backint backup?
4. Name two techniques that make S3-stored SAP backups ransomware-resilient.

<details><summary>Answers</summary>

1. Only the **last data backup** — no point-in-time replay is possible.
2. Backups stream **directly to S3** (no big local backup disk), secured by the host's
   **IAM role** + **KMS CMK** encryption.
3. For **very large** databases where streaming a full backup is too slow — snapshots
   are near-instant and incremental.
4. **S3 Object Lock (WORM)** + **cross-Region copy** (and isolating backups in a
   separate account) so backups can't be altered/deleted or lost with the primary.
</details>
