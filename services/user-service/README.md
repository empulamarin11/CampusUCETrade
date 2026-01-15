# User-Service

## 1. Service Overview
The **User-Service** manages user profiles, preferences, and account metadata (non-auth data). It is the source of truth for user profile information.

## 2. Applied Architecture
- **Architecture:** Hexagonal Architecture (Ports & Adapters)
- **Justification:** Protects the user domain from changes in persistence or external dependencies and supports clean separation of concerns.

## 3. Communication Methods
- **Protocol:** REST API
- **Justification:** Profile operations (read/update) are naturally synchronous.

## 4. Design Principle
- **Encapsulation:** User profile rules and data access are isolated within this service; other services only interact through its API.
