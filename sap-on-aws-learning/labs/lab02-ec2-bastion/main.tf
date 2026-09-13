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
      Lab       = "lab02-ec2-bastion"
    }
  }
}

# Always-current Amazon Linux 2023 AMI, resolved from the public SSM parameter.
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# ---------------------------------------------------------------------------
# IAM role + instance profile for Session Manager
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ssm" {
  name               = "${var.project}-lab02-ssm-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ssm.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ssm" {
  name = "${var.project}-lab02-ssm-profile"
  role = aws_iam_role.ssm.name
}

# ---------------------------------------------------------------------------
# Security group: NO inbound; outbound open (Session Manager is outbound-only).
# ---------------------------------------------------------------------------
resource "aws_security_group" "app" {
  name        = "${var.project}-lab02-app-sg"
  description = "App-tier host; SSM only, no inbound."
  vpc_id      = var.vpc_id

  egress {
    description = "All outbound (to reach SSM / patches)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project}-lab02-app-sg" }
}

# ---------------------------------------------------------------------------
# The instance
# ---------------------------------------------------------------------------
resource "aws_instance" "app" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ssm.name

  # Enforce IMDSv2 (token-based metadata) — a baseline hardening for SAP hosts.
  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  tags = {
    Name        = "${var.project}-lab02-app"
    Tier        = "app"
    Environment = "sandbox"
  }
}

# ---------------------------------------------------------------------------
# Optional: interface endpoints so a PRIVATE instance can use Session Manager
# without a NAT Gateway. (Small hourly cost per endpoint.)
# ---------------------------------------------------------------------------
data "aws_subnet" "selected" {
  id = var.subnet_id
}

resource "aws_security_group" "endpoints" {
  count       = var.create_ssm_endpoints ? 1 : 0
  name        = "${var.project}-lab02-endpoints-sg"
  description = "Allow HTTPS from the VPC to the interface endpoints."
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTPS from within the VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [data.aws_subnet.selected.cidr_block]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.project}-lab02-endpoints-sg" }
}

resource "aws_vpc_endpoint" "ssm" {
  for_each = var.create_ssm_endpoints ? toset(["ssm", "ssmmessages", "ec2messages"]) : toset([])

  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [var.subnet_id]
  security_group_ids  = [aws_security_group.endpoints[0].id]
  private_dns_enabled = true
  tags                = { Name = "${var.project}-lab02-${each.key}-endpoint" }
}
