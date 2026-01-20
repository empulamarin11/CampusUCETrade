data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  role_short = replace(var.role_name, "${var.environment}-", "")
}

resource "aws_security_group" "asg_sg" {
  name        = "${var.name}-${var.role_name}-asg-sg"
  description = "Security Group for ASG ${var.role_name}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [var.bastion_sg_id]
    description     = "SSH from Bastion"
  }

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [var.alb_sg_id]
    description     = "HTTP from ALB"
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
    description = "Internal VPC Traffic"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_launch_template" "lt" {
  name_prefix   = "${var.name}-${var.role_name}-lt-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.ssh_key_name

  vpc_security_group_ids = [aws_security_group.asg_sg.id]

  iam_instance_profile {
    name = var.instance_profile_name
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    usermod -aG docker ubuntu || true
    systemctl enable docker
    systemctl start docker
  EOF)

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.tags, {
      Name      = "${var.name}-${var.role_name}"
      Project   = lookup(var.tags, "Project", "campusuce-trade")
      Env       = var.environment
      Role      = var.role_name
      RoleShort = local.role_short
    })
  }
}

resource "aws_autoscaling_group" "asg" {
  name                = "${var.name}-${var.role_name}-asg"
  vpc_zone_identifier = var.private_subnet_ids

  min_size         = var.min_size
  desired_capacity = var.desired_capacity
  max_size         = var.max_size

  health_check_type         = "ELB"
  health_check_grace_period = 120

  target_group_arns = var.target_group_arns

  launch_template {
    id      = aws_launch_template.lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Project"
    value               = lookup(var.tags, "Project", "campusuce-trade")
    propagate_at_launch = true
  }
  tag {
    key                 = "Env"
    value               = var.environment
    propagate_at_launch = true
  }
  tag {
    key                 = "RoleShort"
    value               = local.role_short
    propagate_at_launch = true
  }
}
