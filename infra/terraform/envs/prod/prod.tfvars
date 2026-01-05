aws_profile = "default"
aws_region  = "us-east-1"

tags = {
  Project   = "campusuce-trade"
  ManagedBy = "terraform"
  Env       = "prod"
}


ssh_ingress_cidrs = ["181.112.8.208/32"]

ssh_public_key_path = "C:/Users/Erick/.ssh/campusuce-qa.pub"

# optional: to more power to prod
# instance_type = "t3.small"
# db_instance_class = "db.t4g.micro