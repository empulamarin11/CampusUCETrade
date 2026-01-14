# Search-Service

## 1. Service Overview
A high-performance service dedicated to "Read" operations, allowing users to find items using complex filters and categories.

## 2. Applied Architecture
* **Architectural Pattern:** **CQRS - Query Side** (Mandatory - Red) + **Layered Architecture** (Chosen - Blue).
* **Justification:** Implementing the Query side of CQRS allows us to use read-optimized databases or views, significantly improving search speed without affecting the main Item-Service.
* **Implementation:** A simple 3-layer structure (Controller -> Service -> Repository) designed for maximum read efficiency.

## 3. Communication Methods
* **Protocol:** **REST API** (Chosen - Blue).
* **Justification:** Standard for client-side search requests, enabling easy integration with the web and mobile frontends.

## 4. Design Principles
* **KISS (Keep It Simple, Stupid):** The logic is kept lean to minimize latency during high-volume search requests.
* **Low Coupling:** Operates independently of the Item-Service by consuming a read-optimized data projection.