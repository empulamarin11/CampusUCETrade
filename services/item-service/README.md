# Item-Service

## 1. Service Overview
The **Item-Service** manages the item catalog lifecycle (Create/Update/Delete) and item state transitions. This is the **write side** of the catalog.

## 2. Applied Architecture
- **Architecture:** CQRS (Command Side)
- **Justification:** Commands (writes) are separated from complex reads/search queries to keep write operations consistent and easier to validate.

## 3. Communication Methods
- **Protocol:** REST API
- **Justification:** CRUD operations require immediate acknowledgement and validation feedback.

## 4. Design Principle
- **SOLID (Single Responsibility - SRP):** This service focuses only on item state mutation; read/search concerns are handled elsewhere.
