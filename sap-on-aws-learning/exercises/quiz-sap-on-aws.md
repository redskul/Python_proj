# Quiz — SAP on AWS

1. What is the "golden rule" that governs whether an SAP-on-AWS config is supported?
2. Why is the certified instance list for **HANA** narrower than for SAP app servers?
3. Which OS images are supported for HANA, and why not Amazon Linux?
4. What is an **overlay IP**, and why must it be **outside** the VPC CIDR?
5. Name the two mechanisms that route an overlay IP to the active node.
6. What three components combine to give automatic multi-AZ HANA failover?
7. Why HSR **sync** across AZs but **async** across Regions?
8. What does the **AWS Data Provider for SAP** do, and which SAP transaction needs it?
9. Where does the **AWS Backint Agent** send HANA backups, and how is that access
   secured?
10. When are **storage/EBS snapshots** preferable to a streamed backup?
11. What tool validates that your AWS storage meets SAP's HANA KPIs, and when do you run
    it?
12. Which VPC endpoints would you add for a HANA host and why?
13. In the "6 Rs", contrast **rehost** and **replatform** for ECC-on-Oracle.
14. Which SAP tool does an ECC→S/4HANA conversion + HANA migration in one run, and which
    variant relocates to AWS in the same step?
15. Why must you use `sapcontrol` (not just stop the EC2 instance) to shut a running SAP
    system down?
16. Which AWS framework/lens reviews an SAP deployment across six pillars?

---

<details><summary>Answers</summary>

1. SAP support is defined by **SAP Notes + AWS certification** — verify the instance/OS/
   storage/HA combo is certified and supported before building.
2. HANA has strict CPU/RAM ratios and performance requirements, so SAP certifies a
   specific subset (the HANA Hardware Directory).
3. **SLES for SAP** / **RHEL for SAP** — they carry SAP-required tuning + vendor support;
   plain distros aren't in SAP's HANA support matrix.
4. A virtual service IP the HA cluster floats across AZs; it must be outside the CIDR so
   failover works by re-pointing a **route** (an in-CIDR IP is bound to one AZ).
5. (a) Cluster updates a **route-table** entry `overlayIP/32 → active ENI`; (b) an
   internal **NLB** targeting the active node.
6. **HSR sync** + **Pacemaker/corosync** + **overlay IP**.
7. AZ latency is low enough for sync (RPO 0); cross-Region latency is too high for sync,
   so async (small RPO) is used for DR.
8. Feeds EC2/EBS/CloudWatch metrics into SAP OS monitoring so **ST06/saposcol** are
   accurate; may be required for support.
9. To **S3**, secured by the host's **IAM role** + **KMS CMK** encryption.
10. For **very large** databases where streaming a full backup is too slow.
11. **HCMT** — after provisioning, before go-live.
12. **S3** (Backint), **KMS** (encryption), **SSM** (Session Manager/patching), plus
    CloudWatch Logs — keeps backup/mgmt traffic private and off NAT/internet.
13. Rehost = lift the Oracle VMs to EC2 unchanged; replatform = also switch the DB (e.g.
    to HANA) during the move.
14. **SUM with DMO**; **DMO with System Move** relocates to AWS in the same procedure.
15. SAP has ordered start/stop dependencies and in-flight work; `sapcontrol` stops the
    app gracefully (app→ASCS→DB) to avoid corruption before instances stop.
16. The **AWS Well-Architected Framework — SAP Lens**.
</details>
