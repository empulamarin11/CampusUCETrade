locals {
  services_a = toset(["auth", "user", "item", "search", "chat"])
}

module "svc_a" {
  source   = "../../modules/microservice_ec2"
  for_each = local.services_a

  name    = "${local.name}-${each.key}"
  service = each.key
  env     = var.env

  vpc_id = module.network.vpc_id
  ghcr_owner    = "empulamarin11"
  ghcr_username = "empulamarin11"
  ghcr_token    = var.ghcr_token

  db_endpoint = var.db_endpoint
  db_port     = var.db_port
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password

  jwt_secret    = var.jwt_secret
  jwt_algorithm = var.jwt_algorithm
  subnet_id = element(
    module.network.public_subnet_ids,
    index(sort(tolist(local.services_a)), each.key) % length(module.network.public_subnet_ids)
  )

  instance_type = var.instance_type
  key_name      = aws_key_pair.svc.key_name

  bastion_sg_id       = module.bastion.bastion_sg_id
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

output "svc_a_eip" {
  value = { for k, m in module.svc_a : k => m.public_ip }
}

output "svc_a_url" {
  value = { for k, m in module.svc_a : k => m.url }
}
