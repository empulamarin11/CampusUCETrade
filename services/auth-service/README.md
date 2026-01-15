# Auth-Service

## 1. Service Overview
The **Auth-Service** handles authentication and authorization for the CampusUCETrade platform. It issues and validates **JWT** access tokens and enforces security rules for protected endpoints.

## 2. Applied Architecture
- **Architecture:** Hexagonal Architecture (Ports & Adapters)
- **Justification:** Keeps authentication domain logic (token generation/validation, credential checks) independent from infrastructure (database, frameworks), making it easier to test and maintain.

## 3. Communication Methods
- **Protocol:** REST API
- **Justification:** Authentication requires immediate synchronous responses (e.g., token issuance).

## 4. Design Principle
- **SOLID (Dependency Inversion - DIP):** Core use cases depend on abstractions (ports/interfaces), not on concrete infrastructure implementations.

## 5. Notes
- Exposes health endpoint for infrastructure validation (e.g., `/health`).
