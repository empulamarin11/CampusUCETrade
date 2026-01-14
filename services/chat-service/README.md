# Chat-Service

## 1. Service Overview
Enables real-time communication between buyers and sellers to negotiate trades.

## 2. Applied Architecture
* **Architectural Pattern:** **Layered Architecture** (Chosen - Blue).
* **Justification:** Simplifies the management of message history and active connection states.

## 3. Communication Methods
* **Protocol:** **Websockets** (Chosen - Blue).
* **Justification:** Required for instant, bidirectional messaging, ensuring a smooth user experience without polling.

## 4. Design Principles
* **Low Coupling:** The chat system functions independently of the trade or reservation logic.
* **Encapsulation:** Individual chat rooms and message states are isolated and secured within the service's domain.