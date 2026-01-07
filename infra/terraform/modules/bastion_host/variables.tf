variable "name" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_id" { type = string }

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "ssh_key_name" {
  type = string
}

variable "ssh_ingress_cidrs" {
  type        = list(string)
  default     = []
  description = "Operator public IPv4 CIDRs allowed to SSH into bastion."
}

variable "tags" {
  type    = map(string)
  default = {}
}
