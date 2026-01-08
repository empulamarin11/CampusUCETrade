output "api_gw_eip" {
  value = aws_eip.api_gw.public_ip
}

output "api_gw_instance_id" {
  value = aws_instance.api_gw.id
}

output "api_gw_sg_id" {
  value = aws_security_group.api_gw.id
}
