variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "project" {
  type    = string
  default = "sap-lab"
}

variable "vpc_id" {
  description = "VPC to launch into (from lab01 output vpc_id)."
  type        = string
}

variable "subnet_id" {
  description = "Subnet to launch into. Use a PUBLIC subnet for the free (no-endpoint) path, or an app/db subnet with create_ssm_endpoints=true."
  type        = string
}

variable "instance_type" {
  description = "Instance type. t3.micro is Free-Tier-eligible."
  type        = string
  default     = "t3.micro"
}

variable "create_ssm_endpoints" {
  description = "Create ssm/ssmmessages/ec2messages interface endpoints so a PRIVATE instance can use Session Manager without NAT. Small hourly cost per endpoint."
  type        = bool
  default     = false
}
