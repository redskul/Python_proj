# Quiz — SAP Fundamentals

1. What does ERP stand for and what problem does it solve?
2. What distinguishes **S/4HANA** from the older **ECC**?
3. Why is ~2027 a driver for so many SAP-on-AWS projects?
4. Name the three tiers of the classic SAP architecture. Which scales horizontally?
5. What is the **(A)SCS**, and why is it the classic single point of failure?
6. What does **ENSA2** change vs ENSA1, and why does it matter for multi-AZ HA?
7. Why is SAP HANA sized primarily by **memory**?
8. On a HANA host, why does `/hana/log` care about latency and `/hana/data` about
   throughput?
9. Which HANA System Replication mode gives **RPO 0**, and where is it used?
10. What is **SAPS** and how do you use it when choosing an EC2 instance?
11. Define **transport** and name the shared directory it flows through.
12. In "self-managed S/4HANA on AWS", who owns the OS, HANA, and HA — you or SAP? How
    does **RISE** differ?
13. What is **Basis**?
14. Which shared SAP directories typically live on **EFS/FSx** rather than EBS, and why?

---

<details><summary>Answers</summary>

1. Enterprise Resource Planning — runs all core business processes on one integrated
   system and shared data model.
2. S/4HANA is rebuilt to run **only on HANA**, with a simplified data model and Fiori UX.
3. Legacy **ECC mainstream maintenance ends ~2027** (extendable to 2030), pushing a mass
   migration to S/4HANA — often to AWS at the same time.
4. Presentation, Application, Database. The **application** tier scales horizontally.
5. ABAP SAP Central Services (message + **enqueue/lock** server); the single enqueue is a
   SPOF, so it must be clustered.
6. ENSA2 lets the enqueue lock table fail over to **any** node (not just a co-located
   one), enabling clean multi-AZ Pacemaker clusters.
7. It's an **in-memory** database — the working dataset lives in RAM.
8. Commits block on synchronous redo-log writes (latency); savepoints flush large data
   images (throughput).
9. **sync** — used for **HA across two AZs**.
10. SAP Application Performance Standard, a throughput unit; size the workload in SAPS,
    then pick a certified instance rated for that many SAPS.
11. A packaged change promoted DEV→QAS→PRD, moved via **`/usr/sap/trans`**.
12. Self-managed: **you** own OS/HANA/HA (AWS owns the infra). Under **RISE**, SAP manages
    technical operations even when AWS is the underlying infra.
13. The SAP system-administration discipline (installs, patching, tuning, HA/DR).
14. `/sapmnt` and `/usr/sap/trans` (and `/hana/shared` in scale-out) — they must be
    shared across hosts/AZs, which needs EFS/FSx, not single-AZ EBS.
</details>
