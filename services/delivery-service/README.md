# Delivery-Service

## 1. Service Overview
Manages the logistics and real-time tracking of item exchanges between users.

## 2. Applied Architecture
* **Architectural Pattern:** **Layered Architecture** (Chosen - Blue).
* **Justification:** A structured approach is used to separate the tracking logic from the logistics provider integrations.

## 3. Communication Methods
* **Protocol:** **MQTT** (Mandatory - Red).
* **Justification:** Essential for real-time GPS tracking with low battery consumption and high efficiency over unstable mobile networks.

## 4. Design Principles
* **SOLID (Single Responsibility):** Manages only the physical movement and status updates of trades.
* **Cohesion:** All modules are dedicated to the logistics domain, ensuring a focused and maintainable codebase.