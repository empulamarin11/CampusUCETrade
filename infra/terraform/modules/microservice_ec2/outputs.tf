output "public_ip" {
  value = aws_eip.this.public_ip
}

output "url" {
  value = "http://${aws_eip.this.public_ip}"
}
