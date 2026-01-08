variable "name" { type = string }

variable "vpc_id" { type = string }

variable "public_subnet_id" {
  description = "Subnet pública donde vivirá el API Gateway"
  type        = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "ssh_public_key_path" {
  description = "Path local a la llave pública .pub"
  type        = string
}

variable "ssh_ingress_cidrs" {
  description = "CIDRs temporales para SSH (opcional). Ej: [\"1.2.3.4/32\"]"
  type        = list(string)
  default     = []
}

variable "bastion_sg_id" {
  description = "SG del bastion para permitir SSH desde bastion -> api gateway"
  type        = string
}

variable "upstream_alb_dns" {
  description = "DNS del ALB al que NGINX hará proxy (por ahora tu ALB actual)"
  type        = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
variable "instance_profile_name" {
  type        = string
  description = "IAM Instance Profile name for SSM access (e.g., LabInstanceProfile)."
  default     = null
}

variable "routes_rendered" {
  type        = string
  description = "Rendered nginx location blocks"
  default     = ""
}