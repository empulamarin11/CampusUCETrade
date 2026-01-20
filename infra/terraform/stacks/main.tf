locals {
  # Standard naming convention: project-environment (e.g., campusuce-trade-qa)
  name = "${var.project}-${var.env}"

  is_qa   = var.env == "qa"
  is_prod = var.env == "prod"
  has_alb = var.env != "dev" # we enable ALB for QA + PROD

  # NEW: enable ASG only in prod
  enable_asg = var.env == "prod"
}

# ==============================================================================
# 1. NETWORK & SECURITY LAYER
# ==============================================================================

module "network" {
  source = "../modules/network_vpc"

  name     = local.name
  vpc_cidr = var.vpc_cidr

  tags = var.tags
}

module "bastion" {
  source = "../modules/bastion_host"

  name             = local.name
  vpc_id           = module.network.vpc_id
  public_subnet_id = module.network.public_subnet_ids[0]

  ssh_key_name        = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  ssh_ingress_cidrs   = var.ssh_ingress_cidrs

  tags = var.tags
}

# ==============================================================================
# 2. LOAD BALANCING (ALB) - We use ALB as "API Gateway"
# ==============================================================================

module "alb" {
  source = "../modules/alb_public"
  count  = local.has_alb ? 1 : 0

  name              = local.name
  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids

  listener_port     = 80
  target_port       = 80
  health_check_path = "/health"

  tags = var.tags
}

# ==============================================================================
# 3. COMPUTE LAYER
# ==============================================================================

# --------------------------------------------
# QA: Microservices Hosts (4)
# --------------------------------------------

module "compute_qa_core" {
  source = "../modules/compute"
  count  = local.is_qa ? 1 : 0

  name          = "${local.name}-core"
  environment   = var.env
  role_name     = "qa-core"
  instance_type = "t3.small"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_qa_business" {
  source = "../modules/compute"
  count  = local.is_qa ? 1 : 0

  name          = "${local.name}-business"
  environment   = var.env
  role_name     = "qa-business"
  instance_type = "t3.small"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_qa_ops" {
  source = "../modules/compute"
  count  = local.is_qa ? 1 : 0

  name          = "${local.name}-ops"
  environment   = var.env
  role_name     = "qa-ops"
  instance_type = "t3.small"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_qa_realtime" {
  source = "../modules/compute"
  count  = local.is_qa ? 1 : 0

  name          = "${local.name}-realtime"
  environment   = var.env
  role_name     = "qa-realtime"
  instance_type = "t3.small"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

# --------------------------------------------
# QA: Middleware Host
# --------------------------------------------
module "compute_qa_middleware" {
  source = "../modules/compute"
  count  = local.is_qa ? 1 : 0

  name          = "${local.name}-middleware"
  environment   = var.env
  role_name     = "qa-middleware"
  instance_type = "t3.medium"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

# --------------------------------------------
# PROD: Functional Groups (base)
# --------------------------------------------

# PROD CORE (EC2) - ONLY when ASG is disabled
module "compute_prod_core" {
  source = "../modules/compute"
  count  = (local.is_prod && !local.enable_asg) ? 1 : 0

  name          = "${local.name}-core"
  environment   = var.env
  role_name     = "prod-core"
  instance_type = "t3.medium"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

# NEW: PROD CORE (ASG) - enabled in prod
module "compute_asg_prod_core" {
  source = "../modules/compute_asg"
  count  = (local.is_prod && local.enable_asg) ? 1 : 0

  name        = "${local.name}-core"
  environment = var.env
  role_name   = "prod-core"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = module.alb[0].alb_sg_id
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  target_group_arns = [module.alb[0].target_group_arn]

  min_size         = 1
  desired_capacity = 1
  max_size         = 2

  tags = var.tags
}

module "compute_prod_business" {
  source = "../modules/compute"
  count  = local.is_prod ? 1 : 0

  name          = "${local.name}-business"
  environment   = var.env
  role_name     = "prod-business"
  instance_type = "t3.medium"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_prod_ops" {
  source = "../modules/compute"
  count  = local.is_prod ? 1 : 0

  name          = "${local.name}-ops"
  environment   = var.env
  role_name     = "prod-ops"
  instance_type = "t3.medium"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_prod_realtime" {
  source = "../modules/compute"
  count  = local.is_prod ? 1 : 0

  name          = "${local.name}-realtime"
  environment   = var.env
  role_name     = "prod-realtime"
  instance_type = "t3.medium"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = local.has_alb ? module.alb[0].alb_sg_id : null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

module "compute_prod_middleware" {
  source = "../modules/compute"
  count  = local.is_prod ? 1 : 0

  name          = "${local.name}-middleware"
  environment   = var.env
  role_name     = "prod-middleware"
  instance_type = "t3.large"

  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  bastion_sg_id         = module.bastion.security_group_id
  alb_sg_id             = null
  ssh_key_name          = var.ssh_key_name != null ? var.ssh_key_name : (length(aws_key_pair.svc) > 0 ? aws_key_pair.svc[0].key_name : null)
  instance_profile_name = var.instance_profile_name

  tags = var.tags
}

# ==============================================================================
# 4. DATA & STORAGE LAYER
# ==============================================================================

module "media_bucket" {
  source = "../modules/s3_media_bucket"
  name   = local.name
  tags   = var.tags
}

module "database" {
  source = "../modules/data_rds_postgres"
  count  = var.env != "dev" ? 1 : 0

  name               = local.name
  vpc_id             = module.network.vpc_id
  vpc_cidr           = var.vpc_cidr
  private_subnet_ids = module.network.private_subnet_ids

  db_name        = var.db_name
  db_username    = var.db_username
  db_password    = var.db_password
  instance_class = var.db_instance_class
  engine_version = var.db_engine_version

  tags = var.tags
}

# ==============================================================================
# 5. ALB ROUTING RULES
# ==============================================================================

# Default TG from module ALB will be used as CORE TG
# IMPORTANT: For PROD core we now attach via ASG, so this attachment stays ONLY for QA.
resource "aws_lb_target_group_attachment" "default_core_attach" {
  count = (local.has_alb && local.is_qa) ? 1 : 0

  target_group_arn = module.alb[0].target_group_arn
  target_id        = module.compute_qa_core[0].instance_id
  port             = 80
}

# Extra target groups
resource "aws_lb_target_group" "tg_business" {
  count    = local.has_alb ? 1 : 0
  name     = "${local.name}-tg-business"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.network.vpc_id

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = var.tags
}

resource "aws_lb_target_group" "tg_ops" {
  count    = local.has_alb ? 1 : 0
  name     = "${local.name}-tg-ops"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.network.vpc_id

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = var.tags
}

resource "aws_lb_target_group" "tg_realtime" {
  count    = local.has_alb ? 1 : 0
  name     = "${local.name}-tg-realtime"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.network.vpc_id

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = var.tags
}

# Attachments for extra TGs
resource "aws_lb_target_group_attachment" "business_attach" {
  count = local.has_alb ? 1 : 0

  target_group_arn = aws_lb_target_group.tg_business[0].arn
  target_id        = local.is_qa ? module.compute_qa_business[0].instance_id : module.compute_prod_business[0].instance_id
  port             = 80
}

resource "aws_lb_target_group_attachment" "ops_attach" {
  count = local.has_alb ? 1 : 0

  target_group_arn = aws_lb_target_group.tg_ops[0].arn
  target_id        = local.is_qa ? module.compute_qa_ops[0].instance_id : module.compute_prod_ops[0].instance_id
  port             = 80
}

resource "aws_lb_target_group_attachment" "realtime_attach" {
  count = local.has_alb ? 1 : 0

  target_group_arn = aws_lb_target_group.tg_realtime[0].arn
  target_id        = local.is_qa ? module.compute_qa_realtime[0].instance_id : module.compute_prod_realtime[0].instance_id
  port             = 80
}

# Listener rules (path-based routing)
resource "aws_lb_listener_rule" "rule_business" {
  count        = local.has_alb ? 1 : 0
  listener_arn = module.alb[0].listener_arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg_business[0].arn
  }

  condition {
    path_pattern {
      values = ["/items*", "/search*", "/reservations*"]
    }
  }
}

resource "aws_lb_listener_rule" "rule_ops" {
  count        = local.has_alb ? 1 : 0
  listener_arn = module.alb[0].listener_arn
  priority     = 30

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg_ops[0].arn
  }

  condition {
    path_pattern {
      values = ["/notifications*", "/reputation*", "/traceability*"]
    }
  }
}

resource "aws_lb_listener_rule" "rule_realtime" {
  count        = local.has_alb ? 1 : 0
  listener_arn = module.alb[0].listener_arn
  priority     = 40

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg_realtime[0].arn
  }

  condition {
    path_pattern {
      values = ["/chat*", "/delivery*"]
    }
  }
}
