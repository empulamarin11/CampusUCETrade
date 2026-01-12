output "public_ip" {
  value = var.use_eip ? aws_eip.this[0].public_ip : aws_instance.this.public_ip
}

output "url" {
  value = "http://${var.use_eip ? aws_eip.this[0].public_ip : aws_instance.this.public_ip}"
}
