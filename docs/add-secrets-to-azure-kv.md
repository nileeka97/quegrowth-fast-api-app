## 🔑 Azure Key Vault & Helm SecretProviderClass Setup

This guide explains how to add secrets to **Azure Key Vault** and configure them in a **Helm SecretProviderClass** for Kubernetes.

---

## 1️⃣ Add Secret to Azure Key Vault

1. Navigate to **Azure Portal → Key Vaults**
2. Select the required Key Vault (example: `fitconnect-web-prod-kv`)
3. In the left sidebar, go to **Objects → Secrets**
4. Click **Generate/Import**
5. Add the secret:

   - **Secret name:** Use hyphens (`-`), e.g. `DATABASE-URL`
   - **Secret value:** Enter the corresponding secret value

6. Click **Create** ✅

> ⏱️ **Note:** After adding a secret, wait approximately **10 minutes** for the Azure Key Vault secret rotation cronjob to sync the secret.

---

## 2️⃣ Clone Backend Repository

Clone the backend repository:

```bash
git clone <repository-url>
```

Navigate to the Helm templates directory:

```bash
cd infra/helm/api/templates
```

Open the relevant `SecretProviderClass` file, for example:

```text
api-secretproviderclass.yaml
```

---

## 3️⃣ Update SecretProviderClass YAML

You must reference your Key Vault secret in **two places** within the `SecretProviderClass`.

---

### a️⃣ `spec.secretObjects.data`

Add your secret mapping as follows:

```yaml
- objectName: DATABASE-URL # Azure Key Vault secret name (hyphens)
  key: DATABASE_URL # Kubernetes secret key (underscores)
```

💡 **Tip:**

- `objectName` must exactly match the Azure Key Vault secret name
- `key` is the Kubernetes secret key consumed by the application

---

### b️⃣ `spec.parameters.objects` Array

Add the secret reference inside the `objects` array:

```yaml
- |
  objectName: DATABASE-URL
  objectType: secret
```

This instructs the CSI driver which Azure Key Vault object to pull into Kubernetes.

---

## ✅ Summary

| Step                        | Description                                               |
| --------------------------- | --------------------------------------------------------- |
| Add Secret                  | Azure Key Vault → Objects → Secrets → Generate/Import     |
| Secret Naming               | Key Vault: `-` (hyphen), Kubernetes key: `_` (underscore) |
| SecretProviderClass Updates | `spec.secretObjects.data` and `spec.parameters.objects`   |
| Sync Time                   | Wait ~10 minutes for Azure Key Vault rotation cronjob     |

---

## 💡 Notes

- Ensure secret names in **Azure Key Vault** and **SecretProviderClass** match exactly
- For multiple secrets, repeat the same steps under `data` and `parameters.objects`
- After deployment, Kubernetes pods can access secrets via:

  - Environment variables, or
  - Mounted volumes (via CSI driver)
