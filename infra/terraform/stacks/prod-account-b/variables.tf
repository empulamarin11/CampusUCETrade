variable "project" {
  type    = string
  default = "campusuce-trade"
}

variable "env" {
  type    = string
  default = "prod"
}

variable "aws_profile" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type = string
}

variable "az_count" {
  type    = number
  default = 2
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "ssh_key_name" {
  type    = string
  default = null
}

variable "ssh_public_key_path" {
  type = string
}

variable "ssh_ingress_cidrs" {
  type    = list(string)
  default = []
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "instance_profile_name" {
  type        = string
  description = "IAM Instance Profile name for SSM (ex: LabInstanceProfile)"
  default     = "LabInstanceProfile"
}
