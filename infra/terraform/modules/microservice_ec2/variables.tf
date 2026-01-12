variable "name" {
  type = string
}

variable "service" {
  type = string
}

variable "env" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "key_name" {
  type = string
}

variable "bastion_sg_id" {
  type = string
}

variable "ssh_ingress_cidrs" {
  type    = list(string)
  default = []
}

variable "instance_profile_name" {
  type    = string
  default = null
}

variable "tags" {
  type    = map(string)
  default = {}
}

# -------------------------
# Container registry (GHCR)
# -------------------------
variable "ghcr_owner" {
  type    = string
  default = "empulamarin11"
}

variable "ghcr_username" {
  type    = string
  default = "empulamarin11"
}

variable "ghcr_token" {
  type      = string
  sensitive = true
  default   = null
}

# -------------
# RDS Postgres
# -------------
variable "db_endpoint" {
  type = string
}

variable "db_port" {
  type = number
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

# ----
# JWT
# ----
variable "jwt_secret" {
  type    = string
  default = "dev_secret_change_me"
}

variable "jwt_algorithm" {
  type    = string
  default = "HS256"
}

variable "use_eip" {
  description = "Whether to allocate and associate an Elastic IP to the instance"
  type        = bool
  default     = true
}
