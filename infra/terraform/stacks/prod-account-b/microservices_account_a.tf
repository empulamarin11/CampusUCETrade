locals {
  services_b = {
    delivery     = {}
    notification = {}
    reputation   = {}
    reservation  = {}
    traceability = {}
  }
}

module "svc_b" {
  for_each = local.services_b

  source = "../../modules/service_asg_alb_hello"

  name = "${local.name}-${each.key}"

  vpc_id              = module.network.vpc_id
  public_subnet_ids   = module.network.public_subnet_ids
  instance_subnet_ids = module.network.public_subnet_ids

  instance_type         = var.instance_type
  instance_profile_name = var.instance_profile_name

  min_size         = 1
  desired_capacity = 1
  max_size         = 2

  service_name = each.key
  env          = var.env

  bastion_sg_id = module.bastion.bastion_sg_id

  tags = merge(var.tags, {
    Name    = "${local.name}-${each.key}"
    Service = each.key
  })
}

output "svc_b_alb_dns" {
  value = { for k, m in module.svc_b : k => m.alb_dns_name }
}
