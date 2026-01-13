locals {
  # Standard naming convention: project-environment (e.g., campus-trade-qa)
  name = "${var.project}-${var.env}"
}

# ==============================================================================
# 1. NETWORK & SECURITY LAYER
# ==============================================================================

# Network VPC Module
module "network" {
  source = "../modules/network_vpc"

  name     = local.name
  vpc_cidr = var.vpc_cidr

  # REMOVED: az_count = var.az_count
  # The module now uses a default list of AZs defined in its variables.tf

  tags = var.tags
}

# Bastion Host for SSH Access (Jumpbox)
# Security Rule: Only accessible via specific IPs (ssh_ingress_cidrs)
module "bastion" {
  source = "../modules/bastion_host"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  # Key Pair management
  ssh_key_name = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  ssh_ingress_cidrs = var.ssh_ingress_cidrs

  tags = var.tags
}

# ==============================================================================
# 2. COMPUTE LAYER (Environment Specific Strategy)
# ==============================================================================

# ------------------------------------------------------------------------------
# SCENARIO A: QA / DEV Environment
# Strategy: Cost Optimization (All-in-One)
# Description: Runs all microservices in a single large instance to save costs.
# ------------------------------------------------------------------------------
module "compute_qa_all_in_one" {
  source = "../modules/compute"

  # CONDITION: Only create if environment is NOT prod
  count = var.env != "prod" ? 1 : 0

  name          = "${local.name}-node-all"
  environment   = var.env
  role_name     = "all-in-one"
  instance_type = "t3.large" # Larger instance for density packing

  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  
  # Security: Allow SSH only from Bastion Host
  # NOTE: Ensure your bastion module outputs 'security_group_id'
  bastion_sg_id      = module.bastion.security_group_id 
  
  tags = var.tags
}

# ------------------------------------------------------------------------------
# SCENARIO B: PROD Environment
# Strategy: Distributed High Availability (3 Functional Groups)
# Description: Isolates failure domains by splitting services into groups.
# ------------------------------------------------------------------------------

# Group 1: Core Services (Auth, User, Chat)
module "compute_prod_core" {
  source = "../modules/compute"
  
  # CONDITION: Only create if environment IS prod
  count = var.env == "prod" ? 1 : 0

  name          = "${local.name}-group-core"
  environment   = var.env
  role_name     = "core-svcs"
  instance_type = "t3.medium"
  
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  bastion_sg_id      = module.bastion.security_group_id
  
  tags = var.tags
}

# Group 2: Business Domain Services (Item, Search, Reservation)
module "compute_prod_business" {
  source = "../modules/compute"
  count  = var.env == "prod" ? 1 : 0

  name          = "${local.name}-group-business"
  environment   = var.env
  role_name     = "biz-svcs"
  instance_type = "t3.medium"
  
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  bastion_sg_id      = module.bastion.security_group_id
  
  tags = var.tags
}

# Group 3: Operations & Logistics (Delivery, Notification, Reputation)
module "compute_prod_ops" {
  source = "../modules/compute"
  count  = var.env == "prod" ? 1 : 0

  name          = "${local.name}-group-ops"
  environment   = var.env
  role_name     = "ops-svcs"
  instance_type = "t3.medium"
  
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  bastion_sg_id      = module.bastion.security_group_id
  
  tags = var.tags
}

# ==============================================================================
# 3. DATA & STORAGE LAYER
# ==============================================================================

# S3 Media Bucket
module "media_bucket" {
  source = "../modules/s3_media_bucket"

  # FIXED: Renamed 'name_prefix' to 'name' to match the new module definition.
  # The module will automatically append "-media-xxxx" to this name.
  name = local.name

  tags = var.tags
}

# RDS Postgres Database
module "database" {
  source = "../modules/data_rds_postgres"

  # CRITICAL: Only create RDS in PROD environment to save costs.
  # If var.env is "dev" or "qa", this evaluates to 0 (do not create).
  count = var.env == "prod" ? 1 : 0

  name               = local.name
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids

  # Note: 'allowed_sg_ids' and 'allowed_cidr_blocks' were removed 
  # because the updated module handles security internally.

  db_name     = var.db_name
  db_username = var.db_username

  instance_class = var.db_instance_class
  engine_version = var.db_engine_version

  tags = var.tags
}

# ==============================================================================
# 4. LOAD BALANCING (PROD ONLY) - "The AWS API Gateway"
# ==============================================================================

resource "aws_lb" "main" {
  # 🛑 STOP: Only create ALB in PROD to save $$ in Academy
  count = var.env == "prod" ? 1 : 0

  name               = "${local.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [module.bastion.security_group_id] # Ojo: Necesitas un SG para Web (Port 80)
  subnets            = module.network.public_subnet_ids

  tags = var.tags
}

resource "aws_lb_listener" "http" {
  count = var.env == "prod" ? 1 : 0

  load_balancer_arn = aws_lb.main[0].arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "404: Not Found - CampusTrade API"
      status_code  = "404"
    }
  }
}

# ------------------------------------------------------------------------------
# REGLAS DE ENRUTAMIENTO (Aquí ocurre la magia del "API Gateway")
# ------------------------------------------------------------------------------

# Regla 1: Tráfico de Usuarios -> Grupo A (Core)
resource "aws_lb_target_group" "tg_core" {
  count    = var.env == "prod" ? 1 : 0
  name     = "${local.name}-tg-core"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.network.vpc_id
}
# Aquí faltaría el "aws_lb_listener_rule" para decir:
# IF path == /api/auth/* THEN forward to tg_core

# ... (Repetir para Business y Ops)