# Terraform Stacks — QA & PROD (infra/terraform/stacks)

This directory is the **execution layer** of the infrastructure.  
Here we wire together the reusable modules from `../modules/` and deploy full environments (**QA** and **PROD**) by selecting the correct **tfvars** file and **AWS profile**.

---

## 1) Folder Contents

Typical files you will find here:

- **`main.tf`**  
  Composes the infrastructure by calling modules (VPC, ALB, Bastion, EC2/ASG, RDS, S3).

- **`providers.tf`**  
  AWS provider configuration (region, credentials via AWS profile).

- **`variables.tf`**  
  Input variable definitions used by the stack.

- **`outputs.tf`**  
  Prints required outputs (ALB DNS, Bastion IP, RDS endpoint, private IPs, ASG name, bucket name, etc.).

- **`keypair.tf`**  
  Key pair configuration (uploads/creates the SSH key used for EC2 access).

- **`terraform.tfvars`**  
  QA environment variables.

- **`terraform.prod.tfvars`**  
  PROD environment variables.

- **`_states/` (optional/local convention)**  
  Local folder used to keep separate state files per environment (recommended).

- **`.terraform/` and `.terraform.lock.hcl`**  
  Terraform internal working directory and provider lock.

- **`terraform.tfstate` / `terraform.tfstate.backup`**  
  Local state files (only when using local backend).

- **`qa-outputs.txt`**  
  Helper artifact used to store outputs during QA validation.

---

## 2) Environments (How to Choose QA vs PROD)

This stack supports two environments using different tfvars files:

- **QA**
  - tfvars: `terraform.tfvars`
  - AWS profile: `qa`

- **PROD**
  - tfvars: `terraform.prod.tfvars`
  - AWS profile: `prod`

---

## 3) Recommended State Strategy (Avoid Mixing QA/PROD)

If you use a **local backend**, do **NOT** share the same `terraform.tfstate` for QA and PROD.

### Recommended approach: use `_states/`
Example:
- `_states/qa.tfstate`
- `_states/prod.tfstate`

This prevents accidental cross-environment corruption.