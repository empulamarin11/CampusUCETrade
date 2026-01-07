data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_key_pair" "api_gw" {
  key_name   = "${var.name}-api-gw-key"
  public_key = file(var.ssh_public_key_path)

  tags = merge(var.tags, { Name = "${var.name}-api-gw-key" })
}

resource "aws_security_group" "api_gw" {
  name        = "${var.name}-api-gw-sg"
  description = "API Gateway SG (HTTP public, SSH only from Bastion + optional operator CIDR)"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # (opcional) HTTPS si luego pones certs en la instancia
  # ingress {
  #   description = "HTTPS from internet"
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

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

  tags = merge(var.tags, { Name = "${var.name}-api-gw-sg" })
}

locals {
  user_data = <<-EOT
    #!/bin/bash
    set -euxo pipefail
    exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

    UPSTREAM="${var.upstream_alb_dns}"

    dnf -y update
    dnf -y install docker

    systemctl enable docker
    systemctl start docker

    mkdir -p /opt/api-gateway

    cat > /opt/api-gateway/nginx.conf <<'CONF'
    events {}
    http {
      server {
        listen 80;

        # Proxy a tu ALB actual (por ahora)
        location / {
          proxy_pass http://UPSTREAM_PLACEHOLDER;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
        }
      }
    }
    CONF

    sed -i "s/UPSTREAM_PLACEHOLDER/$UPSTREAM/g" /opt/api-gateway/nginx.conf

    docker rm -f api-gateway-nginx || true
    docker run -d --name api-gateway-nginx \
      -p 80:80 \
      -v /opt/api-gateway/nginx.conf:/etc/nginx/nginx.conf:ro \
      nginx:alpine

    docker ps
  EOT
}

resource "aws_instance" "api_gw" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = var.public_subnet_id
  vpc_security_group_ids = [aws_security_group.api_gw.id]
  key_name               = aws_key_pair.api_gw.key_name

  user_data = local.user_data

  tags = merge(var.tags, { Name = "${var.name}-api-gateway" })
}

resource "aws_eip" "api_gw" {
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${var.name}-api-gw-eip" })
}

resource "aws_eip_association" "api_gw" {
  allocation_id = aws_eip.api_gw.id
  instance_id   = aws_instance.api_gw.id
}
