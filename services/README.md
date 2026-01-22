# Microservices — `services/`

This folder contains the **core microservices** of CampusUCETrade.  
Each service is an **independent deployable unit** (containerized) with its own codebase, dependencies, and API.

services/
auth-service/
user-service/
item-service/
search-service/
reservation-service/
chat-service/
delivery-service/
notification-service/
reputation-service/
traceability-service/


---

## General Principles

- **Microservice isolation:** each service owns its domain logic and can be built/deployed independently.
- **Container-first:** services are packaged as Docker images and published to a registry (e.g., GHCR).
- **Environment-based configuration:** runtime settings are injected via `.env` / environment variables (DB URL, JWT secret, broker endpoints, etc.).
- **API-first:** services expose REST endpoints (and realtime service may use MQTT/WebSocket depending on implementation).

---

## High-Level Responsibilities (Summary)

- **auth-service:** authentication, JWT issuance/validation, institutional domain rules.
- **user-service:** user profiles and account metadata (non-auth data).
- **item-service:** item/catalog management (CRUD, categories, lifecycle state).
- **search-service:** optimized read-side queries and filters for item discovery.
- **reservation-service:** item reservations and state transitions.
- **chat-service:** user messaging (usually tied to reservations/transactions).
- **delivery-service:** delivery confirmation workflow and evidence handling.
- **notification-service:** notifications/events delivery to users.
- **reputation-service:** reputation scoring based on successful exchanges.
- **traceability-service:** audit trail / trace events for platform actions.

---

## CI/CD Note

Images are typically built and published per service, then pulled by the deployment bundles in:
- `deploy/qa/...`
- `deploy/prod/...`