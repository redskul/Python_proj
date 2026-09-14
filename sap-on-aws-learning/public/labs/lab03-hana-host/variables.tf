variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "project" {
  type    = string
  default = "sap-lab"
}

variable "vpc_id" {
  description = "VPC to launch into (from lab01)."
  type        = string
}

variable "subnet_id" {
  description = "Subnet to launch into (see lab02 SSM connectivity notes)."
  type        = string
}

variable "hana_instance_type" {
  description = "EC2 type. Default r6i.large is TINY (for learning the layout cheaply). A real HANA host is a certified large/high-memory type costing $$$."
  type        = string
  default     = "r6i.large"
}

# Volume sizing — compute realistic values with automation/ebs_storage_planner.py.
# Defaults are deliberately small to keep the lab cheap.
variable "data_size_gb" {
  type    = number
  default = 100
}

variable "data_throughput_mbps" {
  description = "gp3 throughput for /hana/data (throughput-critical). Max 1000 per volume."
  type        = number
  default     = 250
}

variable "data_iops" {
  type    = number
  default = 3000
}

variable "log_size_gb" {
  type    = number
  default = 50
}

variable "log_iops" {
  description = "gp3 IOPS for /hana/log (latency-critical)."
  type        = number
  default     = 4000
}

variable "shared_size_gb" {
  type    = number
  default = 64
}

variable "usrsap_size_gb" {
  type    = number
  default = 50
}
