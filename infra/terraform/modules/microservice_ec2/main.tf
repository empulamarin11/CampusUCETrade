data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "this" {
  name        = "${var.name}-sg"
  description = "QA hello microservice SG (HTTP public, SSH from Bastion + optional operator)"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description     = "SSH from Bastion only"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [var.bastion_sg_id]
  }

  dynamic "ingress" {
    for_each = var.ssh_ingress_cidrs
    content {
      description = "SSH temporary from operator CIDR"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name}-sg" })
}

locals {
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    service       = var.service
    env           = var.env
    ghcr_owner    = var.ghcr_owner
    ghcr_username = var.ghcr_username
    ghcr_token    = var.ghcr_token

    db_endpoint = var.db_endpoint
    db_port     = var.db_port
    db_name     = var.db_name
    db_username = var.db_username
    db_password = var.db_password

    jwt_secret    = var.jwt_secret
    jwt_algorithm = var.jwt_algorithm
  })
}

resource "aws_instance" "this" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.this.id]
  key_name               = var.key_name

  iam_instance_profile = var.instance_profile_name

  user_data                  = local.user_data
  user_data_replace_on_change = true

  tags = merge(var.tags, {
    Name    = var.name
    Service = var.service
    Type    = "qa-hello"
  })
}

resource "aws_eip" "this" {
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-eip" })
}

resource "aws_eip_association" "this" {
  allocation_id = aws_eip.this.id
  instance_id   = aws_instance.this.id
}
