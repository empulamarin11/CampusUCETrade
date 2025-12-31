data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "ec2" {
  name        = "${var.name}-ec2-sg"
  description = "EC2 docker hosts security group (only ALB inbound)"
  vpc_id      = var.vpc_id

  ingress {
    description     = "App traffic from ALB"
    from_port       = var.target_port
    to_port         = var.target_port
    protocol        = "tcp"
    security_groups = [var.alb_sg_id]
  }

    dynamic "ingress" {
    for_each = var.internal_ports
    content {
      description = "Internal traffic within ASG (same SG)"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      self        = true
    }
    }


  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.name}-ec2-sg" })
}

locals {
  user_data = <<-EOT
    #!/bin/bash
    set -euxo pipefail

    dnf -y update
    dnf -y install docker
    systemctl enable docker
    systemctl start docker

    docker rm -f campusuce-nginx || true
    docker run -d --name campusuce-nginx -p 80:80 nginx:alpine
  EOT
}

resource "aws_launch_template" "this" {
  name_prefix   = "${var.name}-lt-"
  image_id      = data.aws_ami.al2023.id
  instance_type = var.instance_type

  key_name = var.ssh_key_name


  vpc_security_group_ids = [aws_security_group.ec2.id]
  user_data = base64encode(file("${path.module}/user_data.sh"))

  tag_specifications {
    resource_type = "instance"
    tags          = merge(var.tags, { Name = "${var.name}-ec2" })
  }

  tag_specifications {
    resource_type = "volume"
    tags          = merge(var.tags, { Name = "${var.name}-volume" })
  }

  tags = merge(var.tags, { Name = "${var.name}-lt" })
}

resource "aws_autoscaling_group" "this" {
  name                = "${var.name}-asg"
  vpc_zone_identifier = var.subnet_ids

  min_size         = var.min_size
  desired_capacity = var.desired_capacity
  max_size         = var.max_size

  health_check_type         = "ELB"
  health_check_grace_period = 120

  target_group_arns = [var.alb_target_group_arn]

  launch_template {
    id      = aws_launch_template.this.id
    version = "$Latest"
  }

  dynamic "tag" {
    for_each = merge(var.tags, { Name = "${var.name}-asg" })
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}
