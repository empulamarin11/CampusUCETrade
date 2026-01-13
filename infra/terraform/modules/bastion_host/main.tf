

# ------------------------------------------------------------------------------
# 1. SECURITY GROUP
# Allows SSH (Port 22) from the internet (or specific IPs)
# ------------------------------------------------------------------------------
resource "aws_security_group" "bastion_sg" {
  name        = "${var.name}-bastion-sg"
  description = "Security Group for Bastion Host (SSH Access)"
  vpc_id      = var.vpc_id

  # Inbound: SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_ingress_cidrs
    description = "Allow SSH access"
  }

  # Outbound: Allow all traffic (needed for updates/installing tools)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name}-bastion-sg"
  })
}

# ------------------------------------------------------------------------------
# 2. AMI SELECTION (Ubuntu 22.04 LTS)
# ------------------------------------------------------------------------------
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical (Official Ubuntu Publisher)

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
# 3. EC2 INSTANCE (The Jumpbox)
# ------------------------------------------------------------------------------
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro" # Small/Cheap instance is enough for a jumpbox

  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  key_name                    = var.ssh_key_name
  associate_public_ip_address = true # REQUIRED: Must be reachable from internet

  tags = merge(var.tags, {
    Name = "${var.name}-bastion"
    Role = "bastion"
  })
}