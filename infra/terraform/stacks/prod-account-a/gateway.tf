locals {
  routes_rendered = join("\n", [
    "location = /auth { return 301 /auth/; }",
    "location ^~ /auth/ { proxy_pass http://${module.svc_a["auth"].alb_dns_name}/; }",

    "location = /user { return 301 /user/; }",
    "location ^~ /user/ { proxy_pass http://${module.svc_a["user"].alb_dns_name}/; }",

    "location = /item { return 301 /item/; }",
    "location ^~ /item/ { proxy_pass http://${module.svc_a["item"].alb_dns_name}/; }",

    "location = /search { return 301 /search/; }",
    "location ^~ /search/ { proxy_pass http://${module.svc_a["search"].alb_dns_name}/; }",

    "location = /chat { return 301 /chat/; }",
    "location ^~ /chat/ { proxy_pass http://${module.svc_a["chat"].alb_dns_name}/; }",
  ])
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  instance_profile_name = var.instance_profile_name
  instance_type         = "t3.micro"

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  routes_rendered = local.routes_rendered
  tags            = var.tags
}

output "api_gateway_eip" {
  value = aws_eip.api_gw.public_ip
}
