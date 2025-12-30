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