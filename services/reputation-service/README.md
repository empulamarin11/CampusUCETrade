# Reputation-Service

## 1. Service Overview
Calculates and maintains user trust scores based on trade history, ratings, and reviews.

## 2. Applied Architecture
* **Architectural Pattern:** **Hexagonal Architecture** (Chosen - Blue).
* **Justification:** Protects the sensitive scoring algorithms from external changes in the database or UI.

## 3. Communication Methods
* **Protocol:** **REST API** (Chosen - Blue).
* **Justification:** Allows other services to synchronously fetch a user's reputation score before allowing a high-value trade.

## 4. Design Principles
* **Encapsulation:** The internal formulas for calculating reputation are hidden; only the final score is exposed through the API.
* **SOLID (Open/Closed):** New rating criteria can be added without modifying existing calculation logic.