# 03 — VPC & Networking

A **VPC (Virtual Private Cloud)** is your own logically isolated network inside AWS.
SAP landscapes live in carefully designed VPCs, so this module is foundational.

## The pieces

| Component | Purpose |
|-----------|---------|
| **VPC** | A private IP range (CIDR), e.g. `10.0.0.0/16`. Regional. |
| **Subnet** | A slice of the VPC CIDR bound to **one AZ**, e.g. `10.0.1.0/24`. |
| **Route table** | Rules that decide where traffic goes. |
| **Internet Gateway (IGW)** | Lets a *public* subnet reach the internet. |
| **NAT Gateway** | Lets *private* subnets make **outbound** internet calls (patching, S3) without being reachable inbound. |
| **Security Group (SG)** | **Stateful** virtual firewall on an ENI/instance. Allow rules only. |
| **Network ACL (NACL)** | **Stateless** firewall at the subnet edge. Allow + deny rules. |
| **VPC Endpoint** | Private connectivity to AWS services (e.g. S3) without traversing the internet. |
| **Elastic Network Interface (ENI)** | A virtual NIC; carries private IPs, used for SAP **overlay IP** patterns. |

### Public vs private subnet — the only real difference
A subnet is **public** if its route table has a route `0.0.0.0/0 → IGW`. Otherwise
it's **private**. That's it.

## The reference SAP layout

```
VPC 10.0.0.0/16  (Region: eu-central-1)
├── AZ-a
│   ├── public-a   10.0.0.0/24     → bastion, NAT GW, load balancer
│   ├── app-a      10.0.1.0/24     → SAP app servers (private)
│   └── db-a       10.0.2.0/24     → SAP HANA primary (private)
└── AZ-b
    ├── public-b   10.0.10.0/24    → NAT GW (2nd), LB
    ├── app-b      10.0.11.0/24    → SAP app servers (private)
    └── db-b       10.0.12.0/24    → SAP HANA standby (private)
```

- SAP servers go in **private** subnets — never directly on the internet.
- A **bastion host** (or SSM Session Manager) in a public subnet gives admin access.
- **Outbound** internet (SAP patches, connecting to S3, AWS APIs) goes via **NAT GW**
  or, better, **VPC endpoints** for S3/KMS/SSM to keep traffic on the AWS backbone.

## Security Groups vs NACLs (a favourite exam topic)

| | Security Group | Network ACL |
|--|----------------|-------------|
| Scope | Instance/ENI | Subnet |
| State | **Stateful** (return traffic auto-allowed) | **Stateless** (must allow both directions) |
| Rules | **Allow only** | Allow **and** Deny |
| Evaluation | All rules evaluated | Rules in **numbered order**, first match wins |

For SAP you'll open ports like: SSH (22, restrict to bastion), HANA SQL (3<inst>15,
e.g. 30015), SAP dispatcher (32<inst>, 33<inst>), Fiori/HTTPS (443), and cluster
comms. Restrict source to the specific SGs, not `0.0.0.0/0`.

## Connecting to on-premises (hybrid — normal for SAP)

Real SAP landscapes are rarely 100% cloud on day one. You connect the VPC to the
corporate data centre by:

- **Site-to-Site VPN** — encrypted tunnel over the internet. Cheap, quick, ~variable
  latency. Good for dev/test or as backup.
- **AWS Direct Connect (DX)** — a **dedicated private line**. Consistent low latency &
  bandwidth. The standard for production SAP (SAP GUI feels local, big data migrations).
- **Transit Gateway** — a hub that connects many VPCs + on-prem in a hub-and-spoke,
  the norm for multi-account SAP landscapes.

## The SAP "overlay IP" — remember this for HA

An **overlay IP** is a virtual IP **outside** the VPC CIDR that the HA cluster
(Pacemaker) moves between the primary and standby HANA/ASCS nodes across AZs. Because
it's outside the VPC range, failover is done by **updating a route table** (or via a
Network Load Balancer) to point the overlay IP at whichever node is active. Clients
always connect to the overlay IP, unaware of which AZ currently serves them.
Details in `03-sap-on-aws/05-high-availability-and-dr.md`.

## DNS

- **Route 53** = AWS DNS (public zones + **private hosted zones** for internal names
  like `hana-db.sap.internal`). SAP hosts rely heavily on consistent hostname
  resolution (the `hostname` must match SAP's expectations), so private hosted zones
  or a resolver forwarding to on-prem AD/DNS is common.

## Lab tie-in

`labs/lab01-vpc-foundation` builds this exact multi-AZ VPC (public + app + db subnets,
IGW, NAT, route tables, endpoints). Deploy it and inspect the route tables.

## Self-check

1. What single route-table entry makes a subnet "public"?
2. Why is a Security Group easier to reason about than a NACL for return traffic?
3. Your private SAP app server must download OS patches. Draw the two ways it reaches
   the internet/S3 without being publicly reachable.
4. Why must the SAP overlay IP live *outside* the VPC CIDR?

<details><summary>Answers</summary>

1. `0.0.0.0/0 → Internet Gateway`.
2. SGs are stateful: allow inbound and the reply is automatically allowed. NACLs are
   stateless, so you must add matching outbound (ephemeral port) rules.
3. (a) Route to a **NAT Gateway** in a public subnet; (b) a **VPC endpoint** for S3 /
   SSM so the traffic never leaves the AWS backbone.
4. So failover can be done by re-pointing a **route** to the active ENI/node across
   AZs; an in-CIDR IP is tied to one subnet/AZ and can't float between AZs.
</details>
