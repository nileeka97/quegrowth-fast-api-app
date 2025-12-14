# Kubernetes Deployment Documentation – Quegrowth Dev

## Overview

The following components are deployed in the **Quegrowth Dev** Kubernetes environment:

- **NGINX Ingress Controller**
- **AKS Workload Identity**

---

## Namespace

All deployments are created under the following namespace:

```text
quegrowth-dev
```

---

## Helm Deployments

Helm is used for package management. Each service has its own Helm release name.

---

### api

**Install:**

```bash
helm install quegrowth-api-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

**Upgrade:**

```bash
helm upgrade quegrowth-api-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

---

### Worker

**Install:**

```bash
helm install quegrowth-worker-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

**Upgrade:**

```bash
helm upgrade quegrowth-worker-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

---

### Redis

**Install:**

```bash
helm install quegrowth-redis-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

**Upgrade:**

```bash
helm upgrade quegrowth-redis-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

---

### RabbitMQ

**Install:**

```bash
helm install quegrowth-rabbitmq-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

**Upgrade:**

```bash
helm upgrade quegrowth-rabbitmq-dev . \
  --namespace quegrowth-dev \
  --values values-dev.yaml
```

---

## Deployment Notes

- All services use `values-dev.yaml` for environment-specific configuration
- Helm release names follow the convention:

  ```text
  quegrowth-<service>-dev
  ```

- Use `helm upgrade` after modifying Helm templates or `values-dev.yaml`
- Check release status:

  ```bash
  helm status <release-name>
  ```

- Check running pods:

  ```bash
  kubectl get pods -n quegrowth-dev
  ```
