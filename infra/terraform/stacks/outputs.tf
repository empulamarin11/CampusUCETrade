# infra/terraform/stacks/outputs.tf

# ==============================================================================
# CONNECTION DETAILS
# ==============================================================================

output "bastion_public_ip" {
  description = "Public IP of the Bastion Host (Jumpbox). SSH here first."
  value       = module.bastion.public_ip
}

output "ssh_command_example" {
  description = "Copy-paste command to connect to Bastion"
  # FIX: Handle null key name safely
  value       = "ssh -i ${var.ssh_key_name != null ? var.ssh_key_name : "${var.project}-${var.env}-svc-key"}.pem ubuntu@${module.bastion.public_ip}"
}

# ==============================================================================
# QA ENVIRONMENT OUTPUTS
# ==============================================================================

output "qa_node_private_ip" {
  description = "Private IP of the All-in-One QA Node (Connect via Bastion)"
  value       = length(module.compute_qa_all_in_one) > 0 ? module.compute_qa_all_in_one[0].private_ip : null
}

# ==============================================================================
# PROD ENVIRONMENT OUTPUTS
# ==============================================================================

output "prod_core_ips" {
  description = "Private IPs of Core Group (Auth/User)"
  value       = length(module.compute_prod_core) > 0 ? module.compute_prod_core[0].private_ip : null
}

output "prod_business_ips" {
  description = "Private IPs of Business Group (Item/Search)"
  value       = length(module.compute_prod_business) > 0 ? module.compute_prod_business[0].private_ip : null
}

output "prod_ops_ips" {
  description = "Private IPs of Ops Group (Delivery/Notif)"
  value       = length(module.compute_prod_ops) > 0 ? module.compute_prod_ops[0].private_ip : null
}

# ==============================================================================
# DATABASE OUTPUTS
# ==============================================================================

output "db_endpoint" {
  description = "RDS Endpoint (Only available in PROD)"
  # ✅ CORRECCIÓN: Usar índice [0] si existe, si no, null.
  value       = length(module.database) > 0 ? module.database[0].db_endpoint : null
}