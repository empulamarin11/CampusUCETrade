variable "project" {
  type    = string
  default = "campusuce-trade"
}

variable "env" {
  type    = string
  default = "qa"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_profile" {
  type    = string
  default = "default"
}

variable "tags" {
  type = map(string)
  default = {
    Project   = "campusuce-trade"
    ManagedBy = "terraform"
    Env       = "qa"
  }
}

# Network
variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "az_count" {
  type    = number
  default = 2
}

# Compute
variable "instance_type" {
  type    = string
  default = "t3.small"
}

# ✅ if empty/null, module may create key pair from ssh_public_key_path
variable "ssh_key_name" {
  type    = string
  default = null
}

# ✅ local path to .pub (Windows path ok)
variable "ssh_public_key_path" {
  type        = string
  default     = ""
  description = "Local path to public SSH key (.pub). If empty, key pair resource is not created."
}

# ✅ Bastion + optional direct SSH debug
variable "ssh_ingress_cidrs" {
  type        = list(string)
  default     = []
  description = "Operator public IPv4 CIDRs allowed to SSH (used by bastion and optional direct EC2 SSH). Example: [\"1.2.3.4/32\"]."
}

# DB
variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_engine_version" {
  type    = string
  default = "16"
}

variable "db_name" {
  type    = string
  default = "campusuce"
}

variable "db_username" {
  type    = string
  default = "campusuce"
}

# IAM instance profile
variable "instance_profile_name" {
  type    = string
  default = "LabInstanceProfile"
}
