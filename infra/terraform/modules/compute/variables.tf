

variable "name" {
  description = "Base name for resources"
  type        = string
}

variable "environment" {
  description = "Environment name (qa, prod)"
  type        = string
}

variable "role_name" {
  description = "Role of this node (e.g., all-in-one, core-svcs, worker)"
  type        = string
  default     = "general"
}

variable "vpc_id" {
  description = "VPC ID where the instance will reside"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for deployment"
  type        = list(string)
}

variable "bastion_sg_id" {
  description = "Security Group ID of the Bastion Host (for SSH access)"
  type        = string
}

variable "instance_type" {
  description = "EC2 Instance Type (e.g., t3.micro, t3.medium)"
  type        = string
  default     = "t3.medium"
}

variable "ssh_key_name" {
  description = "Name of the SSH Key Pair to use"
  type        = string
  default     = null 
}

variable "instance_profile_name" {
  description = "IAM Instance Profile to attach (for ECR access, etc.)"
  type        = string
  default     = "LabInstanceProfile" # Default for AWS Academy
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}