# Overview

Graph Admin Studio is a local control plane for Microsoft 365 and on-prem operations. It is designed to make troubleshooting and admin tasks **repeatable**, **auditable**, and **fast**.

## Design philosophy

- **Graph-first, PowerShell fallback.** Prefer Graph APIs for speed and consistency. When Graph cannot do the job, fall back to PowerShell.
- **Local control plane.** Your data and credentials stay on the admin host, not a cloud service.
- **Operator clarity.** Outputs are structured first, human-friendly second (Pretty, Table, Explain).

## Safety model

Use risk labels and dry-run where available:

- <RiskBadge level="safe" /> Read-only or low impact
- <RiskBadge level="caution" /> Writes or moderate risk
- <RiskBadge level="dangerous" /> High impact or irreversible

## What “Local Control Plane” means

All data collection and actions run from the machine hosting the portal:

- <Badge kind="graph" /> Graph API calls from your app registration
- <Badge kind="powershell" /> PowerShell modules run locally
- <Badge kind="local" /> On-box discovery and diagnostics
- <Badge kind="ssh" /> Remote sessions when explicitly used

> [!NOTE]
> The portal does not store secrets in snapshots or exports by design. Sensitive values are redacted when possible.
