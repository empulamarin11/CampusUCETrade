variable "name" { type = string }
variable "vpc_id" { type = string }

variable "public_subnet_ids" { type = list(string) }
variable "instance_subnet_ids" { type = list(string) }

variable "instance_type" { type = string }
variable "instance_profile_name" { type = string }

variable "min_size" { type = number }
variable "desired_capacity" { type = number }
variable "max_size" { type = number }

variable "service_name" { type = string }
variable "env" { type = string }

variable "bastion_sg_id" { type = string }
variable "tags" { type = map(string) }
