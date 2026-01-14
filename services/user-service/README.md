# User-Service

## 1. Service Overview
Manages detailed user profiles, preferences, and account metadata.

## 2. Applied Architecture
* **Architectural Pattern:** Microservices (Mandatory - Red) + **Hexagonal Architecture** (Chosen - Blue).
* **Justification:** Ensures that profile management rules remain isolated from the persistence layer (PostgreSQL).
* **Implementation:** Separation of domain entities from infrastructure adapters using the Ports and Adapters pattern.

## 3. Communication Methods
* **Protocol:** **REST API** (Chosen - Blue).
* **Justification:** Profile updates and fetches are standard CRUD operations that benefit from the simplicity of REST.

## 4. Design Principles
* **Encapsulation:** User data is strictly managed through the service's API, ensuring data integrity across the system.
* **SOLID (Single Responsibility):** This service focuses exclusively on profile management, delegating authentication to the Auth-Service.