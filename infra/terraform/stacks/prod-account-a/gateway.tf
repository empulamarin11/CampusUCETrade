locals {
  routes_rendered = join("\n", [
    # ===== Services in prod-a (svc_a) =====
    "location = /auth { return 301 /auth/; }",
    format("location ^~ /auth/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", module.svc_a["auth"].alb_dns_name),

    "location = /user { return 301 /user/; }",
    format("location ^~ /user/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", module.svc_a["user"].alb_dns_name),

    "location = /item { return 301 /item/; }",
    format("location ^~ /item/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", module.svc_a["item"].alb_dns_name),

    "location = /search { return 301 /search/; }",
    format("location ^~ /search/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", module.svc_a["search"].alb_dns_name),

    "location = /chat { return 301 /chat/; }",
    format("location ^~ /chat/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", module.svc_a["chat"].alb_dns_name),

    # ===== Services in prod-b (svc_b) via variable map =====
    "location = /delivery { return 301 /delivery/; }",
    format("location ^~ /delivery/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", var.svc_b_alb_dns["delivery"]),

    "location = /notification { return 301 /notification/; }",
    format("location ^~ /notification/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", var.svc_b_alb_dns["notification"]),

    "location = /reputation { return 301 /reputation/; }",
    format("location ^~ /reputation/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", var.svc_b_alb_dns["reputation"]),

    "location = /reservation { return 301 /reservation/; }",
    format("location ^~ /reservation/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", var.svc_b_alb_dns["reservation"]),

    "location = /traceability { return 301 /traceability/; }",
    format("location ^~ /traceability/ { set $upstream \"%s\"; proxy_pass http://$upstream/; }", var.svc_b_alb_dns["traceability"]),
  ])
}

module "api_gateway" {
  source = "../../modules/api_gateway_ec2"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  upstream_alb_dns      = "localhost"
  instance_profile_name = var.instance_profile_name
  instance_type         = "t3.micro"

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  ssh_public_key_path = var.ssh_public_key_path

  routes_rendered = local.routes_rendered
  tags            = var.tags
}
