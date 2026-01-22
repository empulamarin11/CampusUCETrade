variable "name" {
  description = "Base name for RDS resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where RDS will be deployed"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR allowed to access Postgres (avoid hardcode 10.0.0.0/16)"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnets for DB subnet group"
  type        = list(string)
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "RDS instance class (e.g., db.t3.micro)"
  type        = string
  default     = "db.t3.micro"
}

variable "engine_version" {
  description = "Postgres engine version"
  type        = string
  default     = "16.3"
}

variable "allocated_storage" {
  description = "Allocated storage (GiB)"
  type        = number
  default     = 20
}

variable "multi_az" {
  description = "Enable Multi-AZ (recommended for PROD)"
  type        = bool
  default     = false
}

variable "publicly_accessible" {
  description = "Whether DB is publicly accessible (should be false)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply"
  type        = map(string)
  default     = {}
}
