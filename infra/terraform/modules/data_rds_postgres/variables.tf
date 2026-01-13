
variable "name" {
  description = "Base name for resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the RDS will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the DB Subnet Group"
  type        = list(string)
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  default     = "campus_trade_db"
}

variable "db_username" {
  description = "Master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password (should be sensitive in real prod)"
  type        = string
  default     = "ChangeMe123!" # In real life, use AWS Secrets Manager
  sensitive   = true
}

variable "instance_class" {
  description = "RDS Instance Class"
  type        = string
  default     = "db.t3.micro" # Cheapest option for Academy
}

variable "engine_version" {
  description = "PostgreSQL Engine Version"
  type        = string
  default     = "16.3" # FIXED: Changed from 16.1 to 16.3 to avoid AWS errors
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}