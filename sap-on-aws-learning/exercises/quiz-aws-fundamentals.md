# Quiz — AWS Fundamentals

Answers at the bottom. No peeking.

1. What is the relationship between a Region and an Availability Zone?
2. Which IAM object should an EC2 instance use to access S3, and why not access keys?
3. In IAM, an `Allow` and a `Deny` both match a request. What happens?
4. What single route-table entry makes a subnet public?
5. Security Group vs NACL: which is stateful, and which can express explicit *deny*?
6. Why do SAP servers go in **private** subnets, and how do they still get OS patches?
7. Which EBS volume type would you choose for `/hana/log`, and what KPI drives it?
8. Why did **gp3** reduce storage cost for SAP compared with gp2?
9. Is SAP HANA an AWS-managed database service? How is it run on AWS?
10. What's the difference between **durability** and **availability** (use S3 numbers)?
11. Name the service that answers "who made this API call and when?"
12. Which agent must you install for EC2 **memory** metrics to show in CloudWatch?
13. RPO vs RTO — define each in one line.
14. Order these DR strategies by increasing cost: Warm Standby, Backup & Restore, Pilot
    Light, Active/Active.
15. Which EC2 purchase option is best for 24/7 production, and which for the DB tier
    should you never use?
16. Two cost levers cut the SAP bill the most — one for prod, one for non-prod. Name them.

---

<details><summary>Answers</summary>

1. A Region is a geographic area containing multiple isolated AZs (data centres).
2. An **IAM role** (via instance profile) — it provides temporary, auto-rotated
   credentials; access keys can leak and must be rotated manually.
3. **Deny wins** (explicit deny always overrides allow).
4. `0.0.0.0/0 → Internet Gateway`.
5. Security Group is **stateful**; **NACL** can express explicit deny (and is stateless).
6. To keep them off the public internet (attack surface); they reach patches/S3 via a
   **NAT Gateway** or **VPC endpoints**.
7. **gp3** (or io2 for the largest DBs); **low latency** (commits wait on log writes).
8. gp3 decouples IOPS/throughput from capacity, so you don't over-provision GB to hit
   performance KPIs.
9. No — HANA is **self-managed on EC2** using SAP-certified instances + SAP-defined storage.
10. Durability = data survival (S3: 11 nines). Availability = reachable now (S3 Standard
    ~99.99%).
11. **CloudTrail**.
12. The **CloudWatch Agent**.
13. RPO = max acceptable data loss (time); RTO = max acceptable downtime (time).
14. Backup & Restore < Pilot Light < Warm Standby < Active/Active.
15. **Savings Plans / Reserved Instances** for 24/7 prod; **never Spot** for the DB.
16. Prod: **Savings Plans/RIs**; non-prod: **scheduled start/stop**.
</details>
