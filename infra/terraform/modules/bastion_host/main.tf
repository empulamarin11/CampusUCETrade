data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "bastion" {
  name        = "${var.name}-bastion-sg"
  description = "Bastion SG (SSH from operator CIDRs)"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ssh_ingress_cidrs
    content {
      description = "SSH from operator"
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

  tags = merge(var.tags, { Name = "${var.name}-bastion-sg" })
}

locals {
  user_data = <<EOF
#!/bin/bash
set -euxo pipefail
dnf -y update
systemctl enable --now amazon-ssm-agent || true
EOF
}

resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [aws_security_group.bastion.id]
  key_name               = var.ssh_key_name

  user_data = local.user_data

  iam_instance_profile = var.instance_profile_name

  tags = merge(var.tags, { Name = "${var.name}-bastion" })
}

resource "aws_eip" "bastion" {
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-bastion-eip" })
}

resource "aws_eip_association" "bastion" {
  allocation_id = aws_eip.bastion.id
  instance_id   = aws_instance.bastion.id
}
