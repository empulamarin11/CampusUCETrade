############################################
# API Gateway (QA-A) routes
############################################

locals {
  routes_rendered = <<-ROUTES
location = /auth { return 301 /auth/; }
location ^~ /auth/ { proxy_pass ${var.svc_a_url["auth"]}/; }

location = /user { return 301 /user/; }
location ^~ /user/ { proxy_pass ${var.svc_a_url["user"]}/; }

location = /item { return 301 /item/; }
location ^~ /item/ { proxy_pass ${var.svc_a_url["item"]}/; }

location = /search { return 301 /search/; }
location ^~ /search/ { proxy_pass ${var.svc_a_url["search"]}/; }

location = /chat { return 301 /chat/; }
location ^~ /chat/ { proxy_pass ${var.svc_a_url["chat"]}/; }

location = /delivery { return 301 /delivery/; }
location ^~ /delivery/ { proxy_pass ${var.svc_b_url["delivery"]}/; }

location = /notification { return 301 /notification/; }
location ^~ /notification/ { proxy_pass ${var.svc_b_url["notification"]}/; }

location = /reputation { return 301 /reputation/; }
location ^~ /reputation/ { proxy_pass ${var.svc_b_url["reputation"]}/; }

location = /reservation { return 301 /reservation/; }
location ^~ /reservation/ { proxy_pass ${var.svc_b_url["reservation"]}/; }

location = /traceability { return 301 /traceability/; }
location ^~ /traceability/ { proxy_pass ${var.svc_b_url["traceability"]}/; }
ROUTES
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  upstream_alb_dns      = "localhost" # required by module, not used
  instance_profile_name = var.instance_profile_name
  instance_type         = "t3.micro"

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  routes_rendered = local.routes_rendered
  tags            = var.tags
}
