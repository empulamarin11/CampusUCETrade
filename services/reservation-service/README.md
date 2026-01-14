# Reservation-Service

## 1. Service Overview
Handles the booking lifecycle for campus trades and item exchanges.

## 2. Applied Architecture
* **Architectural Pattern:** **Event-Driven Architecture** (Mandatory - Red).
* **Justification:** Reservations trigger multiple side effects (notifications, stock updates). An event-driven approach prevents the system from being blocked by synchronous calls.

## 3. Communication Methods
* **Protocol:** **RabbitMQ** (Mandatory - Red).
* **Justification:** Used as the message broker to publish events like `ReservationCreated`. This allows asynchronous processing and high availability.
* **Implementation:** Integration with RabbitMQ using the NestJS Microservices module.

## 4. Design Principles
* **Low Coupling:** The Reservation-Service does not need to know about the Notification or Item services; it simply broadcasts events to the broker.
* **SOLID (Open/Closed):** New features (like a loyalty system) can be added by simply subscribing to existing events without modifying the Reservation-Service code.