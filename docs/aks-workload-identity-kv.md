## Grant Access to Managed Identity – AKS Workload Identity

## Prerequisites

- AKS cluster with **Workload Identity** enabled
- Azure Managed Identity created
- Azure Key Vault Secrets Provider add-on available

---

## Enable Secret Store CSI Driver

Enable the **Azure Key Vault Secrets Provider (Secret Store CSI Driver)** from the AKS console or via Azure CLI.

---

## Create Kubernetes ServiceAccount

Create a ServiceAccount in the `quegrowth-dev` namespace and annotate it with the Azure Managed Identity **client ID**:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: workload-identity-sa
  namespace: quegrowth-dev
  annotations:
    azure.workload.identity/client-id: <ClientID of your workload identity>
EOF
```

---

## Create Federated Identity Credential

Bind the Kubernetes ServiceAccount with the Azure Managed Identity by creating a federated identity credential:

```bash
az identity federated-credential create \
  --name aks-federated-identity \
  --identity-name azurekeyvaultsecretsprovider-quegrowth-dev-cluster \
  --resource-group quegrowth-dev-rg \
  --issuer <issuer-url> \
  --subject system:serviceaccount:quegrowth-dev:workload-identity-sa
```

### Parameters

- `--issuer` → OIDC issuer URL of your AKS cluster
- `--subject` → Must match the ServiceAccount in the format:

  ```
  system:serviceaccount:<namespace>:<serviceaccount-name>
  ```

---

## Update AKS Add-on (Key Vault Secrets Provider)

Enable secret rotation for the Azure Key Vault Secrets Provider add-on:

```bash
az aks addon update \
  --addon azure-keyvault-secrets-provider \
  --name quegrowth-dev-cluster \
  --resource-group quegrowth-dev-rg \
  --enable-secret-rotation
```

### Optional: Configure Rotation Poll Interval

```bash
az aks addon update \
  --resource-group quegrowth-dev-rg \
  --name quegrowth-dev-cluster \
  --addon azure-keyvault-secrets-provider \
  --enable-secret-rotation \
  --rotation-poll-interval 10m
```

---

## Notes

- Pods running in the `quegrowth-dev` namespace that use the `workload-identity-sa` ServiceAccount can authenticate with Azure Key Vault using **Managed Identity**.
- No secrets are stored in Kubernetes; authentication is handled via **AKS Workload Identity** and **OIDC federation**.
- Ensure the Managed Identity has appropriate access policies or RBAC permissions on the Azure Key Vault.
