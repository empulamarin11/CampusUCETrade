# Auth-Service

## 1. Service Overview
The **Auth-Service** is responsible for identity management, authentication, and authorization within the **CampusUceTrade** ecosystem.

## 2. Applied Architecture
* **Architectural Pattern:** Microservices (Mandatory - Red) + **Hexagonal Architecture** (Chosen - Blue).
* **Justification:** Hexagonal Architecture was implemented to decouple the security domain logic (token generation, credential validation) from infrastructure details like the **Supabase** PaaS. This ensures the business logic remains testable and independent of external tools.
* **Implementation:** * `src/domain`: Contains user entities and repository interfaces (Ports).
    * `src/application`: Handles use cases like `LoginUser` and `ValidateToken`.
    * `src/infrastructure`: Contains adapters for Supabase integration and JWT services.

## 3. Communication Methods
* **Protocol:** **REST API** (Chosen - Blue).
* **Justification:** REST is the industry standard for synchronous authentication processes where the client requires an immediate response (JWT) to proceed.
* **Implementation:** NestJS controllers exposing endpoints such as `POST /auth/login` and `POST /auth/register`.

## 4. Design Principles
* **SOLID (Dependency Inversion):** High-level application logic depends on abstractions (interfaces), not on low-level Supabase implementation.
* **Encapsulation:** Security-sensitive logic and secrets are restricted to this microservice; no other service has direct access to the identity database.

## 5. PaaS Integration
* **Tool:** **Supabase**.
* **Justification:** Used to manage user records and secure profile storage, fulfilling the "Use AWS and any PAaS" requirement (Point 6).