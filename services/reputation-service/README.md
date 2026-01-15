# Reputation-Service

## 1. Service Overview
The **Reputation-Service** calculates user reputation scores based on completed trades, ratings, and feedback.

## 2. Applied Architecture
- **Architecture:** Hexagonal Architecture (Ports & Adapters)
- **Justification:** Protects reputation domain rules and algorithms from infrastructure changes and ensures testability of scoring logic.

## 3. Communication Methods
- **Protocol:** REST API
- **Justification:** Other services may synchronously query a user's reputation for decision-making (e.g., allowing certain transactions).

## 4. Design Principle
- **SOLID (Open/Closed):** Reputation criteria can be extended without changing existing scoring flow.
