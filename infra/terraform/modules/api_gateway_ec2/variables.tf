variable "name" { type = string }
variable "vpc_id" { type = string }

variable "public_subnet_id" {
  description = "Public subnet for API Gateway"
  type        = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "ssh_public_key_path" {
  type = string
}

variable "ssh_ingress_cidrs" {
  type    = list(string)
  default = []
}

variable "bastion_sg_id" {
  type = string
}

variable "upstream_alb_dns" {
  description = "Legacy input (kept for compatibility)"
  type        = string
}

variable "routes_rendered" {
  type    = string
  default = ""
}

variable "instance_profile_name" {
  type    = string
  default = null
}

variable "tags" {
  type    = map(string)
  default = {}
}
