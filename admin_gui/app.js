const navLinks = document.querySelectorAll(".nav-link");
const navGroupToggles = document.querySelectorAll(".nav-group-toggle");
const panels = document.querySelectorAll("[data-panel]");
const pageTitle = document.getElementById("page-title");
const pageSubtitle = document.getElementById("page-subtitle");
const toast = document.getElementById("toast");
const navToggle = document.getElementById("nav-toggle");
const sidebar = document.getElementById("sidebar");
const statusBadge = document.getElementById("status-badge");
const warningBanner = document.getElementById("warning-banner");
const warningMessage = document.getElementById("warning-message");
const warningMeta = document.getElementById("warning-meta");
const warningDismiss = document.getElementById("warning-dismiss");
const graphStatusBanner = document.getElementById("graph-status-banner");
const graphStatusMessage = document.getElementById("graph-status-message");
const graphStatusMeta = document.getElementById("graph-status-meta");
const graphStatusDismiss = document.getElementById("graph-status-dismiss");
const cfgTenantId = document.getElementById("cfg-tenant-id");
const cfgClientId = document.getElementById("cfg-client-id");
const cfgClientSecret = document.getElementById("cfg-client-secret");
const cfgGraphUserId = document.getElementById("cfg-graph-user-id");
const cfgOnedriveDriveId = document.getElementById("cfg-onedrive-drive-id");
const cfgSpoAdminUrl = document.getElementById("cfg-spo-admin-url");
const cfgPsAuthMode = document.getElementById("cfg-ps-auth-mode");
const cfgPsUpn = document.getElementById("cfg-ps-upn");
const cfgPsOrg = document.getElementById("cfg-ps-org");
const cfgAzureTenantId = document.getElementById("cfg-azure-tenant-id");
const cfgAzureSubscriptionId = document.getElementById("cfg-azure-subscription-id");
const cfgUseKeychain = document.getElementById("cfg-use-keychain");
const cfgLock = document.getElementById("cfg-lock");
const cfgKeychainStatus = document.getElementById("cfg-keychain-status");
const cfgLockNote = document.getElementById("cfg-lock-note");
const tenantName = document.getElementById("tenant-name");
const tenantIdField = document.getElementById("tenant-id");
const tenantDomains = document.getElementById("tenant-domains");
const refreshTenantInfoButton = document.getElementById("refresh-tenant-info");
const saveConfigButton = document.getElementById("save-config");
const reloadConfigButton = document.getElementById("reload-config");
const metricTenants = document.getElementById("metric-tenants");
const metricTasks = document.getElementById("metric-tasks");
const metricSuccess = document.getElementById("metric-success");
const quickActionsCard = document.getElementById("quick-actions-card");
const quickActionsGrid = document.getElementById("quick-actions");
const quickActionsEditor = document.getElementById("quick-actions-editor");
const quickActionsEditButton = document.getElementById("edit-quick-actions");
const quickActionServiceSelect = document.getElementById("qa-service");
const quickActionActionSelect = document.getElementById("qa-action");
const quickActionAddButton = document.getElementById("qa-add");
const quickActionResetButton = document.getElementById("qa-reset");
const quickActionTemplateSelect = document.getElementById("qa-template");
const quickActionAddTemplateButton = document.getElementById("qa-add-template");
const activityPageSizeSelect = document.getElementById("activity-page-size");
const activityPrevButton = document.getElementById("activity-prev");
const activityNextButton = document.getElementById("activity-next");
const activityPageInfo = document.getElementById("activity-page-info");
const profileSelect = document.getElementById("profile-select");
const profileNameInput = document.getElementById("profile-name");
const profileSaveButton = document.getElementById("profile-save");
const profileApplyButton = document.getElementById("profile-apply");
const profileDeleteButton = document.getElementById("profile-delete");
const profileExportButton = document.getElementById("profile-export");
const profileImportButton = document.getElementById("profile-import");
const profileImportFile = document.getElementById("profile-import-file");
const healthCheckButton = document.getElementById("run-health-check");
const healthStatusText = document.getElementById("health-status-text");
const healthSpinner = document.getElementById("health-spinner");
const healthProgress = document.getElementById("health-progress");
const exportActionPacksButton = document.getElementById("export-action-packs");
const importActionPacksButton = document.getElementById("import-action-packs");
const actionPackImportFile = document.getElementById("action-pack-import-file");
const exportTemplatesButton = document.getElementById("export-templates");
const importTemplatesButton = document.getElementById("import-templates");
const templateImportFile = document.getElementById("template-import-file");
const packNameInput = document.getElementById("pack-name");
const packDescriptionInput = document.getElementById("pack-description");
const packDefaultsInput = document.getElementById("pack-defaults");
const packStepServiceSelect = document.getElementById("pack-step-service");
const packStepActionSelect = document.getElementById("pack-step-action");
const packStepLabelInput = document.getElementById("pack-step-label");
const packStepOptionalInput = document.getElementById("pack-step-optional");
const packAddStepButton = document.getElementById("pack-add-step");
const packNewButton = document.getElementById("pack-new");
const packDeleteButton = document.getElementById("pack-delete");
const packSaveButton = document.getElementById("pack-save");
const packStepList = document.getElementById("pack-step-list");
const reportsExportDatasetSelect = document.getElementById("reports-export-dataset");
const exportReportsAllButton = document.getElementById("export-reports-all");
const actionPackPrevButton = document.getElementById("action-pack-prev");
const actionPackNextButton = document.getElementById("action-pack-next");
const actionPackPageInfo = document.getElementById("action-pack-page-info");
const presetNameInput = document.getElementById("preset-name");
const presetDescriptionInput = document.getElementById("preset-description");
const presetStepServiceSelect = document.getElementById("preset-step-service");
const presetStepActionSelect = document.getElementById("preset-step-action");
const presetStepLabelInput = document.getElementById("preset-step-label");
const presetAddStepButton = document.getElementById("preset-add-step");
const presetNewButton = document.getElementById("preset-new");
const presetDeleteButton = document.getElementById("preset-delete");
const presetSaveButton = document.getElementById("preset-save");
const presetStepList = document.getElementById("preset-step-list");
const datasetMeta = document.getElementById("dataset-meta");
const datasetContent = document.getElementById("dataset-content");
const reportPresetsList = document.getElementById("report-presets-list");
const healthBreakdown = document.getElementById("health-breakdown");
const healthGraphList = document.getElementById("health-graph-list");
const healthPowerShellList = document.getElementById("health-powershell-list");
const actionPackFilterSelect = document.getElementById("action-pack-filter");
const actionPackRunnerTitle = document.getElementById("action-pack-runner-title");
const actionPackRunnerSteps = document.getElementById("action-pack-runner-steps");
const actionPackRunButton = document.getElementById("action-pack-run");
const actionPackRunCancelButton = document.getElementById("action-pack-run-cancel");
const packScopeSelect = document.getElementById("pack-scope");
const actionPackHistoryList = document.getElementById("action-pack-history-list");
const actionPackHistoryClear = document.getElementById("action-pack-history-clear");
const exportReportPresetsButton = document.getElementById("export-report-presets");
const importReportPresetsButton = document.getElementById("import-report-presets");
const reportPresetsImportFile = document.getElementById("report-presets-import-file");
const reportQueueList = document.getElementById("report-queue-list");
const reportQueueStopButton = document.getElementById("report-queue-stop");
const reportQueueClearButton = document.getElementById("report-queue-clear");
const reportHistoryList = document.getElementById("report-history-list");
const reportHistoryClear = document.getElementById("report-history-clear");
const reportDiffSelectA = document.getElementById("report-diff-a");
const reportDiffSelectB = document.getElementById("report-diff-b");
const reportDiffRunButton = document.getElementById("report-diff-run");
const reportDiffMeta = document.getElementById("report-diff-meta");
const reportDiffOutput = document.getElementById("report-diff-output");
const sshHostInput = document.getElementById("ssh-host");
const sshUserInput = document.getElementById("ssh-user");
const sshPortInput = document.getElementById("ssh-port");
const sshKeyPathInput = document.getElementById("ssh-key-path");
const sshStrictHostInput = document.getElementById("ssh-strict-host");
const sshWsUrlInput = document.getElementById("ssh-ws-url");
const sshConnectButton = document.getElementById("ssh-connect");
const sshDisconnectButton = document.getElementById("ssh-disconnect");
const sshTerminalOutput = document.getElementById("ssh-terminal-output");
const sshTerminalInput = document.getElementById("ssh-terminal-input");
const sshSendButton = document.getElementById("ssh-send");
const sshInterruptButton = document.getElementById("ssh-interrupt");
const outputSearchQueries = {};
const lastOutputs = {};
const outputTimers = new Map();
const outputStartTimes = new Map();
const outputStatusPrefixes = new Map();

const subtitles = {
  dashboard: "Graph-first operations with PowerShell fallback",
  exchange: "Mail, calendars, and shared mailbox controls",
  onedrive: "Drive operations, permissions, and sync",
  sharepoint: "Sites, lists, and pages management",
  teams: "Teams, channels, and messaging",
  entra: "Directory, groups, and app inventory",
  azure: "Subscription and infrastructure inventory",
  defender: "Defender for Cloud",
  powerplatform: "Power Platform admin",
  localad: "Local Active Directory (on-prem)",
  printers: "On-prem print servers and GPO checks",
  network: "On-prem network adapters and IP settings",
  ssh: "Remote workstation sessions over SSH",
  fileserver: "On-prem file share enumeration",
  reports: "Audit-ready reports and summaries",
  purview: "Compliance and data governance",
  settings: "Local session and credentials",
};

const serviceLabels = {
  onedrive: "OneDrive",
  sharepoint: "SharePoint",
  powerplatform: "Power Platform",
  localad: "Local AD",
  printers: "Printers",
  network: "Network",
  ssh: "SSH",
  fileserver: "File Server",
  defender: "Defender for Cloud",
};

const ACTIONS_UI = {
  exchange: {
    list_mail_folders: {
      label: "List mail folders",
      mode: "graph",
      fields: [
        { key: "user_id", label: "User ID / UPN" },
        { key: "include_hidden", label: "Include hidden folders", type: "checkbox" },
        { key: "top", label: "Top", type: "number", placeholder: "100" },
      ],
    },
    list_messages: {
      label: "List messages",
      mode: "graph",
      fields: [
        { key: "user_id", label: "User ID / UPN" },
        { key: "top", label: "Top", type: "number", placeholder: "10" },
        { key: "order_by", label: "Order by", placeholder: "receivedDateTime desc" },
      ],
    },
    list_events: {
      label: "List events",
      mode: "graph",
      fields: [
        { key: "user_id", label: "User ID / UPN" },
        { key: "top", label: "Top", type: "number", placeholder: "10" },
        { key: "start_iso", label: "Start ISO" },
        { key: "end_iso", label: "End ISO" },
      ],
    },
    enable_shared_sent_items: {
      label: "Enable shared sent items",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "execute", label: "Execute now", type: "checkbox", defaultChecked: true },
      ],
    },
  },
  onedrive: {
    list_drive_items: {
      label: "List drive items",
      mode: "graph",
      fields: [{ key: "folder_id", label: "Folder ID (optional)" }],
    },
    get_user_drive_id: {
      label: "Get user drive ID",
      mode: "graph",
      fields: [{ key: "user_id", label: "User UPN or ID (optional)" }],
    },
    create_upload_session: {
      label: "Create upload session",
      mode: "graph",
      fields: [
        { key: "item_path", label: "Item path (Reports/file.csv)" },
        { key: "parent_folder_id", label: "Parent folder ID (optional)" },
        { key: "conflict_behavior", label: "Conflict behavior", placeholder: "replace" },
      ],
    },
    list_personal_sites: {
      label: "List personal sites",
      mode: "powershell",
      fields: [
        { key: "limit", label: "Limit", placeholder: "All" },
        { key: "filter_query", label: "Filter query" },
      ],
    },
  },
  sharepoint: {
    list_sites: {
      label: "List sites",
      mode: "graph",
      fields: [{ key: "search", label: "Search", placeholder: "*" }],
    },
    create_list: {
      label: "Create list",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "display_name", label: "List name" },
        { key: "template", label: "Template", placeholder: "genericList" },
        { key: "description", label: "Description" },
      ],
    },
    list_list_items: {
      label: "List list items",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "list_id", label: "List ID" },
        { key: "top", label: "Top", type: "number", placeholder: "100" },
      ],
    },
    list_sites_admin: {
      label: "List sites (admin)",
      mode: "powershell",
      fields: [
        { key: "filter_query", label: "Filter query" },
        { key: "include_personal", label: "Include personal", type: "checkbox" },
        { key: "limit", label: "Limit", placeholder: "All" },
      ],
    },
  },
  teams: {
    list_joined_teams: { label: "List joined teams", mode: "graph", fields: [] },
    create_channel: {
      label: "Create channel",
      mode: "graph",
      fields: [
        { key: "team_id", label: "Team ID" },
        { key: "display_name", label: "Channel name" },
        { key: "description", label: "Description" },
        { key: "membership_type", label: "Membership type", placeholder: "standard" },
      ],
    },
    list_chat_messages: {
      label: "List chat messages",
      mode: "graph",
      fields: [
        { key: "chat_id", label: "Chat ID" },
        { key: "top", label: "Top", type: "number", placeholder: "20" },
      ],
    },
    list_teams_admin: { label: "List teams (admin)", mode: "powershell", fields: [] },
  },
  entra: {
    list_users: {
      label: "List users",
      mode: "graph",
      fields: [
        { key: "top", label: "Top", type: "number", placeholder: "10" },
        { key: "select", label: "Select fields (comma-separated)" },
      ],
    },
    create_user: {
      label: "Create user",
      mode: "graph",
      fields: [
        { key: "user_principal_name", label: "UserPrincipalName" },
        { key: "display_name", label: "Display name" },
        { key: "password", label: "Temporary password" },
        { key: "account_enabled", label: "Account enabled", type: "checkbox", defaultChecked: true },
      ],
    },
    add_group_member: {
      label: "Add group member",
      mode: "graph",
      fields: [
        { key: "group_id", label: "Group ID" },
        { key: "user_id", label: "User ID" },
      ],
    },
    list_service_principals: {
      label: "List service principals",
      mode: "graph",
      fields: [{ key: "top", label: "Top", type: "number", placeholder: "10" }],
    },
    set_user_license: {
      label: "Set user license",
      mode: "powershell",
      fields: [
        { key: "user_id", label: "User ID" },
        { key: "add_sku_ids", label: "Add SKU IDs (comma-separated)" },
        { key: "remove_sku_ids", label: "Remove SKU IDs (comma-separated)" },
      ],
    },
  },
  azure: {
    list_subscriptions: { label: "List subscriptions", mode: "powershell", fields: [] },
    list_resource_groups: { label: "List resource groups", mode: "powershell", fields: [] },
    list_virtual_machines: {
      label: "List virtual machines",
      mode: "powershell",
      fields: [
        { key: "resource_group", label: "Resource group (optional)" },
        { key: "status", label: "Include status", type: "checkbox" },
      ],
    },
    list_key_vaults: {
      label: "List Key Vaults",
      mode: "powershell",
      fields: [{ key: "resource_group", label: "Resource group (optional)" }],
    },
  },
  defender: {},
  powerplatform: {},
  reports: {
    user_audit: {
      label: "User audit report",
      mode: "graph",
      preflightService: "entra",
      fields: [
        { key: "user_id", label: "User UPN or ID (optional)" },
        { key: "include_groups", label: "Include group membership", type: "checkbox", defaultChecked: true },
        { key: "include_licenses", label: "Include license details", type: "checkbox", defaultChecked: true },
        { key: "include_signins", label: "Include sign-in logs", type: "checkbox" },
        { key: "include_devices", label: "Include device inventory", type: "checkbox" },
        { key: "include_mailbox_stats", label: "Include mailbox stats", type: "checkbox" },
      ],
    },
    gpo_audit: {
      label: "GPO audit report",
      mode: "powershell",
      preflightService: "localad",
      fields: [{ key: "name", label: "GPO name (optional)" }],
    },
    gpo_link_audit: {
      label: "GPO link audit by OU",
      mode: "powershell",
      preflightService: "localad",
      fields: [{ key: "ou_dn", label: "OU distinguished name" }],
    },
  },
  localad: {
    list_users: {
      label: "List AD users",
      mode: "powershell",
      fields: [{ key: "name", label: "Name filter (optional)" }],
    },
    create_user: {
      label: "Create AD user",
      mode: "powershell",
      fields: [
        { key: "name", label: "Display name" },
        { key: "sam_account_name", label: "sAMAccountName" },
        { key: "user_principal_name", label: "UserPrincipalName" },
        { key: "password", label: "Temporary password" },
        { key: "ou_dn", label: "OU DN (optional)" },
        { key: "enabled", label: "Enabled", type: "checkbox", defaultChecked: true },
      ],
    },
    reset_password: {
      label: "Reset password",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "user_dn", label: "User DN" },
        { key: "password", label: "New password" },
        { key: "unlock", label: "Unlock account", type: "checkbox" },
      ],
    },
    unlock_account: {
      label: "Unlock account",
      mode: "powershell",
      fields: [{ key: "user_dn", label: "User DN" }],
    },
    enable_account: {
      label: "Enable account",
      mode: "powershell",
      fields: [{ key: "user_dn", label: "User DN" }],
    },
    disable_account: {
      label: "Disable account",
      mode: "powershell",
      confirm: true,
      fields: [{ key: "user_dn", label: "User DN" }],
    },
    list_groups: {
      label: "List AD groups",
      mode: "powershell",
      fields: [{ key: "name", label: "Name filter (optional)" }],
    },
    create_group: {
      label: "Create AD group",
      mode: "powershell",
      fields: [
        { key: "name", label: "Group name" },
        { key: "sam_account_name", label: "sAMAccountName (optional)" },
        { key: "ou_dn", label: "OU DN (optional)" },
        { key: "scope", label: "Scope", placeholder: "Global" },
        { key: "category", label: "Category", placeholder: "Security" },
      ],
    },
    add_group_member: {
      label: "Add group member",
      mode: "powershell",
      fields: [
        { key: "group_dn", label: "Group DN" },
        { key: "member_dn", label: "Member DN" },
      ],
    },
    remove_group_member: {
      label: "Remove group member",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "group_dn", label: "Group DN" },
        { key: "member_dn", label: "Member DN" },
      ],
    },
    move_user_to_ou: {
      label: "Move user to OU",
      mode: "powershell",
      fields: [
        { key: "user_dn", label: "User DN" },
        { key: "ou_dn", label: "Target OU DN" },
      ],
    },
    list_ous: {
      label: "List OUs",
      mode: "powershell",
      fields: [{ key: "name", label: "Name filter (optional)" }],
    },
    list_gpos: {
      label: "List GPOs",
      mode: "powershell",
      fields: [{ key: "name", label: "Name (optional)" }],
    },
    link_gpo: {
      label: "Link GPO to OU",
      mode: "powershell",
      fields: [
        { key: "gpo_name", label: "GPO name" },
        { key: "ou_dn", label: "OU DN" },
        { key: "enforced", label: "Enforced", type: "checkbox" },
      ],
    },
    unlink_gpo: {
      label: "Unlink GPO from OU",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "gpo_name", label: "GPO name" },
        { key: "ou_dn", label: "OU DN" },
      ],
    },
    backup_gpo: {
      label: "Backup GPO",
      mode: "powershell",
      fields: [
        { key: "gpo_name", label: "GPO name" },
        { key: "path", label: "Backup path" },
        { key: "comment", label: "Comment (optional)" },
      ],
    },
    restore_gpo: {
      label: "Restore GPO",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "gpo_name", label: "GPO name" },
        { key: "path", label: "Backup path" },
      ],
    },
  },
  printers: {
    list_printers: {
      label: "List printers",
      mode: "powershell",
      fields: [
        { key: "name", label: "Name filter (optional)" },
        { key: "include_configuration", label: "Include configuration", type: "checkbox" },
      ],
    },
    list_gpo_printer_mappings: {
      label: "List GPO printer mappings",
      mode: "powershell",
      fields: [
        { key: "name", label: "GPO name filter (optional)" },
        { key: "include_empty", label: "Include empty GPOs", type: "checkbox" },
      ],
    },
    cross_reference_printers_gpo: {
      label: "Cross-reference printers vs GPOs",
      mode: "powershell",
      fields: [
        { key: "name", label: "Printer name filter (optional)" },
        {
          key: "include_unmapped",
          label: "Include printers without GPO",
          type: "checkbox",
          defaultChecked: true,
          sendFalse: true,
        },
      ],
    },
  },
  network: {
    list_adapters: {
      label: "List adapters",
      mode: "powershell",
      fields: [
        { key: "name", label: "Adapter name filter (optional)" },
        { key: "include_hidden", label: "Include hidden adapters", type: "checkbox" },
      ],
    },
    get_adapter_config: {
      label: "Get adapter config",
      mode: "powershell",
      fields: [{ key: "name", label: "Adapter name" }],
    },
    enable_adapter: {
      label: "Enable adapter",
      mode: "powershell",
      confirm: true,
      fields: [{ key: "name", label: "Adapter name" }],
    },
    disable_adapter: {
      label: "Disable adapter",
      mode: "powershell",
      confirm: true,
      fields: [{ key: "name", label: "Adapter name" }],
    },
    rename_adapter: {
      label: "Rename adapter",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Current name" },
        { key: "new_name", label: "New name" },
      ],
    },
    set_dhcp: {
      label: "Set DHCP",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Adapter name" },
        { key: "enabled", label: "Enable DHCP", type: "checkbox", defaultChecked: true, sendFalse: true },
      ],
    },
    set_static_ipv4: {
      label: "Set static IPv4",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Adapter name" },
        { key: "ip_address", label: "IPv4 address" },
        { key: "prefix_length", label: "Prefix length", type: "number", placeholder: "24" },
        { key: "gateway", label: "Default gateway (optional)" },
        { key: "dns_servers", label: "DNS servers (comma-separated)", placeholder: "1.1.1.1, 8.8.8.8" },
        { key: "remove_existing", label: "Remove existing IPv4s", type: "checkbox" },
      ],
    },
    set_dns_servers: {
      label: "Set DNS servers",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Adapter name" },
        { key: "servers", label: "DNS servers (comma-separated)" },
        { key: "reset", label: "Reset to DHCP DNS", type: "checkbox" },
      ],
    },
    set_interface_metric: {
      label: "Set interface metric",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Adapter name" },
        { key: "metric", label: "Metric", type: "number", placeholder: "10" },
        { key: "address_family", label: "Address family", placeholder: "IPv4" },
      ],
    },
    set_mtu: {
      label: "Set MTU",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "name", label: "Adapter name" },
        { key: "mtu", label: "MTU", type: "number", placeholder: "1500" },
        { key: "address_family", label: "Address family", placeholder: "IPv4" },
      ],
    },
    ping_host: {
      label: "Ping host",
      mode: "powershell",
      fields: [
        { key: "host", label: "Host or IP" },
        { key: "count", label: "Count", type: "number", placeholder: "4" },
        { key: "timeout_seconds", label: "Timeout (seconds)", type: "number", placeholder: "2" },
        { key: "ipv6", label: "Use IPv6", type: "checkbox" },
      ],
    },
  },
  ssh: {
    run_command: {
      label: "Run SSH command",
      mode: "ssh",
      fields: [
        { key: "host", label: "Host" },
        { key: "user", label: "User (optional)" },
        { key: "port", label: "Port", type: "number", placeholder: "22" },
        { key: "command", label: "Command" },
        { key: "key_path", label: "Key path (optional)" },
        {
          key: "strict_host_key",
          label: "Strict host key checking",
          type: "checkbox",
          defaultChecked: true,
          sendFalse: true,
        },
        { key: "timeout", label: "Timeout (seconds)", type: "number", placeholder: "60" },
      ],
    },
  },
  fileserver: {
    list_files: {
      label: "List files in share",
      mode: "powershell",
      fields: [
        { key: "unc_path", label: "UNC path (\\\\server\\\\share)" },
        { key: "username", label: "Username (optional)" },
        { key: "password", label: "Password (optional)", type: "password" },
        { key: "recurse", label: "Recurse folders", type: "checkbox", defaultChecked: true, sendFalse: true },
        { key: "include_directories", label: "Include directories", type: "checkbox" },
        { key: "include_hidden", label: "Include hidden", type: "checkbox" },
        { key: "max_items", label: "Max items (optional)", type: "number", placeholder: "10000" },
      ],
    },
  },
  purview: {
    list_retention_policies: { label: "List retention policies", mode: "powershell", fields: [] },
    create_compliance_search: {
      label: "Create compliance search",
      mode: "powershell",
      fields: [
        { key: "name", label: "Search name" },
        { key: "exchange_locations", label: "Exchange locations (comma-separated)" },
        { key: "sharepoint_locations", label: "SharePoint locations (comma-separated)" },
        { key: "content_match_query", label: "Content match query" },
      ],
    },
    list_dlp_policies: { label: "List DLP policies", mode: "powershell", fields: [] },
    list_compliance_actions: {
      label: "List compliance actions",
      mode: "powershell",
      fields: [{ key: "search_name", label: "Search name (optional)" }],
    },
  },
};

const DEFAULT_QUICK_ACTIONS = [
  { type: "action", service: "exchange", action: "enable_shared_sent_items" },
  { type: "action", service: "purview", action: "create_compliance_search" },
  { type: "action", service: "exchange", action: "list_messages" },
  { type: "action", service: "onedrive", action: "list_drive_items" },
  { type: "action", service: "teams", action: "create_channel" },
  { type: "action", service: "azure", action: "list_virtual_machines" },
  { type: "action", service: "purview", action: "list_dlp_policies" },
  { type: "action", service: "azure", action: "list_key_vaults" },
];

const PROFILE_STORAGE_KEY = "configProfiles";
const PROFILE_ENV_MAP = {
  TENANT_ID: "tenant_id",
  CLIENT_ID: "client_id",
  CLIENT_SECRET: "client_secret",
  GRAPH_USER_ID: "graph_user_id",
  ONEDRIVE_DRIVE_ID: "onedrive_drive_id",
  SPO_ADMIN_URL: "spo_admin_url",
  PS_AUTH_MODE: "ps_auth_mode",
  PS_USER_PRINCIPAL_NAME: "ps_user_principal_name",
  PS_ORG: "ps_org",
  AZURE_TENANT_ID: "azure_tenant_id",
  AZURE_SUBSCRIPTION_ID: "azure_subscription_id",
};

const EDITABLE_USER_FIELDS = [
  { key: "displayName", label: "Display name" },
  { key: "givenName", label: "Given name" },
  { key: "surname", label: "Surname" },
  { key: "jobTitle", label: "Job title" },
  { key: "department", label: "Department" },
  { key: "officeLocation", label: "Office location" },
  { key: "mobilePhone", label: "Mobile phone" },
  { key: "businessPhones", label: "Business phones", type: "list", placeholder: "Comma-separated" },
  { key: "streetAddress", label: "Street address" },
  { key: "city", label: "City" },
  { key: "state", label: "State" },
  { key: "postalCode", label: "Postal code" },
  { key: "country", label: "Country" },
  { key: "usageLocation", label: "Usage location" },
  { key: "companyName", label: "Company name" },
  { key: "accountEnabled", label: "Account enabled", type: "checkbox" },
];

const TILE_LAYOUT_KEY = "tileLayout";
const TILE_LAYOUT_VERSION = 2;

const TEMPLATE_STORAGE_KEY = "taskTemplates";
const ACTION_PACK_STORAGE_KEY = "actionPacks";
const ACTION_PACK_PAGE_KEY = "actionPackPageIndex";
const ACTION_PACK_PAGE_SIZE = 3;
const REPORT_PRESET_STORAGE_KEY = "reportPresets";
const ACTION_PACK_FILTER_KEY = "actionPackFilter";
const ACTION_PACK_FAVORITES_KEY = "actionPackFavorites";
const ACTION_PACK_HISTORY_KEY = "actionPackHistory";
const ACTION_PACK_PARAMS_KEY = "actionPackParams";
const REPORT_HISTORY_KEY = "reportHistory";

const DEFAULT_TEMPLATES = [
  {
    id: "template-exchange-recent-mail",
    name: "Recent mail (Top 5)",
    service: "exchange",
    action: "list_messages",
    params: { top: 5, order_by: "receivedDateTime desc" },
  },
  {
    id: "template-reports-user-audit",
    name: "User audit (include groups & licenses)",
    service: "reports",
    action: "user_audit",
    params: { include_groups: true, include_licenses: true },
  },
  {
    id: "template-onedrive-root",
    name: "OneDrive root (current user)",
    service: "onedrive",
    action: "list_drive_items",
    params: {},
  },
];

const POWERSHELL_MODULES_BY_SERVICE = {
  exchange: ["ExchangeOnlineManagement"],
  onedrive: ["Microsoft.Online.SharePoint.PowerShell"],
  sharepoint: ["Microsoft.Online.SharePoint.PowerShell"],
  teams: ["MicrosoftTeams"],
  entra: ["Microsoft.Graph"],
  azure: ["Az.Accounts"],
  purview: ["ExchangeOnlineManagement"],
  localad: ["ActiveDirectory", "GroupPolicy"],
  printers: ["PrintManagement", "GroupPolicy"],
  network: ["NetAdapter", "NetTCPIP"],
  fileserver: [],
};

const GRAPH_HEALTH_SERVICES = ["exchange", "onedrive", "sharepoint", "teams", "entra"];

const graphPreflightCache = {};
const powershellPreflightCache = {};
const activeRequests = new Map();
const actionPackState = new Map();
const reportQueueState = { running: false, cancelled: false, controller: null };
const reportQueue = [];
let currentReportJob = null;

const DEFAULT_ACTION_PACKS = [
  {
    id: "onboard-user",
    name: "Onboard user",
    description: "Create user, assign licenses, add to groups, and prep mailbox settings.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
        optional: true,
        label: "Audit current state (optional)",
      },
      {
        service: "entra",
        action: "create_user",
        label: "Create user",
      },
      {
        service: "entra",
        action: "add_group_member",
        label: "Add to group(s)",
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Assign licenses (PowerShell)",
      },
      {
        service: "onedrive",
        action: "get_user_drive_id",
        label: "Provision OneDrive",
        optional: true,
      },
      {
        service: "exchange",
        action: "list_mail_folders",
        label: "Confirm mailbox",
        optional: true,
      },
    ],
  },
  {
    id: "offboard-user",
    name: "Offboard user",
    description: "Disable account, remove licenses, and capture audit details.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
        label: "Capture user audit",
      },
      {
        service: "localad",
        action: "disable_account",
        label: "Disable on-prem account (optional)",
        optional: true,
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Remove licenses (PowerShell)",
      },
      {
        service: "entra",
        action: "add_group_member",
        label: "Update group memberships (optional)",
        optional: true,
      },
    ],
  },
  {
    id: "shared-mailbox-setup",
    name: "Shared mailbox setup",
    description: "Enable shared mailbox sent item copy and validate mail folders.",
    steps: [
      {
        service: "exchange",
        action: "enable_shared_sent_items",
        label: "Enable shared sent items (PowerShell)",
      },
      {
        service: "exchange",
        action: "list_mail_folders",
        label: "Verify shared mailbox folders",
        optional: true,
      },
    ],
  },
  {
    id: "onedrive-provision",
    name: "OneDrive provisioning check",
    description: "Lookup OneDrive drive ID and list root items.",
    steps: [
      {
        service: "onedrive",
        action: "get_user_drive_id",
        label: "Resolve drive ID",
      },
      {
        service: "onedrive",
        action: "list_drive_items",
        label: "List root items",
        optional: true,
      },
    ],
  },
  {
    id: "shared-mailbox-audit",
    name: "Shared mailbox audit",
    description: "Verify shared mailbox folders and sent item settings.",
    steps: [
      {
        service: "exchange",
        action: "list_mail_folders",
        label: "List shared mailbox folders",
      },
      {
        service: "exchange",
        action: "enable_shared_sent_items",
        label: "Ensure sent items copy (PowerShell)",
        optional: true,
      },
    ],
  },
  {
    id: "localad-user-reset",
    name: "Local AD reset",
    description: "Reset password and unlock on-prem account.",
    steps: [
      {
        service: "localad",
        action: "reset_password",
        label: "Reset password",
      },
      {
        service: "localad",
        action: "unlock_account",
        label: "Unlock account (optional)",
        optional: true,
      },
    ],
  },
  {
    id: "teams-channel-setup",
    name: "Teams channel setup",
    description: "Create a channel and verify chat/message access.",
    steps: [
      {
        service: "teams",
        action: "create_channel",
        label: "Create channel",
      },
      {
        service: "teams",
        action: "list_chat_messages",
        label: "Verify messaging (optional)",
        optional: true,
      },
    ],
  },
];

const ACTION_PACKS = DEFAULT_ACTION_PACKS.map((pack) => ({ ...pack, builtin: true }));

const REPORT_PRESETS = [
  {
    id: "user-audit-core",
    label: "User audit (core)",
    actions: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
      },
    ],
  },
  {
    id: "user-audit-full",
    label: "User audit (full)",
    actions: [
      {
        service: "reports",
        action: "user_audit",
        params: {
          include_groups: true,
          include_licenses: true,
          include_signins: true,
          include_devices: true,
          include_mailbox_stats: true,
        },
      },
    ],
  },
  {
    id: "gpo-audit",
    label: "GPO inventory",
    actions: [{ service: "reports", action: "gpo_audit" }],
  },
  {
    id: "gpo-link-audit",
    label: "GPO link audit by OU",
    actions: [{ service: "reports", action: "gpo_link_audit" }],
  },
  {
    id: "user-audit-plus-gpo",
    label: "User audit + GPO audit",
    actions: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
      },
      { service: "reports", action: "gpo_audit" },
    ],
  },
];

let currentPresetId = null;
let currentPresetSteps = [];
let sshSocket = null;
let sshConnected = false;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

function setRunnerRunning(service, running) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;
  const runButton = form.querySelector(".runner-run");
  const cancelButton = form.querySelector(".runner-cancel");
  if (runButton) runButton.disabled = running;
  if (cancelButton) {
    cancelButton.disabled = !running;
    cancelButton.style.display = running ? "inline-flex" : "none";
  }
}

function cancelAction(service) {
  const controller = activeRequests.get(service);
  if (!controller) {
    showToast("No running action");
    return false;
  }
  controller.abort();
  activeRequests.delete(service);
  setRunnerRunning(service, false);
  showToast("Action cancelled");
  return true;
}

function setActionPackRunning(packId, running) {
  const card = document.querySelector(`[data-pack-id="${packId}"]`);
  if (card) {
    const runButton = card.querySelector(".action-pack-run");
    const cancelButton = card.querySelector(".action-pack-cancel");
    if (runButton) runButton.disabled = running;
    if (cancelButton) cancelButton.disabled = !running;
  }
  if (selectedPackId === packId) {
    if (actionPackRunButton) actionPackRunButton.disabled = running;
    if (actionPackRunCancelButton) actionPackRunCancelButton.disabled = !running;
  }
}

function cancelActionPack(packId) {
  const state = actionPackState.get(packId);
  if (!state) {
    showToast("No running action pack");
    return false;
  }
  state.cancelled = true;
  if (state.controller) {
    state.controller.abort();
  }
  setActionPackRunning(packId, false);
  showToast("Action pack cancelled");
  return true;
}

function hideWarningBanner() {
  if (!warningBanner) return;
  warningBanner.classList.add("hidden");
}

function showWarningBanner(message, meta = "") {
  if (!warningBanner || !warningMessage) return;
  warningMessage.textContent = message || "Preflight warning detected.";
  if (warningMeta) {
    warningMeta.textContent = meta || "";
  }
  warningBanner.classList.remove("hidden");
}

function setOutputStatus(service, { state, text, meta, running } = {}) {
  const statusEl = document.querySelector(`.output-status[data-output-status="${service}"]`);
  if (!statusEl) return;
  if (state) {
    statusEl.classList.remove("ok", "warn", "fail", "running", "idle");
    statusEl.classList.add(state);
  }
  const textEl = statusEl.querySelector(".status-text");
  const metaEl = statusEl.querySelector(".status-meta");
  const spinner = statusEl.querySelector(".spinner");
  if (text !== undefined && textEl) {
    textEl.textContent = text;
  }
  if (meta !== undefined && metaEl) {
    metaEl.textContent = meta;
  }
  if (running !== undefined && spinner) {
    spinner.classList.toggle("active", running);
  }
  if (running !== undefined) {
    const card = statusEl.closest(".output-card");
    if (card) {
      card.classList.toggle("loading", running);
    }
  }
}

function formatElapsed(ms) {
  if (!Number.isFinite(ms)) return "";
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function startOutputTimer(service, prefix) {
  stopOutputTimer(service);
  const start = performance.now();
  outputStartTimes.set(service, start);
  outputStatusPrefixes.set(service, prefix || "");
  const timer = setInterval(() => {
    const elapsed = performance.now() - start;
    const elapsedText = formatElapsed(elapsed);
    const prefixText = outputStatusPrefixes.get(service);
    const meta = prefixText ? `${prefixText} · Elapsed ${elapsedText}` : `Elapsed ${elapsedText}`;
    setOutputStatus(service, { meta });
  }, 250);
  outputTimers.set(service, timer);
}

function stopOutputTimer(service) {
  const timer = outputTimers.get(service);
  if (timer) {
    clearInterval(timer);
    outputTimers.delete(service);
  }
  outputStartTimes.delete(service);
  outputStatusPrefixes.delete(service);
}

function hideGraphStatusBanner() {
  if (!graphStatusBanner) return;
  graphStatusBanner.classList.add("hidden");
}

function showGraphStatusBanner(message, meta = "") {
  if (!graphStatusBanner || !graphStatusMessage) return;
  graphStatusMessage.textContent = message || "Graph service reports degraded status.";
  if (graphStatusMeta) {
    graphStatusMeta.textContent = meta || "";
  }
  graphStatusBanner.classList.remove("hidden");
}

function appendTerminalOutput(content) {
  if (!sshTerminalOutput) return;
  sshTerminalOutput.textContent += content;
  const maxLength = 20000;
  if (sshTerminalOutput.textContent.length > maxLength) {
    sshTerminalOutput.textContent = sshTerminalOutput.textContent.slice(-maxLength);
  }
  sshTerminalOutput.scrollTop = sshTerminalOutput.scrollHeight;
}

function getSshWsUrl() {
  const override = sshWsUrlInput?.value.trim();
  if (override) return override;
  const host = window.location.hostname || "127.0.0.1";
  let port = window.location.port || "8000";
  if (port === "8001") {
    port = "8000";
  }
  return `ws://${host}:${port}/ws/ssh`;
}

function setSshConnectionStatus(state, meta) {
  setOutputStatus("ssh", {
    state,
    text: state === "ok" ? "Connected" : state === "fail" ? "Disconnected" : "Connecting",
    meta: meta || "",
    running: state === "running",
  });
}

function disconnectSsh() {
  if (sshSocket) {
    sshSocket.close();
    sshSocket = null;
  }
  sshConnected = false;
  setSshConnectionStatus("fail", "Session closed");
}

function connectSsh() {
  if (!sshHostInput?.value.trim()) {
    showToast("SSH host is required");
    return;
  }
  if (sshSocket) {
    disconnectSsh();
  }
  const host = sshHostInput.value.trim();
  const user = sshUserInput?.value.trim();
  const port = Number.parseInt(sshPortInput?.value, 10) || 22;
  const keyPath = sshKeyPathInput?.value.trim();
  const strictHost = sshStrictHostInput ? sshStrictHostInput.checked : true;
  const wsUrl = getSshWsUrl();

  try {
    sshSocket = new WebSocket(wsUrl);
  } catch (err) {
    showToast("Failed to open SSH WebSocket");
    return;
  }
  sshSocket.binaryType = "arraybuffer";
  setSshConnectionStatus("running", `Connecting to ${host}`);
  sshSocket.onopen = () => {
    const payload = {
      host,
      user: user || null,
      port,
      key_path: keyPath || null,
      strict_host_key: strictHost,
    };
    sshSocket.send(JSON.stringify(payload));
    sshConnected = true;
    setSshConnectionStatus("ok", `${host}:${port}`);
  };
  sshSocket.onmessage = (event) => {
    if (typeof event.data === "string") {
      appendTerminalOutput(event.data);
      return;
    }
    if (event.data instanceof ArrayBuffer) {
      const decoder = new TextDecoder();
      appendTerminalOutput(decoder.decode(event.data));
    }
  };
  sshSocket.onerror = () => {
    setSshConnectionStatus("fail", "WebSocket error");
  };
  sshSocket.onclose = () => {
    sshConnected = false;
    setSshConnectionStatus("fail", "Disconnected");
  };
}

function sendSshInput(value) {
  if (!sshSocket || sshSocket.readyState !== WebSocket.OPEN) {
    showToast("SSH session not connected");
    return;
  }
  if (value === undefined || value === null) return;
  sshSocket.send(value);
}

function isQuickActionsEditing() {
  return quickActionsCard?.classList.contains("editing");
}

function loadQuickActions() {
  try {
    const raw = localStorage.getItem("quickActions");
    if (raw === null) {
      return DEFAULT_QUICK_ACTIONS.slice();
    }
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) {
      return parsed
        .map((item) => {
          if (!item || typeof item !== "object") return null;
          if (item.type === "template") {
            return { type: "template", templateId: item.templateId };
          }
          if (item.service && item.action) {
            return { type: "action", service: item.service, action: item.action };
          }
          return null;
        })
        .filter(Boolean);
    }
  } catch (err) {
    return DEFAULT_QUICK_ACTIONS.slice();
  }
  return DEFAULT_QUICK_ACTIONS.slice();
}

function saveQuickActions(list) {
  localStorage.setItem("quickActions", JSON.stringify(list));
}

function resolveActionLabel(service, action) {
  const meta = ACTIONS_UI?.[service]?.[action];
  return meta?.label || `${service}.${action}`;
}

function formatServiceLabel(service) {
  if (!service) return "";
  if (serviceLabels[service]) return serviceLabels[service];
  return service.charAt(0).toUpperCase() + service.slice(1);
}

function getAvailableQuickActionServices() {
  return Object.keys(ACTIONS_UI).filter((service) => Object.keys(ACTIONS_UI[service] || {}).length);
}

function populateQuickActionEditor() {
  if (!quickActionServiceSelect || !quickActionActionSelect) return;
  const services = getAvailableQuickActionServices();
  quickActionServiceSelect.innerHTML = "";
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service;
    option.textContent = service.charAt(0).toUpperCase() + service.slice(1);
    quickActionServiceSelect.appendChild(option);
  });

  const updateActions = () => {
    const service = quickActionServiceSelect.value;
    const actions = ACTIONS_UI?.[service] || {};
    quickActionActionSelect.innerHTML = "";
    Object.entries(actions).forEach(([action, meta]) => {
      const option = document.createElement("option");
      option.value = action;
      option.textContent = meta.label;
      quickActionActionSelect.appendChild(option);
    });
    quickActionActionSelect.disabled = !Object.keys(actions).length;
  };

  quickActionServiceSelect.addEventListener("change", updateActions);
  updateActions();
  renderTemplateSelect();
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "")
    .slice(0, 60);
}

function normalizePackStep(step) {
  if (!step || typeof step !== "object") return null;
  const service = step.service;
  const action = step.action;
  if (!ACTIONS_UI?.[service]?.[action]) return null;
  return {
    service,
    action,
    label: step.label || "",
    optional: Boolean(step.optional),
    params: step.params || undefined,
  };
}

function normalizeActionPack(pack) {
  if (!pack || typeof pack !== "object") return null;
  const name = String(pack.name || "").trim();
  if (!name) return null;
  const steps = Array.isArray(pack.steps) ? pack.steps.map(normalizePackStep).filter(Boolean) : [];
  if (!steps.length) return null;
  const id = pack.id || slugify(name) || `custom-pack-${Date.now()}`;
  const defaults = pack.defaults && typeof pack.defaults === "object" ? pack.defaults : undefined;
  const tenantId = pack.tenant_id || pack.tenantId || undefined;
  return {
    id,
    name,
    description: pack.description || "",
    steps,
    defaults,
    tenant_id: tenantId,
    builtin: Boolean(pack.builtin),
  };
}

function loadActionPacks() {
  try {
    const raw = localStorage.getItem(ACTION_PACK_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.map((pack) => normalizeActionPack(pack)).filter(Boolean);
  } catch (err) {
    return [];
  }
}

function saveActionPacks(list) {
  localStorage.setItem(ACTION_PACK_STORAGE_KEY, JSON.stringify(list));
}

function loadActionPackFavorites() {
  try {
    const raw = localStorage.getItem(ACTION_PACK_FAVORITES_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) return new Set(parsed);
  } catch (err) {
    return new Set();
  }
  return new Set();
}

function saveActionPackFavorites(set) {
  localStorage.setItem(ACTION_PACK_FAVORITES_KEY, JSON.stringify(Array.from(set)));
}

function isPackFavorite(packId) {
  return loadActionPackFavorites().has(packId);
}

function togglePackFavorite(packId) {
  const favorites = loadActionPackFavorites();
  if (favorites.has(packId)) {
    favorites.delete(packId);
  } else {
    favorites.add(packId);
  }
  saveActionPackFavorites(favorites);
  renderActionPacks();
}

function getActionPackFilter() {
  return localStorage.getItem(ACTION_PACK_FILTER_KEY) || "current";
}

function setActionPackFilter(value) {
  localStorage.setItem(ACTION_PACK_FILTER_KEY, value);
}

function loadActionPackParams() {
  try {
    const raw = localStorage.getItem(ACTION_PACK_PARAMS_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (err) {
    return {};
  }
}

function saveActionPackParams(data) {
  localStorage.setItem(ACTION_PACK_PARAMS_KEY, JSON.stringify(data));
}

function getPackParams(packId) {
  const data = loadActionPackParams();
  return data[packId] || { stepParams: {}, includeSteps: {} };
}

function setPackParams(packId, payload) {
  const data = loadActionPackParams();
  data[packId] = payload;
  saveActionPackParams(data);
}

function loadActionPackHistory() {
  try {
    const raw = localStorage.getItem(ACTION_PACK_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function saveActionPackHistory(items) {
  localStorage.setItem(ACTION_PACK_HISTORY_KEY, JSON.stringify(items));
}

function addActionPackHistory(entry) {
  const items = loadActionPackHistory();
  items.unshift(entry);
  saveActionPackHistory(items.slice(0, 20));
  renderActionPackHistory();
}

function normalizePresetStep(step) {
  if (!step || typeof step !== "object") return null;
  const service = step.service;
  const action = step.action;
  if (!ACTIONS_UI?.[service]?.[action]) return null;
  return {
    service,
    action,
    label: step.label || "",
    params: step.params || undefined,
  };
}

function normalizeReportPreset(preset) {
  if (!preset || typeof preset !== "object") return null;
  const name = String(preset.label || preset.name || "").trim();
  if (!name) return null;
  const steps = Array.isArray(preset.actions)
    ? preset.actions.map(normalizePresetStep).filter(Boolean)
    : [];
  if (!steps.length) return null;
  return {
    id: preset.id || slugify(name) || `preset-${Date.now()}`,
    label: name,
    description: preset.description || "",
    actions: steps,
  };
}

function loadReportPresets() {
  try {
    const raw = localStorage.getItem(REPORT_PRESET_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.map((preset) => normalizeReportPreset(preset)).filter(Boolean);
  } catch (err) {
    return [];
  }
}

function saveReportPresets(list) {
  localStorage.setItem(REPORT_PRESET_STORAGE_KEY, JSON.stringify(list));
}

function getAllReportPresets() {
  return [...REPORT_PRESETS, ...loadReportPresets()];
}

function getReportPresetById(id) {
  return getAllReportPresets().find((preset) => preset.id === id);
}

function loadReportHistory() {
  try {
    const raw = localStorage.getItem(REPORT_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function saveReportHistory(items) {
  localStorage.setItem(REPORT_HISTORY_KEY, JSON.stringify(items));
}

function addReportHistory(entry) {
  const items = loadReportHistory();
  items.unshift(entry);
  saveReportHistory(items.slice(0, 20));
  renderReportHistory();
}

function getAllActionPacks() {
  return [...ACTION_PACKS, ...loadActionPacks()];
}

function getActionPackById(id) {
  return getAllActionPacks().find((pack) => pack.id === id);
}

function getActionPackPageIndex() {
  const raw = localStorage.getItem(ACTION_PACK_PAGE_KEY);
  const idx = Number.parseInt(raw, 10);
  return Number.isFinite(idx) && idx >= 0 ? idx : 0;
}

function setActionPackPageIndex(value) {
  localStorage.setItem(ACTION_PACK_PAGE_KEY, String(value));
}

function getActionPackPaging(packs) {
  const totalPages = Math.max(1, Math.ceil(packs.length / ACTION_PACK_PAGE_SIZE));
  let pageIndex = getActionPackPageIndex();
  if (pageIndex > totalPages - 1) pageIndex = totalPages - 1;
  if (pageIndex < 0) pageIndex = 0;
  const start = pageIndex * ACTION_PACK_PAGE_SIZE;
  const end = start + ACTION_PACK_PAGE_SIZE;
  return { pageIndex, totalPages, slice: packs.slice(start, end) };
}

function updateActionPackControls(pageIndex, totalPages) {
  if (actionPackPageInfo) {
    actionPackPageInfo.textContent = `Page ${pageIndex + 1} / ${totalPages}`;
  }
  if (actionPackPrevButton) {
    actionPackPrevButton.disabled = pageIndex <= 0;
  }
  if (actionPackNextButton) {
    actionPackNextButton.disabled = pageIndex >= totalPages - 1;
  }
}

function getActionPackStepDefaults(pack, step) {
  if (!pack?.defaults || typeof pack.defaults !== "object") return null;
  const key = `${step.service}.${step.action}`;
  if (pack.defaults.stepParams && typeof pack.defaults.stepParams === "object") {
    return pack.defaults.stepParams[key] || pack.defaults.stepParams[step.action] || null;
  }
  return pack.defaults[key] || pack.defaults[step.action] || null;
}

let currentPackId = null;
let currentPackBuiltin = false;
let currentPackSteps = [];
let reportExportOptions = [];
let currentTenantId = "";
let configLocked = false;
let keychainAvailable = false;
let tenantInfoLoading = false;
let selectedPackId = null;

function renderPackSteps() {
  if (!packStepList) return;
  packStepList.innerHTML = "";
  if (!currentPackSteps.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No steps added yet.";
    packStepList.appendChild(empty);
    return;
  }
  currentPackSteps.forEach((step, index) => {
    const row = document.createElement("div");
    row.classList.add("pack-step-row");
    const meta = document.createElement("div");
    meta.classList.add("pack-step-meta");
    const label = document.createElement("span");
    label.textContent = step.label || activityLabel(step.service, step.action);
    const key = document.createElement("span");
    key.textContent = `${step.service}.${step.action}`;
    const optional = document.createElement("span");
    optional.textContent = step.optional ? "Optional" : "Required";
    meta.appendChild(label);
    meta.appendChild(key);
    meta.appendChild(optional);
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      currentPackSteps.splice(index, 1);
      renderPackSteps();
    });
    row.appendChild(meta);
    row.appendChild(remove);
    packStepList.appendChild(row);
  });
}

function renderPresetSteps() {
  if (!presetStepList) return;
  presetStepList.innerHTML = "";
  if (!currentPresetSteps.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No steps added yet.";
    presetStepList.appendChild(empty);
    return;
  }
  currentPresetSteps.forEach((step, index) => {
    const row = document.createElement("div");
    row.classList.add("pack-step-row");
    const meta = document.createElement("div");
    meta.classList.add("pack-step-meta");
    const label = document.createElement("span");
    label.textContent = step.label || activityLabel(step.service, step.action);
    const key = document.createElement("span");
    key.textContent = `${step.service}.${step.action}`;
    meta.appendChild(label);
    meta.appendChild(key);
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      currentPresetSteps.splice(index, 1);
      renderPresetSteps();
    });
    row.appendChild(meta);
    row.appendChild(remove);
    presetStepList.appendChild(row);
  });
}

function resetPackBuilder() {
  currentPackId = null;
  currentPackBuiltin = false;
  currentPackSteps = [];
  if (packNameInput) packNameInput.value = "";
  if (packDescriptionInput) packDescriptionInput.value = "";
  if (packDefaultsInput) packDefaultsInput.value = "";
  if (packScopeSelect) packScopeSelect.value = "global";
  renderPackSteps();
  const builder = document.getElementById("action-pack-builder");
  if (builder) builder.open = true;
}

function resetPresetBuilder() {
  currentPresetId = null;
  currentPresetSteps = [];
  if (presetNameInput) presetNameInput.value = "";
  if (presetDescriptionInput) presetDescriptionInput.value = "";
  renderPresetSteps();
  const builder = document.getElementById("report-preset-builder");
  if (builder) builder.open = true;
}

function setPackBuilder(pack, { clone } = {}) {
  const useClone = Boolean(clone);
  currentPackId = useClone ? null : pack.id;
  currentPackBuiltin = useClone ? false : Boolean(pack.builtin);
  currentPackSteps = pack.steps.map((step) => ({ ...step }));
  if (packNameInput) packNameInput.value = useClone ? `${pack.name} (Copy)` : pack.name;
  if (packDescriptionInput) packDescriptionInput.value = pack.description || "";
  if (packDefaultsInput) {
    packDefaultsInput.value = pack.defaults ? JSON.stringify(pack.defaults, null, 2) : "";
  }
  if (packScopeSelect) {
    packScopeSelect.value = pack.tenant_id ? "tenant" : "global";
  }
  renderPackSteps();
  const builder = document.getElementById("action-pack-builder");
  if (builder) builder.open = true;
}

function setPresetBuilder(preset, { clone } = {}) {
  const useClone = Boolean(clone);
  currentPresetId = useClone ? null : preset.id;
  currentPresetSteps = preset.actions.map((step) => ({ ...step }));
  if (presetNameInput) presetNameInput.value = useClone ? `${preset.label} (Copy)` : preset.label;
  if (presetDescriptionInput) presetDescriptionInput.value = preset.description || "";
  renderPresetSteps();
  const builder = document.getElementById("report-preset-builder");
  if (builder) builder.open = true;
}

function collectPackDefaults() {
  if (!packDefaultsInput) return undefined;
  const raw = packDefaultsInput.value.trim();
  if (!raw) return undefined;
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch (err) {
    showToast("Defaults JSON is invalid");
    return null;
  }
  return null;
}

function savePackFromBuilder() {
  const name = packNameInput?.value.trim() || "";
  if (!name) {
    showToast("Pack name is required");
    return;
  }
  if (!currentPackSteps.length) {
    showToast("Add at least one step");
    return;
  }
  const defaults = collectPackDefaults();
  if (defaults === null) return;
  const description = packDescriptionInput?.value.trim() || "";
  const scope = packScopeSelect?.value || "global";
  const tenantId = scope === "tenant" ? currentTenantId : undefined;
  if (scope === "tenant" && !tenantId) {
    showToast("Tenant ID not set. Save config first.");
    return;
  }
  const idBase = slugify(name) || `custom-pack-${Date.now()}`;
  const existing = loadActionPacks();
  let id = currentPackId || idBase;
  if (!currentPackId || currentPackBuiltin) {
    id = idBase;
    if (existing.some((pack) => pack.id === id)) {
      id = `${idBase}-${Date.now()}`;
    }
  }
  const entry = normalizeActionPack({
    id,
    name,
    description,
    steps: currentPackSteps,
    defaults,
    tenant_id: tenantId,
    builtin: false,
  });
  if (!entry) {
    showToast("Pack data invalid");
    return;
  }
  const idx = existing.findIndex((pack) => pack.id === id);
  if (idx >= 0) {
    existing[idx] = entry;
  } else {
    existing.push(entry);
  }
  saveActionPacks(existing);
  currentPackId = entry.id;
  currentPackBuiltin = false;
  setActionPackPageIndex(0);
  renderActionPacks();
  showToast("Action pack saved");
}

function deletePackFromBuilder() {
  if (!currentPackId) {
    showToast("Select a custom pack to delete");
    return;
  }
  if (currentPackBuiltin) {
    showToast("Built-in packs cannot be deleted");
    return;
  }
  const confirmDelete = window.confirm("Delete this action pack?");
  if (!confirmDelete) return;
  const existing = loadActionPacks().filter((pack) => pack.id !== currentPackId);
  saveActionPacks(existing);
  resetPackBuilder();
  renderActionPacks();
  showToast("Action pack deleted");
}

function populatePackStepBuilder() {
  if (!packStepServiceSelect || !packStepActionSelect) return;
  const services = Object.keys(ACTIONS_UI);
  packStepServiceSelect.innerHTML = "";
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service;
    option.textContent = service.charAt(0).toUpperCase() + service.slice(1);
    packStepServiceSelect.appendChild(option);
  });

  const updateActions = () => {
    const service = packStepServiceSelect.value;
    const actions = ACTIONS_UI?.[service] || {};
    packStepActionSelect.innerHTML = "";
    Object.entries(actions).forEach(([action, meta]) => {
      const option = document.createElement("option");
      option.value = action;
      option.textContent = meta.label || action;
      packStepActionSelect.appendChild(option);
    });
  };
  packStepServiceSelect.addEventListener("change", updateActions);
  updateActions();
}

function addStepToPack() {
  const service = packStepServiceSelect?.value;
  const action = packStepActionSelect?.value;
  if (!service || !action) return;
  const step = normalizePackStep({
    service,
    action,
    label: packStepLabelInput?.value.trim() || "",
    optional: packStepOptionalInput?.checked || false,
  });
  if (!step) {
    showToast("Invalid step selection");
    return;
  }
  currentPackSteps.push(step);
  if (packStepLabelInput) packStepLabelInput.value = "";
  if (packStepOptionalInput) packStepOptionalInput.checked = false;
  renderPackSteps();
}

function populatePresetStepBuilder() {
  if (!presetStepServiceSelect || !presetStepActionSelect) return;
  const services = Object.keys(ACTIONS_UI);
  presetStepServiceSelect.innerHTML = "";
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service;
    option.textContent = service.charAt(0).toUpperCase() + service.slice(1);
    presetStepServiceSelect.appendChild(option);
  });

  const updateActions = () => {
    const service = presetStepServiceSelect.value;
    const actions = ACTIONS_UI?.[service] || {};
    presetStepActionSelect.innerHTML = "";
    Object.entries(actions).forEach(([action, meta]) => {
      const option = document.createElement("option");
      option.value = action;
      option.textContent = meta.label || action;
      presetStepActionSelect.appendChild(option);
    });
  };
  presetStepServiceSelect.addEventListener("change", updateActions);
  updateActions();
}

function addStepToPreset() {
  const service = presetStepServiceSelect?.value;
  const action = presetStepActionSelect?.value;
  if (!service || !action) return;
  const step = normalizePresetStep({
    service,
    action,
    label: presetStepLabelInput?.value.trim() || "",
  });
  if (!step) {
    showToast("Invalid step selection");
    return;
  }
  currentPresetSteps.push(step);
  if (presetStepLabelInput) presetStepLabelInput.value = "";
  renderPresetSteps();
}

function savePresetFromBuilder() {
  const name = presetNameInput?.value.trim() || "";
  if (!name) {
    showToast("Preset name is required");
    return;
  }
  if (!currentPresetSteps.length) {
    showToast("Add at least one step");
    return;
  }
  const description = presetDescriptionInput?.value.trim() || "";
  const idBase = slugify(name) || `preset-${Date.now()}`;
  const existing = loadReportPresets();
  let id = currentPresetId || idBase;
  if (!currentPresetId) {
    if (existing.some((preset) => preset.id === id)) {
      id = `${idBase}-${Date.now()}`;
    }
  }
  const entry = normalizeReportPreset({
    id,
    label: name,
    description,
    actions: currentPresetSteps,
  });
  if (!entry) {
    showToast("Preset data invalid");
    return;
  }
  const idx = existing.findIndex((preset) => preset.id === id);
  if (idx >= 0) {
    existing[idx] = entry;
  } else {
    existing.push(entry);
  }
  saveReportPresets(existing);
  currentPresetId = entry.id;
  renderReportPresets();
  showToast("Preset saved");
}

function deletePresetFromBuilder() {
  if (!currentPresetId) {
    showToast("Select a custom preset to delete");
    return;
  }
  const confirmDelete = window.confirm("Delete this report preset?");
  if (!confirmDelete) return;
  const existing = loadReportPresets().filter((preset) => preset.id !== currentPresetId);
  saveReportPresets(existing);
  resetPresetBuilder();
  renderReportPresets();
  showToast("Preset deleted");
}

function exportActionPacks() {
  const packs = loadActionPacks();
  const payload = { packs };
  downloadJson(payload, "action-packs.json");
}

function importActionPacks(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const parsed = JSON.parse(reader.result);
      const incoming = Array.isArray(parsed) ? parsed : parsed?.packs;
      if (!Array.isArray(incoming)) {
        showToast("No packs found");
        return;
      }
      const existing = loadActionPacks();
      incoming.forEach((pack) => {
        const normalized = normalizeActionPack(pack);
        if (!normalized) return;
        const idx = existing.findIndex((item) => item.id === normalized.id);
        if (idx >= 0) {
          existing[idx] = normalized;
        } else {
          existing.push(normalized);
        }
      });
      saveActionPacks(existing);
      setActionPackPageIndex(0);
      renderActionPacks();
      showToast("Action packs imported");
    } catch (err) {
      showToast("Import failed");
    }
  };
  reader.readAsText(file);
}

function exportTemplates() {
  const templates = loadTemplates();
  const payload = { templates };
  downloadJson(payload, "task-templates.json");
}

function importTemplates(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const parsed = JSON.parse(reader.result);
      const incoming = Array.isArray(parsed) ? parsed : parsed?.templates;
      if (!Array.isArray(incoming)) {
        showToast("No templates found");
        return;
      }
      const existing = loadTemplates();
      incoming.forEach((tmpl) => {
        const normalized = tmpl && typeof tmpl === "object" ? tmpl : null;
        if (!normalized?.id) return;
        const idx = existing.findIndex((item) => item.id === normalized.id);
        if (idx >= 0) {
          existing[idx] = normalized;
        } else {
          existing.push(normalized);
        }
      });
      saveTemplates(existing);
      renderTemplateSelect();
      renderQuickActions();
      showToast("Templates imported");
    } catch (err) {
      showToast("Import failed");
    }
  };
  reader.readAsText(file);
}

function downloadJson(payload, filename) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function sanitizeFilename(value) {
  return String(value || "")
    .replace(/[^a-z0-9-_]+/gi, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase()
    .slice(0, 80) || "report";
}

function formatDatasetLabel(key) {
  return String(key || "")
    .replace(/_/g, " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildReportDatasetOptions(payload) {
  const options = [];
  options.push({
    key: "__full__",
    label: "Full report",
    data: payload,
  });
  if (!payload || typeof payload !== "object") return options;

  const candidates = new Map();
  if (Array.isArray(payload.value)) {
    candidates.set("value", payload.value);
  }
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    if (Array.isArray(value)) {
      candidates.set(key, value);
      return;
    }
    if (value && typeof value === "object" && Array.isArray(value.value)) {
      candidates.set(key, value.value);
      return;
    }
    if (value && typeof value === "object") {
      candidates.set(key, value);
    }
  });

  candidates.forEach((data, key) => {
    if (key === "__full__") return;
    options.push({
      key,
      label: formatDatasetLabel(key),
      data,
    });
  });
  return options;
}

function updateReportExportOptions(payload) {
  reportExportOptions = buildReportDatasetOptions(payload);
  if (!reportsExportDatasetSelect) return;
  const current = reportsExportDatasetSelect.value;
  reportsExportDatasetSelect.innerHTML = "";
  reportExportOptions.forEach((option) => {
    const el = document.createElement("option");
    el.value = option.key;
    el.textContent = option.label;
    reportsExportDatasetSelect.appendChild(el);
  });
  const fallback = reportExportOptions.find((opt) => opt.key === current)
    ? current
    : "__full__";
  reportsExportDatasetSelect.value = fallback;
  updateDatasetPreview();
}

function getSelectedReportDataset() {
  const selected = reportsExportDatasetSelect?.value || "__full__";
  return reportExportOptions.find((option) => option.key === selected);
}

function updateDatasetPreview() {
  if (!datasetMeta || !datasetContent) return;
  const selection = getSelectedReportDataset();
  if (!selection) {
    datasetMeta.textContent = "Select a dataset to preview.";
    datasetContent.textContent = "";
    return;
  }
  const data = selection.data;
  let count = "";
  if (Array.isArray(data)) {
    count = `${data.length} items`;
  } else if (data && typeof data === "object") {
    count = `${Object.keys(data).length} keys`;
  } else if (data) {
    count = "1 value";
  } else {
    count = "No data";
  }
  datasetMeta.textContent = `${selection.label} · ${count}`;
  datasetContent.textContent = JSON.stringify(data, null, 2).slice(0, 2000);
}

function buildParamsWithDefaults(service, action, defaults = {}) {
  const fields = ACTIONS_UI?.[service]?.[action]?.fields || [];
  const params = { ...defaults };
  let cancelled = false;
  fields.forEach((field) => {
    if (params[field.key] !== undefined) return;
    if (field.type === "checkbox") {
      const confirmValue = window.confirm(`${field.label}?`);
      if (confirmValue) params[field.key] = true;
      return;
    }
    const value = window.prompt(field.label, "");
    if (value === null) {
      cancelled = true;
      return;
    }
    if (value.trim() !== "") {
      params[field.key] = value.trim();
    }
  });
  if (cancelled) return null;
  return params;
}

async function runReportPreset(preset) {
  if (!preset) return;
  for (const step of preset.actions) {
    const label = activityLabel(step.service, step.action);
    const meta = ACTIONS_UI?.[step.service]?.[step.action];
    let params = step.params ? { ...step.params } : {};
    if (meta?.fields?.length) {
      const filled = buildParamsWithDefaults(step.service, step.action, params);
      if (filled === null) {
        showToast("Preset cancelled");
        return;
      }
      params = filled;
    }
    const result = await runAction(step.service, step.action, params);
    if (!result?.ok) {
      const proceed = window.confirm(`Preset step failed: ${label}. Continue?`);
      if (!proceed) {
        showToast("Preset stopped");
        return;
      }
    }
  }
  showToast("Preset completed");
}

function queueReportPreset(preset) {
  if (!preset) return;
  preset.actions.forEach((step) => {
    enqueueReport({
      service: step.service,
      action: step.action,
      params: step.params || {},
      label: preset.label,
    });
  });
  showToast("Preset queued");
}

function setHealthProgress(items) {
  if (!healthProgress) return;
  healthProgress.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = item.label;
    const status = document.createElement("span");
    status.classList.add("status");
    status.classList.add(item.state || "warn");
    status.textContent = item.text;
    row.appendChild(label);
    row.appendChild(status);
    healthProgress.appendChild(row);
  });
}

function upsertHealthListItem(listEl, key, label, statusText, state, metaText) {
  if (!listEl) return;
  let row = listEl.querySelector(`li[data-key="${key}"]`);
  if (!row) {
    row = document.createElement("li");
    row.classList.add("health-item");
    row.dataset.key = key;
    const labelEl = document.createElement("span");
    labelEl.classList.add("label");
    labelEl.textContent = label;
    const statusEl = document.createElement("span");
    statusEl.classList.add("status");
    const metaEl = document.createElement("span");
    metaEl.classList.add("meta");
    row.appendChild(labelEl);
    row.appendChild(statusEl);
    row.appendChild(metaEl);
    listEl.appendChild(row);
  }
  const statusEl = row.querySelector(".status");
  const metaEl = row.querySelector(".meta");
  if (statusEl) {
    statusEl.className = `status ${state || "warn"}`;
    statusEl.textContent = statusText;
  }
  if (metaEl) {
    metaEl.textContent = metaText || "";
  }
}

function resetHealthBreakdown() {
  if (healthGraphList) healthGraphList.innerHTML = "";
  if (healthPowerShellList) healthPowerShellList.innerHTML = "";
  GRAPH_HEALTH_SERVICES.forEach((service) => {
    const label = formatServiceLabel(service);
    upsertHealthListItem(healthGraphList, service, label, "Pending", "warn");
  });
  const modules = Object.values(POWERSHELL_MODULES_BY_SERVICE)
    .flat()
    .filter((item, idx, arr) => arr.indexOf(item) === idx);
  modules.forEach((module) => {
    upsertHealthListItem(healthPowerShellList, module, module, "Pending", "warn");
  });
}

function summarizeGraphCheck(graphData) {
  if (!graphData || typeof graphData !== "object") {
    return { state: "fail", text: "No data" };
  }
  if (graphData.ok) {
    const checks = graphData.checks || {};
    const latencyStates = Object.values(checks)
      .map((check) => {
        const latencyMs = Number(check?.latency_ms ?? check?.latencyMs);
        return getLatencySla(Number.isFinite(latencyMs) ? latencyMs : undefined, check?.ok).state;
      })
      .filter(Boolean);
    if (latencyStates.includes("fail")) {
      return { state: "warn", text: "Latency degraded" };
    }
    if (latencyStates.includes("warn")) {
      return { state: "warn", text: "Latency slow" };
    }
    return { state: "ok", text: "OK" };
  }
  const checks = graphData.checks || {};
  const errors = Object.values(checks).filter((entry) => entry && entry.ok === false);
  if (!errors.length) {
    return { state: "warn", text: "Warning" };
  }
  const transient = errors.some((entry) => Number(entry?.status || 0) >= 500);
  if (transient) {
    return { state: "warn", text: "Transient issues" };
  }
  return { state: "fail", text: `${errors.length} failing` };
}

const GRAPH_SLA_THRESHOLDS = {
  ok: 500,
  warn: 1500,
};

function getLatencySla(latencyMs, ok) {
  if (ok === false) {
    return { label: "Degraded", state: "fail" };
  }
  if (!Number.isFinite(latencyMs)) {
    return { label: "Unknown", state: "warn" };
  }
  if (latencyMs <= GRAPH_SLA_THRESHOLDS.ok) {
    return { label: "OK", state: "ok" };
  }
  if (latencyMs <= GRAPH_SLA_THRESHOLDS.warn) {
    return { label: "Slow", state: "warn" };
  }
  return { label: "Degraded", state: "fail" };
}

function buildHealthMeta({ status, latencyMs, slaLabel, message }) {
  const parts = [];
  if (status) {
    parts.push(`HTTP ${status}`);
  }
  if (Number.isFinite(latencyMs)) {
    parts.push(`${latencyMs} ms`);
  }
  if (slaLabel) {
    parts.push(`SLA: ${slaLabel}`);
  }
  if (message) {
    parts.push(message);
  }
  return parts.join(" · ");
}

function summarizePowerShellCheck(psData) {
  if (!psData || typeof psData !== "object") {
    return { state: "fail", text: "No data" };
  }
  if (psData.ok) {
    return { state: "ok", text: "OK" };
  }
  const modules = psData.modules || {};
  const missing = Object.values(modules).filter((entry) => !entry?.installed);
  if (!missing.length) {
    return { state: "warn", text: "Warning" };
  }
  return { state: "fail", text: `${missing.length} missing` };
}

function createCrcTable() {
  const table = [];
  for (let i = 0; i < 256; i += 1) {
    let c = i;
    for (let k = 0; k < 8; k += 1) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[i] = c >>> 0;
  }
  return table;
}

const CRC_TABLE = createCrcTable();

function crc32(bytes) {
  let crc = 0 ^ -1;
  for (let i = 0; i < bytes.length; i += 1) {
    crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ bytes[i]) & 0xff];
  }
  return (crc ^ -1) >>> 0;
}

function createZip(entries) {
  const encoder = new TextEncoder();
  const fileChunks = [];
  const centralChunks = [];
  let offset = 0;

  entries.forEach((entry) => {
    const data = encoder.encode(entry.data);
    const nameBytes = encoder.encode(entry.name);
    const crc = crc32(data);

    const localHeader = new Uint8Array(30 + nameBytes.length);
    const view = new DataView(localHeader.buffer);
    view.setUint32(0, 0x04034b50, true);
    view.setUint16(4, 20, true);
    view.setUint16(6, 0, true);
    view.setUint16(8, 0, true);
    view.setUint16(10, 0, true);
    view.setUint16(12, 0, true);
    view.setUint32(14, crc, true);
    view.setUint32(18, data.length, true);
    view.setUint32(22, data.length, true);
    view.setUint16(26, nameBytes.length, true);
    view.setUint16(28, 0, true);
    localHeader.set(nameBytes, 30);
    fileChunks.push(localHeader, data);

    const centralHeader = new Uint8Array(46 + nameBytes.length);
    const cv = new DataView(centralHeader.buffer);
    cv.setUint32(0, 0x02014b50, true);
    cv.setUint16(4, 20, true);
    cv.setUint16(6, 20, true);
    cv.setUint16(8, 0, true);
    cv.setUint16(10, 0, true);
    cv.setUint16(12, 0, true);
    cv.setUint16(14, 0, true);
    cv.setUint32(16, crc, true);
    cv.setUint32(20, data.length, true);
    cv.setUint32(24, data.length, true);
    cv.setUint16(28, nameBytes.length, true);
    cv.setUint16(30, 0, true);
    cv.setUint16(32, 0, true);
    cv.setUint16(34, 0, true);
    cv.setUint16(36, 0, true);
    cv.setUint32(38, 0, true);
    cv.setUint32(42, offset, true);
    centralHeader.set(nameBytes, 46);
    centralChunks.push(centralHeader);

    offset += localHeader.length + data.length;
  });

  const centralSize = centralChunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const end = new Uint8Array(22);
  const ev = new DataView(end.buffer);
  ev.setUint32(0, 0x06054b50, true);
  ev.setUint16(4, 0, true);
  ev.setUint16(6, 0, true);
  ev.setUint16(8, entries.length, true);
  ev.setUint16(10, entries.length, true);
  ev.setUint32(12, centralSize, true);
  ev.setUint32(16, offset, true);
  ev.setUint16(20, 0, true);

  const chunks = [...fileChunks, ...centralChunks, end];
  const total = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const zipBytes = new Uint8Array(total);
  let cursor = 0;
  chunks.forEach((chunk) => {
    zipBytes.set(chunk, cursor);
    cursor += chunk.length;
  });
  return zipBytes;
}

function downloadZip(filename, entries) {
  const zipBytes = createZip(entries);
  const blob = new Blob([zipBytes], { type: "application/zip" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function exportReportsAllZip() {
  const payload = getExportPayload("reports");
  if (!payload) {
    showToast("No report data to export");
    return;
  }
  const options = buildReportDatasetOptions(payload);
  const entries = [];
  entries.push({
    name: "reports-full.json",
    data: JSON.stringify(payload, null, 2),
  });
  options.forEach((option) => {
    if (option.key === "__full__") return;
    const base = sanitizeFilename(option.key);
    const data = option.data;
    entries.push({
      name: `reports-${base}.json`,
      data: JSON.stringify(data, null, 2),
    });
    let rows = selectExportArray(data, { preferredKey: option.key, allowPrompt: false });
    if (!rows) {
      if (Array.isArray(data)) {
        rows = data;
      } else if (data && typeof data === "object") {
        rows = [data];
      }
    }
    if (rows && rows.length) {
      entries.push({
        name: `reports-${base}.csv`,
        data: toCsv(rows),
      });
    }
  });
  downloadZip("reports-export.zip", entries);
}

function renderActionPacks() {
  const container = document.getElementById("action-pack-list");
  if (!container) return;
  container.innerHTML = "";

  const filter = getActionPackFilter();
  const favorites = loadActionPackFavorites();
  const packs = getAllActionPacks().filter((pack) => {
    const tenantId = pack.tenant_id;
    if (filter === "favorites") {
      return favorites.has(pack.id);
    }
    if (filter === "global") {
      return !tenantId;
    }
    if (filter === "all") {
      return true;
    }
    if (!tenantId) return true;
    return tenantId === currentTenantId;
  });
  packs.sort((a, b) => {
    const favA = favorites.has(a.id) ? 1 : 0;
    const favB = favorites.has(b.id) ? 1 : 0;
    if (favA !== favB) return favB - favA;
    return (a.name || "").localeCompare(b.name || "");
  });

  const { pageIndex, totalPages, slice } = getActionPackPaging(packs);
  updateActionPackControls(pageIndex, totalPages);

  if (!slice.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No action packs available.";
    container.appendChild(empty);
    return;
  }

  slice.forEach((pack) => {
    const card = document.createElement("div");
    card.classList.add("action-pack-card");
    card.dataset.packId = pack.id;

    const title = document.createElement("div");
    title.classList.add("action-pack-title");
    title.textContent = pack.name;
    card.appendChild(title);

    const subtitle = document.createElement("div");
    subtitle.classList.add("action-pack-subtitle");
    subtitle.textContent = pack.description || "";
    card.appendChild(subtitle);

    const meta = document.createElement("div");
    meta.classList.add("pack-step-meta");
    const scopeLabel = document.createElement("span");
    scopeLabel.textContent = pack.tenant_id ? "Tenant" : "Global";
    meta.appendChild(scopeLabel);
    if (pack.tenant_id) {
      const tenantTag = document.createElement("span");
      tenantTag.textContent = pack.tenant_id.slice(0, 8);
      meta.appendChild(tenantTag);
    }
    card.appendChild(meta);

    const steps = document.createElement("div");
    steps.classList.add("action-pack-steps");
    pack.steps.forEach((step, index) => {
      const row = document.createElement("span");
      const badge = document.createElement("span");
      badge.classList.add("badge");
      badge.classList.add(step.optional ? "ps" : "graph");
      badge.textContent = step.optional ? "Optional" : "Step";
      const label = document.createElement("span");
      label.textContent = `${index + 1}. ${step.label || activityLabel(step.service, step.action)}`;
      row.appendChild(badge);
      row.appendChild(label);
      steps.appendChild(row);
    });
    card.appendChild(steps);

    const actions = document.createElement("div");
    actions.classList.add("action-pack-actions");
    const favorite = document.createElement("button");
    favorite.type = "button";
    favorite.classList.add("ghost", "small", "pack-favorite");
    if (favorites.has(pack.id)) {
      favorite.classList.add("active");
      favorite.textContent = "★ Favorite";
    } else {
      favorite.textContent = "☆ Favorite";
    }
    favorite.addEventListener("click", () => togglePackFavorite(pack.id));
    const edit = document.createElement("button");
    edit.type = "button";
    edit.classList.add("ghost", "small");
    edit.textContent = pack.builtin ? "Clone" : "Edit";
    edit.addEventListener("click", () => setPackBuilder(pack, { clone: pack.builtin }));
    const configure = document.createElement("button");
    configure.type = "button";
    configure.classList.add("ghost", "small");
    configure.textContent = "Configure";
    configure.addEventListener("click", () => selectActionPack(pack, { scroll: true }));
    const run = document.createElement("button");
    run.type = "button";
    run.classList.add("primary", "small", "action-pack-run");
    run.textContent = "Run";
    run.addEventListener("click", () => {
      selectActionPack(pack, { scroll: false });
      runSelectedActionPack();
    });
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.classList.add("ghost", "small", "action-pack-cancel");
    cancel.textContent = "Cancel";
    cancel.disabled = true;
    cancel.addEventListener("click", () => cancelActionPack(pack.id));
    actions.appendChild(favorite);
    actions.appendChild(edit);
    actions.appendChild(configure);
    actions.appendChild(run);
    actions.appendChild(cancel);
    card.appendChild(actions);

    container.appendChild(card);
  });
}

function renderActionPackHistory() {
  if (!actionPackHistoryList) return;
  const items = loadActionPackHistory();
  actionPackHistoryList.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("li");
    empty.classList.add("note");
    empty.textContent = "No action pack runs yet.";
    actionPackHistoryList.appendChild(empty);
    return;
  }
  items.forEach((entry) => {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = entry.pack_name || entry.packId;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = `${new Date(entry.timestamp).toLocaleString()} · ${entry.status}`;
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const rerun = document.createElement("button");
    rerun.type = "button";
    rerun.classList.add("ghost", "small");
    rerun.textContent = "Rerun";
    rerun.addEventListener("click", () => {
      const pack = getActionPackById(entry.packId);
      if (!pack) {
        showToast("Pack not found");
        return;
      }
      selectActionPack(pack, { scroll: true });
      setPackParams(pack.id, {
        stepParams: entry.stepParams || {},
        includeSteps: entry.includeSteps || {},
      });
      renderActionPackRunner(pack);
      runActionPack(pack, {
        stepParams: entry.stepParams || {},
        includeSteps: entry.includeSteps || {},
      });
    });
    actions.appendChild(rerun);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    actionPackHistoryList.appendChild(row);
  });
}

function renderActionPackRunner(pack) {
  if (!actionPackRunnerSteps) return;
  actionPackRunnerSteps.innerHTML = "";
  if (!pack) {
    if (actionPackRunnerTitle) {
      actionPackRunnerTitle.textContent = "Select a pack to configure";
    }
    if (actionPackRunnerSteps) {
      actionPackRunnerSteps.innerHTML = "";
      const note = document.createElement("div");
      note.classList.add("note");
      note.textContent = "Choose an action pack to load its steps.";
      actionPackRunnerSteps.appendChild(note);
    }
    if (actionPackRunButton) actionPackRunButton.disabled = true;
    if (actionPackRunCancelButton) actionPackRunCancelButton.disabled = true;
    return;
  }
  if (actionPackRunnerTitle) {
    actionPackRunnerTitle.textContent = `${pack.name} · ${pack.tenant_id ? "Tenant" : "Global"}`;
  }
  const saved = getPackParams(pack.id);
  pack.steps.forEach((step) => {
    const meta = ACTIONS_UI?.[step.service]?.[step.action];
    const stepKey = `${step.service}.${step.action}`;
    const defaults = getActionPackStepDefaults(pack, step) || {};
    const baseParams = { ...defaults, ...(step.params || {}), ...(saved.stepParams?.[stepKey] || {}) };
    const includeDefault = saved.includeSteps?.[stepKey];
    const stepWrap = document.createElement("div");
    stepWrap.classList.add("pack-step");
    stepWrap.dataset.stepKey = stepKey;
    stepWrap.dataset.service = step.service;
    stepWrap.dataset.action = step.action;

    const header = document.createElement("div");
    header.classList.add("pack-step-header");
    const title = document.createElement("div");
    title.classList.add("pack-step-title");
    title.textContent = step.label || activityLabel(step.service, step.action);
    const metaWrap = document.createElement("div");
    metaWrap.classList.add("pack-step-meta");
    const modeLabel = document.createElement("span");
    modeLabel.textContent = meta?.mode === "powershell" ? "PowerShell" : "Graph";
    metaWrap.appendChild(modeLabel);
    if (step.optional) {
      const includeLabel = document.createElement("label");
      includeLabel.classList.add("field", "checkbox");
      const includeInput = document.createElement("input");
      includeInput.type = "checkbox";
      includeInput.classList.add("pack-step-include");
      includeInput.checked = includeDefault !== undefined ? includeDefault : true;
      includeLabel.appendChild(includeInput);
      includeLabel.appendChild(document.createTextNode("Include"));
      metaWrap.appendChild(includeLabel);
    }
    header.appendChild(title);
    header.appendChild(metaWrap);
    stepWrap.appendChild(header);

    const fieldsWrap = document.createElement("div");
    fieldsWrap.classList.add("pack-step-fields");
    const fields = meta?.fields || [];
    if (!fields.length) {
      const note = document.createElement("div");
      note.classList.add("note");
      note.textContent = "No inputs required.";
      fieldsWrap.appendChild(note);
    }
    fields.forEach((field) => {
      const fieldWrap = document.createElement("label");
      fieldWrap.classList.add("field");
      fieldWrap.dataset.field = field.key;
      fieldWrap.textContent = field.label;
      let input;
      if (field.type === "textarea") {
        input = document.createElement("textarea");
        input.rows = 3;
      } else {
        input = document.createElement("input");
        input.type = field.type || "text";
      }
      if (field.placeholder) {
        input.placeholder = field.placeholder;
      }
      const value = baseParams[field.key];
      if (field.type === "checkbox") {
        input.type = "checkbox";
        input.checked = Boolean(value ?? field.defaultChecked);
      } else if (value !== undefined && value !== null) {
        input.value = value;
      }
      fieldWrap.appendChild(input);
      fieldsWrap.appendChild(fieldWrap);
    });
    stepWrap.appendChild(fieldsWrap);
    actionPackRunnerSteps.appendChild(stepWrap);
  });
}

function selectActionPack(pack, options = {}) {
  if (!pack) return;
  selectedPackId = pack.id;
  renderActionPackRunner(pack);
  const running = actionPackState.has(pack.id);
  if (actionPackRunButton) actionPackRunButton.disabled = running ? true : false;
  if (actionPackRunCancelButton) actionPackRunCancelButton.disabled = !running;
  if (options.scroll && actionPackRunnerSteps) {
    actionPackRunnerSteps.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function collectActionPackRunnerParams(pack) {
  const stepParams = {};
  const includeSteps = {};
  if (!actionPackRunnerSteps) return { stepParams, includeSteps };
  actionPackRunnerSteps.querySelectorAll(".pack-step").forEach((stepEl) => {
    const stepKey = stepEl.dataset.stepKey;
    const params = {};
    stepEl.querySelectorAll(".field").forEach((fieldEl) => {
      const key = fieldEl.dataset.field;
      const input = fieldEl.querySelector("input, textarea, select");
      if (!input || !key) return;
      if (input.type === "checkbox") {
        if (input.checked) params[key] = true;
        return;
      }
      const value = input.value.trim();
      if (value !== "") {
        if (input.type === "number") {
          const num = Number(value);
          params[key] = Number.isNaN(num) ? value : num;
        } else {
          params[key] = value;
        }
      }
    });
    stepParams[stepKey] = params;
    const includeInput = stepEl.querySelector(".pack-step-include");
    if (includeInput) {
      includeSteps[stepKey] = includeInput.checked;
    }
  });
  return { stepParams, includeSteps };
}

function runSelectedActionPack() {
  if (!selectedPackId) {
    showToast("Select a pack first");
    return;
  }
  const pack = getActionPackById(selectedPackId);
  if (!pack) {
    showToast("Pack not found");
    return;
  }
  const params = collectActionPackRunnerParams(pack);
  setPackParams(pack.id, params);
  runActionPack(pack, params);
}

function renderReportPresets() {
  if (!reportPresetsList) return;
  reportPresetsList.innerHTML = "";
  const presets = getAllReportPresets();
  presets.forEach((preset) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.classList.add("chip", "report-preset");
    chip.dataset.reportPreset = preset.id;
    chip.textContent = preset.label;
    chip.addEventListener("click", (event) => {
      if (event.shiftKey) {
        queueReportPreset(preset);
        return;
      }
      runReportPreset(preset);
    });
    reportPresetsList.appendChild(chip);
  });
}

function renderReportHistory() {
  if (!reportHistoryList) return;
  const items = loadReportHistory();
  reportHistoryList.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("li");
    empty.classList.add("note");
    empty.textContent = "No report history yet.";
    reportHistoryList.appendChild(empty);
    return;
  }
  items.forEach((entry) => {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = entry.label || entry.action;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = `${new Date(entry.timestamp).toLocaleString()}`;
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const useA = document.createElement("button");
    useA.type = "button";
    useA.classList.add("ghost", "small");
    useA.textContent = "Use as A";
    useA.addEventListener("click", () => {
      if (reportDiffSelectA) {
        reportDiffSelectA.value = entry.id;
      }
      runReportDiff();
    });
    const useB = document.createElement("button");
    useB.type = "button";
    useB.classList.add("ghost", "small");
    useB.textContent = "Use as B";
    useB.addEventListener("click", () => {
      if (reportDiffSelectB) {
        reportDiffSelectB.value = entry.id;
      }
      runReportDiff();
    });
    actions.appendChild(useA);
    actions.appendChild(useB);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    reportHistoryList.appendChild(row);
  });
  renderReportDiffSelects(items);
}

function renderReportDiffSelects(items) {
  if (!reportDiffSelectA || !reportDiffSelectB) return;
  const fill = (select) => {
    const current = select.value;
    select.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a run";
    select.appendChild(placeholder);
    items.forEach((entry) => {
      const option = document.createElement("option");
      option.value = entry.id;
      option.textContent = `${entry.label || entry.action} · ${new Date(entry.timestamp).toLocaleTimeString()}`;
      select.appendChild(option);
    });
    if (current) {
      select.value = current;
    }
  };
  fill(reportDiffSelectA);
  fill(reportDiffSelectB);
}

function formatDiffSummary(summary) {
  if (!summary) return "";
  return JSON.stringify(summary, null, 2);
}

function getDiffKey(item) {
  if (!item || typeof item !== "object") return null;
  return item.id || item.userPrincipalName || item.mail || item.name || item.displayName || null;
}

function diffArrays(a, b) {
  const mapA = new Map();
  const mapB = new Map();
  a.forEach((item, idx) => {
    const key = getDiffKey(item) || `idx-${idx}`;
    mapA.set(key, item);
  });
  b.forEach((item, idx) => {
    const key = getDiffKey(item) || `idx-${idx}`;
    mapB.set(key, item);
  });
  const added = [];
  const removed = [];
  const changed = [];
  mapB.forEach((value, key) => {
    if (!mapA.has(key)) {
      added.push({ key, item: value });
    } else {
      const prev = mapA.get(key);
      if (JSON.stringify(prev) !== JSON.stringify(value)) {
        changed.push({ key, before: prev, after: value });
      }
    }
  });
  mapA.forEach((value, key) => {
    if (!mapB.has(key)) {
      removed.push({ key, item: value });
    }
  });
  return { added, removed, changed };
}

function diffObjects(a, b) {
  const keys = new Set([...Object.keys(a || {}), ...Object.keys(b || {})]);
  const added = [];
  const removed = [];
  const changed = [];
  keys.forEach((key) => {
    if (!(key in (a || {}))) {
      added.push(key);
    } else if (!(key in (b || {}))) {
      removed.push(key);
    } else if (JSON.stringify(a[key]) !== JSON.stringify(b[key])) {
      changed.push(key);
    }
  });
  return { added, removed, changed };
}

function buildReportDiff(a, b) {
  if (Array.isArray(a) && Array.isArray(b)) {
    const diff = diffArrays(a, b);
    return {
      type: "array",
      summary: {
        added: diff.added.length,
        removed: diff.removed.length,
        changed: diff.changed.length,
      },
      details: {
        added: diff.added.slice(0, 5),
        removed: diff.removed.slice(0, 5),
        changed: diff.changed.slice(0, 5),
      },
    };
  }
  if (a && b && typeof a === "object" && typeof b === "object") {
    const diff = diffObjects(a, b);
    return {
      type: "object",
      summary: {
        added: diff.added.length,
        removed: diff.removed.length,
        changed: diff.changed.length,
      },
      details: {
        added: diff.added.slice(0, 10),
        removed: diff.removed.slice(0, 10),
        changed: diff.changed.slice(0, 10),
      },
    };
  }
  const changed = JSON.stringify(a) !== JSON.stringify(b);
  return {
    type: "scalar",
    summary: { changed },
    details: { before: a, after: b },
  };
}

function runReportDiff() {
  if (!reportDiffSelectA || !reportDiffSelectB) return;
  const idA = reportDiffSelectA.value;
  const idB = reportDiffSelectB.value;
  if (!idA || !idB) {
    if (reportDiffMeta) reportDiffMeta.textContent = "Select two runs to compare.";
    if (reportDiffOutput) reportDiffOutput.textContent = "";
    return;
  }
  const items = loadReportHistory();
  const entryA = items.find((entry) => entry.id === idA);
  const entryB = items.find((entry) => entry.id === idB);
  if (!entryA || !entryB) return;
  const diff = buildReportDiff(entryA.data, entryB.data);
  if (reportDiffMeta) {
    reportDiffMeta.innerHTML = "";
    const header = document.createElement("span");
    header.textContent = `${entryA.label || entryA.action} ↔ ${entryB.label || entryB.action}`;
    const summary = diff.summary || {};
    const added = document.createElement("span");
    added.classList.add("diff-added");
    added.textContent = `Added: ${summary.added ?? ""}`;
    const removed = document.createElement("span");
    removed.classList.add("diff-removed");
    removed.textContent = `Removed: ${summary.removed ?? ""}`;
    const changed = document.createElement("span");
    changed.classList.add("diff-change");
    const changedValue = summary.changed ?? (summary.changed === false ? "false" : "");
    changed.textContent = `Changed: ${changedValue}`;
    reportDiffMeta.appendChild(header);
    reportDiffMeta.appendChild(document.createTextNode(" · "));
    reportDiffMeta.appendChild(added);
    reportDiffMeta.appendChild(document.createTextNode(" · "));
    reportDiffMeta.appendChild(removed);
    reportDiffMeta.appendChild(document.createTextNode(" · "));
    reportDiffMeta.appendChild(changed);
  }
  if (reportDiffOutput) {
    reportDiffOutput.textContent = formatDiffSummary(diff);
  }
}

function enqueueReport(job) {
  reportQueue.push(job);
  renderReportQueue();
  processReportQueue();
}

function renderReportQueue() {
  if (!reportQueueList) return;
  reportQueueList.innerHTML = "";
  if (currentReportJob) {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = currentReportJob.label || currentReportJob.action;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = "Running";
    row.appendChild(title);
    row.appendChild(meta);
    reportQueueList.appendChild(row);
  }
  if (!reportQueue.length && !currentReportJob) {
    const empty = document.createElement("li");
    empty.classList.add("note");
    empty.textContent = "No queued reports.";
    reportQueueList.appendChild(empty);
    return;
  }
  reportQueue.forEach((job, index) => {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = job.label || job.action;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = job.status || "Queued";
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      reportQueue.splice(index, 1);
      renderReportQueue();
    });
    actions.appendChild(remove);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    reportQueueList.appendChild(row);
  });
}

async function processReportQueue() {
  if (reportQueueState.running || reportQueueState.cancelled) return;
  if (!reportQueue.length) return;
  reportQueueState.running = true;
  while (reportQueue.length) {
    if (reportQueueState.cancelled) break;
    const job = reportQueue.shift();
    if (!job) continue;
    job.status = "Running";
    currentReportJob = job;
    renderReportQueue();
    const controller = new AbortController();
    reportQueueState.controller = controller;
    const result = await runAction(job.service, job.action, job.params || {}, {
      controller,
      track: false,
    });
    if (result?.cancelled) {
      break;
    }
    currentReportJob = null;
  }
  reportQueueState.running = false;
  reportQueueState.cancelled = false;
  reportQueueState.controller = null;
  renderReportQueue();
}

function stopReportQueue() {
  reportQueueState.cancelled = true;
  if (reportQueueState.controller) {
    reportQueueState.controller.abort();
  }
  reportQueueState.running = false;
  currentReportJob = null;
  renderReportQueue();
}
function renderQuickActions() {
  if (!quickActionsGrid) return;
  let list = loadQuickActions();
  list = list.filter((item) => {
    if (item.type === "template") {
      const tmpl = getTemplateById(item.templateId);
      return tmpl && ACTIONS_UI?.[tmpl.service]?.[tmpl.action];
    }
    return ACTIONS_UI?.[item.service]?.[item.action];
  });
  quickActionsGrid.innerHTML = "";
  if (!list.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No quick actions pinned.";
    quickActionsGrid.appendChild(empty);
    return;
  }
  list.forEach((item) => {
    const type = item.type || "action";
    let service = item.service;
    let action = item.action;
    let labelText = "";
    let templateId = null;
    if (type === "template") {
      templateId = item.templateId;
      const tmpl = getTemplateById(templateId);
      if (!tmpl) return;
      service = tmpl.service;
      action = tmpl.action;
      labelText = tmpl.name || `${tmpl.service}.${tmpl.action}`;
    } else {
      labelText = resolveActionLabel(service, action);
    }
    const chip = document.createElement("button");
    chip.type = "button";
    chip.classList.add("chip");
    chip.dataset.type = type;
    if (type === "template") {
      chip.dataset.templateId = templateId;
    } else {
      chip.dataset.service = service;
      chip.dataset.action = action;
    }

    const label = document.createElement("span");
    label.textContent = labelText;
    chip.appendChild(label);

    const remove = document.createElement("span");
    remove.classList.add("chip-remove");
    remove.dataset.type = type;
    if (type === "template") {
      remove.dataset.templateId = templateId;
    } else {
      remove.dataset.service = service;
      remove.dataset.action = action;
    }
    remove.setAttribute("role", "button");
    remove.setAttribute("tabindex", "0");
    remove.setAttribute("aria-label", "Remove quick action");
    remove.textContent = "×";
    chip.appendChild(remove);

    quickActionsGrid.appendChild(chip);
  });

  decorateChips();
}

function setQuickActionsEditing(enabled) {
  if (!quickActionsCard) return;
  quickActionsCard.classList.toggle("editing", enabled);
  if (quickActionsEditButton) {
    quickActionsEditButton.textContent = enabled ? "Done" : "Edit";
  }
}

function setConfigLocked(locked) {
  configLocked = locked;
  const fields = [
    cfgTenantId,
    cfgClientId,
    cfgClientSecret,
    cfgGraphUserId,
    cfgOnedriveDriveId,
    cfgSpoAdminUrl,
    cfgPsAuthMode,
    cfgPsUpn,
    cfgPsOrg,
    cfgAzureTenantId,
    cfgAzureSubscriptionId,
    cfgUseKeychain,
    profileSaveButton,
    profileApplyButton,
    profileDeleteButton,
    profileExportButton,
    profileImportButton,
  ];
  fields.forEach((field) => {
    if (!field) return;
    field.disabled = locked;
  });
  if (saveConfigButton) {
    saveConfigButton.disabled = locked;
  }
  if (cfgLockNote) {
    cfgLockNote.textContent = locked ? "Locked" : "Unlocked";
    cfgLockNote.classList.toggle("warn", locked);
  }
  document.body.classList.toggle("config-locked", locked);
}

function renderKeychainStatus() {
  if (!cfgUseKeychain || !cfgKeychainStatus) return;
  const enabled = Boolean(cfgUseKeychain.checked);
  if (!keychainAvailable) {
    cfgKeychainStatus.textContent = "Keychain unavailable";
    cfgKeychainStatus.classList.add("warn");
    cfgUseKeychain.disabled = true;
    return;
  }
  cfgKeychainStatus.textContent = enabled ? "Keychain enabled" : "Keychain available";
  cfgKeychainStatus.classList.remove("warn");
  cfgUseKeychain.disabled = configLocked;
}

function renderTenantInfo(data, error) {
  if (!tenantName || !tenantDomains || !tenantIdField) return;
  tenantDomains.innerHTML = "";
  if (error) {
    tenantName.textContent = "Unavailable";
    tenantIdField.textContent = "";
    const li = document.createElement("li");
    li.className = "tenant-domain";
    li.textContent = "Tenant info unavailable.";
    tenantDomains.appendChild(li);
    return;
  }
  if (!data || !data.display_name) {
    tenantName.textContent = "Not loaded";
    tenantIdField.textContent = "";
    const li = document.createElement("li");
    li.className = "tenant-domain";
    li.textContent = "Click Refresh to load tenant info.";
    tenantDomains.appendChild(li);
    return;
  }
  tenantName.textContent = data.display_name || "Unknown tenant";
  tenantIdField.textContent = data.tenant_id ? `Tenant ID: ${data.tenant_id}` : "";
  const domains = Array.isArray(data.verified_domains) ? data.verified_domains : [];
  if (!domains.length) {
    const li = document.createElement("li");
    li.className = "tenant-domain";
    li.textContent = "No verified domains returned.";
    tenantDomains.appendChild(li);
    return;
  }
  domains.forEach((domain) => {
    const li = document.createElement("li");
    li.className = "tenant-domain";
    const name = document.createElement("span");
    name.textContent = domain.name || "unknown";
    const tags = document.createElement("div");
    tags.className = "domain-tags";
    if (domain.is_default) {
      const tag = document.createElement("span");
      tag.className = "domain-tag ok";
      tag.textContent = "default";
      tags.appendChild(tag);
    }
    if (domain.is_verified) {
      const tag = document.createElement("span");
      tag.className = "domain-tag ok";
      tag.textContent = "verified";
      tags.appendChild(tag);
    }
    if (domain.is_initial) {
      const tag = document.createElement("span");
      tag.className = "domain-tag";
      tag.textContent = "initial";
      tags.appendChild(tag);
    }
    if (domain.type) {
      const tag = document.createElement("span");
      tag.className = "domain-tag";
      tag.textContent = domain.type;
      tags.appendChild(tag);
    }
    li.appendChild(name);
    li.appendChild(tags);
    tenantDomains.appendChild(li);
  });
}

async function loadTenantInfo(options = {}) {
  if (tenantInfoLoading) return;
  if (!currentTenantId || !cfgClientId?.value.trim()) {
    renderTenantInfo(null);
    return;
  }
  tenantInfoLoading = true;
  if (refreshTenantInfoButton) {
    refreshTenantInfoButton.disabled = true;
  }
  try {
    const res = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service: "system", action: "tenant_info", params: {} }),
    });
    const data = await res.json();
    if (!data.ok) {
      throw new Error(data.error || "Tenant info failed");
    }
    renderTenantInfo(data.data || {});
  } catch (err) {
    renderTenantInfo(null, err);
    if (!options.silent) {
      showToast("Tenant info failed");
    }
  } finally {
    tenantInfoLoading = false;
    if (refreshTenantInfoButton) {
      refreshTenantInfoButton.disabled = false;
    }
  }
}

async function updateConfigPartial(payload, successMessage) {
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Config update failed");
      return false;
    }
    await fetchConfig();
    fetchStatus();
    resetPreflightCache();
    if (successMessage) {
      showToast(successMessage);
    }
    return true;
  } catch (err) {
    showToast("Config update failed");
    return false;
  }
}

function getConfigPayloadFromForm() {
  const payload = {
    tenant_id: cfgTenantId?.value.trim(),
    client_id: cfgClientId?.value.trim(),
    graph_user_id: cfgGraphUserId?.value.trim(),
    onedrive_drive_id: cfgOnedriveDriveId?.value.trim(),
    spo_admin_url: cfgSpoAdminUrl?.value.trim(),
    ps_auth_mode: cfgPsAuthMode?.value || "interactive",
    ps_user_principal_name: cfgPsUpn?.value.trim(),
    ps_org: cfgPsOrg?.value.trim(),
    azure_tenant_id: cfgAzureTenantId?.value.trim(),
    azure_subscription_id: cfgAzureSubscriptionId?.value.trim(),
  };
  const secret = cfgClientSecret?.value.trim();
  if (secret) {
    payload.client_secret = secret;
  }
  return payload;
}

function applyConfigToForm(config) {
  cfgTenantId.value = config.tenant_id || "";
  cfgClientId.value = config.client_id || "";
  cfgGraphUserId.value = config.graph_user_id || "";
  cfgOnedriveDriveId.value = config.onedrive_drive_id || "";
  cfgSpoAdminUrl.value = config.spo_admin_url || "";
  cfgPsAuthMode.value = config.ps_auth_mode || "interactive";
  cfgPsUpn.value = config.ps_user_principal_name || "";
  cfgPsOrg.value = config.ps_org || "";
  cfgAzureTenantId.value = config.azure_tenant_id || "";
  cfgAzureSubscriptionId.value = config.azure_subscription_id || "";
  cfgClientSecret.value = config.client_secret || "";
  if (!config.client_secret && cfgClientSecret.placeholder.includes("set")) {
    cfgClientSecret.placeholder = "Enter to update";
  }
}

function normalizeProfileConfig(config) {
  const normalized = {};
  Object.values(PROFILE_ENV_MAP).forEach((key) => {
    if (config[key] !== undefined) {
      normalized[key] = config[key];
    }
  });
  return normalized;
}

function loadProfiles() {
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) {
      return parsed.filter((profile) => profile?.name && profile?.config);
    }
  } catch (err) {
    return [];
  }
  return [];
}

function saveProfiles(profiles) {
  localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profiles));
}

function renderProfileSelect() {
  if (!profileSelect) return;
  const profiles = loadProfiles();
  profileSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = profiles.length ? "Select a profile" : "No saved profiles";
  profileSelect.appendChild(placeholder);
  profiles.forEach((profile) => {
    const option = document.createElement("option");
    option.value = profile.name;
    option.textContent = profile.name;
    profileSelect.appendChild(option);
  });
}

function getProfileByName(name) {
  const profiles = loadProfiles();
  return profiles.find((profile) => profile.name === name);
}

function upsertProfile(name, config) {
  const profiles = loadProfiles();
  const idx = profiles.findIndex((profile) => profile.name === name);
  const entry = { name, config: normalizeProfileConfig(config) };
  if (idx >= 0) {
    profiles[idx] = entry;
  } else {
    profiles.push(entry);
  }
  saveProfiles(profiles);
  renderProfileSelect();
}

function deleteProfile(name) {
  const profiles = loadProfiles().filter((profile) => profile.name !== name);
  saveProfiles(profiles);
  renderProfileSelect();
}

function parseEnvContent(content) {
  const config = {};
  content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"))
    .forEach((line) => {
      const idx = line.indexOf("=");
      if (idx === -1) return;
      const key = line.slice(0, idx).trim();
      let value = line.slice(idx + 1).trim();
      if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      const target = PROFILE_ENV_MAP[key];
      if (target) {
        config[target] = value;
      }
    });
  return config;
}

function formatEnv(profile) {
  const reverse = Object.entries(PROFILE_ENV_MAP).reduce((acc, [envKey, cfgKey]) => {
    acc[cfgKey] = envKey;
    return acc;
  }, {});
  const lines = Object.keys(reverse)
    .map((cfgKey) => {
      const envKey = reverse[cfgKey];
      const value = profile.config?.[cfgKey];
      if (!value) return null;
      return `${envKey}=${value}`;
    })
    .filter(Boolean);
  return lines.join("\n") + "\n";
}

function downloadFile(filename, content) {
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function loadTemplates() {
  try {
    const raw = localStorage.getItem(TEMPLATE_STORAGE_KEY);
    if (raw === null) {
      localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(DEFAULT_TEMPLATES));
      return DEFAULT_TEMPLATES.slice();
    }
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) {
      return parsed.filter((tmpl) => tmpl?.id && tmpl?.service && tmpl?.action);
    }
  } catch (err) {
    return DEFAULT_TEMPLATES.slice();
  }
  return DEFAULT_TEMPLATES.slice();
}

function saveTemplates(templates) {
  localStorage.setItem(TEMPLATE_STORAGE_KEY, JSON.stringify(templates));
}

function generateTemplateId() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `template-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function upsertTemplate(template) {
  const templates = loadTemplates();
  const idx = templates.findIndex((item) => item.id === template.id);
  if (idx >= 0) {
    templates[idx] = template;
  } else {
    templates.push(template);
  }
  saveTemplates(templates);
}

function getTemplateById(id) {
  return loadTemplates().find((tmpl) => tmpl.id === id);
}

function renderTemplateSelect() {
  if (!quickActionTemplateSelect) return;
  const templates = loadTemplates().filter((tmpl) => ACTIONS_UI?.[tmpl.service]?.[tmpl.action]);
  quickActionTemplateSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = templates.length ? "Select template" : "No templates";
  quickActionTemplateSelect.appendChild(placeholder);
  templates.forEach((tmpl) => {
    const option = document.createElement("option");
    option.value = tmpl.id;
    option.textContent = tmpl.name || `${tmpl.service}.${tmpl.action}`;
    quickActionTemplateSelect.appendChild(option);
  });
}

function resetPreflightCache() {
  Object.keys(graphPreflightCache).forEach((key) => delete graphPreflightCache[key]);
  Object.keys(powershellPreflightCache).forEach((key) => delete powershellPreflightCache[key]);
}

async function runSystemTask(action, params) {
  const res = await fetch("/api/task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service: "system", action, params }),
  });
  const data = await res.json();
  return data;
}

async function runHealthCheck() {
  if (healthCheckButton) {
    healthCheckButton.disabled = true;
    healthCheckButton.textContent = "Running...";
  }
  const healthCard = document.getElementById("health-card");
  if (healthCard) healthCard.classList.add("loading");
  if (healthSpinner) healthSpinner.classList.add("active");
  if (healthStatusText) {
    healthStatusText.textContent = `Started ${new Date().toLocaleTimeString()}`;
  }
  if (healthBreakdown) {
    healthBreakdown.open = true;
  }
  resetHealthBreakdown();
  let graphProgressText = "Starting";
  let psProgressText = "Pending";
  let graphProgressState = "warn";
  let psProgressState = "warn";
  setOutputStatus("health", {
    state: "running",
    text: "Health check running",
    meta: "Elapsed 0.0s",
    running: true,
  });
  startOutputTimer("health", "Health check");
  setHealthProgress([
    { label: "Graph", text: graphProgressText, state: graphProgressState },
    { label: "PowerShell", text: psProgressText, state: psProgressState },
  ]);
  setOutput("health", "Running health check... Please wait.");
  showToast("Running health check...");
  try {
    const graphChecks = {};
    const total = GRAPH_HEALTH_SERVICES.length;
    for (let i = 0; i < total; i += 1) {
      const service = GRAPH_HEALTH_SERVICES[i];
      const label = formatServiceLabel(service);
      graphProgressText = `Checking ${label} (${i + 1}/${total})`;
      setHealthProgress([
        { label: "Graph", text: graphProgressText, state: "warn" },
        { label: "PowerShell", text: psProgressText, state: psProgressState },
      ]);
      upsertHealthListItem(healthGraphList, service, label, "Running", "warn");
      const response = await runSystemTask("graph_check", { service });
      let check = null;
      if (!response.ok) {
        check = {
          ok: false,
          status: response.status_code,
          message: response.error,
        };
      } else {
        check = response.data?.checks?.[service] || {
          ok: false,
          message: "No response",
        };
      }
      graphChecks[service] = check;
      const status = Number(check?.status || 0);
      const latencyMs = Number(check?.latency_ms ?? check?.latencyMs);
      const sla = getLatencySla(Number.isFinite(latencyMs) ? latencyMs : undefined, check?.ok);
      let statusLabel = "Failed";
      let statusState = "fail";
      let statusMeta = "";
      if (check.ok) {
        statusLabel = "OK";
        statusState = "ok";
        if (sla.state && sla.state !== "ok") {
          statusLabel = sla.label;
          statusState = sla.state;
        }
        statusMeta = buildHealthMeta({ status: status || 200, latencyMs, slaLabel: sla.label });
      } else if (status >= 500) {
        statusLabel = "Transient";
        statusState = "warn";
        statusMeta = buildHealthMeta({
          status,
          latencyMs,
          slaLabel: sla.label,
          message: check?.message || "",
        });
      } else {
        statusMeta = buildHealthMeta({
          status: status || undefined,
          latencyMs,
          slaLabel: sla.label,
          message: check?.message || check?.error || "",
        });
      }
      upsertHealthListItem(healthGraphList, service, label, statusLabel, statusState, statusMeta);
      graphProgressText = `Checked ${label}: ${statusLabel}`;
      setHealthProgress([
        { label: "Graph", text: graphProgressText, state: statusState },
        { label: "PowerShell", text: psProgressText, state: psProgressState },
      ]);
    }

    graphProgressText = "Complete";
    const graphOk = Object.values(graphChecks).every((check) => check?.ok);
    const graphSummary = summarizeGraphCheck({ ok: graphOk, checks: graphChecks });
    graphProgressState = graphSummary.state;

    const degradedServices = Object.entries(graphChecks)
      .filter(([, check]) => {
        const status = Number(check?.status || 0);
        const latencyMs = Number(check?.latency_ms ?? check?.latencyMs);
        const sla = getLatencySla(Number.isFinite(latencyMs) ? latencyMs : undefined, check?.ok);
        const latencyDegraded = Boolean(check?.ok) && sla.state === "fail";
        return status >= 500 || latencyDegraded;
      })
      .map(([service]) => formatServiceLabel(service));
    if (degradedServices.length) {
      showGraphStatusBanner(
        `Graph reports degraded status for ${degradedServices.join(", ")}.`,
        `Last checked ${new Date().toLocaleTimeString()}`
      );
    } else {
      hideGraphStatusBanner();
    }

    psProgressText = "Checking modules";
    psProgressState = "warn";
    setHealthProgress([
      { label: "Graph", text: graphSummary.text, state: graphSummary.state },
      { label: "PowerShell", text: psProgressText, state: psProgressState },
    ]);

    const modules = Object.values(POWERSHELL_MODULES_BY_SERVICE)
      .flat()
      .filter((item, idx, arr) => arr.indexOf(item) === idx);
    const psResponse = await runSystemTask("check_powershell_modules", { modules });
    let psData = null;
    if (!psResponse.ok) {
      psData = { ok: false, modules: {} };
      modules.forEach((module) => {
        upsertHealthListItem(
          healthPowerShellList,
          module,
          module,
          "Error",
          "fail",
          psResponse.error || "Check failed"
        );
      });
    } else {
      psData = psResponse.data || { ok: false, modules: {} };
      Object.entries(psData.modules || {}).forEach(([module, info]) => {
        if (info?.installed) {
          upsertHealthListItem(
            healthPowerShellList,
            module,
            module,
            "OK",
            "ok",
            info?.version ? `v${info.version}` : ""
          );
        } else {
          upsertHealthListItem(
            healthPowerShellList,
            module,
            module,
            "Missing",
            "fail",
            info?.error || ""
          );
        }
      });
    }
    const psSummary = summarizePowerShellCheck(psData);
    psProgressText = psSummary.text;
    psProgressState = psSummary.state;
    setHealthProgress([
      { label: "Graph", text: graphSummary.text, state: graphSummary.state },
      { label: "PowerShell", text: psSummary.text, state: psSummary.state },
    ]);

    const report = {
      graph: { ok: graphSummary.state === "ok", checks: graphChecks },
      powershell: psData,
    };
    setOutput("health", report);
    addActivity("Ran: Health check");
    const finalState =
      graphSummary.state === "fail" || psSummary.state === "fail"
        ? "fail"
        : graphSummary.state === "warn" || psSummary.state === "warn"
          ? "warn"
          : "ok";
    const healthElapsed = outputStartTimes.has("health")
      ? formatElapsed(performance.now() - outputStartTimes.get("health"))
      : "";
    setOutputStatus("health", {
      state: finalState,
      text: "Health check complete",
      meta: healthElapsed ? `Duration ${healthElapsed}` : "",
      running: false,
    });
    if (healthStatusText) {
      healthStatusText.textContent =
        graphSummary.state === "fail" || psSummary.state === "fail" ? "Completed with issues" : "Complete";
    }
    showToast("Health check complete");
    return { ok: true, data: report };
  } catch (err) {
    setOutput("health", `Error: ${err.message}`);
    addActivity("Health check error");
    if (healthStatusText) healthStatusText.textContent = "Error";
    setHealthProgress([
      { label: "Graph", text: "Error", state: "fail" },
      { label: "PowerShell", text: "Error", state: "fail" },
    ]);
    upsertHealthListItem(healthGraphList, "graph-error", "Graph", "Error", "fail", err.message);
    upsertHealthListItem(healthPowerShellList, "ps-error", "PowerShell", "Error", "fail", err.message);
    setOutputStatus("health", {
      state: "fail",
      text: "Health check error",
      meta: err.message || "Error",
      running: false,
    });
    return { ok: false, error: err };
  } finally {
    stopOutputTimer("health");
    if (healthCheckButton) {
      healthCheckButton.disabled = false;
      healthCheckButton.textContent = "Run health check";
    }
    const healthCard = document.getElementById("health-card");
    if (healthCard) healthCard.classList.remove("loading");
    if (healthSpinner) healthSpinner.classList.remove("active");
  }
}

async function preflightPowerShell(service) {
  if (powershellPreflightCache[service]) {
    return { ok: true, cached: true };
  }
  const modules = POWERSHELL_MODULES_BY_SERVICE[service] || [];
  if (!modules.length) {
    return { ok: true };
  }
  const response = await runSystemTask("check_powershell_modules", { service, modules });
  if (!response.ok) {
    return { ok: false, data: response };
  }
  if (!response.data.ok) {
    return { ok: false, data: response.data };
  }
  powershellPreflightCache[service] = true;
  return { ok: true };
}

async function preflightGraph(service) {
  if (graphPreflightCache[service]) {
    return { ok: true, cached: true };
  }
  const response = await runSystemTask("graph_check", { service });
  if (!response.ok) {
    return { ok: false, data: response };
  }
  const check = response.data?.checks?.[service];
  if (!check?.ok) {
    const status = Number(check?.status || 0);
    if (status >= 500) {
      return { ok: true, warning: check };
    }
    return { ok: false, data: response.data };
  }
  graphPreflightCache[service] = true;
  return { ok: true };
}

async function preflightAction(service, action) {
  if (service === "system") return { ok: true };
  const meta = ACTIONS_UI?.[service]?.[action];
  if (!meta) return { ok: true };
  const targetService = meta.preflightService || service;
  if (meta.mode === "powershell") {
    return preflightPowerShell(targetService);
  }
  if (meta.mode === "graph") {
    return preflightGraph(targetService);
  }
  return { ok: true };
}

function handlePreflightFailure(service, action, details) {
  const label = activityLabel(service, action);
  setOutput(service, {
    ok: false,
    error: "Preflight failed",
    details,
  });
  setOutputStatus(service, {
    state: "fail",
    text: `${label} preflight failed`,
    meta: "Check permissions and health",
    running: false,
  });
  addActivity(`Preflight failed: ${label}`);
  showToast("Preflight failed");
}

function handlePreflightWarning(service, action, warning) {
  const label = activityLabel(service, action);
  const status = warning?.status ? `HTTP ${warning.status}` : "HTTP 5xx";
  const code = warning?.code ? ` · ${warning.code}` : "";
  const requestId = warning?.request_id ? ` · req ${warning.request_id}` : "";
  const message = warning?.message || warning?.error || "Transient Graph error detected.";
  showWarningBanner(
    `Preflight warning for ${label}: ${status}. Action will still run.`,
    `${message}${code}${requestId}`
  );
  addActivity(`Preflight warning: ${label}`);
}

async function runActionPack(pack, options = {}) {
  if (actionPackState.has(pack.id)) {
    showToast("Action pack already running");
    return;
  }
  const stepParams = options.stepParams || getPackParams(pack.id).stepParams || {};
  const includeSteps = options.includeSteps || getPackParams(pack.id).includeSteps || {};
  const state = { cancelled: false, controller: null };
  actionPackState.set(pack.id, state);
  setActionPackRunning(pack.id, true);
  let hadFailures = false;
  let stoppedEarly = false;
  const runParamsSnapshot = { stepParams, includeSteps };
  for (const step of pack.steps) {
    if (state.cancelled) {
      addActivity(`Cancelled pack: ${pack.name}`);
      showToast("Action pack cancelled");
      break;
    }
    const label = step.label || activityLabel(step.service, step.action);
    if (step.optional) {
      const stepKey = `${step.service}.${step.action}`;
      if (includeSteps[stepKey] === false) {
        addActivity(`Skipped: ${label}`);
        continue;
      }
    }
    const stepKey = `${step.service}.${step.action}`;
    const override = stepParams[stepKey] || {};
    const defaults = getActionPackStepDefaults(pack, step) || {};
    const params = { ...defaults, ...(step.params || {}), ...(override?.params || {}), ...override };
    const controller = new AbortController();
    state.controller = controller;
    const result = await runAction(step.service, step.action, params, {
      controller,
      track: false,
    });
    if (state.cancelled || result?.cancelled) {
      addActivity(`Cancelled pack: ${pack.name}`);
      showToast("Action pack cancelled");
      break;
    }
    if (!result?.ok) {
      hadFailures = true;
      const continueRun = window.confirm(`Step failed: ${label}. Continue?`);
      if (!continueRun) {
        showToast("Action pack stopped");
        stoppedEarly = true;
        break;
      }
    }
  }
  actionPackState.delete(pack.id);
  setActionPackRunning(pack.id, false);
  const status = state.cancelled
    ? "cancelled"
    : stoppedEarly
      ? "stopped"
      : hadFailures
        ? "completed-with-errors"
        : "completed";
  addActionPackHistory({
    packId: pack.id,
    pack_name: pack.name,
    timestamp: Date.now(),
    status,
    stepParams: runParamsSnapshot.stepParams,
    includeSteps: runParamsSnapshot.includeSteps,
  });
  if (!state.cancelled) {
    showToast("Action pack completed");
  }
}

function loadTileLayout() {
  try {
    const raw = localStorage.getItem(TILE_LAYOUT_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    if (parsed && typeof parsed === "object") {
      if (parsed.__version !== TILE_LAYOUT_VERSION) {
        return { __version: TILE_LAYOUT_VERSION };
      }
      return parsed;
    }
    return { __version: TILE_LAYOUT_VERSION };
  } catch (err) {
    return { __version: TILE_LAYOUT_VERSION };
  }
}

function saveTileLayout(layout) {
  const next = { ...layout, __version: TILE_LAYOUT_VERSION };
  localStorage.setItem(TILE_LAYOUT_KEY, JSON.stringify(next));
}

function slugify(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function ensureTileId(card, section, index) {
  if (card.dataset.tileId) return card.dataset.tileId;
  const title = card.querySelector(".card-title")?.textContent?.trim() || `tile-${index + 1}`;
  const base = `${section}-${slugify(title) || "tile"}-${index + 1}`;
  card.dataset.tileId = base;
  return base;
}

function getInitialSpan(card) {
  if (card.classList.contains("span-1") || card.classList.contains("span-2") || card.classList.contains("span-3")) {
    return Number(card.className.match(/span-(\d)/)?.[1] || 1);
  }
  const panel = card.dataset.panel || "default";
  if (panel !== "dashboard") {
    if (card.classList.contains("form-card")) return 1;
    if (card.classList.contains("output-card")) return 2;
    return 3;
  }
  if (card.classList.contains("full")) return 3;
  if (card.classList.contains("wide")) return 2;
  return 1;
}

function getDefaultTileOrder(card) {
  const panel = card.dataset.panel || "default";
  if (panel === "dashboard") return 10;
  if (card.classList.contains("form-card")) return 1;
  if (card.classList.contains("output-card")) return 2;
  return 3;
}

function setTileSpan(card, span, persist = true) {
  card.classList.remove("span-1", "span-2", "span-3");
  card.classList.add(`span-${span}`);
  const resizeButton = card.querySelector(".tile-resize");
  if (resizeButton) {
    resizeButton.textContent = `${span}/3`;
  }
  if (persist) {
    persistTileLayout(card.closest(".grid"));
  }
}

function persistTileLayout(grid) {
  if (!grid) return;
  const layout = loadTileLayout();
  const panels = new Set();
  grid.querySelectorAll(".card.tile").forEach((card) => {
    panels.add(card.dataset.panel || "default");
  });
  panels.forEach((panel) => {
    const order = [];
    const spans = {};
    grid.querySelectorAll(`.card.tile[data-panel="${panel}"]`).forEach((card) => {
      const tileId = card.dataset.tileId;
      if (!tileId) return;
      order.push(tileId);
      const span = Number(card.className.match(/span-(\d)/)?.[1] || 1);
      spans[tileId] = span;
    });
    layout[panel] = { order, spans };
  });
  saveTileLayout(layout);
}

function applyTileLayout(grid) {
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll(".card"));
  const panelOrder = [];
  cards.forEach((card) => {
    const panel = card.dataset.panel || "default";
    if (!panelOrder.includes(panel)) {
      panelOrder.push(panel);
    }
  });

  const layout = loadTileLayout();

  panelOrder.forEach((panel) => {
    const panelCards = cards.filter((card) => (card.dataset.panel || "default") === panel);
    panelCards.forEach((card, index) => {
      card.classList.add("tile");
      ensureTileId(card, panel, index);
    });

    let ordered = [];
    const map = new Map(panelCards.map((card) => [card.dataset.tileId, card]));
    const saved = layout?.[panel]?.order || [];
    if (saved.length) {
      saved.forEach((tileId) => {
        const card = map.get(tileId);
        if (card) {
          ordered.push(card);
          map.delete(tileId);
        }
      });
      map.forEach((card) => ordered.push(card));
    } else {
      ordered = panelCards
        .map((card, idx) => ({ card, idx }))
        .sort((a, b) => {
          const orderA = getDefaultTileOrder(a.card);
          const orderB = getDefaultTileOrder(b.card);
          if (orderA !== orderB) return orderA - orderB;
          return a.idx - b.idx;
        })
        .map((entry) => entry.card);
    }
    ordered.forEach((card) => {
      grid.appendChild(card);
      const span = layout?.[panel]?.spans?.[card.dataset.tileId] || getInitialSpan(card);
      setTileSpan(card, span, false);
    });
  });
}

function setupTileControls(card) {
  if (card.querySelector(".tile-controls")) return;
  const controls = document.createElement("div");
  controls.classList.add("tile-controls");

  const handle = document.createElement("button");
  handle.type = "button";
  handle.classList.add("ghost", "small", "tile-handle");
  handle.textContent = "Move";
  handle.title = "Drag to move";

  const resize = document.createElement("button");
  resize.type = "button";
  resize.classList.add("ghost", "small", "tile-resize");
  resize.title = "Resize tile";
  const span = getInitialSpan(card);
  resize.textContent = `${span}/3`;

  resize.addEventListener("click", () => {
    const current = Number(card.className.match(/span-(\d)/)?.[1] || span);
    const next = current === 3 ? 1 : current + 1;
    setTileSpan(card, next);
  });

  controls.appendChild(handle);
  controls.appendChild(resize);

  const header = card.querySelector(".card-header");
  if (header) {
    let actionWrap = header.querySelector(".card-actions");
    if (!actionWrap) {
      actionWrap = document.createElement("div");
      actionWrap.classList.add("card-actions");
      const children = Array.from(header.children);
      children.slice(1).forEach((child) => actionWrap.appendChild(child));
      header.appendChild(actionWrap);
    }
    controls.classList.add("inline");
    actionWrap.appendChild(controls);
  } else {
    card.appendChild(controls);
  }
}

function setupTileDragging(grid) {
  let draggingCard = null;

  grid.addEventListener("dragover", (event) => {
    event.preventDefault();
    if (!draggingCard) return;
    const target = event.target.closest(".card.tile");
    if (!target || target === draggingCard) return;
    if ((target.dataset.panel || "default") !== (draggingCard.dataset.panel || "default")) return;
    const rect = target.getBoundingClientRect();
    const before = event.clientY < rect.top + rect.height / 2;
    grid.insertBefore(draggingCard, before ? target : target.nextSibling);
  });

  grid.addEventListener("drop", (event) => {
    event.preventDefault();
    if (draggingCard) {
      persistTileLayout(grid);
    }
  });

  grid.querySelectorAll(".card.tile").forEach((card) => {
    card.setAttribute("draggable", "false");
    const handle = card.querySelector(".tile-handle");
    if (!handle) return;
    if (handle.dataset.dragBound === "true") return;
    handle.dataset.dragBound = "true";
    handle.setAttribute("draggable", "true");

    handle.addEventListener("dragstart", (event) => {
      draggingCard = card;
      card.classList.add("dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.dataset.tileId || "");
      event.dataTransfer.setDragImage(card, 20, 20);
    });

    handle.addEventListener("dragend", () => {
      if (draggingCard) {
        draggingCard.classList.remove("dragging");
        draggingCard = null;
      }
    });
  });
}

function initTileLayout() {
  document.querySelectorAll(".grid").forEach((grid, idx) => {
    applyTileLayout(grid);
    grid.querySelectorAll(".card").forEach((card) => {
      card.classList.add("tile");
      setupTileControls(card);
    });
    setupTileDragging(grid);
  });
}

function setSection(section) {
  navLinks.forEach((link) => link.classList.toggle("active", link.dataset.section === section));
  panels.forEach((panel) => {
    if (panel.dataset.panel === section) {
      panel.style.display = panel.dataset.display || "flex";
    } else {
      panel.style.display = "none";
    }
  });
  pageTitle.textContent = section.charAt(0).toUpperCase() + section.slice(1);
  pageSubtitle.textContent = subtitles[section] || "";
  sidebar.classList.remove("open");
}

async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.graph_configured) {
      statusBadge.textContent = "Graph ready";
      statusBadge.classList.add("ok");
    } else {
      statusBadge.textContent = "Graph missing env";
      statusBadge.classList.add("warn");
    }
  } catch (err) {
    statusBadge.textContent = "API offline";
    statusBadge.classList.add("warn");
  }
}

async function fetchConfig() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    cfgTenantId.value = data.tenant_id || "";
    currentTenantId = data.tenant_id || "";
    cfgClientId.value = data.client_id || "";
    cfgGraphUserId.value = data.graph_user_id || "";
    cfgOnedriveDriveId.value = data.onedrive_drive_id || "";
    cfgSpoAdminUrl.value = data.spo_admin_url || "";
    cfgPsAuthMode.value = data.ps_auth_mode || "interactive";
    cfgPsUpn.value = data.ps_user_principal_name || "";
    cfgPsOrg.value = data.ps_org || "";
    cfgAzureTenantId.value = data.azure_tenant_id || "";
    cfgAzureSubscriptionId.value = data.azure_subscription_id || "";
    if (data.client_secret_set) {
      cfgClientSecret.placeholder = data.use_keychain ? "Stored in keychain" : "•••••• (set)";
    } else if (cfgClientSecret.placeholder.includes("set")) {
      cfgClientSecret.placeholder = "Enter to update";
    }
    if (cfgUseKeychain) {
      cfgUseKeychain.checked = Boolean(data.use_keychain);
    }
    if (cfgLock) {
      cfgLock.checked = Boolean(data.config_lock);
    }
    keychainAvailable = Boolean(data.keychain_available);
    setConfigLocked(Boolean(data.config_lock));
    renderKeychainStatus();
    renderActionPacks();
    if (packScopeSelect && packScopeSelect.value === "tenant" && !currentTenantId) {
      packScopeSelect.value = "global";
    }
    if (data.tenant_id && data.client_id && data.client_secret_set) {
      loadTenantInfo({ silent: true });
    } else {
      renderTenantInfo(null);
    }
  } catch (err) {
    showToast("Failed to load config");
  }
}

async function saveConfig() {
  if (configLocked) {
    showToast("Config is locked. Disable the lock to update.");
    return;
  }
  const payload = {
    tenant_id: cfgTenantId.value.trim(),
    client_id: cfgClientId.value.trim(),
    graph_user_id: cfgGraphUserId.value.trim(),
    onedrive_drive_id: cfgOnedriveDriveId.value.trim(),
    spo_admin_url: cfgSpoAdminUrl.value.trim(),
    ps_auth_mode: cfgPsAuthMode.value,
    ps_user_principal_name: cfgPsUpn.value.trim(),
    ps_org: cfgPsOrg.value.trim(),
    azure_tenant_id: cfgAzureTenantId.value.trim(),
    azure_subscription_id: cfgAzureSubscriptionId.value.trim(),
    reload: true,
  };
  const secret = cfgClientSecret.value.trim();
  if (secret) {
    payload.client_secret = secret;
  }
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Config update failed");
      return;
    }
    cfgClientSecret.value = "";
    await fetchConfig();
    fetchStatus();
    resetPreflightCache();
    showToast("Config saved & reloaded");
  } catch (err) {
    showToast("Config update failed");
  }
}

async function reloadConfig() {
  try {
    await fetch("/api/config/reload", { method: "POST" });
    await fetchConfig();
    fetchStatus();
    resetPreflightCache();
    showToast("Config reloaded");
  } catch (err) {
    showToast("Config reload failed");
  }
}

function getOutputPanel(service) {
  return document.querySelector(`.output[data-output="${service}"]`);
}

function getPrettyPanel(service) {
  return document.querySelector(`.output-pretty[data-output="${service}"]`);
}

function getTablePanel(service) {
  return document.querySelector(`.output-table[data-output="${service}"]`);
}

function tryParseJson(text) {
  if (typeof text !== "string") return null;
  const trimmed = text.trim();
  if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) return null;
  try {
    return JSON.parse(trimmed);
  } catch (err) {
    return null;
  }
}

function formatValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value, null, 2);
}

function toCsv(rows) {
  if (!rows.length) return "";
  const headers = Array.from(
    rows.reduce((set, row) => {
      Object.keys(row || {}).forEach((key) => set.add(key));
      return set;
    }, new Set())
  );
  const escapeValue = (value) => {
    if (value === null || value === undefined) return "";
    const raw = typeof value === "string" ? value : JSON.stringify(value);
    const escaped = raw.replace(/\"/g, "\"\"");
    return `"${escaped}"`;
  };
  const lines = [];
  lines.push(headers.join(","));
  rows.forEach((row) => {
    const line = headers.map((key) => escapeValue(row?.[key])).join(",");
    lines.push(line);
  });
  return lines.join("\n") + "\n";
}

function getArrayCandidates(data) {
  const candidates = {};
  if (Array.isArray(data)) {
    candidates.items = data;
    return candidates;
  }
  if (data && typeof data === "object") {
    if (Array.isArray(data.value)) {
      candidates.value = data.value;
    }
    Object.entries(data).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        candidates[key] = value;
      }
    });
  }
  return candidates;
}

function selectExportArray(data, options = {}) {
  const { preferredKey, allowPrompt = true } = options;
  const candidates = getArrayCandidates(data);
  const keys = Object.keys(candidates);
  if (!keys.length) return null;
  if (preferredKey && candidates[preferredKey]) {
    return candidates[preferredKey];
  }
  if (keys.length === 1) return candidates[keys[0]];
  if (!allowPrompt) return null;
  const choice = window.prompt(`Select dataset to export: ${keys.join(", ")}`, keys[0]);
  if (choice === null) return null;
  return candidates[choice] || null;
}

function getExportPayload(service) {
  if (lastOutputs[service]) return lastOutputs[service];
  const panel = getOutputPanel(service);
  if (panel?.textContent) {
    return tryParseJson(panel.textContent) || panel.textContent;
  }
  return null;
}

function extractErrorMeta(data) {
  if (!data || typeof data !== "object") return null;
  const status = data.status_code || data.status || data.statusCode;
  const requestId = data.request_id || data.requestId;
  let code = data.code || data.error_code;
  let message = data.error || data.message;
  let hint = data.hint;
  let detail = data.detail;
  const rateLimit = data.rate_limit || data.rateLimit;
  const suggestedWait = data.suggested_wait_seconds || data.retry_after;
  if (detail && typeof detail === "object" && detail.error) {
    const err = detail.error;
    code = code || err.code;
    message = message || err.message;
  }
  if (data.details && typeof data.details === "object") {
    const d = data.details;
    if (!status && d.status) status = d.status;
    if (!message && d.message) message = d.message;
  }
  return {
    status,
    code,
    message,
    hint,
    requestId,
    detail,
    rateLimit,
    suggestedWait,
    raw: data,
  };
}

function buildTriage(meta) {
  if (!meta) return null;
  const recommendations = [];
  const status = Number(meta.status || 0);
  const code = String(meta.code || "");
  const message = String(meta.message || "");

  if (meta.hint) {
    recommendations.push(meta.hint);
  }

  if (status === 401) {
    recommendations.push("Check client secret/tenant ID and ensure the app has a valid token.");
  }
  if (status === 403 || code.includes("Insufficient") || code.includes("Authorization_RequestDenied")) {
    recommendations.push("Grant the required Graph application permissions and admin consent in Entra.");
  }
  if (status === 404 || code.includes("Request_ResourceNotFound")) {
    recommendations.push("Verify the ID/UPN is correct and the resource exists.");
  }
  if (status === 429) {
    recommendations.push("Request throttled. Retry after a short delay or reduce request volume.");
  }
  if (meta.suggestedWait) {
    recommendations.push(`Suggested wait: ${meta.suggestedWait} seconds before retrying.`);
  }
  if (meta.rateLimit && typeof meta.rateLimit === "object") {
    const entries = Object.entries(meta.rateLimit)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => `${key}: ${value}`);
    if (entries.length) {
      recommendations.push(`Rate-limit headers: ${entries.slice(0, 5).join(", ")}.`);
    }
  }
  if (status >= 500) {
    recommendations.push("Transient Graph error. Retry the action or check service health.");
  }
  if (message.toLowerCase().includes("powershell")) {
    recommendations.push("Ensure PowerShell 7 and the required modules are installed on this host.");
  }
  if (meta.detail && typeof meta.detail === "string" && meta.detail.toLowerCase().includes("module")) {
    recommendations.push("Install the missing PowerShell module and retry.");
  }
  if (!recommendations.length) {
    recommendations.push("Review the error details and retry after verifying inputs.");
  }

  return {
    title: "Recommended fixes",
    status,
    code,
    message,
    requestId: meta.requestId,
    recommendations,
  };
}

function isEditableUserRecord(service, data) {
  if (service !== "entra") return false;
  if (!data || typeof data !== "object") return false;
  if (!data.id) return false;
  if (data["@odata.type"] && !String(data["@odata.type"]).includes("user")) return false;
  return Boolean(data.userPrincipalName || data.mail || data.givenName || data.surname);
}

function cloneRecord(value) {
  if (typeof structuredClone === "function") {
    return structuredClone(value);
  }
  return JSON.parse(JSON.stringify(value || {}));
}

function buildSearchIndex(value) {
  try {
    return JSON.stringify(value).toLowerCase();
  } catch (err) {
    return String(value ?? "").toLowerCase();
  }
}

function formatCellValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch (err) {
    return String(value);
  }
}

function trimText(text, limit = 140) {
  if (!text) return "";
  if (text.length <= limit) return text;
  return `${text.slice(0, limit - 3)}...`;
}

function getPrimaryLabel(item) {
  const candidates = ["displayName", "name", "subject", "title", "userPrincipalName", "mail", "id"];
  for (const key of candidates) {
    if (item && typeof item === "object" && item[key]) {
      return `${item[key]}`;
    }
  }
  return "Item details";
}

function getSummaryFields(item) {
  const keys = ["displayName", "name", "subject", "userPrincipalName", "mail", "status", "id"];
  const results = [];
  keys.forEach((key) => {
    if (item && typeof item === "object" && item[key] !== undefined && item[key] !== null) {
      if (typeof item[key] !== "object") {
        results.push({ key, value: item[key] });
      }
    }
  });
  if (!results.length && item && typeof item === "object") {
    Object.keys(item).some((key) => {
      const value = item[key];
      if (value === null || value === undefined || typeof value === "object") return false;
      results.push({ key, value });
      return results.length >= 3;
    });
  }
  return results.slice(0, 3);
}

function getOutputSearchQuery(service) {
  return (outputSearchQueries[service] || "").toLowerCase().trim();
}

function setOutputSearchQuery(service, query) {
  outputSearchQueries[service] = query || "";
}

function toggleSearchEmpty(container, visible, message) {
  if (!container) return;
  let empty = container.querySelector(".search-empty");
  if (!empty) {
    empty = document.createElement("div");
    empty.classList.add("search-empty");
    container.appendChild(empty);
  }
  empty.textContent = message || "No matches found.";
  empty.style.display = visible ? "block" : "none";
}

function applyOutputSearch(service) {
  const query = getOutputSearchQuery(service);
  const pretty = getPrettyPanel(service);
  if (pretty) {
    const rows = Array.from(pretty.querySelectorAll(".pretty-row"));
    let visibleCount = 0;
    rows.forEach((row) => {
      const hay = row.dataset.search || row.textContent.toLowerCase();
      const match = !query || hay.includes(query);
      row.style.display = match ? "" : "none";
      if (match) visibleCount += 1;
    });
    toggleSearchEmpty(
      pretty,
      !!query && rows.length > 0 && visibleCount === 0,
      "No pretty matches."
    );
  }

  const table = getTablePanel(service);
  if (table) {
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    let visibleCount = 0;
    rows.forEach((row) => {
      const hay = row.dataset.search || row.textContent.toLowerCase();
      const match = !query || hay.includes(query);
      row.style.display = match ? "" : "none";
      if (match) visibleCount += 1;
    });
    toggleSearchEmpty(
      table,
      !!query && rows.length > 0 && visibleCount === 0,
      "No table matches."
    );
  }
}

function getTableRows(parsed) {
  if (!parsed) return null;
  if (Array.isArray(parsed)) return parsed;
  if (Array.isArray(parsed?.value)) return parsed.value;
  if (typeof parsed === "object") return [parsed];
  return null;
}

function computeTableColumns(rows) {
  const counts = new Map();
  rows.forEach((row) => {
    if (!row || typeof row !== "object") return;
    Object.keys(row).forEach((key) => {
      counts.set(key, (counts.get(key) || 0) + 1);
    });
  });
  const priority = [
    "displayName",
    "name",
    "subject",
    "userPrincipalName",
    "mail",
    "id",
    "createdDateTime",
    "lastModifiedDateTime",
    "start",
    "end",
    "webUrl",
    "status",
  ];
  const sorted = Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([key]) => key);
  const columns = [];
  priority.forEach((key) => {
    if (counts.has(key) && !columns.includes(key)) {
      columns.push(key);
    }
  });
  const maxColumns = 10;
  sorted.forEach((key) => {
    if (columns.length >= maxColumns) return;
    if (!columns.includes(key)) {
      columns.push(key);
    }
  });
  if (!columns.length) {
    return ["value"];
  }
  return columns;
}

function ensureModal() {
  let modal = document.getElementById("detail-modal");
  if (modal) return modal;

  modal = document.createElement("div");
  modal.id = "detail-modal";
  modal.classList.add("modal");
  modal.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title" id="modal-title">Details</div>
        <div class="modal-actions">
          <button class="ghost small" id="modal-edit">Edit</button>
          <button class="primary small" id="modal-save">Save</button>
          <button class="ghost small" id="modal-close">Close</button>
        </div>
      </div>
      <div class="modal-body" id="modal-body"></div>
    </div>
  `;
  document.body.appendChild(modal);

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("open");
    }
  });

  modal.querySelector("#modal-close").addEventListener("click", () => {
    modal.classList.remove("open");
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      modal.classList.remove("open");
    }
  });

  return modal;
}

function showModal(title, data, service) {
  const modal = ensureModal();
  modal.classList.remove("editing");
  const titleEl = modal.querySelector("#modal-title");
  const bodyEl = modal.querySelector("#modal-body");
  const editButton = modal.querySelector("#modal-edit");
  const saveButton = modal.querySelector("#modal-save");
  titleEl.textContent = title;
  bodyEl.innerHTML = "";

  if (!data || typeof data !== "object") {
    bodyEl.textContent = formatValue(data);
    if (editButton) editButton.style.display = "none";
    if (saveButton) saveButton.style.display = "none";
    modal.classList.add("open");
    return;
  }

  const meta = extractErrorMeta(data);
  const triage = buildTriage(meta);
  if (triage && (data.ok === false || meta?.status || meta?.code || meta?.message)) {
    const panel = document.createElement("div");
    panel.classList.add("triage-panel");
    const heading = document.createElement("div");
    heading.classList.add("triage-title");
    heading.textContent = triage.title;
    panel.appendChild(heading);

    const summary = document.createElement("div");
    summary.classList.add("triage-summary");
    const parts = [];
    if (triage.status) parts.push(`Status: ${triage.status}`);
    if (triage.code) parts.push(`Code: ${triage.code}`);
    if (triage.requestId) parts.push(`Request ID: ${triage.requestId}`);
    summary.textContent = parts.join(" · ");
    if (summary.textContent) panel.appendChild(summary);

    if (triage.message) {
      const message = document.createElement("div");
      message.classList.add("triage-message");
      message.textContent = triage.message;
      panel.appendChild(message);
    }

    const list = document.createElement("ul");
    list.classList.add("triage-list");
    triage.recommendations.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    });
    panel.appendChild(list);
    bodyEl.appendChild(panel);
  }

  const detailMap = new Map();
  Object.entries(data).forEach(([key, value]) => {
    const row = document.createElement("div");
    row.classList.add("detail-row");
    const label = document.createElement("div");
    label.classList.add("detail-key");
    label.textContent = key;
    const val = document.createElement("pre");
    val.classList.add("detail-value");
    val.textContent = formatValue(value);
    row.appendChild(label);
    row.appendChild(val);
    bodyEl.appendChild(row);
    detailMap.set(key, val);
  });

  const editable = isEditableUserRecord(service, data);
  let editInputs = {};
  let original = cloneRecord(data);

  if (editable) {
    const editPanel = document.createElement("div");
    editPanel.classList.add("edit-panel");

    const editTitle = document.createElement("div");
    editTitle.classList.add("edit-title");
    editTitle.textContent = "Edit user profile";
    editPanel.appendChild(editTitle);

    const grid = document.createElement("div");
    grid.classList.add("edit-grid");

    EDITABLE_USER_FIELDS.forEach((field) => {
      const wrapper = document.createElement("label");
      wrapper.classList.add("edit-field");
      wrapper.textContent = field.label;
      let input;

      if (field.type === "checkbox") {
        input = document.createElement("input");
        input.type = "checkbox";
        input.checked = Boolean(data[field.key]);
        wrapper.classList.add("checkbox");
      } else {
        input = document.createElement("input");
        input.type = "text";
        if (field.placeholder) {
          input.placeholder = field.placeholder;
        }
        const value = data[field.key];
        if (field.type === "list") {
          input.value = Array.isArray(value) ? value.join(", ") : value || "";
        } else {
          input.value = value ?? "";
        }
      }

      input.dataset.key = field.key;
      wrapper.appendChild(input);
      grid.appendChild(wrapper);
      editInputs[field.key] = input;
    });

    editPanel.appendChild(grid);
    const hint = document.createElement("div");
    hint.classList.add("edit-hint");
    hint.textContent = "Only editable fields are shown. Changes are sent to Graph on Save.";
    editPanel.appendChild(hint);
    bodyEl.appendChild(editPanel);
  }

  if (editButton) {
    editButton.style.display = editable ? "inline-flex" : "none";
    editButton.textContent = "Edit";
    editButton.onclick = () => {
      if (!editable) return;
      const isEditing = modal.classList.toggle("editing");
      if (saveButton) {
        saveButton.style.display = isEditing ? "inline-flex" : "none";
      }
      editButton.textContent = isEditing ? "Cancel" : "Edit";
    };
  }

  if (saveButton) {
    saveButton.style.display = "none";
    saveButton.onclick = async () => {
      if (!editable) return;
      const updates = {};
      EDITABLE_USER_FIELDS.forEach((field) => {
        const input = editInputs[field.key];
        if (!input) return;
        let nextValue;
        if (field.type === "checkbox") {
          nextValue = input.checked;
        } else if (field.type === "list") {
          const parts = input.value
            .split(",")
            .map((part) => part.trim())
            .filter(Boolean);
          nextValue = parts;
        } else {
          const raw = input.value.trim();
          nextValue = raw === "" ? null : raw;
        }

        const originalValue = original[field.key];
        if (field.type === "checkbox") {
          if (Boolean(originalValue) !== Boolean(nextValue)) {
            updates[field.key] = nextValue;
          }
        } else if (field.type === "list") {
          const originalList = Array.isArray(originalValue) ? originalValue : [];
          if (JSON.stringify(originalList) !== JSON.stringify(nextValue)) {
            updates[field.key] = nextValue;
          }
        } else {
          const normalizedOriginal = originalValue === undefined ? null : originalValue;
          if (normalizedOriginal !== nextValue) {
            updates[field.key] = nextValue;
          }
        }
      });

      if (!Object.keys(updates).length) {
        showToast("No changes to save");
        return;
      }

      const result = await runAction("entra", "update_user", {
        user_id: data.id,
        updates,
      });

      if (result?.ok) {
        Object.assign(data, updates);
        Object.assign(original, updates);
        Object.entries(updates).forEach(([key, value]) => {
          const el = detailMap.get(key);
          if (el) {
            el.textContent = formatValue(value);
          }
        });
        modal.classList.remove("editing");
        if (saveButton) saveButton.style.display = "none";
        if (editButton) editButton.textContent = "Edit";
        showToast("User updated");
      }
    };
  }

  modal.classList.add("open");
}

function renderPretty(service, parsed) {
  const container = getPrettyPanel(service);
  if (!container) return;
  container.innerHTML = "";
  if (!parsed) {
    const empty = document.createElement("div");
    empty.classList.add("pretty-empty");
    empty.textContent = "No structured data to display.";
    container.appendChild(empty);
    return;
  }

  const list = Array.isArray(parsed) ? parsed : Array.isArray(parsed?.value) ? parsed.value : null;
  if (list) {
    const listEl = document.createElement("div");
    listEl.classList.add("pretty-list");
    list.forEach((item) => {
      const row = document.createElement("div");
      row.classList.add("pretty-row");
      row.dataset.search = buildSearchIndex(item);

      const title = document.createElement("div");
      title.classList.add("pretty-title");
      title.textContent = getPrimaryLabel(item);

      const meta = document.createElement("div");
      meta.classList.add("pretty-meta");
      const summary = getSummaryFields(item);
      summary.forEach((field) => {
        const chip = document.createElement("span");
        chip.classList.add("meta-chip");
        chip.textContent = `${field.key}: ${field.value}`;
        meta.appendChild(chip);
      });

      const actions = document.createElement("div");
      actions.classList.add("pretty-actions");
      const viewBtn = document.createElement("button");
      viewBtn.type = "button";
      viewBtn.classList.add("ghost", "small");
      viewBtn.textContent = "View";
      viewBtn.addEventListener("click", () => showModal(getPrimaryLabel(item), item, service));
      actions.appendChild(viewBtn);

      row.appendChild(title);
      row.appendChild(meta);
      row.appendChild(actions);
      listEl.appendChild(row);
    });
    container.appendChild(listEl);
    applyOutputSearch(service);
    return;
  }

  const card = document.createElement("div");
  card.classList.add("pretty-single");
  const viewBtn = document.createElement("button");
  viewBtn.type = "button";
  viewBtn.classList.add("ghost", "small");
  viewBtn.textContent = "View details";
  viewBtn.addEventListener("click", () => showModal(getPrimaryLabel(parsed), parsed, service));
  card.appendChild(viewBtn);
  container.appendChild(card);
  applyOutputSearch(service);
}

function renderTable(service, parsed) {
  const container = getTablePanel(service);
  if (!container) return;
  container.innerHTML = "";
  const rows = getTableRows(parsed);
  if (!rows || !rows.length) {
    const empty = document.createElement("div");
    empty.classList.add("table-empty");
    empty.textContent = "No tabular data to display.";
    container.appendChild(empty);
    return;
  }

  const normalized = rows.map((row) => {
    if (row && typeof row === "object") return row;
    return { value: row };
  });
  const columns = computeTableColumns(normalized);

  const wrap = document.createElement("div");
  wrap.classList.add("table-wrap");
  const table = document.createElement("table");
  table.classList.add("data-table");
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col;
    headerRow.appendChild(th);
  });
  const thActions = document.createElement("th");
  thActions.textContent = "Details";
  headerRow.appendChild(thActions);
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  normalized.forEach((row) => {
    const tr = document.createElement("tr");
    tr.dataset.search = buildSearchIndex(row);
    columns.forEach((col) => {
      const td = document.createElement("td");
      const rawValue = row?.[col];
      const formatted = formatCellValue(rawValue);
      const shortValue = trimText(formatted, 140);
      td.textContent = shortValue;
      if (formatted && formatted !== shortValue) {
        td.title = formatted.slice(0, 600);
      }
      tr.appendChild(td);
    });
    const actionTd = document.createElement("td");
    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.classList.add("ghost", "small");
    viewBtn.textContent = "View";
    viewBtn.addEventListener("click", () => showModal(getPrimaryLabel(row), row, service));
    actionTd.appendChild(viewBtn);
    tr.appendChild(actionTd);
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  container.appendChild(wrap);
  applyOutputSearch(service);
}

function setOutput(service, content) {
  const target = getOutputPanel(service);
  const dashboard = getOutputPanel("dashboard");
  let rawText = "";
  let parsed = null;

  if (typeof content === "string") {
    rawText = content;
    parsed = tryParseJson(content);
  } else {
    parsed = content;
    rawText = JSON.stringify(content, null, 2) || "OK";
  }

  if (target) {
    target.textContent = rawText;
  }
  if (dashboard && service !== "dashboard") {
    dashboard.textContent = rawText;
  }
  lastOutputs[service] = parsed ?? rawText;
  renderPretty(service, parsed);
  renderTable(service, parsed);
  if (service === "reports") {
    updateReportExportOptions(parsed);
  }
}

function confirmAction(service, action, params = {}) {
  const meta = ACTIONS_UI?.[service]?.[action];
  if (!meta?.confirm) return true;
  const label = meta.label || `${service}.${action}`;
  const detailKeys = [
    "user_dn",
    "group_dn",
    "member_dn",
    "gpo_name",
    "ou_dn",
    "name",
    "sam_account_name",
    "user_principal_name",
  ];
  const details = detailKeys
    .map((key) => {
      if (key.toLowerCase().includes("password")) return null;
      const value = params?.[key];
      if (!value) return null;
      return `${key}: ${value}`;
    })
    .filter(Boolean);
  const message = details.length
    ? `Confirm ${label}?\n\n${details.join("\n")}`
    : `Confirm ${label}?`;
  return window.confirm(message);
}

async function runAction(service, action, params = {}, options = {}) {
  const preflight = await preflightAction(service, action);
  if (!preflight.ok) {
    handlePreflightFailure(service, action, preflight.data || preflight.error);
    return { ok: false, preflight };
  }
  if (preflight.warning) {
    handlePreflightWarning(service, action, preflight.warning);
  }
  const track = options.track !== false;
  if (track && activeRequests.has(service)) {
    showToast("Action already running");
    return { ok: false, busy: true };
  }
  const controller = options.controller || new AbortController();
  if (track) {
    activeRequests.set(service, controller);
    setRunnerRunning(service, true);
  }
  if (!confirmAction(service, action, params)) {
    showToast("Action cancelled");
    addActivity(`Cancelled: ${activityLabel(service, action)}`);
    setOutputStatus(service, {
      state: "warn",
      text: `${activityLabel(service, action)} cancelled`,
      meta: "Cancelled by user",
      running: false,
    });
    if (track) {
      activeRequests.delete(service);
      setRunnerRunning(service, false);
    }
    return { ok: false, cancelled: true };
  }
  const label = activityLabel(service, action);
  const mode = ACTIONS_UI?.[service]?.[action]?.mode || "graph";
  const modeText = modeLabel(mode);
  showToast("Dispatching action...");
  setOutput(service, "Running...");
  setOutputStatus(service, {
    state: "running",
    text: `${label} running`,
    meta: `${modeText} · Elapsed 0.0s`,
    running: true,
  });
  startOutputTimer(service, modeText);
  const stats = getStats();
  stats.total += 1;
  saveStats(stats);
  updateMetrics();

  try {
    const startedAt = performance.now();
    const res = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service, action, params }),
      signal: controller.signal,
    });
    const data = await res.json();
    const elapsedMs = performance.now() - startedAt;
    if (!data.ok) {
      setOutput(service, data);
      const status = data.status_code || data.status || "";
      const statusLabel = status ? `HTTP ${status}` : "Failed";
      setOutputStatus(service, {
        state: "fail",
        text: `${label} failed`,
        meta: `${statusLabel} · ${formatElapsed(elapsedMs)}`,
        running: false,
      });
      addActivity(`Failed: ${activityLabel(service, action)}`);
      updateMetrics();
      return { ok: false, data };
    }
    setOutput(service, data.data);
    setOutputStatus(service, {
      state: "ok",
      text: `${label} complete`,
      meta: `${modeText} · ${formatElapsed(elapsedMs)}`,
      running: false,
    });
    addActivity(`Ran: ${activityLabel(service, action)}`);
    if (service === "reports") {
      addReportHistory({
        id: `report-${Date.now()}-${Math.random().toString(16).slice(2)}`,
        action,
        label: activityLabel(service, action),
        timestamp: Date.now(),
        params,
        data: data.data,
      });
    }
    stats.success += 1;
    saveStats(stats);
    updateMetrics();
    showToast("Action completed");
    return { ok: true, data: data.data };
  } catch (err) {
    if (err.name === "AbortError") {
      setOutput(service, "Cancelled.");
      addActivity(`Cancelled: ${activityLabel(service, action)}`);
      setOutputStatus(service, {
        state: "warn",
        text: `${label} cancelled`,
        meta: "Cancelled by user",
        running: false,
      });
      showToast("Action cancelled");
      return { ok: false, cancelled: true };
    }
    setOutput(service, `Error: ${err.message}`);
    addActivity(`Error: ${activityLabel(service, action)}`);
    setOutputStatus(service, {
      state: "fail",
      text: `${label} error`,
      meta: err.message || "Error",
      running: false,
    });
    updateMetrics();
    return { ok: false, error: err };
  } finally {
    stopOutputTimer(service);
    if (track) {
      activeRequests.delete(service);
      setRunnerRunning(service, false);
    }
  }
}

function buildParams(service, action) {
  const prompts = ACTIONS_UI?.[service]?.[action]?.fields || [];
  const params = {};
  let cancelled = false;
  prompts.forEach((prompt) => {
    const value = window.prompt(prompt.label, "");
    if (value === null) {
      cancelled = true;
      return;
    }
    params[prompt.key] = value;
  });
  if (cancelled) return null;
  return params;
}

function loadPresets() {
  try {
    const raw = localStorage.getItem("runnerPresets");
    return raw ? JSON.parse(raw) : {};
  } catch (err) {
    return {};
  }
}

function savePresets(data) {
  localStorage.setItem("runnerPresets", JSON.stringify(data));
}

function getActionSelection(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return "";
  const select = form.querySelector(".action-select");
  return select ? select.value : "";
}

function updatePresetOptions(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;
  const action = getActionSelection(service);
  const select = form.querySelector(".preset-select");
  if (!select) return;
  const presets = loadPresets();
  const entries = presets?.[service]?.[action] || {};
  select.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select preset";
  select.appendChild(placeholder);
  Object.keys(entries).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  });
}

function applyParamsToForm(service, params) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;
  form.querySelectorAll(".field").forEach((field) => {
    const key = field.dataset.field;
    const input = field.querySelector("input, select, textarea");
    if (!input) return;
    const value = params?.[key];
    if (input.type === "checkbox") {
      input.checked = Boolean(value);
    } else if (value !== undefined && value !== null) {
      input.value = value;
    } else {
      input.value = "";
    }
  });
}

function collectParams(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return null;
  const base = readRunnerParams(service);
  const jsonInput = form.querySelector(".advanced-json");
  if (jsonInput && jsonInput.value.trim()) {
    try {
      const extra = JSON.parse(jsonInput.value.trim());
      return { ...base, ...extra };
    } catch (err) {
      showToast("Invalid JSON parameters");
      return null;
    }
  }
  return base;
}

function attachAdvancedControls(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form || form.dataset.advancedReady === "true") return;
  form.dataset.advancedReady = "true";

  const details = document.createElement("details");
  details.classList.add("advanced");
  const summary = document.createElement("summary");
  summary.textContent = "Advanced";
  details.appendChild(summary);

  const jsonLabel = document.createElement("label");
  jsonLabel.classList.add("field");
  jsonLabel.textContent = "JSON parameters (merge with form)";
  const textarea = document.createElement("textarea");
  textarea.classList.add("advanced-json");
  textarea.rows = 6;
  textarea.placeholder = '{\"key\": \"value\"}';
  jsonLabel.appendChild(textarea);
  details.appendChild(jsonLabel);

  const presetRow = document.createElement("div");
  presetRow.classList.add("runner-actions");

  const presetSelect = document.createElement("select");
  presetSelect.classList.add("preset-select");

  const presetLoad = document.createElement("button");
  presetLoad.type = "button";
  presetLoad.classList.add("ghost", "small");
  presetLoad.textContent = "Load preset";

  const presetSave = document.createElement("button");
  presetSave.type = "button";
  presetSave.classList.add("ghost", "small");
  presetSave.textContent = "Save preset";

  const preview = document.createElement("button");
  preview.type = "button";
  preview.classList.add("ghost", "small");
  preview.textContent = "Preview payload";

  presetRow.appendChild(presetSelect);
  presetRow.appendChild(presetLoad);
  presetRow.appendChild(presetSave);
  presetRow.appendChild(preview);
  details.appendChild(presetRow);

  const templateRow = document.createElement("div");
  templateRow.classList.add("runner-actions");
  const templateSave = document.createElement("button");
  templateSave.type = "button";
  templateSave.classList.add("ghost", "small");
  templateSave.textContent = "Save template";
  templateRow.appendChild(templateSave);
  details.appendChild(templateRow);

  form.appendChild(details);

  presetSave.addEventListener("click", () => {
    const action = getActionSelection(service);
    const params = collectParams(service);
    if (!params) return;
    const name = window.prompt("Preset name");
    if (!name) return;
    const presets = loadPresets();
    presets[service] = presets[service] || {};
    presets[service][action] = presets[service][action] || {};
    presets[service][action][name] = params;
    savePresets(presets);
    updatePresetOptions(service);
    showToast("Preset saved");
  });

  presetLoad.addEventListener("click", () => {
    const action = getActionSelection(service);
    const presets = loadPresets();
    const name = presetSelect.value;
    if (!name) return;
    const params = presets?.[service]?.[action]?.[name];
    if (!params) return;
    applyParamsToForm(service, params);
    showToast("Preset loaded");
  });

  preview.addEventListener("click", () => {
    const params = collectParams(service);
    if (!params) return;
    setOutput(service, JSON.stringify(params, null, 2));
  });

  templateSave.addEventListener("click", () => {
    const action = getActionSelection(service);
    const params = collectParams(service);
    if (!params) return;
    const defaultName = `${activityLabel(service, action)}`;
    const name = window.prompt("Template name", defaultName);
    if (!name) return;
    const template = {
      id: generateTemplateId(),
      name,
      service,
      action,
      params,
    };
    upsertTemplate(template);
    renderTemplateSelect();
    showToast("Template saved");
  });
}

function activityLabel(service, action) {
  const meta = ACTIONS_UI?.[service]?.[action];
  return meta ? meta.label : `${service}.${action}`;
}

function loadActivity() {
  try {
    const raw = localStorage.getItem("adminActivity");
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    return [];
  }
}

function saveActivity(entries) {
  const maxEntries = 500;
  localStorage.setItem("adminActivity", JSON.stringify(entries.slice(0, maxEntries)));
}

function getActivityPageSize() {
  const raw = localStorage.getItem("activityPageSize");
  const size = Number.parseInt(raw, 10);
  if ([5, 10, 20, 50, 100].includes(size)) return size;
  return 5;
}

function setActivityPageSize(size) {
  localStorage.setItem("activityPageSize", String(size));
}

function getActivityPageIndex() {
  const raw = localStorage.getItem("activityPageIndex");
  const idx = Number.parseInt(raw, 10);
  if (Number.isFinite(idx) && idx >= 0) return idx;
  return 0;
}

function setActivityPageIndex(index) {
  localStorage.setItem("activityPageIndex", String(index));
}

function getActivityPaging(entries) {
  const pageSize = getActivityPageSize();
  const totalPages = Math.max(1, Math.ceil(entries.length / pageSize));
  let pageIndex = getActivityPageIndex();
  if (pageIndex >= totalPages) {
    pageIndex = totalPages - 1;
  }
  if (pageIndex < 0) pageIndex = 0;
  setActivityPageIndex(pageIndex);
  return { pageSize, pageIndex, totalPages };
}

function renderActivity(entries) {
  const activityList = document.getElementById("activity-list");
  if (!activityList) return;
  activityList.innerHTML = "";
  if (!entries.length) {
    const li = document.createElement("li");
    li.classList.add("empty");
    li.textContent = "No activity yet.";
    activityList.appendChild(li);
    if (activityPageInfo) activityPageInfo.textContent = "Page 1 / 1";
    if (activityPrevButton) activityPrevButton.disabled = true;
    if (activityNextButton) activityNextButton.disabled = true;
    const pagination = activityPrevButton?.closest(".activity-pagination");
    if (pagination) pagination.style.display = "none";
    return;
  }
  const { pageSize, pageIndex, totalPages } = getActivityPaging(entries);
  const start = pageIndex * pageSize;
  const pageEntries = entries.slice(start, start + pageSize);
  pageEntries.forEach((entry) => {
    const li = document.createElement("li");
    const time = document.createElement("span");
    time.classList.add("time");
    time.textContent = entry.time;
    const text = document.createElement("span");
    text.textContent = entry.text;
    li.appendChild(time);
    li.appendChild(text);
    activityList.appendChild(li);
  });
  if (activityPageInfo) {
    activityPageInfo.textContent = `Page ${pageIndex + 1} / ${totalPages}`;
  }
  if (activityPrevButton) {
    activityPrevButton.disabled = totalPages <= 1 || pageIndex === 0;
  }
  if (activityNextButton) {
    activityNextButton.disabled = totalPages <= 1 || pageIndex >= totalPages - 1;
  }
  const pagination = activityPrevButton?.closest(".activity-pagination");
  if (pagination) {
    pagination.style.display = totalPages > 1 ? "inline-flex" : "none";
  }
}

function addActivity(text) {
  const entries = loadActivity();
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  entries.unshift({ time, text });
  saveActivity(entries);
  setActivityPageIndex(0);
  renderActivity(entries);
}

function getStats() {
  try {
    const raw = localStorage.getItem("adminStats");
    return raw ? JSON.parse(raw) : { total: 0, success: 0 };
  } catch (err) {
    return { total: 0, success: 0 };
  }
}

function saveStats(stats) {
  localStorage.setItem("adminStats", JSON.stringify(stats));
}

function updateMetrics() {
  const stats = getStats();
  if (metricTasks) {
    metricTasks.textContent = stats.total || 0;
  }
  if (metricSuccess) {
    const rate = stats.total ? Math.round((stats.success / stats.total) * 1000) / 10 : 0;
    metricSuccess.textContent = stats.total ? `${rate}%` : "--";
  }
}

function modeLabel(mode) {
  if (mode === "powershell") return "PowerShell";
  if (mode === "ssh") return "SSH";
  return "Graph";
}

function addChipBadge(chip, mode) {
  if (chip.querySelector(".badge")) return;
  const badge = document.createElement("span");
  badge.classList.add("badge");
  badge.classList.add(mode === "powershell" ? "ps" : "graph");
  badge.textContent = modeLabel(mode);
  chip.appendChild(badge);
}

function decorateChips() {
  document.querySelectorAll(".chip[data-action]").forEach((chip) => {
    const { service, action } = chip.dataset;
    const meta = ACTIONS_UI?.[service]?.[action];
    if (!meta) return;
    const mode = meta.mode || "graph";
    chip.dataset.mode = mode;
    addChipBadge(chip, mode);
  });
}

function setupOutputViews() {
  document.querySelectorAll(".output").forEach((pre) => {
    if (pre.dataset.enhanced === "true") return;
    const card = pre.closest(".output-card");
    if (!card) return;
    const service = pre.dataset.output;
    const isTerminal = pre.dataset.outputMode === "terminal";

    const status = document.createElement("div");
    status.classList.add("output-status", "idle");
    status.dataset.outputStatus = service;
    const spinner = document.createElement("span");
    spinner.classList.add("spinner");
    const statusText = document.createElement("span");
    statusText.classList.add("status-text");
    statusText.textContent = "Idle";
    const statusMeta = document.createElement("span");
    statusMeta.classList.add("status-meta");
    status.appendChild(spinner);
    status.appendChild(statusText);
    status.appendChild(statusMeta);

    const anchor = pre;
    card.insertBefore(status, anchor);

    if (isTerminal) {
      pre.dataset.enhanced = "true";
      return;
    }

    const tabs = document.createElement("div");
    tabs.classList.add("output-tabs");
    const rawButton = document.createElement("button");
    rawButton.type = "button";
    rawButton.classList.add("tab", "active");
    rawButton.dataset.view = "raw";
    rawButton.textContent = "Raw";
    const prettyButton = document.createElement("button");
    prettyButton.type = "button";
    prettyButton.classList.add("tab");
    prettyButton.dataset.view = "pretty";
    prettyButton.textContent = "Pretty";
    const tableButton = document.createElement("button");
    tableButton.type = "button";
    tableButton.classList.add("tab");
    tableButton.dataset.view = "table";
    tableButton.textContent = "Table";
    tabs.appendChild(rawButton);
    tabs.appendChild(prettyButton);
    tabs.appendChild(tableButton);

    const searchWrap = document.createElement("div");
    searchWrap.classList.add("output-search");
    const searchInput = document.createElement("input");
    searchInput.type = "search";
    searchInput.placeholder = "Search output";
    searchInput.value = getOutputSearchQuery(service);
    searchInput.addEventListener("input", () => {
      setOutputSearchQuery(service, searchInput.value);
      applyOutputSearch(service);
    });
    searchWrap.appendChild(searchInput);

    const wrapper = document.createElement("div");
    wrapper.classList.add("output-panels");

    const pretty = document.createElement("div");
    pretty.classList.add("output-pretty");
    pretty.dataset.output = pre.dataset.output;
    const table = document.createElement("div");
    table.classList.add("output-table");
    table.dataset.output = pre.dataset.output;

    pre.classList.add("output-raw");
    card.insertBefore(searchWrap, anchor);
    card.insertBefore(tabs, anchor);
    card.insertBefore(wrapper, anchor);
    wrapper.appendChild(pre);
    wrapper.appendChild(pretty);
    wrapper.appendChild(table);

    const switchView = (view) => {
      rawButton.classList.toggle("active", view === "raw");
      prettyButton.classList.toggle("active", view === "pretty");
      tableButton.classList.toggle("active", view === "table");
      pre.style.display = view === "raw" ? "block" : "none";
      pretty.style.display = view === "pretty" ? "block" : "none";
      table.style.display = view === "table" ? "block" : "none";
    };

    rawButton.addEventListener("click", () => switchView("raw"));
    prettyButton.addEventListener("click", () => switchView("pretty"));
    tableButton.addEventListener("click", () => switchView("table"));
    switchView("raw");
    pre.dataset.enhanced = "true";
  });
}

function populateRunner(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;

  const select = form.querySelector(".action-select");
  const container = form.querySelector(".runner-fields");
  const actions = ACTIONS_UI[service] || {};
  const runButton = form.querySelector(".runner-run");
  const resetButton = form.querySelector(".runner-reset");
  const actionsRow = form.querySelector(".runner-actions");
  let cancelButton = form.querySelector(".runner-cancel");
  if (!cancelButton && actionsRow) {
    cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.classList.add("ghost", "small", "runner-cancel");
    cancelButton.dataset.service = service;
    cancelButton.textContent = "Cancel";
    cancelButton.style.display = "none";
    actionsRow.appendChild(cancelButton);
  }
  if (cancelButton && !cancelButton.dataset.bound) {
    cancelButton.dataset.bound = "true";
    cancelButton.addEventListener("click", () => cancelAction(service));
  }

  if (!Object.keys(actions).length) {
    select.innerHTML = "";
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No actions configured";
    select.appendChild(option);
    select.disabled = true;
    if (runButton) runButton.disabled = true;
    if (resetButton) resetButton.disabled = true;
    container.innerHTML = "";
    const note = document.createElement("div");
    note.classList.add("runner-mode");
    note.textContent = "No actions configured yet.";
    container.appendChild(note);
    return;
  }

  select.disabled = false;
  if (runButton) runButton.disabled = false;
  if (resetButton) resetButton.disabled = false;

  select.innerHTML = "";
  Object.entries(actions).forEach(([action, meta]) => {
    const option = document.createElement("option");
    option.value = action;
    option.textContent = `${meta.label} · ${modeLabel(meta.mode)}`;
    select.appendChild(option);
  });

  function renderFields(action) {
    container.innerHTML = "";
    const meta = actions[action];
    const fields = meta?.fields || [];

    const modeLine = document.createElement("div");
    modeLine.classList.add("runner-mode");
    modeLine.textContent = `Mode: ${modeLabel(meta?.mode)}`;
    container.appendChild(modeLine);

    fields.forEach((field) => {
      const wrapper = document.createElement("label");
      wrapper.classList.add("field");
      wrapper.dataset.field = field.key;
      if (field.type === "checkbox") {
        wrapper.classList.add("checkbox");
        if (field.sendFalse) {
          wrapper.dataset.sendFalse = "true";
        }
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = Boolean(field.defaultChecked);
        const span = document.createElement("span");
        span.textContent = field.label;
        wrapper.appendChild(input);
        wrapper.appendChild(span);
      } else {
        wrapper.textContent = field.label;
        const input = document.createElement("input");
        input.type = field.type || "text";
        if (field.placeholder) {
          input.placeholder = field.placeholder;
        }
        wrapper.appendChild(input);
      }
      container.appendChild(wrapper);
    });
  }

  renderFields(select.value);
  select.addEventListener("change", () => renderFields(select.value));
  attachAdvancedControls(service);
  updatePresetOptions(service);
  select.addEventListener("change", () => updatePresetOptions(service));
}

function readRunnerParams(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return {};
  const params = {};
  form.querySelectorAll(".field").forEach((field) => {
    const key = field.dataset.field;
    const input = field.querySelector("input, select, textarea");
    if (!input) return;
    if (input.type === "checkbox") {
      if (input.checked) {
        params[key] = true;
      } else if (field.dataset.sendFalse === "true") {
        params[key] = false;
      }
      return;
    }
    const value = input.value.trim();
    if (value !== "") {
      params[key] = value;
    }
  });
  return params;
}

navLinks.forEach((link) => {
  link.addEventListener("click", () => setSection(link.dataset.section));
});

navGroupToggles.forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const group = toggle.closest(".nav-group");
    if (!group) return;
    group.classList.toggle("open");
  });
});

navToggle.addEventListener("click", () => {
  sidebar.classList.toggle("open");
});

document.getElementById("connect-ps").addEventListener("click", () => {
  showToast("PowerShell connection queued");
});

document.getElementById("open-task-runner").addEventListener("click", () => {
  setSection("exchange");
  showToast("Opened Task Runner");
});

document.getElementById("view-activity").addEventListener("click", () => {
  const list = document.getElementById("activity-list");
  if (list) {
    list.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

if (activityPageSizeSelect) {
  activityPageSizeSelect.value = String(getActivityPageSize());
  activityPageSizeSelect.addEventListener("change", () => {
    const size = Number.parseInt(activityPageSizeSelect.value, 10);
    if ([5, 10, 20, 50, 100].includes(size)) {
      setActivityPageSize(size);
      setActivityPageIndex(0);
      renderActivity(loadActivity());
    }
  });
}

if (activityPrevButton) {
  activityPrevButton.addEventListener("click", () => {
    const entries = loadActivity();
    const { pageIndex } = getActivityPaging(entries);
    if (pageIndex > 0) {
      setActivityPageIndex(pageIndex - 1);
      renderActivity(entries);
    }
  });
}

if (activityNextButton) {
  activityNextButton.addEventListener("click", () => {
    const entries = loadActivity();
    const { pageIndex, totalPages } = getActivityPaging(entries);
    if (pageIndex < totalPages - 1) {
      setActivityPageIndex(pageIndex + 1);
      renderActivity(entries);
    }
  });
}

if (profileSelect) {
  renderProfileSelect();
  profileSelect.addEventListener("change", () => {
    const name = profileSelect.value;
    if (profileNameInput) {
      profileNameInput.value = name;
    }
  });
}

if (profileSaveButton) {
  profileSaveButton.addEventListener("click", () => {
    const name = profileNameInput?.value.trim();
    if (!name) {
      showToast("Enter a profile name");
      return;
    }
    const config = getConfigPayloadFromForm();
    upsertProfile(name, config);
    if (profileSelect) {
      profileSelect.value = name;
    }
    showToast("Profile saved");
  });
}

if (profileApplyButton) {
  profileApplyButton.addEventListener("click", async () => {
    const name = profileSelect?.value || profileNameInput?.value.trim();
    if (!name) {
      showToast("Select a profile");
      return;
    }
    const profile = getProfileByName(name);
    if (!profile) {
      showToast("Profile not found");
      return;
    }
    applyConfigToForm(profile.config || {});
    if (!profile.config?.client_secret) {
      showToast("Client secret not stored; enter it and Save & Reload.");
      return;
    }
    await saveConfig();
  });
}

if (profileDeleteButton) {
  profileDeleteButton.addEventListener("click", () => {
    const name = profileSelect?.value || profileNameInput?.value.trim();
    if (!name) {
      showToast("Select a profile");
      return;
    }
    const confirmDelete = window.confirm(`Delete profile "${name}"?`);
    if (!confirmDelete) return;
    deleteProfile(name);
    if (profileNameInput) profileNameInput.value = "";
    if (profileSelect) profileSelect.value = "";
    showToast("Profile deleted");
  });
}

if (profileExportButton) {
  profileExportButton.addEventListener("click", () => {
    const name = profileSelect?.value || profileNameInput?.value.trim();
    if (!name) {
      showToast("Select a profile");
      return;
    }
    const profile = getProfileByName(name);
    if (!profile) {
      showToast("Profile not found");
      return;
    }
    const content = formatEnv(profile);
    downloadFile(`${name}.env`, content);
  });
}

if (profileImportButton && profileImportFile) {
  profileImportButton.addEventListener("click", () => {
    profileImportFile.value = "";
    profileImportFile.click();
  });

  profileImportFile.addEventListener("change", () => {
    const file = profileImportFile.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result || "");
      let imported = [];
      if (file.name.endsWith(".env")) {
        const config = parseEnvContent(content);
        const name = file.name.replace(/\.env$/i, "") || "Imported profile";
        imported = [{ name, config }];
      } else {
        try {
          const parsed = JSON.parse(content);
          if (Array.isArray(parsed)) {
            imported = parsed;
          } else if (Array.isArray(parsed?.profiles)) {
            imported = parsed.profiles;
          } else if (parsed?.name && parsed?.config) {
            imported = [parsed];
          }
        } catch (err) {
          showToast("Import failed");
          return;
        }
      }

      if (!imported.length) {
        showToast("No profiles found");
        return;
      }

      const existing = loadProfiles();
      imported.forEach((profile) => {
        const name = profile?.name?.trim();
        if (!name || !profile?.config) return;
        const exists = existing.find((item) => item.name === name);
        if (exists) {
          const overwrite = window.confirm(`Profile "${name}" exists. Overwrite?`);
          if (!overwrite) return;
          existing.splice(existing.indexOf(exists), 1);
        }
        existing.push({ name, config: normalizeProfileConfig(profile.config) });
      });
      saveProfiles(existing);
      renderProfileSelect();
      showToast("Profiles imported");
    };
    reader.readAsText(file);
  });
}

document.getElementById("save-config").addEventListener("click", (event) => {
  event.preventDefault();
  saveConfig();
});

document.getElementById("reload-config").addEventListener("click", (event) => {
  event.preventDefault();
  reloadConfig();
});

if (cfgUseKeychain) {
  cfgUseKeychain.addEventListener("change", async () => {
    if (!keychainAvailable) {
      cfgUseKeychain.checked = false;
      showToast("Keychain unavailable");
      renderKeychainStatus();
      return;
    }
    if (configLocked) {
      cfgUseKeychain.checked = !cfgUseKeychain.checked;
      showToast("Config is locked");
      renderKeychainStatus();
      return;
    }
    const desired = cfgUseKeychain.checked;
    const ok = await updateConfigPartial(
      { use_keychain: desired },
      desired ? "Keychain enabled" : "Keychain disabled"
    );
    if (!ok) {
      cfgUseKeychain.checked = !desired;
    }
    renderKeychainStatus();
  });
}

if (cfgLock) {
  cfgLock.addEventListener("change", async () => {
    const desired = cfgLock.checked;
    const ok = await updateConfigPartial(
      { config_lock: desired },
      desired ? "Environment locked" : "Environment unlocked"
    );
    if (!ok) {
      cfgLock.checked = !desired;
    }
  });
}

if (refreshTenantInfoButton) {
  refreshTenantInfoButton.addEventListener("click", () => {
    loadTenantInfo();
  });
}

if (healthCheckButton) {
  healthCheckButton.addEventListener("click", (event) => {
    event.preventDefault();
    runHealthCheck();
  });
}

if (warningDismiss) {
  warningDismiss.addEventListener("click", () => {
    hideWarningBanner();
  });
}

if (graphStatusDismiss) {
  graphStatusDismiss.addEventListener("click", () => {
    hideGraphStatusBanner();
  });
}

if (sshConnectButton) {
  sshConnectButton.addEventListener("click", () => {
    connectSsh();
  });
}

if (sshDisconnectButton) {
  sshDisconnectButton.addEventListener("click", () => {
    disconnectSsh();
  });
}

if (sshSendButton && sshTerminalInput) {
  sshSendButton.addEventListener("click", () => {
    const value = sshTerminalInput.value;
    if (!value) return;
    sendSshInput(`${value}\n`);
    sshTerminalInput.value = "";
  });
}

if (sshTerminalInput) {
  sshTerminalInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const value = sshTerminalInput.value;
      if (!value) return;
      sendSshInput(`${value}\n`);
      sshTerminalInput.value = "";
    }
    if (event.ctrlKey && event.key.toLowerCase() === "c") {
      event.preventDefault();
      sendSshInput("\u0003");
    }
  });
}

if (sshInterruptButton) {
  sshInterruptButton.addEventListener("click", () => {
    sendSshInput("\u0003");
  });
}

if (actionPackPrevButton) {
  actionPackPrevButton.addEventListener("click", () => {
    const packs = getAllActionPacks();
    const { pageIndex } = getActionPackPaging(packs);
    if (pageIndex > 0) {
      setActionPackPageIndex(pageIndex - 1);
      renderActionPacks();
    }
  });
}

if (actionPackNextButton) {
  actionPackNextButton.addEventListener("click", () => {
    const packs = getAllActionPacks();
    const { pageIndex, totalPages } = getActionPackPaging(packs);
    if (pageIndex < totalPages - 1) {
      setActionPackPageIndex(pageIndex + 1);
      renderActionPacks();
    }
  });
}

if (actionPackFilterSelect) {
  actionPackFilterSelect.value = getActionPackFilter();
  actionPackFilterSelect.addEventListener("change", () => {
    setActionPackFilter(actionPackFilterSelect.value);
    setActionPackPageIndex(0);
    renderActionPacks();
  });
}

if (actionPackRunButton) {
  actionPackRunButton.addEventListener("click", () => {
    runSelectedActionPack();
  });
}

if (actionPackRunCancelButton) {
  actionPackRunCancelButton.addEventListener("click", () => {
    if (!selectedPackId) {
      showToast("No pack selected");
      return;
    }
    cancelActionPack(selectedPackId);
  });
}

if (actionPackHistoryClear) {
  actionPackHistoryClear.addEventListener("click", () => {
    const confirmDelete = window.confirm("Clear action pack history?");
    if (!confirmDelete) return;
    saveActionPackHistory([]);
    renderActionPackHistory();
  });
}

if (reportQueueStopButton) {
  reportQueueStopButton.addEventListener("click", () => {
    stopReportQueue();
  });
}

if (reportQueueClearButton) {
  reportQueueClearButton.addEventListener("click", () => {
    reportQueue.length = 0;
    renderReportQueue();
  });
}

if (reportHistoryClear) {
  reportHistoryClear.addEventListener("click", () => {
    const confirmDelete = window.confirm("Clear report history?");
    if (!confirmDelete) return;
    saveReportHistory([]);
    renderReportHistory();
  });
}

if (reportDiffRunButton) {
  reportDiffRunButton.addEventListener("click", () => {
    runReportDiff();
  });
}

if (reportDiffSelectA) {
  reportDiffSelectA.addEventListener("change", () => {
    runReportDiff();
  });
}

if (reportDiffSelectB) {
  reportDiffSelectB.addEventListener("change", () => {
    runReportDiff();
  });
}

if (packAddStepButton) {
  packAddStepButton.addEventListener("click", () => {
    addStepToPack();
  });
}

if (packSaveButton) {
  packSaveButton.addEventListener("click", () => {
    savePackFromBuilder();
  });
}

if (packNewButton) {
  packNewButton.addEventListener("click", () => {
    resetPackBuilder();
  });
}

if (packDeleteButton) {
  packDeleteButton.addEventListener("click", () => {
    deletePackFromBuilder();
  });
}

if (exportActionPacksButton) {
  exportActionPacksButton.addEventListener("click", () => {
    exportActionPacks();
  });
}

if (importActionPacksButton && actionPackImportFile) {
  importActionPacksButton.addEventListener("click", () => {
    actionPackImportFile.value = "";
    actionPackImportFile.click();
  });
  actionPackImportFile.addEventListener("change", () => {
    const file = actionPackImportFile.files?.[0];
    if (!file) return;
    importActionPacks(file);
  });
}

if (exportTemplatesButton) {
  exportTemplatesButton.addEventListener("click", () => {
    exportTemplates();
  });
}

if (importTemplatesButton && templateImportFile) {
  importTemplatesButton.addEventListener("click", () => {
    templateImportFile.value = "";
    templateImportFile.click();
  });
  templateImportFile.addEventListener("change", () => {
    const file = templateImportFile.files?.[0];
    if (!file) return;
    importTemplates(file);
  });
}

if (exportReportPresetsButton) {
  exportReportPresetsButton.addEventListener("click", () => {
    const presets = loadReportPresets();
    downloadJson({ presets }, "report-presets.json");
  });
}

if (importReportPresetsButton && reportPresetsImportFile) {
  importReportPresetsButton.addEventListener("click", () => {
    reportPresetsImportFile.value = "";
    reportPresetsImportFile.click();
  });
  reportPresetsImportFile.addEventListener("change", () => {
    const file = reportPresetsImportFile.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const parsed = JSON.parse(reader.result);
        const incoming = Array.isArray(parsed) ? parsed : parsed?.presets;
        if (!Array.isArray(incoming)) {
          showToast("No presets found");
          return;
        }
        const existing = loadReportPresets();
        incoming.forEach((preset) => {
          const normalized = normalizeReportPreset(preset);
          if (!normalized) return;
          const idx = existing.findIndex((item) => item.id === normalized.id);
          if (idx >= 0) {
            existing[idx] = normalized;
          } else {
            existing.push(normalized);
          }
        });
        saveReportPresets(existing);
        renderReportPresets();
        showToast("Presets imported");
      } catch (err) {
        showToast("Import failed");
      }
    };
    reader.readAsText(file);
  });
}

if (presetAddStepButton) {
  presetAddStepButton.addEventListener("click", () => {
    addStepToPreset();
  });
}

if (presetSaveButton) {
  presetSaveButton.addEventListener("click", () => {
    savePresetFromBuilder();
  });
}

if (presetNewButton) {
  presetNewButton.addEventListener("click", () => {
    resetPresetBuilder();
  });
}

if (presetDeleteButton) {
  presetDeleteButton.addEventListener("click", () => {
    deletePresetFromBuilder();
  });
}

if (reportsExportDatasetSelect) {
  reportsExportDatasetSelect.addEventListener("change", () => {
    updateDatasetPreview();
  });
}

if (quickActionsEditButton) {
  quickActionsEditButton.addEventListener("click", () => {
    setQuickActionsEditing(!isQuickActionsEditing());
  });
}

if (quickActionAddButton) {
  quickActionAddButton.addEventListener("click", () => {
    const service = quickActionServiceSelect?.value;
    const action = quickActionActionSelect?.value;
    if (!service || !action) return;
    const list = loadQuickActions();
    const exists = list.some(
      (item) => item.type === "action" && item.service === service && item.action === action
    );
    if (exists) {
      showToast("Quick action already added");
      return;
    }
    list.push({ type: "action", service, action });
    saveQuickActions(list);
    renderQuickActions();
    showToast("Quick action added");
  });
}

if (quickActionResetButton) {
  quickActionResetButton.addEventListener("click", () => {
    saveQuickActions(DEFAULT_QUICK_ACTIONS.slice());
    renderQuickActions();
    showToast("Quick actions reset");
  });
}

if (quickActionAddTemplateButton) {
  quickActionAddTemplateButton.addEventListener("click", () => {
    const templateId = quickActionTemplateSelect?.value;
    if (!templateId) {
      showToast("Select a template");
      return;
    }
    const list = loadQuickActions();
    const exists = list.some((item) => item.type === "template" && item.templateId === templateId);
    if (exists) {
      showToast("Template already pinned");
      return;
    }
    list.push({ type: "template", templateId });
    saveQuickActions(list);
    renderQuickActions();
    showToast("Template pinned");
  });
}

if (quickActionsGrid) {
  quickActionsGrid.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".chip-remove");
    if (removeButton) {
      event.stopPropagation();
      const { type, service, action, templateId } = removeButton.dataset;
      const list = loadQuickActions().filter((item) => {
        if (type === "template") {
          return !(item.type === "template" && item.templateId === templateId);
        }
        return !(item.type === "action" && item.service === service && item.action === action);
      });
      saveQuickActions(list);
      renderQuickActions();
      showToast("Quick action removed");
      return;
    }

    const chip = event.target.closest(".chip");
    if (!chip) return;
    if (isQuickActionsEditing()) {
      showToast("Exit edit mode to run actions");
      return;
    }
    const { type } = chip.dataset;
    if (type === "template") {
      const templateId = chip.dataset.templateId;
      const template = getTemplateById(templateId);
      if (!template) {
        showToast("Template not found");
        return;
      }
      runAction(template.service, template.action, template.params || {});
      return;
    }
    const { service, action } = chip.dataset;
    const params = buildParams(service, action);
    if (params === null) {
      showToast("Action cancelled");
      return;
    }
    runAction(service, action, params);
  });
}

document.querySelectorAll(".runner-run").forEach((button) => {
  button.addEventListener("click", () => {
    const service = button.dataset.service;
    const form = document.querySelector(`.runner[data-service="${service}"]`);
    if (!form) return;
    const action = form.querySelector(".action-select").value;
    const params = collectParams(service);
    if (!params) return;
    runAction(service, action, params);
  });
});

document.querySelectorAll(".runner-queue").forEach((button) => {
  button.addEventListener("click", () => {
    const service = button.dataset.service;
    if (service !== "reports") return;
    const form = document.querySelector(`.runner[data-service="${service}"]`);
    if (!form) return;
    const action = form.querySelector(".action-select").value;
    const params = collectParams(service);
    if (!params) return;
    enqueueReport({ service, action, params, label: activityLabel(service, action) });
  });
});

document.querySelectorAll(".runner-reset").forEach((button) => {
  button.addEventListener("click", () => {
    const service = button.dataset.service;
    const form = document.querySelector(`.runner[data-service="${service}"]`);
    if (!form) return;
    form.reset();
    const jsonInput = form.querySelector(".advanced-json");
    if (jsonInput) {
      jsonInput.value = "";
    }
    const select = form.querySelector(".action-select");
    if (select) {
      select.dispatchEvent(new Event("change"));
    }
    updatePresetOptions(service);
  });
});

document.querySelectorAll(".clear-output").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.outputTarget;
    const panel = document.querySelector(`.output[data-output="${target}"]`);
    if (panel) {
      panel.textContent = "";
    }
    if (target === "ssh") {
      setSshConnectionStatus(sshConnected ? "ok" : "fail", sshConnected ? "Connected" : "Disconnected");
      return;
    }
    setOutputStatus(target, { state: "idle", text: "Idle", meta: "", running: false });
  });
});

document.querySelectorAll(".export-json").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.exportTarget;
    let payload = getExportPayload(target);
    if (!payload) {
      showToast("No data to export");
      return;
    }
    let filename = `${target}-report.json`;
    if (target === "reports") {
      const selection = getSelectedReportDataset();
      if (selection) {
        payload = selection.data;
        const suffix = selection.key && selection.key !== "__full__" ? selection.key : "full";
        filename = `reports-${sanitizeFilename(suffix)}.json`;
      }
    }
    const content = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
    downloadFile(filename, content);
  });
});

document.querySelectorAll(".export-csv").forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.exportTarget;
    let payload = getExportPayload(target);
    if (!payload) {
      showToast("No data to export");
      return;
    }
    let rows = null;
    let filename = `${target}-report.csv`;
    if (target === "reports") {
      const selection = getSelectedReportDataset();
      if (selection) {
        payload = selection.data;
        rows = selectExportArray(payload, {
          preferredKey: selection.key,
          allowPrompt: false,
        });
        const suffix = selection.key && selection.key !== "__full__" ? selection.key : "full";
        filename = `reports-${sanitizeFilename(suffix)}.csv`;
      }
    } else {
      rows = selectExportArray(payload);
    }
    if (rows === null) {
      if (payload && typeof payload === "object" && !Array.isArray(payload)) {
        rows = [payload];
      } else if (Array.isArray(payload)) {
        rows = payload;
      }
    }
    if (!rows || !rows.length) {
      showToast("No tabular data to export");
      return;
    }
    const content = toCsv(rows);
    downloadFile(filename, content);
  });
});

if (exportReportsAllButton) {
  exportReportsAllButton.addEventListener("click", () => {
    exportReportsAllZip();
  });
}

setSection("dashboard");
fetchStatus();
Object.keys(ACTIONS_UI).forEach((service) => populateRunner(service));
fetchConfig();
populateQuickActionEditor();
renderQuickActions();
renderTemplateSelect();
populatePackStepBuilder();
resetPackBuilder();
renderActionPackRunner(null);
populatePresetStepBuilder();
resetPresetBuilder();
setQuickActionsEditing(false);
decorateChips();
setupOutputViews();
initTileLayout();
renderActionPacks();
renderReportPresets();
updateReportExportOptions(getExportPayload("reports"));
renderActionPackHistory();
renderReportHistory();
renderReportQueue();
renderActivity(loadActivity());
updateMetrics();
if (sshTerminalOutput) {
  setSshConnectionStatus("fail", "Disconnected");
}
