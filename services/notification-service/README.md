# Notification-Service

## 1. Service Overview
The **Notification-Service** centralizes outbound notifications (email/push/SMS) triggered by platform activity.

## 2. Applied Architecture
- **Architecture:** Event-Driven Architecture
- **Justification:** Notifications are reactive by nature. This service responds to events and triggers delivery workflows.

## 3. Communication Methods
- **Protocol:** Webhooks
- **Justification:** Webhooks provide a simple integration channel to automation tools (n8n) to execute notification workflows.

## 4. Design Principle
- **DRY:** Shared templates and reusable notification logic reduce duplication across different notification types.

## 5. n8n Integration
- **Where n8n is applied:** This service calls **n8n via Webhooks** to execute automated workflows (e.g., email formatting, chained actions, reporting).
