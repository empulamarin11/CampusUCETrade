
output "db_endpoint" {
  description = "The connection endpoint (host:port)"
  value       = aws_db_instance.this.endpoint
}

output "db_hostname" {
  description = "The hostname of the RDS instance"
  value       = aws_db_instance.this.address
}

output "db_port" {
  description = "The port of the RDS instance"
  value       = aws_db_instance.this.port
}

output "db_name" {
  value = aws_db_instance.this.db_name
}