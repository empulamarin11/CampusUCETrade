variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_profile" {
  type    = string
  default = "default"
}

variable "state_bucket_name" {
  type = string
}

variable "lock_table_name" {
  type    = string
  default = "campusuce-trade-terraform-locks"
}

variable "tags" {
  type    = map(string)
  default = {}
}
