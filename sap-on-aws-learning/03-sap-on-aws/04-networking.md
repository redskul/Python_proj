# 04 — Networking for SAP on AWS

Builds on `01-aws-fundamentals/03-vpc-networking.md` with the SAP-specific details.

## Subnet design

- **Two AZs** minimum for production (primary + standby).
- Separate subnets per tier per AZ: `public`, `app`, `db` — keeps SG rules clean and
  blast radius small.
- SAP hosts (app + db) always in **private** subnets.

## The overlay IP pattern (the thing to truly understand)

Problem: an EC2 private IP belongs to **one subnet in one AZ**, so it can't "move" to a
node in another AZ during failover. SAP HA (HANA, ASCS) needs a **virtual service
address** clients use that follows the active node **across AZs**.

Solution: an **overlay IP** — an address chosen **outside the VPC CIDR** (so it isn't
tied to any subnet). Two ways to make it route:

1. **Route-table method**: the Pacemaker cluster's AWS resource agent updates a
   **VPC route table** entry (`overlay-IP/32 → active node's ENI`) on failover. Clients
   in the VPC reach the overlay IP via that route. On-prem clients reach it via routes
   propagated through Transit Gateway / DX + a route in the on-prem network.
2. **Network Load Balancer method**: an internal **NLB** targets both nodes; health
   checks send traffic only to the active one. Clients hit the NLB address.

Either way, the client address is stable while the backend floats across AZs.

## Why the overlay IP must be outside the VPC CIDR

If it were inside the CIDR, VPC routing would treat it as a normal subnet address bound
to one AZ. Placing it **outside** the CIDR forces traffic through the **route table**
(or NLB), which the cluster can repoint — enabling cross-AZ failover.

## Keeping traffic private: VPC endpoints

Add **VPC endpoints** so SAP hosts reach AWS services without the internet:

- **S3 (Gateway endpoint)** — HANA Backint backups, software downloads.
- **KMS, SSM, SSM Messages, EC2 Messages (Interface endpoints)** — encryption, Session
  Manager, patching.
- **CloudWatch/Logs endpoints** — metrics/log shipping.

Benefits: lower latency, no NAT egress cost for that traffic, and it never leaves the
AWS backbone (security & compliance win).

## Hybrid connectivity

- **Direct Connect (DX)** — standard for production SAP: consistent low latency for SAP
  GUI/Fiori and large migration data transfer.
- **Site-to-Site VPN** — dev/test or DX backup.
- **Transit Gateway** — hub for multi-VPC / multi-account SAP landscapes + on-prem.

## DNS & hostnames

- SAP is picky about **hostnames** (the SAP host agent, profiles, and HANA topology
  depend on stable names). Use **Route 53 private hosted zones** (e.g.
  `hana01.sap.internal`) and/or forward to corporate DNS/AD.
- Keep hostnames stable across stop/start (don't rely on the auto-assigned public DNS).

## Security groups for SAP (typical ports)

| Traffic | Port(s) | Rule |
|---------|---------|------|
| SSH admin | 22 | From bastion SG / SSM only |
| HANA SQL | 3<inst>13/15 (e.g. 30013/30015) | app-tier SG → db-tier SG |
| HANA System Replication | 4<inst>0x (e.g. 40001–40007) | between HANA nodes only |
| SAP dispatcher / gateway | 32<inst>, 33<inst> | app tier |
| Message server | 36<inst> (e.g. 3600) | app tier |
| Fiori / HTTPS | 443 | ALB → Web Dispatcher |
| Cluster (corosync) | 5405/udp etc. | between cluster nodes only |

Scope **source** to specific SGs, never `0.0.0.0/0`.

## Self-check

1. Why can't a normal EC2 private IP serve as the floating service address for a
   cross-AZ HANA cluster?
2. Describe the two mechanisms that make an overlay IP reach the active node.
3. Give three VPC endpoints you'd add for a HANA host and what each is for.
4. Why does SAP care so much about stable hostnames, and how do you provide them?

<details><summary>Answers</summary>

1. A private IP is bound to one subnet/AZ and can't move to another AZ; failover across
   AZs needs an address decoupled from any subnet.
2. (a) Cluster updates a **route-table** entry `overlayIP/32 → active ENI`; (b) an
   internal **NLB** health-checks and forwards only to the active node.
3. **S3** (Backint backups), **KMS** (encryption), **SSM** (Session Manager/patching) —
   also CloudWatch Logs. Keeps traffic private and off NAT/internet.
4. SAP profiles/host agent/HANA topology bind to hostnames; use **Route 53 private
   hosted zones** and keep names stable across restarts.
</details>
