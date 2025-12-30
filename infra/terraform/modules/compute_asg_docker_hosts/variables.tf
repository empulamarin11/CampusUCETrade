variable "name" { type = string }
variable "vpc_id" { type = string }

# As per your low-cost model: EC2 in public subnets (no NAT)
variable "subnet_ids" { type = list(string) }

variable "alb_sg_id" { type = string }
variable "alb_target_group_arn" { type = string }

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ssh_key_name" {
  type    = string
  default = null
}

variable "min_size" {
  type    = number
  default = 1
}

variable "desired_capacity" {
  type    = number
  default = 1
}

variable "max_size" {
  type    = number
  default = 2
}

variable "target_port" {
  type    = number
  default = 80
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "instance_profile_name" {
  type    = string
  default = "LabInstanceProfile"
}

variable "internal_ports" {
  type = list(number)
  default = [
    8000,  # internal services
    9092,  # kafka
    5672,  # rabbitmq
    1883,  # mqtt
    8883,  # mqtt tls (optional)
    9090,  # prometheus (optional)
    3000   # grafana (optional)
  ]
}