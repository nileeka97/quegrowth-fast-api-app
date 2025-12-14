## Ingress NGINX Deployment on Kubernetes (Azure)

### Add the Ingress NGINX Helm repository

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
```

### Update the Helm repository

```bash
helm repo update
```

### Install ingress-nginx with Azure Load Balancer settings

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --create-namespace \
  --namespace ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --set controller.service.externalTrafficPolicy=Local
```

### Upgrade ingress-nginx

```bash
helm upgrade ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --set controller.service.externalTrafficPolicy=Local
```

## Notes

- **Namespace:** `ingress-nginx`
- The Azure Load Balancer health probe is configured to use the path `/healthz`.
- `externalTrafficPolicy` is set to `Local` to preserve the source IP.
