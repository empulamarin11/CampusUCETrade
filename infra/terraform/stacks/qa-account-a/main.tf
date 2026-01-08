locals {
  name = "${var.project}-${var.env}"
}

module "network" {
  source   = "../../modules/network_vpc"
  name     = local.name
  vpc_cidr = var.vpc_cidr
  az_count = var.az_count
  tags     = var.tags
}

#module "alb" {
 # source            = "../../modules/alb_public"
  #name              = local.name
  #vpc_id            = module.network.vpc_id
  #public_subnet_ids = module.network.public_subnet_ids
  #tags              = var.tags
#}

# ✅ NEW: Bastion (1 per account)
module "bastion" {
  source = "../../modules/bastion_host"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  ssh_key_name      = var.ssh_key_name
  ssh_ingress_cidrs = var.ssh_ingress_cidrs

  tags = var.tags
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  # esto es CLAVE: proxy al ALB actual (por ahora)
  upstream_alb_dns = ""
  instance_profile_name = var.instance_profile_name

  # ssh
  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  instance_type = "t3.micro"
  tags          = var.tags
}

#module "compute" {
 # source = "../../modules/compute_asg_docker_hosts"

  #name   = local.name
  #vpc_id = module.network.vpc_id

  # Low-cost: EC2 in public subnets (no NAT)
  #subnet_ids = module.network.public_subnet_ids

  #alb_sg_id            = module.alb.alb_sg_id
  #alb_target_group_arn = module.alb.target_group_arn

  #instance_type = var.instance_type

  # ✅ important:
  # - if you created key pair via ssh_public_key_path, leave ssh_key_name = null
  # - if you want to use an existing key pair name, set ssh_key_name in tfvars
  #ssh_key_name        = var.ssh_key_name
  #ssh_public_key_path = var.ssh_public_key_path

  # optional debug from your IPs (can be empty when bastion is used)
  #ssh_ingress_cidrs = var.ssh_ingress_cidrs

  # ✅ NEW: allow SSH from bastion SG to ASG instances
  #bastion_sg_id = module.bastion.bastion_sg_id

  #instance_profile_name = var.instance_profile_name
  #tags                  = var.tags
#}

module "media_bucket" {
  source      = "../../modules/s3_media_bucket"
  name_prefix = "${local.name}-media"
  tags        = var.tags
}

#module "database" {
 # source = "../../modules/data_rds_postgres"

  #name   = local.name
  #vpc_id = module.network.vpc_id

  #private_subnet_ids = module.network.private_subnet_ids

  # Allow DB access only from EC2 hosts (Docker)
  #allowed_sg_ids = [module.compute.ec2_sg_id]

  #db_name     = var.db_name
  #db_username = var.db_username

  #instance_class = var.db_instance_class
  #engine_version = var.db_engine_version

  #tags = var.tags
#}
