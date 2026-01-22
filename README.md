# CampusUCETrade — Monorepo Overview

CampusUCETrade is organized as a **monorepo** (single repository) that contains:
- the **frontend apps**
- the **backend microservices**
- the **deployment bundles**
- the **infrastructure as code (Terraform)**
- shared tooling for builds and CI/CD

This structure makes it easier to manage the project as one product while still deploying services independently.

---

## 1) Repository Structure (Top-Level)

.github/ # GitHub Actions workflows (CI/CD)
apps/ # Frontend applications (web/PWA, etc.)
deploy/ # Docker Compose deployment bundles (qa/ and prod/)
docker/ # Shared Docker configs (e.g., MQTT config)
gateway/ # Nginx gateway (reverse proxy / routing)
infra/ # Infrastructure as Code (Terraform modules + stacks)
services/ # Backend microservices (auth, user, item, etc.)

docker-compose.yml # Local full stack compose (if used)
docker-compose.core.yml # Local compose for core dependencies/services
Dockerfile # Root docker build (if used)
package.json # Monorepo scripts / tooling entry
pnpm-workspace.yaml # pnpm workspace definition (monorepo packages)
pnpm-lock.yaml # lockfile for reproducible installs
turbo.json # Turborepo pipeline definition (build/lint/test caching)
README.md # Main documentation


---

## 2) What each main folder is for

### `.github/`
CI/CD automation:
- build/publish Docker images
- deploy QA/PROD via Bastion + Docker Compose
- run quality checks (lint/tests) when configured

### `apps/`
Frontend applications.
Example:
- `apps/web` → Vite web app / PWA, deployable to Netlify.

### `services/`
All backend microservices (each one a standalone deployable container).
Examples:
- `auth-service`, `user-service`, `item-service`, etc.

### `gateway/`
Nginx reverse proxy used as the “internal gateway”:
- routes paths to the correct services
- exposes `/health` for ALB health checks

### `deploy/`
Ready-to-run deployment bundles split by environment:
- `deploy/qa/*` and `deploy/prod/*`
Each block (core/business/ops/realtime/middleware) contains its own `docker-compose.yml`
and related configs. This is what the servers actually run.

### `infra/`
Terraform infrastructure:
- `infra/terraform/modules` → reusable blocks (VPC, ALB, Bastion, RDS, S3, compute)
- `infra/terraform/stacks` → environment composition (QA/PROD via tfvars + AWS_PROFILE)

### `docker/`
Shared container configs that are reused by deployment bundles:
- e.g., `docker/mqtt/mosquitto.conf`

---

## 3) Tooling: pnpm + Turborepo (why they exist)

This repo uses:
- **pnpm workspaces** (`pnpm-workspace.yaml`) to manage dependencies across packages
- **Turborepo** (`turbo.json`) to run tasks efficiently:
  - build/lint/test only what changed
  - cache results to speed up CI and local development

In practice, this helps when:
- you change one service → you don’t rebuild everything
- CI/CD becomes faster and more stable

---

## 4) Typical Workflow (high level)

1) Develop locally:
- run services with docker compose (local)
- run frontend from `apps/web`

2) Build & publish images:
- CI builds Docker images for services and pushes to GHCR

3) Deploy to AWS:
- Terraform creates infra (VPC, ALB, Bastion, EC2/ASG, RDS, S3)
- GitHub Actions deploy workflow:
  - discovers private IPs by tags
  - SSH through Bastion
  - copies `deploy/<env>/<block>` to servers
  - runs `docker compose pull && up -d`

---

## 5) Environments

- **QA**: for validation/testing
- **PROD**: for final demo/production-like deployment

Both environments share the same architecture but use different:
- AWS profiles / credentials
- tfvars values
- ALB DNS endpoints
- deployment bundles (`deploy/qa` vs `deploy/prod`)