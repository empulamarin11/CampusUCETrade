# Deployment Layout — QA & PROD (`/deploy`)

This folder contains the **runtime deployment bundles** used by our servers to start the platform using **Docker Compose**.  
We keep **two separate deployment trees**:

- `deploy/qa/`  → QA environment
- `deploy/prod/` → Production environment

Each environment is split into **blocks** (hosts) to simplify operations and isolate responsibilities.

---

## 1) Folder Structure
deploy/
qa/
core/
business/
ops/
realtime/
middleware/
prod/
core/
business/
ops/
realtime/
middleware/
deploy/
qa/
core/
business/
ops/
realtime/
middleware/
prod/
core/
business/
ops/
realtime/


Each block folder contains the files required to run that block, typically:
- `docker-compose.yml`
- `nginx.conf` (for gateway blocks)
- optional config files (e.g., broker configs, prometheus config, etc.)

---

## 2) Blocks (What runs where)

### `middleware/`
Shared infrastructure containers, for example:
- Redis
- RabbitMQ (+ management UI)
- Kafka + Zookeeper
- MQTT broker
- n8n (automation)

This block is deployed **first**, because other blocks depend on it.

### `core/`
API entry block inside the private network. Usually contains:
- **nginx** (reverse proxy / gateway on port 80)
- core microservices (e.g., auth-service, user-service, etc.)

The ALB typically targets this block and checks:
- `GET /health`

> Note: in PROD, core may run in an **Auto Scaling Group**, so the workflow discovers and selects a reachable core instance.

### `business/`
Business-domain services (catalog/items, reservations, delivery, reputation, traceability, etc. depending on the project stage).

### `ops/`
Operational services (notifications, background workers, orchestration helpers, etc.).

### `realtime/`
Realtime/chat services (websocket or MQTT-based, depending on the implementation).

---

## 3) Environment Variables (`.env`)

We do **not** commit `.env` files in Git for production credentials.

During deployment, the pipeline (GitHub Actions) generates a `.env` file on each host, typically including:
- `DATABASE_URL`
- `JWT_SECRET`
- `REDIS_URL`
- broker endpoints (RabbitMQ/Kafka/MQTT)
- `S3_BUCKET` and `S3_REGION` (when needed)

Paths on the target host:


---

## 4) How the CI/CD Deploy Works (High-Level)

The deployment workflow:
1. Finds instance private IPs by tags (Project/Env/RoleShort).
2. Connects through the Bastion Host.
3. Copies the correct folder (`deploy/<env>/<block>`) to the instance.
4. Writes `.env` on the instance.
5. Runs Docker Compose:
   - `docker compose pull`
   - `docker compose up -d --remove-orphans`

Recommended order:
1) `middleware`  
2) `core`  
3) `business`  
4) `ops`  
5) `realtime`

---

## 5) Manual Deploy (Emergency / Debug)

Example: deploy `core` manually to a private host through the Bastion:

```bash
ssh -i ~/.ssh/<KEY> -o IdentitiesOnly=yes \
  -o "ProxyCommand=ssh -i ~/.ssh/<KEY> -o IdentitiesOnly=yes -W %h:%p ubuntu@<BASTION_PUBLIC_IP>" \
  ubuntu@<PRIVATE_IP> "cd /home/ubuntu/deploy/core && docker compose --env-file .env pull && docker compose --env-file .env up -d --remove-orphans"
