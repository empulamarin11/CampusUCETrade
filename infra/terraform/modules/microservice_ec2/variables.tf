variable "name" { type = string }
variable "service" { type = string }
variable "env" { type = string }

variable "vpc_id" { type = string }
variable "subnet_id" { type = string }

variable "instance_type" { type = string }
variable "key_name" { type = string }

variable "bastion_sg_id" { type = string }
variable "ssh_ingress_cidrs" { type = list(string) default = [] }

variable "instance_profile_name" { type = string default = null }
variable "tags" { type = map(string) default = {} }
