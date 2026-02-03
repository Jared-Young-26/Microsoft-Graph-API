# Troubleshooting

## Graph status degraded

Symptoms:
- 5xx responses
- Slow latency
- Output shows "Transient Graph Error 503"

What to check:
- Microsoft service health
- App permissions and consent
- Retry after header (throttling)

## Graph request handler not configured

Meaning:
- The Graph session is not configured with a token provider.

Fix:
1. Set Tenant ID, Client ID, Client Secret in Settings
2. Click **Save config**
3. Click **Reload config**

## PowerShell connection issues

Common causes:
- PowerShell 7 not installed
- Required modules missing
- Permissions or MFA blocking the session

Fix checklist:
- Install PowerShell 7 and modules
- Use System → Health Check to confirm
- Reconnect PowerShell in the sidebar

## Snapshot capture not saving

Common causes:
- Invalid subject identifier
- Storage path permissions
- Snapshot engine not running

Fix:
- Try a core snapshot for admin_host
- Check backend logs for storage errors

## Explain view unavailable

Explain depends on:
- Probe metadata
- Error classification
- Coverage limitations

If missing:
- Confirm probe registry is loaded
- Update the app and reload

## Performance tips

- Use filters before running large reports
- Avoid deep snapshots unless necessary
- Use Table view for large arrays
