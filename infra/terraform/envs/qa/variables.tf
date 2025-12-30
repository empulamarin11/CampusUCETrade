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

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ssh_key_name" {
  type    = string
  default = null
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_engine_version" {
  type    = string
  default = "16"
}

variable "db_name" {
  type    = string
  default = "campusuce"
}

variable "db_username" {
  type    = string
  default = "campusuce"
}
