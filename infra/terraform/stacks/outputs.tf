# ==============================================================================
# NETWORK
# ==============================================================================

output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_ids" {
  value = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  value = module.network.private_subnet_ids
}

# ==============================================================================
# BASTION
# ==============================================================================

output "bastion_public_ip" {
  value = module.bastion.public_ip
}

output "bastion_security_group_id" {
  value = module.bastion.security_group_id
}

# ==============================================================================
# ALB (acts as API Gateway)
# ==============================================================================

output "alb_dns" {
  value = var.env != "dev" ? module.alb[0].alb_dns_name : null
}

output "alb_security_group_id" {
  value = var.env != "dev" ? module.alb[0].alb_sg_id : null
}

# ==============================================================================
# QA COMPUTE (private IPs)
# ==============================================================================

output "qa_core_private_ip" {
  value = var.env == "qa" ? module.compute_qa_core[0].private_ip : null
}

output "qa_business_private_ip" {
  value = var.env == "qa" ? module.compute_qa_business[0].private_ip : null
}

output "qa_ops_private_ip" {
  value = var.env == "qa" ? module.compute_qa_ops[0].private_ip : null
}

output "qa_realtime_private_ip" {
  value = var.env == "qa" ? module.compute_qa_realtime[0].private_ip : null
}

output "qa_middleware_private_ip" {
  value = var.env == "qa" ? module.compute_qa_middleware[0].private_ip : null
}

# ==============================================================================
# PROD COMPUTE (private IPs)
# ==============================================================================

output "prod_core_private_ip" {
  value = var.env == "prod" ? module.compute_prod_core[0].private_ip : null
}

output "prod_business_private_ip" {
  value = var.env == "prod" ? module.compute_prod_business[0].private_ip : null
}

output "prod_ops_private_ip" {
  value = var.env == "prod" ? module.compute_prod_ops[0].private_ip : null
}

output "prod_realtime_private_ip" {
  value = var.env == "prod" ? module.compute_prod_realtime[0].private_ip : null
}

output "prod_middleware_private_ip" {
  value = var.env == "prod" ? module.compute_prod_middleware[0].private_ip : null
}

# ==============================================================================
# RDS POSTGRES
# ==============================================================================

output "rds_endpoint" {
  value = (var.env != "dev" && length(module.database) > 0) ? module.database[0].db_endpoint : null
}

output "rds_port" {
  value = (var.env != "dev" && length(module.database) > 0) ? module.database[0].db_port : null
}

output "rds_db_name" {
  value = (var.env != "dev" && length(module.database) > 0) ? module.database[0].db_name : null
}

# ==============================================================================
# S3 MEDIA BUCKET
# ==============================================================================

output "media_bucket_name" {
  value = module.media_bucket.bucket_id
}