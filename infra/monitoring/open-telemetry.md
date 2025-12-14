# Installing OpenTelemetry Collectors on Kubernetes with Helm

There are multiple ways to deploy **OpenTelemetry (OTel) Collectors** on a Kubernetes cluster using Helm.

---

## Deployment Options Overview

### 1️⃣ Official OpenTelemetry Helm Charts

- **DaemonSet** → Collects pod- and node-level metrics
- **Deployment** → Collects host/cluster-level metrics

### 2️⃣ SigNoz K8s Infra Helm Chart (**Recommended**)

- Deploys **both a DaemonSet and a Deployment** in a single Helm release
- Pre-optimized for **SigNoz ingestion and dashboards**
- Easier setup with better defaults for Kubernetes observability

---

## 1️⃣ OpenTelemetry Collector – DaemonSet (Pod-level Metrics)

### Prepare Values File: `otel-collector-daemonset.yaml`

```yaml
mode: daemonset

image:
  repository: otel/opentelemetry-collector-k8s

replicaCount: 1

presets:
  kubernetesAttributes:
    enabled: true
  kubeletMetrics:
    enabled: true
  logsCollection:
    enabled: true

config:
  exporters:
    otlp:
      endpoint: http://signoz.quegrowth.me:4317
      tls:
        insecure: true

  connectors:
    spanmetrics:

  service:
    pipelines:
      traces:
        exporters: [spanmetrics, otlp]
      metrics:
        receivers: [otlp, spanmetrics]
        exporters: [otlp]
      logs:
        exporters: [otlp]
```

---

### Helm Commands

```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
kubectl create namespace otel   # optional
```

**Install:**

```bash
helm install otel-collector open-telemetry/opentelemetry-collector \
  -n otel --values otel-collector-daemonset.yaml
```

**Upgrade:**

```bash
helm upgrade otel-collector open-telemetry/opentelemetry-collector \
  -n otel --values otel-collector-daemonset.yaml
```

📖 **Reference:** SigNoz – Kubernetes Observability

---

## 2️⃣ OpenTelemetry Collector – Deployment (Cluster-level Metrics)

### Prepare Values File: `otel-collector-deployment.yaml`

```yaml
mode: deployment

image:
  repository: otel/opentelemetry-collector-k8s

replicaCount: 1

presets:
  clusterMetrics:
    enabled: true
  kubernetesEvents:
    enabled: true

config:
  exporters:
    otlp:
      endpoint: http://signoz.quegrowth.me:4317
      tls:
        insecure: true

  connectors:
    spanmetrics:

  service:
    pipelines:
      traces:
        exporters: [spanmetrics, otlp]
      metrics:
        receivers: [otlp, spanmetrics]
        exporters: [otlp]
      logs:
        exporters: [otlp]
```

---

### Helm Commands

```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
kubectl create namespace otel   # optional
```

**Install:**

```bash
helm install otel-collector-cluster open-telemetry/opentelemetry-collector \
  -n otel --values otel-collector-deployment.yaml
```

**Upgrade:**

```bash
helm upgrade otel-collector-cluster open-telemetry/opentelemetry-collector \
  -n otel --values otel-collector-deployment.yaml
```

📖 **Reference:** OTel Collector as Deployment

---

## 3️⃣ SigNoz K8s Infra (**Recommended**)

This approach deploys **both a DaemonSet and a Deployment** in a single Helm release, optimized for SigNoz.

### Prepare Values File: `otel-collector-signoz-k8s-infra.yaml`

```yaml
global:
  cloud: aks
  clusterName: fitconnect-dev-cluster
  deploymentEnvironment: deployment

otelCollectorEndpoint: http://signoz.quegrowth.me:4317
otelInsecure: true

presets:
  otlpExporter:
    enabled: true
  hostMetrics:
    enabled: true
    collectionInterval: 30s
  logsCollection:
    enabled: true
  kubeletMetrics:
    enabled: true
  kubernetesAttributes:
    enabled: true
  resourceDetection:
    detectors:
      - azure
      - system
```

---

### Helm Commands

```bash
helm repo add signoz https://charts.signoz.io
helm repo update
kubectl create namespace otel   # optional
```

**Install:**

```bash
helm install otel-collector-k8s-infra signoz/k8s-infra \
  -n otel --values otel-collector-signoz-k8s-infra.yaml
```

**Upgrade:**

```bash
helm upgrade otel-collector-k8s-infra signoz/k8s-infra \
  -n otel --values otel-collector-signoz-k8s-infra.yaml
```

📖 **References:**

- Install K8s Infra Collector
- Configure K8s Infra Collector

---

## 🔍 Comparison of OTel Collector Deployment Methods

| Method                 | Workload Type          | What It Collects                          | Pros                                 | Cons                     | Best Use Case                |
| ---------------------- | ---------------------- | ----------------------------------------- | ------------------------------------ | ------------------------ | ---------------------------- |
| DaemonSet (OTel Helm)  | DaemonSet (per node)   | Pod logs, kubelet metrics, node telemetry | Simple pod-level visibility          | No cluster-wide events   | Pod/node metrics & logs only |
| Deployment (OTel Helm) | Deployment             | Kubernetes events, cluster metrics        | Good cluster-wide insights           | Limited pod/node details | Cluster state & events       |
| SigNoz K8s Infra       | DaemonSet + Deployment | Pod/node + cluster metrics, logs, traces  | Single optimized chart, SigNoz-ready | Tied to SigNoz           | End-to-end K8s observability |

---

## ✅ Summary

- Use **DaemonSet** → Pod/node-level metrics and logs
- Use **Deployment** → Cluster-level events and metrics
- Use **SigNoz K8s Infra** → Combined observability with minimal configuration (recommended)
