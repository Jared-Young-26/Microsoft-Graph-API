# Getting Started (First 10 minutes)

## 1) Connect Graph

1. Go to **System → Settings**.
2. Enter Tenant ID, Client ID, and Client Secret.
3. Click **Save config** and then **Reload config**.
4. Look for **Graph ready** in the session card.

If Graph is not ready, check:
- The app registration has the required permissions.
- Admin consent has been granted.
- The client secret is valid and not expired.

## 2) Connect PowerShell

1. Install PowerShell 7 on the admin host.
2. Install required modules (see System → Health Check).
3. Click **Connect PowerShell** in the sidebar.

Common failure modes:
- Module missing (ExchangeOnlineManagement, Microsoft.Graph, etc.)
- Permissions not granted
- PowerShell not on PATH

## 3) Understand the dashboard

- **Active tenants**: number of configs currently loaded
- **Pending tasks**: running operations
- **Graph success**: overall success ratio from recent requests

The **Output** panel shows the latest response. Use Raw/Pretty/Table/Explain to interpret results.

## 4) Run your first action

Example: Entra → List users

1. Navigate to **Explore → Entra**.
2. Choose **List users**.
3. Click **Run**.
4. Use **Pretty** or **Table** view to explore results.

> [!TIP]
> If results are empty, confirm the Graph app has `User.Read.All` and that your tenant ID is correct.
