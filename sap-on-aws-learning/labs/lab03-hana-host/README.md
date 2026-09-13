# Lab 03 — A HANA-shaped EC2 host (storage layout)

Provision a single EC2 instance with the **correct HANA EBS volume layout** — separate,
encrypted **gp3** volumes for `/hana/data`, `/hana/log`, `/hana/shared`, and `/usr/sap`,
each with SAP-appropriate IOPS/throughput. This teaches the storage design from
`../../03-sap-on-aws/03-storage.md` **without** forcing you to run a giant, expensive
instance.

## ⚠️ Cost & support caveats — read carefully

- This lab is **architecture-accurate, not a supported HANA install.** It builds the
  *infrastructure*; it does **not** install HANA (that's HDBLCM/SWPM) and does **not**
  use a SAP-certified OS by default.
- The **default `hana_instance_type` is a small `r6i.large`** so you can see the layout
  cheaply. A real HANA host would be a certified type with **hundreds of GB to multiple
  TB of RAM** and would cost **many dollars per hour**. Only raise it deliberately.
- **The extra gp3 volumes cost money while they exist.** `terraform destroy` when done.
- For a *supported* build, use **SLES for SAP / RHEL for SAP** AMIs, a **certified
  instance**, and validate with **HCMT**. See the compute & storage modules.

## What it creates

- 1 EC2 instance (`var.hana_instance_type`, default `r6i.large`), IMDSv2 enforced.
- Encrypted **gp3** EBS volumes attached at the standard HANA device names:
  - `/hana/data`   (high throughput, striped in real life)
  - `/hana/log`    (low latency)
  - `/hana/shared`
  - `/usr/sap`
- An IAM role/instance profile (SSM + room to add Backint later).
- A `user_data` script that formats & mounts the volumes at the HANA paths, so you can
  connect via SSM and run `df -h` to see the layout.
- A security group with no inbound (SSM access, like lab02).

Volume **sizes/IOPS/throughput** are driven by variables you can compute with
`../../automation/ebs_storage_planner.py`.

## Run

```bash
terraform init
terraform apply \
  -var 'aws_region=eu-central-1' \
  -var 'vpc_id=vpc-xxxx' \
  -var 'subnet_id=subnet-xxxx' \
  -var 'hana_instance_type=r6i.large'      # keep small for learning!

aws ssm start-session --target "$(terraform output -raw instance_id)"
#   then inside:  df -h | grep hana   ;  lsblk
terraform destroy -var 'vpc_id=vpc-xxxx' -var 'subnet_id=subnet-xxxx'
```

(Use the same subnet-connectivity rules as lab02 for SSM: public subnet = free, private
subnet needs the interface endpoints from lab02 or a NAT.)

## Learning questions

1. Why are `/hana/data` and `/hana/log` on **separate** volumes with different
   IOPS/throughput?
2. What would you change to make this a **supported** HANA host?
3. How would you exceed a single gp3 volume's 1,000 MB/s throughput cap for
   `/hana/data`?
4. After building the real thing, what tool proves the storage meets SAP's KPIs?
