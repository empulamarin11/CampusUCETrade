variable "name" { type = string }
variable "vpc_id" { type = string }
variable "public_subnet_id" { type = string }

variable "ssh_key_name" {
  type    = string
  default = null
}

variable "ssh_ingress_cidrs" {
  type    = list(string)
  default = []
}

variable "instance_profile_name" {
  type    = string
  default = null
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "tags" {
  type    = map(string)
  default = {}
}
