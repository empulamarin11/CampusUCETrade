

output "instance_id" {
  description = "ID of the Bastion EC2 instance"
  value       = aws_instance.bastion.id
}

output "public_ip" {
  description = "Public IP address of the Bastion Host"
  value       = aws_instance.bastion.public_ip
}

output "security_group_id" {
  description = "The ID of the Security Group attached to the Bastion"
  value       = aws_security_group.bastion_sg.id
}