output "instance_id" {
  value = aws_instance.hana.id
}

output "availability_zone" {
  value = aws_instance.hana.availability_zone
}

output "connect_command" {
  value = "aws ssm start-session --target ${aws_instance.hana.id} --region ${var.aws_region}"
}

output "volume_layout" {
  description = "The HANA volume layout this lab created."
  value = {
    "/hana/data"   = "${var.data_size_gb} GB gp3, ${var.data_throughput_mbps} MB/s, ${var.data_iops} IOPS"
    "/hana/log"    = "${var.log_size_gb} GB gp3, ${var.log_iops} IOPS (latency-critical)"
    "/hana/shared" = "${var.shared_size_gb} GB gp3"
    "/usr/sap"     = "${var.usrsap_size_gb} GB gp3"
  }
}
