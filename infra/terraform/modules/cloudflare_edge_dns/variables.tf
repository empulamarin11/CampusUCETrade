variable "zone_id" {
  type = string
}

variable "subdomain" {
  type = string # e.g. "api-qa" or "api"
}

variable "target" {
  type = string # e.g. ALB DNS name
}

variable "proxied" {
  type    = bool
  default = true
}

variable "ttl" {
  type    = number
  default = 1 # 1 = auto in Cloudflare
}
