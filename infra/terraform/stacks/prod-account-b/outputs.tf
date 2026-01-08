output "vpc_id" { value = module.network.vpc_id }

output "public_subnet_ids" { value = module.network.public_subnet_ids }
output "private_subnet_ids" { value = module.network.private_subnet_ids }

output "bastion_eip" { value = module.bastion.bastion_eip }
output "bastion_sg_id" { value = module.bastion.bastion_sg_id }

output "media_bucket_name" { value = module.media_bucket.bucket_name }

