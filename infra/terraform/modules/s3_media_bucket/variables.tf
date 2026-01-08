variable "name_prefix" { type = string }

variable "force_destroy" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
