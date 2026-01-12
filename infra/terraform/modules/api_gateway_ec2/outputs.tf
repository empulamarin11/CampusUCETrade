output "api_gw_eip" {
  value       = aws_eip.api_gw.public_ip
  description = "Elastic IP (public) of the API Gateway instance"
}

output "api_gw_instance_id" {
  value       = aws_instance.api_gw.id
  description = "EC2 Instance ID of the API Gateway"
}

output "api_gw_sg_id" {
  value       = aws_security_group.api_gw.id
  description = "Security group ID of the API Gateway"
}