# Item-Service

## 1. Service Overview
Responsible for managing the catalog of products and items available for trade. It handles all "Write" operations (Create/Update/Delete).

## 2. Applied Architecture
* **Architectural Pattern:** **CQRS - Command Side** (Mandatory - Red) + **Hexagonal Architecture** (Chosen - Blue).
* **Justification:** By separating commands from queries, we ensure that the item creation logic is highly optimized and decoupled from complex search filters.
* **Implementation:** Uses a command-bus pattern to process item modifications, ensuring data integrity before persistence.

## 3. Communication Methods
* **Protocol:** **REST API** (Chosen - Blue).
* **Justification:** Provides a reliable and straightforward interface for users to submit new items or edit existing ones.

## 4. Design Principles
* **SOLID (Single Responsibility):** This service is exclusively focused on the state mutation of items, delegating data retrieval to the Search-Service.
* **Cohesion:** All components within this service are strictly related to item lifecycle management.