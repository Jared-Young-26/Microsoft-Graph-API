# Modules & Tools

Each module has a dedicated page in the left nav. The badges indicate how each module executes.

## Exchange

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- List mail folders and messages
- Shared mailbox sent items
- Delegate permissions

Where to find IDs:
- User ID / UPN from Entra user profile
- Shared mailbox UPN from Exchange admin center

## OneDrive

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- Resolve user drive ID
- List drive items
- Provision personal site

Where to find IDs:
- Use UPN or Object ID for the user
- Drive ID can be discovered via "Get user drive ID"

## SharePoint

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- List sites
- Create lists
- Update site permissions

Where to find IDs:
- Site ID from SharePoint Admin Center or Graph site search
- List ID from site lists panel

## Teams

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- List teams and channels
- Create channels

Where to find IDs:
- Team ID from Teams admin center or Graph

## Entra

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- Manage users and groups
- Assign roles and licenses
- Audit sign-ins

Where to find IDs:
- User UPN or Object ID
- Group ID from Entra admin center

## Azure

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- List subscriptions and VMs
- Inspect resource groups

Where to find IDs:
- Subscription ID from Azure portal

## Defender for Cloud

<Badge kind="graph" />

Placeholder module: add integrations as Defender APIs are configured.

## Power Platform

<Badge kind="graph" />

Placeholder module: use for environments, DLP, and governance when configured.

## Local AD

<Badge kind="powershell" />

Common tasks:
- Create users and groups
- Reset passwords / unlock accounts
- Move users to OUs

Where to find IDs:
- OU DN from Active Directory Users and Computers
- Group DN from AD group properties

## Endpoints

<Badge kind="powershell" />

Common tasks:
- System inventory
- Event log query
- Service/process checks

## Domain Controller

<Badge kind="powershell" />

Common tasks:
- Replication health
- FSMO role discovery
- Time sync validation

Where to find IDs:
- DC hostname or FQDN

## Printers

<Badge kind="powershell" />

Common tasks:
- Printer inventory
- GPO mapping
- Queue health

## Network

<Badge kind="powershell" />

Common tasks:
- DNS resolve
- Ping/port checks
- Interface and route snapshots

## SSH

<Badge kind="ssh" />

Common tasks:
- Remote shell for non-Windows devices
- Ad-hoc troubleshooting

## File Server

<Badge kind="powershell" />

Common tasks:
- SMB session checks
- Share enumeration

## Network Topology

<Badge kind="local" />

Common tasks:
- Build device graphs
- Ping targets
- Export correlation report

## Event Logs

<Badge kind="powershell" />

Common tasks:
- Event log summaries
- EVTX import/export

## Registry

<Badge kind="powershell" />

Common tasks:
- Watchlist snapshots
- Registry export
- Diff registry changes

## Time & Drift

<Badge kind="powershell" />

Common tasks:
- Local time status
- DC offset monitoring
- NTP drift trends

## Certificates

<Badge kind="local" />

Common tasks:
- Local machine certificate inventory
- TLS validation checks

## Processes

<Badge kind="local" />

Common tasks:
- Process inventory
- Service → process mapping

## Reports

<Badge kind="graph" /> <Badge kind="powershell" />

Common tasks:
- User audit
- GPO audit
- Sign-in summaries
