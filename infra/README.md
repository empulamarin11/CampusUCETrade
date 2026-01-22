# CampusUCETrade — AWS Infrastructure (Terraform) — QA & PROD

This repository deploys **CampusUCETrade** on AWS using **Terraform** with a **multi-environment** setup:
- **QA** for testing and validation
- **PROD** for the production-like deployment

The infrastructure follows a secure design: **all application hosts run in private subnets**, exposed only through an **Application Load Balancer (ALB)**, and managed via a **Bastion Host** for SSH access.

---

## 1) High-Level Architecture

### Networking
- **One VPC per environment** (QA and PROD).
- **2 Public Subnets**: ALB + Bastion Host.
- **2 Private Subnets**: application hosts + RDS.

### Public Entry Point
- **Application Load Balancer (ALB)** is the public entry point.
- Standard health check endpoint: `GET /health`.

### Secure Access (SSH)
- **Bastion Host** is the only public SSH entry point.
- Private hosts are accessed via SSH **through** the Bastion.

### Compute Blocks (Private Hosts)
Workloads are split into blocks to simplify deployments and isolate responsibilities:

- **core (ASG)**  
  Runs nginx (gateway) + core services (e.g., auth/user).  
  ✅ Uses an **Auto Scaling Group** → **core private IPs can change** when instances are replaced.

- **business (EC2)**  
  Runs business domain services (catalog / reservations / etc., depending on your compose).

- **ops (EC2)**  
  Runs operational services (notifications, traceability, etc., depending on your compose).

- **realtime (EC2)**  
  Runs realtime/chat services.

- **middleware (EC2)**  
  Runs shared infrastructure containers (Redis, RabbitMQ, Kafka, MQTT, etc.).

### Data & Storage
- **Amazon RDS PostgreSQL** for relational data.
- **S3 Media Bucket** per environment for multimedia (images/files).

---

## 2) Repository Structure (Infrastructure)

Terraform stack path:

Key files:
- `main.tf`, `variables.tf`, `outputs.tf`
- `providers.tf`
- `terraform.tfvars` (QA)
- `terraform.prod.tfvars` (PROD)

---

## 3) Environment Configuration (QA vs PROD)

We maintain separate tfvars for each environment:

### QA
- Variable file: `terraform.tfvars`
- Typical usage:
```bash
AWS_PROFILE=qa terraform plan  -var-file=terraform.tfvars
AWS_PROFILE=qa terraform apply -var-file=terraform.tfvars

### PROD
- Variable file: `tterraform.prod.tfvars`
- Typical usage:
```bash
AWS_PROFILE=prod terraform plan -var-file=terraform.prod.tfvars
AWS_PROFILE=prod terraform apply -var-file=terraform.prod.tfvars

### QA and PROD

AWS_PROFILE=qa   terraform destroy -var-file=terraform.tfvars
AWS_PROFILE=prod terraform destroy -var-file=terraform.prod.tfvars