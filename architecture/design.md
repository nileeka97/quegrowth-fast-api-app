# Architecture & Infrastructure Design

## 1. High-Level Architecture (Microservice → Queue → Worker)

This system follows an **asynchronous, event-driven architecture** designed for scalability and fault tolerance.

**Flow:**

1. **Service A (API – FastAPI)**
   - `POST /task`: Accepts JSON payloads and publishes messages to a **RabbitMQ queue**.
   - `GET /stats`: Returns system statistics collected from RabbitMQ and Valkey.
2. **Message Queue (RabbitMQ)**
   - Handles reliable message delivery between services.
   - Maintains queue backlog and ensures messages are processed at least once.
3. **Worker Service (FastAPI)**
   - Consumes messages from RabbitMQ.
   - Processes tasks asynchronously.
   - Updates processed task counters and runtime metrics in **Valkey**.

This separation allows the API layer and workers to scale independently without tight coupling.

---

## 2. Cache & Storage Choices

### Valkey (Caching & Metrics Store)

- Used for:
  - Application caching.
  - Storing runtime metrics:
    - Cached keys count.
    - Worker processed task count.

### RabbitMQ (Message Queue)

- Used for:
  - Task queuing and backlog management.
  - Decoupling request ingestion from processing.

No traditional database is required for this architecture.

---

## 3. Deployment Strategy

- **Platform:** Azure Kubernetes Service (AKS)
- **Packaging:** Helm charts per component
  - API Service
  - Worker
  - RabbitMQ
  - Valkey
- **CI/CD:** Fully automated **GitHub Actions**
  - Build and scan container images.
  - Deploy using Helm with environment-specific values.
- Supports rolling updates with minimal downtime.

---

## 4. Observability & Monitoring (OpenTelemetry + SigNoz)

- **OpenTelemetry Instrumentation**
  - FastAPI services are instrumented using OpenTelemetry SDKs.
  - Automatic collection of:
    - Distributed traces (API → RabbitMQ → Worker).
    - Application metrics (latency, error rates, throughput).
    - Structured logs (correlated with traces).
- **SigNoz**
  - Deployed in Azure VM as the observability backend.
  - Acts as a unified platform for:
    - Metrics
    - Traces
    - Logs
  - Enables end-to-end request visibility and root cause analysis.
- **Custom Metrics**
  - Worker processed count.
  - Queue backlog length.
  - Cache hit/miss rates from Valkey.
- **Alerting**
  - Alerts configured in SigNoz for:
    - High queue backlog.
    - Increased error rates.
    - Worker processing latency.

---

## 5. Scaling Across Azure

- **AKS Cluster Autoscaler**
  - Dynamically scales nodes based on pod resource demands.
- **Horizontal Pod Autoscaling**
  - API Gateway scales on CPU and request load.
  - API Gateway. Worker service, RabbitMQ and Valkey scale based on CPU and memory usage.

---

## 6. Secrets Management Strategy

- **Azure Key Vault**
  - Stores all sensitive data:
    - RabbitMQ credentials.
    - Valkey authentication details.
  - No secrets are hardcoded in source code or Helm charts.
- **Runtime Injection**
  - Secrets are mounted or injected into pods at runtime.
  - Enables secure rotation without application changes.

---

## 7. Network Topology

- **Ingress Layer**
  - NGINX Ingress Controller deployed in AKS.
  - Exposed via **Azure Load Balancer**.
  - Routes external traffic to the API Gateway.
- **Internal Services**
  - RabbitMQ, Valkey, and Worker services use `ClusterIP`.
  - Accessible only within the Kubernetes cluster.

---

## Summary

This architecture delivers a **secure, scalable, and cloud-native solution** using:

- FastAPI microservices.
- RabbitMQ for reliable queuing.
- Valkey for caching and metrics.
- AKS with cluster autoscaling.
- Helm + GitHub Actions for automated deployments.
- Azure Key Vault for secrets management.
- NGINX Ingress and Azure Load Balancer for traffic control.
