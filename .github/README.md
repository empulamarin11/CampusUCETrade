# GitHub Actions — Workflows (`.github/workflows`)

This project uses **GitHub Actions** to automate:
1) **CI validation** (lint/build with turbo)
2) **Docker image publishing** (QA and PROD)
3) **Remote deployment to AWS** (QA and PROD) through a **Bastion Host**
4) **Connectivity checks** (SSH test)

All workflow files live in:

.github/workflows/
ci-turbo.yml
qa-images.yml
prod-images.yml
deploy-qa.yml
deploy-prod.yml
qa-ssh-test.yml


---

## 1) `ci-turbo.yml` — Continuous Integration (Monorepo CI)

Purpose:
- Runs repository quality checks using **Turborepo**
- Typical tasks: lint, tests, build (depending on turbo.json configuration)

When it runs:
- usually on PRs and/or pushes (depends on triggers inside the file)

Why it matters:
- ensures changes don’t break the monorepo before building images or deploying

---

## 2) `qa-images.yml` — Build & Publish Docker Images (QA)

Purpose:
- Builds Docker images for the backend services
- Pushes them to GHCR with QA tags (example: `:qa`)

When it runs:
- on pushes/PRs to the QA branch (depends on triggers)

Output:
- images available in GHCR for QA deployments

---

## 3) `prod-images.yml` — Build & Publish Docker Images (PROD)

Purpose:
- Same as QA images, but for production
- Publishes images with production tags (example: `:prod` or `:latest`, depending on the chosen convention)

When it runs:
- typically on `main` (or release branch) pushes

---

## 4) `deploy-qa.yml` — Deploy QA to AWS (via Bastion)

Purpose:
- Connects to AWS using secrets
- Discovers private instance IPs by tags (Project/Env/RoleShort)
- SSH through the **QA Bastion**
- Copies `deploy/qa/<block>` to each host
- Runs Docker Compose (`pull` + `up -d`) per block

Order (typical):
1) middleware
2) core
3) business
4) ops
5) realtime

---

## 5) `deploy-prod.yml` — Deploy PROD to AWS (via Bastion)

Purpose:
- Same as deploy-qa, but targeting PROD resources and secrets
- Uses PROD Bastion + PROD instance tags
- Must handle the fact that **core can be an ASG** (dynamic IPs)

Key behavior:
- discovers `CORE_IPS`
- selects a reachable core instance (SSH test) and deploys there

---

## 6) `qa-ssh-test.yml` — Quick SSH Connectivity Test (QA)

Purpose:
- Validates SSH connectivity to the bastion/hosts
- Useful for debugging network/key issues before running full deploy

---

## 7) Secrets & Required Variables (High-Level)

These workflows depend on GitHub Secrets such as:
- AWS credentials (access key / secret / session token)
- region
- bastion host public IP or DNS
- SSH private key for bastion and private hosts
- GHCR username/token
- runtime secrets (DB host/name/user/password, JWT secret, bucket name, etc.)

---

## Notes / Best Practices
- Keep QA and PROD secrets separated (`QA_*` vs `PROD_*`)
- Avoid hardcoding environment endpoints in code; inject via `.env` during deploy
- If the lab credentials expire, deployments will fail until secrets are refreshed