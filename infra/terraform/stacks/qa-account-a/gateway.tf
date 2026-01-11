############################################
# gateway.tf (QA Account A)
# Path: infra/terraform/stacks/qa-account-a/gateway.tf
############################################

locals {
  # Render routes from an external template
  routes_rendered = templatefile("${path.module}/nginx_routes.conf.tftpl", {
    svc_a_url = var.svc_a_url
    svc_b_url = var.svc_b_url
  })
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  upstream_alb_dns = "localhost" # legacy, not used

  instance_profile_name = var.instance_profile_name
  instance_type         = "t3.micro"

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  routes_rendered = local.routes_rendered
  tags            = var.tags
}
