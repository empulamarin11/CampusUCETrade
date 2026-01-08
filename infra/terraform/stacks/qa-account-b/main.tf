locals {
  name = "${var.project}-${var.env}-${var.account}"
}

module "network" {
  source   = "../../modules/network_vpc"
  name     = local.name
  vpc_cidr = var.vpc_cidr
  az_count = var.az_count
  tags     = var.tags
}

module "bastion" {
  source = "../../modules/bastion_host"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  ssh_key_name      = var.ssh_key_name
  ssh_ingress_cidrs = var.ssh_ingress_cidrs

  tags = var.tags
}

module "media_bucket" {
  source      = "../../modules/s3_media_bucket"
  name_prefix = "${local.name}-media"
  tags        = var.tags
}
