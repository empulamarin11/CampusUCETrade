# API Gateway (Nginx) — `gateway/`

This folder contains the **Nginx-based gateway** for CampusUCETrade.  
It is used as the **internal reverse proxy** in front of the microservices and is typically deployed inside the **core block** (behind the ALB).

---

## 1) Contents

gateway/
Dockerfile
nginx/
(nginx configuration files)


- **`Dockerfile`**  
  Builds a custom Nginx image (if required) including the project’s Nginx configuration.

- **`nginx/`**  
  Holds the Nginx config used to:
  - route requests to the correct microservices (reverse proxy)
  - expose a unified HTTP entry point (usually port 80)
  - provide a stable **`/health`** endpoint for ALB health checks

---

## 2) How It Works in the Platform

### External flow
Client → **ALB (public)** → **core nginx (private)** → microservices (private)

### Responsibilities
- Path-based routing (example patterns):
  - `/auth/*` → auth-service
  - `/users/*` → user-service
  - `/items/*` → item-service
- Central place for basic HTTP behaviors:
  - timeouts
  - headers (forwarded headers)
  - request size limits (if needed)

---

## 3) Health Check

The ALB target group expects:
- `GET /health` → `200 OK`

This health endpoint is typically handled directly by Nginx (no upstream dependency), to keep health checks stable.

---

## 4) Notes / Best Practices
- Keep the gateway config environment-agnostic; environment differences should be handled via variables or deploy configs.
- Avoid hardcoding private IPs; use service/container DNS names when running on a single host, or internal DNS if distributed.
- If you add new microservices, update the Nginx routes consistently across QA