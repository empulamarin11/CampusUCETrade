
# ------------------------------------------------------------------------------
# 1. DB SUBNET GROUP
# Tells RDS which subnets it can use (Must be Private Subnets)
# ------------------------------------------------------------------------------
resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.name}-db-subnet-group"
  })
}

# ------------------------------------------------------------------------------
# 2. SECURITY GROUP
# Allows traffic to Port 5432 (Postgres) from within the VPC
# ------------------------------------------------------------------------------
resource "aws_security_group" "rds_sg" {
  name        = "${var.name}-rds-sg"
  description = "Allow PostgreSQL traffic from VPC"
  vpc_id      = var.vpc_id

  # Inbound: Allow connection from any internal IP (App Nodes)
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Assuming this is your VPC CIDR
    description = "PostgreSQL access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# ------------------------------------------------------------------------------
# 3. RDS INSTANCE
# ------------------------------------------------------------------------------
resource "aws_db_instance" "this" {
  identifier = "${var.name}-postgres"
  
  # Engine
  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  # Storage
  allocated_storage     = 20
  max_allocated_storage = 50 # Autoscaling storage cap
  storage_type          = "gp2"

  # Credentials
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = false # SECURITY: Never expose DB to internet

  # Maintenance & Backups (Optimized for Academy/Dev)
  skip_final_snapshot = true  # CRITICAL for Academy (avoids destroy errors)
  deletion_protection = false 
  
  tags = var.tags
}