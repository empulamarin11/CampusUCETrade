

output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.app_node.id
}

output "private_ip" {
  description = "The Private IP address of the instance (Use Bastion to connect)"
  value       = aws_instance.app_node.private_ip
}

output "security_group_id" {
  description = "The ID of the Security Group attached to the instance"
  value       = aws_security_group.app_sg.id
}