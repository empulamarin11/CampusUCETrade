locals {
  # Build nginx routes dynamically from the modules created with for_each
  routes_rendered = join("\n", flatten([
    for k, m in module.svc_b : [
      "location = /${k} { return 301 /${k}/; }",
      "location ^~ /${k}/ { proxy_pass http://${m.alb_dns_name}/; }"
    ]
  ]))
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  # required by module variables (not used)
  upstream_alb_dns = "localhost"

  instance_profile_name = var.instance_profile_name
  instance_type         = "t3.micro"

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  routes_rendered = local.routes_rendered
  tags            = var.tags
}

