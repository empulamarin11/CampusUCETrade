# Delivery-Service

## 1. Service Overview
The **Delivery-Service** manages delivery confirmation and exchange logistics. It can support real-time tracking signals for exchange updates.

## 2. Applied Architecture
- **Architecture:** Layered Architecture
- **Justification:** Clear separation between API endpoints, business logic, and infrastructure integration keeps delivery workflows maintainable.

## 3. Communication Methods
- **Protocol:** MQTT
- **Justification:** MQTT is lightweight and suitable for real-time delivery/tracking signals over unreliable networks.

## 4. Design Principle
- **Cohesion:** All components focus strictly on delivery and exchange logistics responsibilities.
