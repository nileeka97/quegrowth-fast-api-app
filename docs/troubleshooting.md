### **1. Why might a Valkey cluster in Kubernetes experience split-brain, and how do you prevent it?**

**Possible causes of split-brain:**

- Network partition between Valkey nodes, leading multiple nodes to believe they are the primary.
- Node restarts or pod evictions causing quorum loss in cluster mode.
- Misconfigured cluster topology (e.g., insufficient number of master nodes for consensus).
- Heavy load or slow communication causing heartbeat timeouts.

**Prevention strategies:**

- Use **PodAntiAffinity rules** to ensure nodes are spread across different physical nodes.
- Configure **proper health checks** and `maxmemory-policy` to avoid unintentional failovers under memory pressure.
- Enable **persistent storage** with StatefulSets to preserve data across restarts.
- Monitor cluster state and set alerts for node partition or failover events.

---

### **2. Your worker pods constantly restart. Logs show:**

```
Error: connection refused to queue service
```

**Five possible root causes and diagnostic steps:**

| Root Cause                                      | Diagnostic Steps                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **1. RabbitMQ service not running**             | Run `kubectl get pods -n <namespace>` and `kubectl logs <rabbitmq-pod>` to check service health.              |
| **2. Wrong connection string or credentials**   | Verify secrets in Azure Key Vault, inspect env vars in worker pod (`kubectl describe pod <worker>`).          |
| **3. DNS resolution failure in cluster**        | `kubectl exec <worker> -- nslookup <rabbitmq-service>` or `ping <rabbitmq-service>` to test connectivity.     |
| **4. Network policy blocking traffic**          | Check any `NetworkPolicy` objects restricting pod-to-pod communication. Use `kubectl describe networkpolicy`. |
| **5. RabbitMQ pod is overloaded or restarting** | Inspect `kubectl get events` and `kubectl logs <rabbitmq-pod>` for crashes or memory issues.                  |

---

### **3. A deployment rollout is stuck. `kubectl rollout status` never completes. Step-by-step investigation:**

1. **Check rollout status:**

   ```bash
   kubectl rollout status deployment/<deployment-name>
   ```

2. **Inspect pod events:**

   ```bash
   kubectl get pods -l app=<deployment-name> -o wide
   kubectl describe pod <stuck-pod>
   ```

3. **Check for container errors or crashloops:**

   ```bash
   kubectl logs <stuck-pod>
   ```

4. **Inspect readiness/liveness probes:**

   - Misconfigured probes may prevent pods from becoming ready.

5. **Check node resource availability:**

   ```bash
   kubectl describe node <node-name>
   ```

   - CPU/memory pressure can block pod scheduling.

6. **Check for pending pods:**

   ```bash
   kubectl get pods | grep Pending
   ```

   - May indicate insufficient resources or affinity/taints.

7. **Examine Deployment strategy:**

   - RollingUpdate `maxUnavailable` or `maxSurge` values may slow deployment.

---

### **4. API latency spikes every 5 minutes. Kubernetes and cloud-level reasons:**

- **Kubernetes-level:**

  - Periodic **CronJobs or batch jobs** consuming resources.
  - **Horizontal Pod Autoscaler (HPA) scaling events**, which can cause temporary CPU/memory spikes.
  - **Garbage collection in language runtime** (Python GC) or Valkey cache eviction spikes.

- **Cloud-level:**

  - AKS node **autoscaler adding/removing nodes**, temporarily affecting scheduling or network routing.
  - Azure Load Balancer health probes or DNS TTL refresh causing brief routing latency.
  - Network throttling or transient congestion in cloud virtual networks.

**Diagnostics:**

- Check `kubectl top pod` and `kubectl top node` around spike times.
- Inspect HPA events:

  ```bash
  kubectl get hpa -o yaml
  ```

- Use **OpenTelemetry traces (SigNoz)** to pinpoint latency source per request.

---

### **5. How to design safe rollbacks in a microservice + queue + worker architecture:**

**Principles:**

1. **Versioned deployments:**

   - Use Helm charts with explicit chart and container image versions.

2. **Immutable worker behavior:**

   - Avoid schema changes that break backward compatibility for queued messages.

3. **Queue safety:**

   - Ensure that older worker versions can safely process messages in the queue.
   - Use feature flags if message format changes are introduced.

4. **Blue/Green or Canary deployments:**

   - Route small percentage of traffic to new API version.
   - Monitor queue backlog and worker metrics.

5. **Automated rollback triggers:**

   - Use GitHub Actions or ArgoCD with health checks.
   - Rollback if:

     - Queue backlog spikes.
     - Error rate exceeds threshold.
     - Worker pod restarts increase.

6. **Data compatibility:**

   - If message payloads evolve, workers should handle both old and new formats.

7. **Observability before rollback:**

   - Use OpenTelemetry + SigNoz metrics/traces to verify rollback effectiveness.

---
