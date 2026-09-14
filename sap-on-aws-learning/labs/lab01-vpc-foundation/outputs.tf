output "vpc_id" {
  description = "The VPC ID (feed this into lab02/lab03)."
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  value = aws_vpc.main.cidr_block
}

output "availability_zones" {
  value = local.azs
}

output "public_subnet_ids" {
  value = { for az, s in aws_subnet.public : az => s.id }
}

output "app_subnet_ids" {
  value = { for az, s in aws_subnet.app : az => s.id }
}

output "db_subnet_ids" {
  value = { for az, s in aws_subnet.db : az => s.id }
}

output "s3_endpoint_id" {
  value = aws_vpc_endpoint.s3.id
}

output "nat_gateway_ids" {
  description = "Empty unless enable_nat=true."
  value       = [for n in aws_nat_gateway.nat : n.id]
}
