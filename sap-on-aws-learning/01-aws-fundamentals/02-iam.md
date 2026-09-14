# 02 — IAM: Identity & Access Management

IAM controls **who** (identity) can do **what** (actions) on **which** resources,
under **which conditions**. It's global (not Region-specific) and free.

## The building blocks

| Object | What it is |
|--------|-----------|
| **Root user** | The account owner. Almighty. Use it only to set up billing & the first admin, then lock it away with MFA. |
| **IAM user** | A person or app with long-term credentials (password / access keys). |
| **IAM group** | A bucket of users that share policies (e.g. `SAPBasisAdmins`). |
| **IAM role** | A set of permissions **assumed temporarily** — no long-term keys. Used by EC2 instances, Lambda, cross-account access, federation. |
| **Policy** | A JSON document listing `Allow`/`Deny` on `Action` + `Resource` (+ `Condition`). |
| **IAM Identity Center** (successor to AWS SSO) | Central workforce login, ideal for multi-account SAP landscapes. |

## Policies: the JSON you must be able to read

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadHanaBackupsBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-hana-backups",
        "arn:aws:s3:::my-hana-backups/*"
      ]
    }
  ]
}
```

- **Effect**: `Allow` or `Deny` (an explicit `Deny` always wins).
- **Action**: service:operation, wildcards allowed (`s3:*`).
- **Resource**: the ARN(s) it applies to.
- **Condition** (optional): e.g. only from a VPC, only with MFA, only in a Region.

### Policy types
- **Identity-based**: attached to a user/group/role (most common).
- **Resource-based**: attached to a resource (S3 bucket policy, KMS key policy).
- **Permissions boundary**: a *ceiling* on what an identity can be granted.
- **Service control policies (SCPs)**: org-wide guardrails (AWS Organizations).

## The golden rule: least privilege

Grant only the permissions actually needed. Start with **AWS managed policies** for
learning, then tighten to custom policies. For SAP you'll create roles like:

- **`SAP-HANA-Backint-Role`** — lets the HANA instance write backups to a specific
  S3 bucket and read a KMS key (via **AWS Backint Agent**).
- **`SAP-SystemsManager-Role`** — lets Systems Manager patch/administer the host.
- **`SAP-CloudWatch-Role`** — lets the **AWS Data Provider for SAP** publish metrics
  that SAP's monitoring (ST06/OS collector) reads.

## Roles on EC2 = instance profiles (critical for SAP)

**Never put access keys on an EC2 instance.** Instead attach an **IAM role** via an
**instance profile**. The instance gets **temporary, auto-rotated credentials** from
the instance metadata service (IMDS). This is exactly how your SAP HANA host gets
permission to write to the S3 backup bucket — no secrets on disk.

```bash
# From inside an EC2 instance, the SDK/CLI transparently uses the role. To see it:
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/   # IMDSv1
# Prefer IMDSv2 (token-based) — enforce it on all SAP hosts.
```

## MFA, password policy, credential hygiene

- Enforce **MFA** for all human users, especially anything with write access.
- Rotate access keys; better yet, use **IAM Identity Center** / roles so there are
  no long-lived keys at all.
- Use **IAM Access Analyzer** to find resources shared too broadly.

## How a request is evaluated (simplified)

1. Default = **implicit deny**.
2. Any explicit **Deny** anywhere → denied. (SCPs, boundaries, session policies all apply.)
3. Otherwise, if some policy **Allows** it → allowed.
4. Else → denied.

## Lab tie-in

- `labs/lab01-vpc-foundation` creates an IAM role + instance profile for the bastion.
- `automation/preflight_check.py` calls `sts:GetCallerIdentity` to prove your identity.

## Self-check

1. Why is an IAM **role** on EC2 safer than baking in access keys?
2. You attach a policy that `Allow`s `s3:*` and another that `Deny`s
   `s3:DeleteObject`. Can the user delete objects?
3. Which IAM object would you use to give your entire org a guardrail like "no one may
   disable CloudTrail"?

<details><summary>Answers</summary>

1. Roles hand out temporary, auto-rotated credentials via IMDS — nothing to leak or
   rotate manually.
2. **No** — an explicit `Deny` always overrides an `Allow`.
3. A **Service Control Policy (SCP)** in AWS Organizations.
</details>
