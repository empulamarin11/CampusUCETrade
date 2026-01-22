

variable "name" {
  description = "Base name for resources (e.g., campus-trade-dev)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the bastion will be deployed"
  type        = string
}

variable "public_subnet_id" {
  description = "ID of the public subnet where the bastion instance will sit"
  type        = string
}

variable "ssh_key_name" {
  description = "Name of the SSH Key Pair to use for access"
  type        = string
}

variable "ssh_ingress_cidrs" {
  description = "List of CIDR blocks allowed to SSH into Bastion (e.g., your home IP)"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Open to world by default (ok for dev/academy)
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}