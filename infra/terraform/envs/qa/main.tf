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

module "alb" {
  source            = "../../modules/alb_public"
  name              = local.name
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  tags              = var.tags
}

module "compute" {
  source = "../../modules/compute_asg_docker_hosts"

  name = local.name
  vpc_id = module.network.vpc_id

  # Low-cost: EC2 in public subnets (no NAT)
  subnet_ids = module.network.public_subnet_ids

  alb_sg_id            = module.alb.alb_sg_id
  alb_target_group_arn = module.alb.target_group_arn

  instance_type = var.instance_type
  ssh_key_name  = var.ssh_key_name

  tags = var.tags
}

module "media_bucket" {
  source      = "../../modules/s3_media_bucket"
  name_prefix = "${local.name}-media"
  tags        = var.tags
}