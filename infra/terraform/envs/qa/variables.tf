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
