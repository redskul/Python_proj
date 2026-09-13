terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
      Lab       = "lab03-hana-host"
    }
  }
}

# NOTE: for a *supported* HANA host you would use a SLES-for-SAP / RHEL-for-SAP AMI
# from the Marketplace. We use Amazon Linux 2023 here purely to demonstrate the
# storage layout cheaply. This is NOT a supported HANA configuration.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "hana" {
  name               = "${var.project}-lab03-hana-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.hana.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "hana" {
  name = "${var.project}-lab03-hana-profile"
  role = aws_iam_role.hana.name
}

resource "aws_security_group" "hana" {
  name        = "${var.project}-lab03-hana-sg"
  description = "HANA host; SSM only, no inbound in this lab."
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.project}-lab03-hana-sg" }
}

# Bootstrap: format + mount each volume at its HANA path so `df -h` shows the layout.
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -euo pipefail
    # Map the attached NVMe/EBS devices to HANA mount points and format them.
    declare -A mounts=(
      ["/dev/sdf"]="/hana/data"
      ["/dev/sdg"]="/hana/log"
      ["/dev/sdh"]="/hana/shared"
      ["/dev/sdi"]="/usr/sap"
    )
    # On Nitro instances device names may appear as /dev/nvmeXn1; resolve by serial.
    for dev in "$${!mounts[@]}"; do
      mp="$${mounts[$dev]}"
      # find the actual device (Nitro remaps names)
      real=$(readlink -f "$dev" 2>/dev/null || echo "$dev")
      if [ ! -b "$real" ]; then real="$dev"; fi
      mkfs.xfs -f "$real" || true
      mkdir -p "$mp"
      mount "$real" "$mp" || true
    done
    echo "HANA-shaped mounts prepared (lab03)." > /var/log/lab03-hana.log
    df -h | grep -E 'hana|usr/sap' >> /var/log/lab03-hana.log || true
  EOF
}

resource "aws_instance" "hana" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.hana_instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.hana.id]
  iam_instance_profile   = aws_iam_instance_profile.hana.name
  user_data              = local.user_data

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  # Root volume
  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name        = "${var.project}-lab03-hana"
    Tier        = "db"
    Role        = "hana"
    Environment = "sandbox"
  }
}

# ---------------------------------------------------------------------------
# HANA data/log/shared/usr-sap volumes — separate, encrypted gp3.
# /hana/data  -> throughput-tuned ; /hana/log -> IOPS/latency-tuned.
# ---------------------------------------------------------------------------
resource "aws_ebs_volume" "data" {
  availability_zone = aws_instance.hana.availability_zone
  type              = "gp3"
  size              = var.data_size_gb
  throughput        = var.data_throughput_mbps
  iops              = var.data_iops
  encrypted         = true
  tags              = { Name = "${var.project}-hana-data", Mount = "/hana/data" }
}

resource "aws_ebs_volume" "log" {
  availability_zone = aws_instance.hana.availability_zone
  type              = "gp3"
  size              = var.log_size_gb
  iops              = var.log_iops
  encrypted         = true
  tags              = { Name = "${var.project}-hana-log", Mount = "/hana/log" }
}

resource "aws_ebs_volume" "shared" {
  availability_zone = aws_instance.hana.availability_zone
  type              = "gp3"
  size              = var.shared_size_gb
  encrypted         = true
  tags              = { Name = "${var.project}-hana-shared", Mount = "/hana/shared" }
}

resource "aws_ebs_volume" "usrsap" {
  availability_zone = aws_instance.hana.availability_zone
  type              = "gp3"
  size              = var.usrsap_size_gb
  encrypted         = true
  tags              = { Name = "${var.project}-usr-sap", Mount = "/usr/sap" }
}

resource "aws_volume_attachment" "data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.data.id
  instance_id = aws_instance.hana.id
}

resource "aws_volume_attachment" "log" {
  device_name = "/dev/sdg"
  volume_id   = aws_ebs_volume.log.id
  instance_id = aws_instance.hana.id
}

resource "aws_volume_attachment" "shared" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.shared.id
  instance_id = aws_instance.hana.id
}

resource "aws_volume_attachment" "usrsap" {
  device_name = "/dev/sdi"
  volume_id   = aws_ebs_volume.usrsap.id
  instance_id = aws_instance.hana.id
}
