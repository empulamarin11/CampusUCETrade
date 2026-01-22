
variable "name" {
  description = "Base name for the bucket (e.g., project-env)"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}