# Traceability-Service

## 1. Service Overview
Provides a centralized, immutable audit log of every significant action within the platform.

## 2. Applied Architecture
* **Architectural Pattern:** **Event-Driven Architecture** (Mandatory - Red).
* **Justification:** It acts as a global listener for system events to record them for legal and audit purposes.

## 3. Communication Methods
* **Protocol:** **Kafka** (Mandatory - Red).
* **Justification:** Kafka is chosen for its high-throughput capabilities and persistent log, ensuring that no audit event is lost even under high system load.
* **Implementation:** Producers in various services send events to specific Kafka topics consumed by this service.

## 4. Design Principles
* **Low Coupling:** This service is entirely isolated; it only consumes data without affecting the operation of the services it monitors.
* **Cohesion:** The service has one single purpose: persistent and immutable event logging.