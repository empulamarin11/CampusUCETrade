# ------------------------------------------------------------------------------
# 1. DB SUBNET GROUP (Private subnets only)
# ------------------------------------------------------------------------------
resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.name}-db-subnet-group"
  })
}

# ------------------------------------------------------------------------------
# 2. SECURITY GROUP (Allow Postgres only from inside the VPC)
# ------------------------------------------------------------------------------
resource "aws_security_group" "db_sg" {
  name        = "${var.name}-db-sg"
  description = "RDS PostgreSQL security group"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name}-db-sg"
  })
}

# ------------------------------------------------------------------------------
# 3. RDS INSTANCE
# ------------------------------------------------------------------------------
resource "aws_db_instance" "this" {
  identifier = "${var.name}-postgres"

  engine         = "postgres"
  engine_version = var.engine_version

  instance_class = var.instance_class

  allocated_storage = var.allocated_storage
  storage_type       = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.this.name

  publicly_accessible = var.publicly_accessible
  multi_az            = var.multi_az

  skip_final_snapshot = true
  deletion_protection = false

  backup_retention_period = 7
  backup_window           = "03:00-04:00"

  maintenance_window = "sun:05:00-sun:06:00"

  tags = merge(var.tags, {
    Name = "${var.name}-postgres"
  })
}
