# Reservation-Service

## 1. Service Overview
The **Reservation-Service** manages reservation lifecycles for item exchanges, including status transitions and reservation rules.

## 2. Applied Architecture
- **Architecture:** Event-Driven Architecture
- **Justification:** Reservations trigger side effects (notifications, audit, downstream processes). Publishing events avoids blocking the main flow with synchronous dependencies.

## 3. Communication Methods
- **Protocol:** RabbitMQ
- **Justification:** RabbitMQ enables reliable asynchronous event distribution (e.g., `ReservationCreated`) to multiple consumers.

## 4. Design Principle
- **Low Coupling:** The service publishes events without knowing which downstream services will handle them.
