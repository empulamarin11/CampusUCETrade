output "vpc_id" { value = module.network.vpc_id }

output "public_subnet_ids" { value = module.network.public_subnet_ids }
output "private_subnet_ids" { value = module.network.private_subnet_ids }

output "alb_dns_name" { value = module.alb.alb_dns_name }
output "asg_name" { value = module.compute.asg_name }

output "s3_media_bucket" { value = module.media_bucket.bucket_name }

output "db_endpoint" { value = module.database.db_endpoint }
output "db_port" { value = module.database.db_port }
