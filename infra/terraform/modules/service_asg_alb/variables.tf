variable "name" {
  description = "Base name for resources (e.g., campusuce-trade-qa-auth)"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  description = "Public subnets for the ALB"
  type        = list(string)
}

variable "instance_subnet_ids" {
  description = "Subnets for the ASG instances (can be public or private)"
  type        = list(string)
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "desired_capacity" {
  type    = number
  default = 1
}

variable "min_size" {
  type    = number
  default = 1
}

variable "max_size" {
  type    = number
  default = 1
}

variable "target_port" {
  description = "Service port on EC2 (container host port)"
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "HTTP health check path (e.g., /health)"
  type        = string
  default     = "/health"
}

variable "ssh_ingress_cidrs" {
  description = "Temporary SSH access CIDRs (IPv4). Example: [\"1.2.3.4/32\"]."
  type        = list(string)
  default     = []
}

variable "ssh_key_name" {
  description = "EC2 key pair name to use (optional). If empty, no key is set."
  type        = string
  default     = null
}

variable "instance_profile_name" {
  description = "IAM instance profile name (e.g., LabInstanceProfile)"
  type        = string
  default     = "LabInstanceProfile"
}

variable "repo_url" {
  description = "Git repo URL (public) to clone in user_data"
  type        = string
}

variable "repo_branch" {
  description = "Git branch to checkout"
  type        = string
  default     = "dev"
}

variable "service_dir" {
  description = "Service directory under /services (e.g., auth-service)"
  type        = string
}

variable "service_root_path" {
  description = "Root path for FastAPI behind a prefix (e.g., /auth)"
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}


variable "image_name" {
  description = "Docker image name to build/run (e.g., campusucetrade-auth-service)"
  type        = string
}