variable "name" { type = string }
variable "environment" { type = string }
variable "role_name" { type = string }

variable "vpc_id" { type = string }
variable "vpc_cidr" { type = string }
variable "private_subnet_ids" { type = list(string) }

variable "bastion_sg_id" { type = string }
variable "alb_sg_id" { type = string }

variable "ssh_key_name" { type = string }
variable "instance_profile_name" { type = string }

variable "instance_type" { type = string default = "t3.medium" }
variable "min_size" { type = number default = 1 }
variable "desired_capacity" { type = number default = 1 }
variable "max_size" { type = number default = 2 }

variable "target_group_arns" { type = list(string) }

variable "tags" { type = map(string) default = {} }
