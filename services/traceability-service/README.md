# Traceability-Service

## 1. Service Overview
The **Traceability-Service** stores an immutable audit log of significant system events for monitoring, compliance, and reporting.

## 2. Applied Architecture
- **Architecture:** Event-Driven Architecture
- **Justification:** Audit logging should be decoupled from business workflows; it listens to events and persists them asynchronously.

## 3. Communication Methods
- **Protocol:** Kafka
- **Justification:** Kafka provides durable, high-throughput event streaming suitable for audit trails.

## 4. Design Principle
- **Low Coupling:** This service consumes events without impacting the producers or transactional flows.
