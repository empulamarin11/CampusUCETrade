locals {
  # 5 "microservices" (simulados) for Account A
  services_a = {
    auth   = {}
    user   = {}
    item   = {}
    search = {}
    chat   = {}
  }
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# One shared SG for all hello instances
resource "aws_security_group" "svc_hello" {
  name        = "${local.name}-svc-hello-sg"
  description = "QA hello microservices SG (HTTP public, SSH from Bastion only)"
  vpc_id      = module.network.vpc_id

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
    security_groups = [module.bastion.bastion_sg_id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${local.name}-svc-hello-sg" })
}

# Create 5 EC2 (one per service) with Hello World
resource "aws_instance" "svc_hello" {
  for_each = local.services_a

  ami           = data.aws_ami.al2023.id
  instance_type = var.instance_type
  key_name = aws_key_pair.svc.key_name


  subnet_id = element(
    module.network.public_subnet_ids,
    index(sort(keys(local.services_a)), each.key) % length(module.network.public_subnet_ids)
  )

  vpc_security_group_ids = [aws_security_group.svc_hello.id]

  # SSM access (optional but recommended)
  iam_instance_profile = var.instance_profile_name

  user_data = <<-EOT
    #!/bin/bash
    set -euxo pipefail
    exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

    dnf -y update
    dnf -y install nginx

    cat > /usr/share/nginx/html/index.html <<'HTML'
    <html>
      <head><title>${each.key}</title></head>
      <body>
        <h1>Hello World</h1>
        <p>Service: ${each.key}</p>
        <p>Env: ${var.env}</p>
      </body>
    </html>
    HTML

    systemctl enable --now nginx
  EOT

  tags = merge(var.tags, {
    Name    = "${local.name}-${each.key}"
    Service = each.key
    Type    = "qa-hello"
  })
}

# One EIP per service (so you can test each in the browser)
resource "aws_eip" "svc_hello" {
  for_each = local.services_a
  domain   = "vpc"

  tags = merge(var.tags, { Name = "${local.name}-${each.key}-eip" })
}

resource "aws_eip_association" "svc_hello" {
  for_each      = local.services_a
  allocation_id = aws_eip.svc_hello[each.key].id
  instance_id   = aws_instance.svc_hello[each.key].id
}

# Outputs (replace the old svc_a_alb_dns)
output "svc_a_eip" {
  value = { for k, e in aws_eip.svc_hello : k => e.public_ip }
}

output "svc_a_url" {
  value = { for k, e in aws_eip.svc_hello : k => "http://${e.public_ip}" }
}
