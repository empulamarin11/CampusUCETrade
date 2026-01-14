# Notification-Service

## 1. Service Overview
Centralizes all outbound communications (Email, Push, SMS) triggered by system events.

## 2. Applied Architecture
* **Architectural Pattern:** **Event-Driven Architecture** (Mandatory - Red).
* **Justification:** Notifications are inherently reactive. This service waits for events to occur in other parts of the system to trigger specific alerts.

## 3. Communication Methods
* **Protocols:** **RabbitMQ** (Mandatory - Red) + **Webhooks** (Chosen - Blue).
* **Justification:** It consumes events from **RabbitMQ** and uses **Webhooks** to integrate with **n8n** for advanced workflow automation.

## 4. Design Principles
* **DRY (Don't Repeat Yourself):** Uses shared notification templates and logic stored in the monorepo's shared packages.
* **KISS:** Focuses only on the delivery of messages, not on the business logic that triggered them.

## 5. Automation Integration
* **Tool:** **n8n**.
* **Justification:** Fulfils requirement #20 by using n8n to automate complex business processes, such as sending stylized PDF reports via email after a trade.