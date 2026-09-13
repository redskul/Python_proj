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
      Lab       = "lab01-vpc-foundation"
    }
  }
}

# Discover the available AZs in the chosen Region.
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  # Carve /24 subnets out of the VPC CIDR. Offsets keep the three tiers separate:
  #   public : .0.x   app : .1x.x   db : .2x.x  (per AZ index)
  public_subnets = { for i, az in local.azs : az => cidrsubnet(var.vpc_cidr, 8, i) }
  app_subnets    = { for i, az in local.azs : az => cidrsubnet(var.vpc_cidr, 8, i + 10) }
  db_subnets     = { for i, az in local.azs : az => cidrsubnet(var.vpc_cidr, 8, i + 20) }

  nat_count = var.enable_nat ? (var.single_nat ? 1 : var.az_count) : 0
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${var.project}-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-igw" }
}

# ---------------------------------------------------------------------------
# Subnets
# ---------------------------------------------------------------------------
resource "aws_subnet" "public" {
  for_each                = local.public_subnets
  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = true
  tags = { Name = "${var.project}-public-${each.key}", Tier = "public" }
}

resource "aws_subnet" "app" {
  for_each          = local.app_subnets
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = each.key
  tags = { Name = "${var.project}-app-${each.key}", Tier = "app" }
}

resource "aws_subnet" "db" {
  for_each          = local.db_subnets
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = each.key
  tags = { Name = "${var.project}-db-${each.key}", Tier = "db" }
}

# ---------------------------------------------------------------------------
# NAT (optional, costs money)
# ---------------------------------------------------------------------------
resource "aws_eip" "nat" {
  count  = local.nat_count
  domain = "vpc"
  tags   = { Name = "${var.project}-nat-eip-${count.index}" }
}

resource "aws_nat_gateway" "nat" {
  count         = local.nat_count
  allocation_id = aws_eip.nat[count.index].id
  # Place NAT GW in a public subnet. With single_nat, use the first AZ's public subnet.
  subnet_id     = values(aws_subnet.public)[count.index].id
  tags          = { Name = "${var.project}-nat-${count.index}" }
  depends_on    = [aws_internet_gateway.igw]
}

# ---------------------------------------------------------------------------
# Route tables
# ---------------------------------------------------------------------------
# Public: default route to the Internet Gateway.
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.project}-rt-public" }
}

resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

# App: one route table per AZ; default route to NAT if enabled.
resource "aws_route_table" "app" {
  for_each = aws_subnet.app
  vpc_id   = aws_vpc.main.id
  tags     = { Name = "${var.project}-rt-app-${each.key}" }
}

resource "aws_route" "app_nat" {
  for_each               = var.enable_nat ? aws_route_table.app : {}
  route_table_id         = each.value.id
  destination_cidr_block = "0.0.0.0/0"
  # single_nat -> everyone uses nat[0]; else map AZ index to its NAT.
  nat_gateway_id = var.single_nat ? aws_nat_gateway.nat[0].id : aws_nat_gateway.nat[index(keys(aws_subnet.app), each.key)].id
}

resource "aws_route_table_association" "app" {
  for_each       = aws_subnet.app
  subnet_id      = each.value.id
  route_table_id = aws_route_table.app[each.key].id
}

# DB: fully private route table (no default internet route at all).
resource "aws_route_table" "db" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-rt-db" }
}

resource "aws_route_table_association" "db" {
  for_each       = aws_subnet.db
  subnet_id      = each.value.id
  route_table_id = aws_route_table.db.id
}

# ---------------------------------------------------------------------------
# S3 Gateway VPC Endpoint (free) — lets HANA hosts reach S3 (Backint) privately.
# Attach it to the app + db route tables.
# ---------------------------------------------------------------------------
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = concat(
    [for rt in aws_route_table.app : rt.id],
    [aws_route_table.db.id],
  )
  tags = { Name = "${var.project}-s3-endpoint" }
}
