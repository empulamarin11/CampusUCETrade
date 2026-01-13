

# ------------------------------------------------------------------------------
# 1. SECURITY GROUP
# Controls traffic to the Application Node
# ------------------------------------------------------------------------------
resource "aws_security_group" "app_sg" {
  name        = "${var.name}-${var.role_name}-sg"
  description = "Security Group for App Node ${var.role_name}"
  vpc_id      = var.vpc_id

  # Inbound: SSH (ONLY from Bastion Host)
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [var.bastion_sg_id]
    description     = "SSH from Bastion"
  }

  # Inbound: Internal VPC Traffic 
  # (Allows microservices to talk to each other and the DB on any port)
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"] # Adjust if your VPC CIDR is different
    description = "Internal VPC Traffic"
  }

  # Outbound: Allow all (Needed for Docker pull, apt-get update)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# ------------------------------------------------------------------------------
# 2. AMI SELECTION (Ubuntu 22.04 LTS)
# ------------------------------------------------------------------------------
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ------------------------------------------------------------------------------
# 3. EC2 INSTANCE (Docker Host)
# ------------------------------------------------------------------------------
resource "aws_instance" "app_node" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  # Networking
  subnet_id                   = var.private_subnet_ids[0] # Deploy in first private subnet
  vpc_security_group_ids      = [aws_security_group.app_sg.id]
  associate_public_ip_address = false # IT IS PRIVATE (Secure)

  # Access & Identity
  key_name             = var.ssh_key_name
  iam_instance_profile = var.instance_profile_name

  # ----------------------------------------------------------------------------
  # BOOTSTRAP SCRIPT (User Data)
  # Installs Docker and Docker Compose automatically on startup
  # ----------------------------------------------------------------------------
  user_data = <<-EOF
              #!/bin/bash
              echo "Initializing ${var.role_name} node..."
              
              # 1. Install prerequisites
              apt-get update -y
              apt-get install -y ca-certificates curl gnupg lsb-release

              # 2. Add Docker's official GPG key
              mkdir -p /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

              # 3. Set up the repository
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

              # 4. Install Docker Engine
              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

              # 5. Post-installation steps (Allow ubuntu user to run docker)
              usermod -aG docker ubuntu
              systemctl enable docker
              systemctl start docker
              
              echo "Docker installed successfully."
              EOF

  tags = merge(var.tags, {
    Name = "${var.name}-${var.role_name}"
    Role = var.role_name
    Env  = var.environment
  })
}