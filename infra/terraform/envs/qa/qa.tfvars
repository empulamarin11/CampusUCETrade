aws_profile = "default"
aws_region  = "us-east-1"

tags = {
  Project   = "campusuce-trade"
  ManagedBy = "terraform"
  Env       = "qa"
}

ssh_ingress_cidrs = ["181.112.8.208/32"]

ssh_public_key_path = "C:/Users/Erick/.ssh/campusuce-qa.pub"
