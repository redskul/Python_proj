variable "aws_region" {
  description = "AWS region to deploy into. Pick one with the SAP instances you need."
  type        = string
  default     = "eu-central-1"
}

variable "project" {
  description = "Name prefix and tag applied to all resources."
  type        = string
  default     = "sap-lab"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

# Two AZs are the minimum for SAP HA (primary + standby).
variable "az_count" {
  description = "Number of Availability Zones to spread subnets across."
  type        = number
  default     = 2
}

variable "enable_nat" {
  description = "Create NAT Gateway(s) for private-subnet outbound internet. COSTS MONEY (~$0.045/hr each). Leave false unless you need it."
  type        = bool
  default     = false
}

variable "single_nat" {
  description = "If NAT is enabled, use a single shared NAT GW (cheaper, less HA) instead of one per AZ."
  type        = bool
  default     = true
}
