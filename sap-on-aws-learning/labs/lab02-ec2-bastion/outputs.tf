output "instance_id" {
  description = "Use with: aws ssm start-session --target <this>"
  value       = aws_instance.app.id
}

output "private_ip" {
  value = aws_instance.app.private_ip
}

output "connect_command" {
  value = "aws ssm start-session --target ${aws_instance.app.id} --region ${var.aws_region}"
}

output "ssm_endpoints_created" {
  value = var.create_ssm_endpoints ? [for e in aws_vpc_endpoint.ssm : e.id] : []
}
