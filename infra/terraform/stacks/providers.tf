terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }

    random = {
      source  = "hashicorp/random"
      version = ">= 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  # REMOVED: profile = var.aws_profile 
  # Reason: We rely on environment variables or default profile for CI/CD compatibility.

  default_tags {
    tags = var.tags
  }
}