# Chat-Service

## 1. Service Overview
The **Chat-Service** enables real-time communication between users involved in a trade/reservation flow.

## 2. Applied Architecture
- **Architecture:** Layered Architecture
- **Justification:** Separates real-time connection handling from message logic and persistence concerns.

## 3. Communication Methods
- **Protocol:** WebSocket
- **Justification:** WebSocket supports real-time, bidirectional communication without polling.

## 4. Design Principle
- **KISS:** Keep the real-time messaging flow simple and stable to reduce operational complexity.
