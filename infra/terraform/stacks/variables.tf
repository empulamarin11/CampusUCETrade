# ==============================================================================
# GLOBAL PROJECT VARIABLES
# ==============================================================================

variable "project" {
  description = "Project identifier"
  type        = string
  default     = "campusuce-trade"
}

variable "env" {
  description = "Target environment (qa, prod)"
  type        = string
  default     = "qa"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "tags" {
  description = "Default tags for all resources"
  type        = map(string)
  default = {
    Project   = "campusuce-trade"
    ManagedBy = "terraform"
  }
}

# ==============================================================================
# NETWORK CONFIGURATION
# ==============================================================================

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of Availability Zones to use"
  type        = number
  default     = 2
}

# ==============================================================================
# COMPUTE & SECURITY
# ==============================================================================

variable "instance_type" {
  description = "EC2 Instance type"
  type        = string
  default     = "t3.medium" # Changed to medium to support Docker workloads
}

variable "instance_profile_name" {
  description = "IAM Profile for AWS Academy (Must be LabInstanceProfile)"
  type        = string
  default     = "LabInstanceProfile"
}

# SSH Key Management
# Note: If ssh_key_name is provided, it uses existing key. 
# If empty, it tries to create one using ssh_public_key_path.
variable "ssh_key_name" {
  description = "Name of an existing AWS Key Pair (preferred for Academy)"
  type        = string
  default     = null
}

variable "ssh_public_key_path" {
  description = "Local path to .pub key if creating a new pair"
  type        = string
  default     = ""
}

variable "ssh_ingress_cidrs" {
  description = "List of public IPs allowed to SSH into Bastion"
  type        = list(string)
  default     = ["0.0.0.0/0"] # WARNING: Change this to your IP in prod
}

# ==============================================================================
# DATABASE & SECRETS (Sensitive)
# ==============================================================================

variable "db_name" {
  type    = string
  default = "campusuce_db"
}

variable "db_username" {
  type    = string
  default = "campus_user"
}

variable "db_password" {
  description = "Database password (passed to Docker or RDS)"
  type        = string
  sensitive   = true
  # No default to force passing it via tfvars or env vars
}

# Remove db_endpoint and db_port inputs. 
# Reason: Terraform calculates these when creating the infra, or we define them.

variable "ghcr_token" {
  description = "GitHub Container Registry Token for pulling images"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "Secret key for JWT generation in Microservices"
  type        = string
  sensitive   = true
}

# ==============================================================================
# OPTIONAL RDS CONFIG (Only used if creating RDS in Prod)
# ==============================================================================

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_engine_version" {
  type    = string
  default = "16.11"
}