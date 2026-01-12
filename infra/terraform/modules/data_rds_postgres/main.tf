resource "aws_security_group" "db" {
  name        = "${var.name}-db-sg"
  description = "RDS PostgreSQL security group"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from app/hosts"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_sg_ids
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name}-db-sg" })
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = merge(var.tags, { Name = "${var.name}-db-subnets" })
}

resource "random_password" "db" {
  length  = 20
  special = true

  # RDS restriction: only printable ASCII except '/', '@', '"', and space
  override_special = "!#$%&'()*+,-.:;<=>?[]^_{|}~"
}

resource "aws_db_instance" "this" {
  identifier = "${var.name}-postgres"

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage = var.allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db.result
  port     = 5432

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.this.name

  publicly_accessible     = var.publicly_accessible
  multi_az                = false
  backup_retention_period = 0

  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot

  performance_insights_enabled = false
  monitoring_interval          = 0

  tags = merge(var.tags, { Name = "${var.name}-postgres" })
}
