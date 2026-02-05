const navLinks = document.querySelectorAll(".nav-link");
const navGroupToggles = document.querySelectorAll(".nav-group-toggle");
const panels = document.querySelectorAll("[data-panel]");
const pageTitle = document.getElementById("page-title");
const pageSubtitle = document.getElementById("page-subtitle");
const toast = document.getElementById("toast");
const navToggle = document.getElementById("nav-toggle");
const sidebar = document.getElementById("sidebar");
const navList = document.querySelector(".nav");
const helpLinkButton = document.getElementById("help-link");
const modePill = document.getElementById("mode-pill");
const modeTitle = document.getElementById("mode-title");
const modeSubtitle = document.getElementById("mode-subtitle");
const statusBadge = document.getElementById("status-badge");
const warningBanner = document.getElementById("warning-banner");
const warningMessage = document.getElementById("warning-message");
const warningMeta = document.getElementById("warning-meta");
const warningDismiss = document.getElementById("warning-dismiss");
const graphStatusBanner = document.getElementById("graph-status-banner");
const graphStatusMessage = document.getElementById("graph-status-message");
const graphStatusMeta = document.getElementById("graph-status-meta");
const graphStatusActions = document.getElementById("graph-status-actions");
const graphStatusDismiss = document.getElementById("graph-status-dismiss");
const snapshotDiffTriage = document.getElementById("snapshot-diff-triage");
const reportDiffTriage = document.getElementById("report-diff-triage");
const snapshotDiffCopy = document.getElementById("snapshot-diff-copy");
const reportDiffCopy = document.getElementById("report-diff-copy");
const workspaceSelect = document.getElementById("workspace-select");
const workspaceNewButton = document.getElementById("workspace-new");
const workspaceRenameButton = document.getElementById("workspace-rename");
const workspaceDuplicateButton = document.getElementById("workspace-duplicate");
const workspaceDeleteButton = document.getElementById("workspace-delete");
const workspaceAddTileButton = document.getElementById("workspace-add-tile");
const workspaceExportButton = document.getElementById("workspace-export");
const workspaceImportButton = document.getElementById("workspace-import");
const workspaceImportFile = document.getElementById("workspace-import-file");
const workspaceSaveButton = document.getElementById("workspace-save");
const workspaceGrid = document.getElementById("workspace-grid");
const workspaceEmpty = document.getElementById("workspace-empty");
const workspaceTemplates = document.getElementById("workspace-templates");
let diffImpactOverrides = {};
let activeIncidentId = null;
const snapshotDiffCache = new Map();
const reportDiffCache = new Map();
const SECTION_ALIASES = {
  incidents: "reports",
  snapshotcapture: "reports",
  quickactions: "dashboard",
  healthcheck: "settings",
  auditlog: "settings",
  snapshots: "reports",
};
const MODE_MAP = {
  dashboard: "observe",
  incidents: "observe",
  workspaces: "observe",
  baselines: "analyze",
  healthcheck: "configure",
  auditlog: "observe",
  reports: "analyze",
  snapshots: "observe",
  eventlogs: "observe",
  registry: "observe",
  time: "observe",
  certificates: "observe",
  processes: "observe",
  topology: "observe",
  exchange: "act",
  onedrive: "act",
  sharepoint: "act",
  teams: "act",
  entra: "act",
  azure: "act",
  defender: "act",
  powerplatform: "act",
  purview: "act",
  localad: "act",
  endpoint: "act",
  domaincontroller: "act",
  printers: "act",
  network: "act",
  remote_workflows: "act",
  ssh: "act",
  fileserver: "act",
  actionpacks: "act",
  snapshotcapture: "act",
  quickactions: "act",
  settings: "configure",
  help: "learn",
};

const MODE_META = {
  observe: {
    label: "Observe",
    subtitle: "System status, snapshots, baselines, and read-only diagnostics.",
  },
  analyze: {
    label: "Analyze",
    subtitle: "Diffs, baselines, reports, and trend reasoning.",
  },
  act: {
    label: "Act",
    subtitle: "Run task runners and action packs with explicit execution controls.",
  },
  configure: {
    label: "Configure",
    subtitle: "Environment configuration, profiles, targets, and secrets.",
  },
  learn: {
    label: "Learn",
    subtitle: "Reference documentation, workflows, and troubleshooting guidance.",
  },
};
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
const cfgMockMode = document.getElementById("cfg-mock-mode");
const cfgKeychainStatus = document.getElementById("cfg-keychain-status");
const cfgLockNote = document.getElementById("cfg-lock-note");
const cfgTimeWarn = document.getElementById("cfg-time-warn");
const cfgTimeHigh = document.getElementById("cfg-time-high");
const cfgNtpServers = document.getElementById("cfg-ntp-servers");
const cfgCertStores = document.getElementById("cfg-cert-stores");
const cfgCertExpiring = document.getElementById("cfg-cert-expiring");
const cfgTlsEndpoints = document.getElementById("cfg-tls-endpoints");
const cfgLatencyEndpoints = document.getElementById("cfg-latency-endpoints");
const cfgProcessMax = document.getElementById("cfg-process-max");
const cfgProcessCmdline = document.getElementById("cfg-process-cmdline");
const cfgDnsProbeTargets = document.getElementById("cfg-dns-probe-targets");
const cfgDnsResolvers = document.getElementById("cfg-dns-resolvers");
const cfgPublicResolvers = document.getElementById("cfg-public-resolvers");
const cfgZoneMap = document.getElementById("cfg-zone-map");
const cfgDiffImpactOverrides = document.getElementById("cfg-diff-impact-overrides");
const cfgAllowRemoteDangerous = document.getElementById("cfg-allow-remote-dangerous");
const sshTargetIdInput = document.getElementById("ssh-target-id");
const sshTargetNameInput = document.getElementById("ssh-target-name");
const sshTargetHostInput = document.getElementById("ssh-target-host");
const sshTargetUserInput = document.getElementById("ssh-target-user");
const sshTargetPortInput = document.getElementById("ssh-target-port");
const sshTargetKeyInput = document.getElementById("ssh-target-key");
const sshTargetTagsInput = document.getElementById("ssh-target-tags");
const sshTargetStrictInput = document.getElementById("ssh-target-strict");
const sshTargetSaveButton = document.getElementById("ssh-target-save");
const sshTargetClearButton = document.getElementById("ssh-target-clear");
const sshTargetList = document.getElementById("ssh-target-list");
const tenantName = document.getElementById("tenant-name");
const tenantIdField = document.getElementById("tenant-id");
const tenantDomains = document.getElementById("tenant-domains");
const refreshTenantInfoButton = document.getElementById("refresh-tenant-info");
const saveConfigButton = document.getElementById("save-config");
const reloadConfigButton = document.getElementById("reload-config");
const configExportButton = document.getElementById("config-export");
const configImportButton = document.getElementById("config-import");
const configPassphraseInput = document.getElementById("config-passphrase");
const configImportFile = document.getElementById("config-import-file");
const metricTenants = document.getElementById("metric-tenants");
const metricTasks = document.getElementById("metric-tasks");
const metricSuccess = document.getElementById("metric-success");
const statusCompleteness = document.getElementById("status-completeness");
const statusWarnings = document.getElementById("status-warnings");
const statusWarningSummary = document.getElementById("status-warning-summary");
const statusLastSnapshot = document.getElementById("status-last-snapshot");
const statusGraphReady = document.getElementById("status-graph-ready");
const statusPsReady = document.getElementById("status-ps-ready");
const statusViewDetails = document.getElementById("status-view-details");
const recentSnapshotsList = document.getElementById("recent-snapshots-list");
const snapshotsViewHistory = document.getElementById("snapshots-view-history");
const quickActionsCard = document.getElementById("quick-actions-card");
const quickActionsGrid = document.getElementById("quick-actions");
const quickActionsEditor = document.getElementById("quick-actions-editor");
const quickActionsEditButton = document.getElementById("edit-quick-actions");
const quickLinks = document.getElementById("quick-links");
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
const smokeTestButton = document.getElementById("run-smoke-test");
const healthStatusText = document.getElementById("health-status-text");
const healthSpinner = document.getElementById("health-spinner");
const healthProgress = document.getElementById("health-progress");
const securityRefreshButton = document.getElementById("security-refresh");
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
const packSaveCopyButton = document.getElementById("pack-save-copy");
const packVersionSelect = document.getElementById("pack-version-select");
const packVersionRestoreButton = document.getElementById("pack-version-restore");
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
const actionPackPreviewButton = document.getElementById("action-pack-preview");
const actionPackValidateButton = document.getElementById("action-pack-validate");
const actionPackDryRunToggle = document.getElementById("action-pack-dry-run");
const actionPackRunCancelButton = document.getElementById("action-pack-run-cancel");
const actionPackHowPanel = document.getElementById("action-pack-how");
const actionPackPlanPanel = document.getElementById("action-pack-plan");
const actionPackLastRun = document.getElementById("action-pack-last-run");
const packScopeSelect = document.getElementById("pack-scope");
const actionPackHistoryList = document.getElementById("action-pack-history-list");
const actionPackHistoryClear = document.getElementById("action-pack-history-clear");
const actionPackDeletedList = document.getElementById("action-pack-deleted-list");
const exportReportPresetsButton = document.getElementById("export-report-presets");
const importReportPresetsButton = document.getElementById("import-report-presets");
const reportPresetsImportFile = document.getElementById("report-presets-import-file");
const reportQueueList = document.getElementById("report-queue-list");
const reportQueueStopButton = document.getElementById("report-queue-stop");
const reportQueueClearButton = document.getElementById("report-queue-clear");
const auditRefreshButton = document.getElementById("audit-refresh");
const auditExportJsonButton = document.getElementById("audit-export-json");
const auditExportCsvButton = document.getElementById("audit-export-csv");
const auditServiceSelect = document.getElementById("audit-service");
const auditActionInput = document.getElementById("audit-action");
const auditStatusSelect = document.getElementById("audit-status");
const auditUserInput = document.getElementById("audit-user");
const auditQueryInput = document.getElementById("audit-query");
const auditSinceInput = document.getElementById("audit-since");
const auditUntilInput = document.getElementById("audit-until");
const auditLimitSelect = document.getElementById("audit-limit");
const auditTableBody = document.getElementById("audit-table-body");
const auditEmptyNote = document.getElementById("audit-empty");
const reportHistoryList = document.getElementById("report-history-list");
const reportHistoryClear = document.getElementById("report-history-clear");
const incidentRunButton = document.getElementById("incident-run");
const incidentRunFixButton = document.getElementById("incident-run-fix");
const incidentUserInput = document.getElementById("incident-user");
const incidentDeviceInput = document.getElementById("incident-device");
const incidentLookbackInput = document.getElementById("incident-lookback");
const incidentStartInput = document.getElementById("incident-start");
const incidentEndInput = document.getElementById("incident-end");
const incidentSymptomInput = document.getElementById("incident-symptom");
const reportDiffSelectA = document.getElementById("report-diff-a");
const reportDiffSelectB = document.getElementById("report-diff-b");
const reportDiffRunButton = document.getElementById("report-diff-run");
const reportDiffMeta = document.getElementById("report-diff-meta");
const reportDiffOutput = document.getElementById("report-diff-output");
const draftSelect = document.getElementById("draft-select");
const draftNewButton = document.getElementById("draft-new");
const draftArchiveButton = document.getElementById("draft-archive");
const draftTitleInput = document.getElementById("draft-title");
const draftNotesInput = document.getElementById("draft-notes");
const draftSubjectKind = document.getElementById("draft-subject-kind");
const draftSubjectValue = document.getElementById("draft-subject-value");
const draftSubjectName = document.getElementById("draft-subject-name");
const draftProfileSelect = document.getElementById("draft-profile");
const draftFinalizeButton = document.getElementById("draft-finalize");
const draftClearButton = document.getElementById("draft-clear");
const draftEntriesList = document.getElementById("draft-entries-list");
const draftEmptyNote = document.getElementById("draft-empty");
const incidentReportSelect = document.getElementById("incident-report-select");
const incidentReportLoadButton = document.getElementById("incident-report-load");
const incidentReportTitle = document.getElementById("incident-report-title");
const incidentReportClient = document.getElementById("incident-report-client");
const incidentReportReportedBy = document.getElementById("incident-report-reported-by");
const incidentReportSeverity = document.getElementById("incident-report-severity");
const incidentReportStatus = document.getElementById("incident-report-status");
const incidentReportReportedAt = document.getElementById("incident-report-reported-at");
const incidentReportResolvedAt = document.getElementById("incident-report-resolved-at");
const incidentReportImpactStart = document.getElementById("incident-report-impact-start");
const incidentReportImpactEnd = document.getElementById("incident-report-impact-end");
const incidentReportSummaryReported = document.getElementById("incident-report-summary-reported");
const incidentReportSummaryActual = document.getElementById("incident-report-summary-actual");
const incidentReportRootCause = document.getElementById("incident-report-root-cause");
const incidentReportResolution = document.getElementById("incident-report-resolution");
const incidentReportValidation = document.getElementById("incident-report-validation");
const incidentReportPreventive = document.getElementById("incident-report-preventive");
const incidentReportAffected = document.getElementById("incident-report-affected");
const incidentReportTimeline = document.getElementById("incident-report-timeline");
const incidentReportTimelineAuto = document.getElementById("incident-report-timeline-auto");
const incidentReportTimelineAdd = document.getElementById("incident-report-timeline-add");
const incidentReportEvidence = document.getElementById("incident-report-evidence");
const incidentReportEvidenceRefresh = document.getElementById("incident-report-evidence-refresh");
const incidentReportPreview = document.getElementById("incident-report-preview");
const incidentReportPreviewOutput = document.getElementById("incident-report-preview-output");
const incidentReportRedaction = document.getElementById("incident-report-redaction");
const incidentReportExportMd = document.getElementById("incident-report-export-md");
const incidentReportExportText = document.getElementById("incident-report-export-text");
const incidentReportExportPdf = document.getElementById("incident-report-export-pdf");
const incidentReportSave = document.getElementById("incident-report-save");
const incidentReportReset = document.getElementById("incident-report-reset");
const reportCollapsibleButtons = document.querySelectorAll(".report-collapsible summary .card-actions button");
const snapshotSubjectSelect = document.getElementById("snapshot-subject-select");
const snapshotHistoryList = document.getElementById("snapshot-history-list");
const snapshotHistoryRefresh = document.getElementById("snapshot-history-refresh");
const snapshotDiffSelectA = document.getElementById("snapshot-diff-a");
const snapshotDiffSelectB = document.getElementById("snapshot-diff-b");
const snapshotDiffRunButton = document.getElementById("snapshot-diff-run");
const snapshotDiffMeta = document.getElementById("snapshot-diff-meta");
const snapshotDiffOutput = document.getElementById("snapshot-diff-output");
const snapshotQualityMeta = document.getElementById("snapshot-quality-meta");
const snapshotQualityOutput = document.getElementById("snapshot-quality-output");
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
const topologyCollectButton = document.getElementById("topology-collect");
const topologyPingButton = document.getElementById("topology-ping");
const topologyReportButton = document.getElementById("topology-report");
const topologyExportJsonButton = document.getElementById("topology-export-json");
const topologyExportCsvButton = document.getElementById("topology-export-csv");
const topologyHistoryDepthSelect = document.getElementById("topology-history-depth");
const topologyDiff24hButton = document.getElementById("topology-diff-24h");
const topologyDiffSelectA = document.getElementById("topology-diff-a");
const topologyDiffSelectB = document.getElementById("topology-diff-b");
const topologyDiffRunButton = document.getElementById("topology-diff-run");
const topologyTimelineList = document.getElementById("topology-timeline");
const issueUserInput = document.getElementById("issue-user");
const issueDeviceInput = document.getElementById("issue-device");
const issueSymptomTemplate = document.getElementById("issue-symptom-template");
const issueSymptomInput = document.getElementById("issue-symptom");
const issueAddButton = document.getElementById("issue-add");
const issueClearButton = document.getElementById("issue-clear");
const issueList = document.getElementById("issue-list");
const incidentList = document.getElementById("incident-list");
const outputSearchQueries = {};
const lastOutputs = {};
const lastNormalized = {};
const lastRunMeta = {};
const lastOutputStatus = {};
const GLOBAL_ADMIN_CACHE = new Map();
const GLOBAL_ADMIN_CACHE_TTL_MS = 5 * 60 * 1000;
const IMPACT_WARN_THRESHOLD = 25;
const GLOBAL_ADMIN_CHECK_SERVICES = new Set(["entra", "exchange", "onedrive", "sharepoint", "teams", "reports"]);
const outputTimers = new Map();
const outputStartTimes = new Map();
const outputStatusPrefixes = new Map();
const lastActionContext = {};
let snapshotHistoryItems = [];
let snapshotEntities = [];
let symptomTemplates = [];
let goldenBaselines = [];
let draftSnapshots = [];
let activeDraftId = null;
let incidentReport = null;
const tableRowCurrent = new WeakMap();
const tableRowOriginal = new WeakMap();
const prettyRowCurrent = new WeakMap();
const prettyRowOriginal = new WeakMap();
const graphStates = {};
const SENSITIVE_PARAM_KEYS = new Set([
  "password",
  "passphrase",
  "secret",
  "token",
  "access_token",
  "refresh_token",
  "client_secret",
  "private_key",
  "apikey",
  "api_key",
  "credential",
  "credentials",
  "pfx",
]);

const subtitles = {
  dashboard: "Graph-first operations with PowerShell fallback",
  incidents: "Incident workspace, timeline, and evidence",
  workspaces: "Saved multi-block dashboards",
  actionpacks: "Run multi-step workflows",
  snapshotcapture: "Draft snapshots built from collected results",
  quickactions: "Dashboard shortcuts and pinned tasks",
  healthcheck: "System health, readiness, and diagnostics",
  auditlog: "Audit trail and system events",
  exchange: "Mail, calendars, and shared mailbox controls",
  onedrive: "Drive operations, permissions, and sync",
  sharepoint: "Sites, lists, and pages management",
  teams: "Teams, channels, and messaging",
  entra: "Directory, groups, and app inventory",
  azure: "Subscription and infrastructure inventory",
  defender: "Defender for Cloud",
  powerplatform: "Power Platform admin",
  localad: "Local Active Directory (on-prem)",
  endpoint: "Endpoint inventory and diagnostics",
  domaincontroller: "Domain controller replication and health",
  printers: "On-prem print servers and GPO checks",
  network: "On-prem network adapters and IP settings",
  ssh: "Remote workstation sessions over SSH",
  fileserver: "On-prem file share enumeration",
  topology: "Live on-prem device and service topology",
  remote_workflows: "Remote-only workflows with explainable guidance",
  time: "Time sync and drift intelligence",
  certificates: "Certificate inventory and TLS trust",
  processes: "Process, service, and binary reality checks",
  baselines: "Golden baselines and drift comparison",
  snapshots: "Snapshot history, diffs, and coverage",
  eventlogs: "Event log summaries and EVTX evidence",
  registry: "Registry watchlists and exports",
  reports: "Audit-ready reports and summaries",
  purview: "Compliance and data governance",
  settings: "Local session and credentials",
  help: "In-app documentation and how-to guidance",
};

const serviceLabels = {
  incidents: "Incidents",
  workspaces: "Workspaces",
  actionpacks: "Action Packs",
  snapshotcapture: "Draft Snapshots",
  quickactions: "Quick Actions",
  healthcheck: "Health Check",
  auditlog: "Audit Log",
  onedrive: "OneDrive",
  sharepoint: "SharePoint",
  powerplatform: "Power Platform",
  localad: "Local AD",
  endpoint: "Endpoints",
  domaincontroller: "Domain Controller",
  printers: "Printers",
  network: "Network",
  ssh: "SSH",
  fileserver: "File Server",
  topology: "Network Topology",
  remote_workflows: "Remote Workflows",
  defender: "Defender for Cloud",
  time: "Time & Drift",
  certificates: "Certificates",
  processes: "Processes",
  baselines: "Baselines",
  snapshots: "Snapshots",
  eventlogs: "Event Logs",
  registry: "Registry",
  help: "Help",
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
    list_mailbox_permissions: {
      label: "List mailbox permissions",
      mode: "powershell",
      fields: [{ key: "shared_mailbox", label: "Shared mailbox UPN" }],
    },
    add_mailbox_permission: {
      label: "Add mailbox permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
        { key: "access_rights", label: "Access rights", placeholder: "FullAccess" },
        { key: "automapping", label: "Auto mapping", type: "checkbox", defaultChecked: true },
      ],
    },
    remove_mailbox_permission: {
      label: "Remove mailbox permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
        { key: "access_rights", label: "Access rights", placeholder: "FullAccess" },
      ],
    },
    list_send_as_permissions: {
      label: "List send-as permissions",
      mode: "powershell",
      fields: [{ key: "shared_mailbox", label: "Shared mailbox UPN" }],
    },
    add_send_as_permission: {
      label: "Add send-as permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
      ],
    },
    remove_send_as_permission: {
      label: "Remove send-as permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
      ],
    },
    list_send_on_behalf: {
      label: "List send-on-behalf delegates",
      mode: "powershell",
      fields: [{ key: "shared_mailbox", label: "Shared mailbox UPN" }],
    },
    add_send_on_behalf: {
      label: "Add send-on-behalf delegate",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
      ],
    },
    remove_send_on_behalf: {
      label: "Remove send-on-behalf delegate",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Shared mailbox UPN" },
        { key: "user_id", label: "User UPN or ID" },
      ],
    },
    list_mailbox_folder_permissions: {
      label: "List folder permissions",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Mailbox UPN" },
        { key: "folder_path", label: "Folder path", placeholder: "Calendar" },
      ],
    },
    add_mailbox_folder_permission: {
      label: "Add folder permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Mailbox UPN" },
        { key: "folder_path", label: "Folder path", placeholder: "Calendar" },
        { key: "user_id", label: "User UPN or ID" },
        { key: "access_rights", label: "Access rights", placeholder: "Editor" },
        { key: "delegate", label: "Delegate", type: "checkbox" },
      ],
    },
    update_mailbox_folder_permission: {
      label: "Update folder permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Mailbox UPN" },
        { key: "folder_path", label: "Folder path", placeholder: "Calendar" },
        { key: "user_id", label: "User UPN or ID" },
        { key: "access_rights", label: "Access rights", placeholder: "Editor" },
        { key: "delegate", label: "Delegate", type: "checkbox" },
      ],
    },
    remove_mailbox_folder_permission: {
      label: "Remove folder permission",
      mode: "powershell",
      fields: [
        { key: "shared_mailbox", label: "Mailbox UPN" },
        { key: "folder_path", label: "Folder path", placeholder: "Calendar" },
        { key: "user_id", label: "User UPN or ID" },
      ],
    },
  },
  onedrive: {
    list_drive_items: {
      label: "List drive items",
      mode: "graph",
      fields: [
        { key: "user_id", label: "User UPN or ID (optional)" },
        { key: "folder_id", label: "Folder ID (optional)" },
      ],
    },
    get_user_drive_id: {
      label: "Resolve OneDrive drive ID from user (UPN/Object ID)",
      mode: "graph",
      fields: [
        { key: "user_id", label: "User UPN or ID (optional)" },
        { key: "force_live", label: "Refresh (force live)", type: "checkbox" },
      ],
    },
    drive_cache_status: {
      label: "OneDrive drive cache status",
      mode: "local",
      fields: [],
    },
    warm_drive_cache: {
      label: "Warm OneDrive drive cache",
      mode: "graph",
      fields: [
        { key: "upns", label: "UPNs (optional)", placeholder: "user1@contoso.com, user2@contoso.com" },
        { key: "max_items", label: "Max items", type: "number", placeholder: "50" },
      ],
    },
    requeue_drive_resolution: {
      label: "Requeue drive resolution",
      mode: "local",
      fields: [
        { key: "user_upn", label: "User UPN" },
        { key: "delay_seconds", label: "Delay seconds", type: "number", placeholder: "5" },
      ],
    },
    force_live_resolve: {
      label: "Force live drive resolution",
      mode: "graph",
      fields: [
        { key: "user_upn", label: "User UPN" },
        { key: "ignore_circuit_breaker", label: "Ignore circuit breaker", type: "checkbox" },
      ],
    },
    seed_drive_cache: {
      label: "Seed drive cache (manual)",
      mode: "local",
      fields: [
        { key: "user_upn", label: "User UPN" },
        { key: "drive_id", label: "Drive ID" },
        { key: "web_url", label: "Web URL (optional)" },
        { key: "drive_type", label: "Drive type (optional)" },
        { key: "user_object_id", label: "User object ID (optional)" },
      ],
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
    list_list_columns: {
      label: "List list columns",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "list_id", label: "List ID" },
      ],
    },
    create_list_column: {
      label: "Create list column",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "list_id", label: "List ID" },
        { key: "display_name", label: "Column name" },
        { key: "column_type", label: "Column type", placeholder: "text" },
        { key: "required", label: "Required", type: "checkbox" },
        { key: "description", label: "Description" },
        { key: "default_value", label: "Default value" },
        { key: "choices", label: "Choices (comma-separated)" },
      ],
    },
    update_list_column: {
      label: "Update list column",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "list_id", label: "List ID" },
        { key: "column_id", label: "Column ID" },
        { key: "display_name", label: "Display name" },
        { key: "description", label: "Description" },
        { key: "required", label: "Required", type: "checkbox" },
        { key: "hidden", label: "Hidden", type: "checkbox" },
        { key: "default_value", label: "Default value" },
        { key: "choices", label: "Choices (comma-separated)" },
      ],
    },
    delete_list_column: {
      label: "Delete list column",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "list_id", label: "List ID" },
        { key: "column_id", label: "Column ID" },
      ],
    },
    list_site_permissions: {
      label: "List site permissions",
      mode: "graph",
      fields: [{ key: "site_id", label: "Site ID" }],
    },
    grant_site_permission: {
      label: "Grant site permission",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "principal_id", label: "Principal ID" },
        { key: "principal_type", label: "Principal type", placeholder: "user" },
        { key: "roles", label: "Roles (comma-separated)", placeholder: "read,write" },
      ],
    },
    delete_site_permission: {
      label: "Delete site permission",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "permission_id", label: "Permission ID" },
      ],
    },
    update_site_permission: {
      label: "Update site permission",
      mode: "graph",
      fields: [
        { key: "site_id", label: "Site ID" },
        { key: "permission_id", label: "Permission ID" },
        { key: "roles", label: "Roles (comma-separated)", placeholder: "read,write" },
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
    list_channels: {
      label: "List channels",
      mode: "graph",
      fields: [{ key: "team_id", label: "Team ID" }],
    },
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
    list_groups: {
      label: "List groups",
      mode: "graph",
      fields: [
        { key: "top", label: "Top", type: "number", placeholder: "10" },
        { key: "select", label: "Select fields (comma-separated)" },
      ],
    },
    create_group: {
      label: "Create group",
      mode: "graph",
      fields: [
        { key: "display_name", label: "Display name" },
        { key: "mail_nickname", label: "Mail nickname (optional)" },
        { key: "description", label: "Description" },
        { key: "mail_enabled", label: "Mail enabled", type: "checkbox" },
        { key: "security_enabled", label: "Security enabled", type: "checkbox", defaultChecked: true },
        { key: "group_types", label: "Group types (comma-separated)", placeholder: "Unified" },
        { key: "visibility", label: "Visibility", placeholder: "Private" },
      ],
    },
    update_group: {
      label: "Update group",
      mode: "graph",
      fields: [
        { key: "group_id", label: "Group ID" },
        { key: "displayName", label: "Display name" },
        { key: "description", label: "Description" },
        { key: "mailEnabled", label: "Mail enabled", type: "checkbox" },
        { key: "securityEnabled", label: "Security enabled", type: "checkbox" },
        { key: "visibility", label: "Visibility" },
      ],
    },
    delete_group: {
      label: "Delete group",
      mode: "graph",
      fields: [{ key: "group_id", label: "Group ID" }],
    },
    add_group_member: {
      label: "Add group member",
      mode: "graph",
      fields: [
        { key: "group_id", label: "Group ID" },
        { key: "user_id", label: "User ID" },
      ],
    },
    list_group_members: {
      label: "List group members",
      mode: "graph",
      fields: [
        { key: "group_id", label: "Group ID" },
        { key: "top", label: "Top", type: "number", placeholder: "50" },
      ],
    },
    remove_group_member: {
      label: "Remove group member",
      mode: "graph",
      fields: [
        { key: "group_id", label: "Group ID" },
        { key: "member_id", label: "Member ID" },
      ],
    },
    list_role_definitions: {
      label: "List role definitions",
      mode: "graph",
      fields: [{ key: "top", label: "Top", type: "number", placeholder: "20" }],
    },
    list_role_assignments: {
      label: "List role assignments",
      mode: "graph",
      fields: [
        { key: "top", label: "Top", type: "number", placeholder: "50" },
        { key: "principal_id", label: "Principal ID (optional)" },
        { key: "role_definition_id", label: "Role definition ID (optional)" },
        { key: "directory_scope_id", label: "Directory scope ID", placeholder: "/" },
      ],
    },
    assign_role: {
      label: "Assign role",
      mode: "graph",
      fields: [
        { key: "principal_id", label: "Principal ID" },
        { key: "role_definition_id", label: "Role definition ID" },
        { key: "directory_scope_id", label: "Directory scope ID", placeholder: "/" },
      ],
    },
    remove_role_assignment: {
      label: "Remove role assignment",
      mode: "graph",
      fields: [{ key: "role_assignment_id", label: "Role assignment ID" }],
    },
    list_applications: {
      label: "List app registrations",
      mode: "graph",
      fields: [{ key: "top", label: "Top", type: "number", placeholder: "10" }],
    },
    create_application: {
      label: "Create app registration",
      mode: "graph",
      fields: [
        { key: "display_name", label: "Display name" },
        { key: "sign_in_audience", label: "Sign-in audience", placeholder: "AzureADMyOrg" },
        { key: "notes", label: "Notes (optional)" },
      ],
    },
    update_application: {
      label: "Update app registration",
      mode: "graph",
      fields: [
        { key: "app_id", label: "Application ID" },
        { key: "display_name", label: "Display name" },
        { key: "sign_in_audience", label: "Sign-in audience" },
        { key: "notes", label: "Notes" },
      ],
    },
    delete_application: {
      label: "Delete app registration",
      mode: "graph",
      fields: [{ key: "app_id", label: "Application ID" }],
    },
    create_service_principal: {
      label: "Create service principal",
      mode: "graph",
      fields: [{ key: "app_id", label: "Application ID" }],
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
    sign_in_summary: {
      label: "Sign-in summary",
      mode: "graph",
      preflightService: "entra",
      fields: [
        { key: "user_id", label: "User UPN or ID (optional)" },
        { key: "top", label: "Top", type: "number", placeholder: "25" },
        { key: "lookback_hours", label: "Lookback hours (optional)", type: "number", placeholder: "24" },
      ],
    },
    conditional_access_summary: {
      label: "Conditional Access summary",
      mode: "graph",
      preflightService: "entra",
      fields: [],
    },
    device_compliance: {
      label: "Device compliance summary",
      mode: "graph",
      preflightService: "entra",
      fields: [
        { key: "user_id", label: "User UPN or ID (optional)" },
        { key: "top", label: "Top", type: "number", placeholder: "50" },
      ],
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
      label: "List GPOs (Get-GPO -All)",
      mode: "powershell",
      fields: [{ key: "name", label: "Name (optional)" }],
    },
    gpo_links: {
      label: "GPO links (Get-GPLink)",
      mode: "powershell",
      fields: [{ key: "ou_dn", label: "OU distinguished name" }],
    },
    gpo_inheritance: {
      label: "GPO inheritance (Get-GPInheritance)",
      mode: "powershell",
      fields: [{ key: "ou_dn", label: "OU distinguished name" }],
    },
    gpo_report: {
      label: "GPO report (XML/HTML)",
      mode: "powershell",
      fields: [
        { key: "name", label: "GPO name" },
        { key: "report_type", label: "Report type", placeholder: "Xml" },
        { key: "output_path", label: "Output path (optional)" },
      ],
    },
    gppref_registry: {
      label: "GPP registry preferences",
      mode: "powershell",
      fields: [
        { key: "gpo_name", label: "GPO name" },
        { key: "key", label: "Registry key (HKLM\\...)" },
        { key: "value_name", label: "Value name (optional)" },
      ],
    },
    gpresult_report: {
      label: "GPResult report (summary/html)",
      mode: "powershell",
      fields: [
        { key: "report_type", label: "Report type", placeholder: "summary|html" },
        { key: "output_path", label: "Output path (optional)" },
        { key: "include_summary", label: "Include summary", type: "checkbox", defaultChecked: true, sendFalse: true },
      ],
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
  endpoint: {
    computer_info: {
      label: "Computer info",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [],
    },
    cim_summary: {
      label: "CIM summary (system/OS/BIOS)",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [],
    },
    systeminfo: {
      label: "Systeminfo baseline",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [],
    },
    system_inventory: {
      label: "System info snapshot",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [],
    },
    list_processes: {
      label: "List top processes",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [{ key: "top", label: "Top", type: "number", placeholder: "25" }],
    },
    list_services: {
      label: "List services",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [
        { key: "name", label: "Service name filter (optional)" },
        { key: "status", label: "Status filter (optional)", placeholder: "Running" },
      ],
    },
    query_event_logs: {
      label: "Query event logs",
      mode: "powershell",
      fields: [
        { key: "log_name", label: "Log name", placeholder: "System" },
        { key: "provider", label: "Provider (optional)" },
        { key: "level", label: "Level (optional)", placeholder: "2" },
        { key: "event_ids", label: "Event IDs (comma-separated)", placeholder: "6005,6006" },
        { key: "start_time", label: "Start time (optional)" },
        { key: "end_time", label: "End time (optional)" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "50" },
        { key: "contains", label: "Message contains (optional)" },
      ],
    },
    wevtutil_query: {
      label: "Wevtutil query",
      mode: "powershell",
      fields: [
        { key: "log_name", label: "Log name", placeholder: "System" },
        { key: "query", label: "XPath query (optional)" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "50" },
      ],
    },
    legacy_event_log: {
      label: "Legacy event log (Get-EventLog)",
      mode: "powershell",
      fields: [
        { key: "log_name", label: "Log name", placeholder: "System" },
        { key: "source", label: "Source (optional)" },
        { key: "entry_type", label: "Entry type (optional)", placeholder: "Error" },
        { key: "after", label: "After (optional)" },
        { key: "before", label: "Before (optional)" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "50" },
      ],
    },
    list_hotfixes: {
      label: "List hotfixes",
      mode: "powershell",
      fields: [],
    },
    list_dism_packages: {
      label: "DISM packages (raw)",
      mode: "powershell",
      fields: [],
    },
    whoami_all: {
      label: "Whoami /all",
      mode: "powershell",
      fields: [],
    },
    gpresult_report: {
      label: "GPResult report",
      mode: "powershell",
      fields: [
        { key: "report_type", label: "Report type", placeholder: "summary|html" },
        { key: "output_path", label: "Output path (optional)" },
        { key: "include_summary", label: "Include summary", type: "checkbox", defaultChecked: true, sendFalse: true },
      ],
    },
    rsop_report: {
      label: "RSoP report (HTML)",
      mode: "powershell",
      fields: [{ key: "report_path", label: "Output path (optional)" }],
    },
  },
  domaincontroller: {
    list_domain_controllers: {
      label: "List domain controllers",
      mode: "powershell",
      fields: [{ key: "domain", label: "Domain/server (optional)" }],
    },
    list_dcs_nltest: {
      label: "List DCs via nltest",
      mode: "powershell",
      fields: [{ key: "domain", label: "Domain (contoso.local)" }],
    },
    locate_active_dc: {
      label: "Locate active DC via nltest",
      mode: "powershell",
      fields: [{ key: "domain", label: "Domain (contoso.local)" }],
    },
    replication_health_summary: {
      label: "Replication summary",
      mode: "powershell",
      fields: [],
    },
    show_replication_partners: {
      label: "Show replication partners",
      mode: "powershell",
      fields: [{ key: "dc", label: "Domain controller name" }],
    },
    replication_queue: {
      label: "Replication queue",
      mode: "powershell",
      fields: [{ key: "dc", label: "Domain controller name" }],
    },
    force_replication_sync: {
      label: "Force replication sync (careful)",
      mode: "powershell",
      confirm: true,
      fields: [
        { key: "dc", label: "Domain controller name" },
        { key: "flags", label: "Sync flags", placeholder: "AdeP" },
        { key: "execute", label: "Execute now", type: "checkbox" },
      ],
    },
    ad_replication_partner_metadata: {
      label: "AD replication partner metadata",
      mode: "powershell",
      fields: [{ key: "dc", label: "Domain controller (optional)" }],
    },
    ad_replication_failures: {
      label: "AD replication failures",
      mode: "powershell",
      fields: [{ key: "dc", label: "Domain controller (optional)" }],
    },
    ad_replication_queue_operations: {
      label: "AD replication queue operations",
      mode: "powershell",
      fields: [{ key: "dc", label: "Domain controller (optional)" }],
    },
    dc_diagnostics: {
      label: "Run dcdiag",
      mode: "powershell",
      fields: [{ key: "verbose", label: "Verbose mode", type: "checkbox" }],
    },
    get_forest_facts: {
      label: "Forest facts",
      mode: "powershell",
      fields: [],
    },
    get_domain_facts: {
      label: "Domain facts",
      mode: "powershell",
      fields: [],
    },
    list_fsmo_roles: {
      label: "List FSMO roles",
      mode: "powershell",
      fields: [],
    },
    sysvol_migration_state: {
      label: "SYSVOL migration state",
      mode: "powershell",
      fields: [],
    },
    time_sync_status: {
      label: "Time sync status",
      mode: "powershell",
      fields: [],
    },
    time_sync_monitor: {
      label: "Time sync monitor",
      mode: "powershell",
      fields: [{ key: "domain", label: "Domain (optional)" }],
    },
    time_sync_health: {
      label: "Time sync health",
      mode: "powershell",
      fields: [{ key: "domain", label: "Domain (optional)" }],
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
      allowed_targets: ["local", "ssh"],
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
        { key: "hosts", label: "Hosts (comma-separated, optional)" },
        { key: "count", label: "Count", type: "number", placeholder: "4" },
        { key: "timeout_seconds", label: "Timeout (seconds)", type: "number", placeholder: "2" },
        { key: "ipv6", label: "Use IPv6", type: "checkbox" },
        { key: "parallel", label: "Parallel ping", type: "checkbox", defaultChecked: true, sendFalse: true },
        { key: "throttle", label: "Parallel throttle", type: "number", placeholder: "8" },
      ],
    },
    test_port: {
      label: "Test port (TCP probe)",
      mode: "powershell",
      fields: [
        { key: "host", label: "Host or IP" },
        { key: "port", label: "Port", type: "number", placeholder: "443" },
        { key: "information_level", label: "Info level", placeholder: "Detailed" },
      ],
    },
    trace_route: {
      label: "Trace route",
      mode: "powershell",
      fields: [
        { key: "host", label: "Host or IP" },
        { key: "max_hops", label: "Max hops", type: "number", placeholder: "30" },
        { key: "timeout_ms", label: "Timeout (ms)", type: "number", placeholder: "3000" },
        { key: "resolve_names", label: "Resolve hostnames", type: "checkbox" },
      ],
    },
    pathping_analysis: {
      label: "Pathping analysis",
      mode: "powershell",
      fields: [
        { key: "host", label: "Host or IP" },
        { key: "max_hops", label: "Max hops", type: "number", placeholder: "30" },
        { key: "timeout_ms", label: "Timeout (ms)", type: "number", placeholder: "1000" },
        { key: "query_count", label: "Query count", type: "number", placeholder: "1" },
      ],
    },
    resolve_dns_name: {
      label: "Resolve hostname (DNS)",
      mode: "powershell",
      fields: [
        { key: "name", label: "Hostname" },
        { key: "record_type", label: "Record type", placeholder: "A" },
        { key: "server", label: "DNS server (optional)" },
      ],
    },
    list_dns_records: {
      label: "List DNS records",
      mode: "powershell",
      fields: [
        { key: "zone", label: "Zone name" },
        { key: "record_type", label: "Record type (optional)", placeholder: "A" },
        { key: "server", label: "DNS server (optional)" },
        { key: "name_pattern", label: "Name pattern (optional)", placeholder: "*" },
        { key: "max_results", label: "Max results", type: "number", placeholder: "500" },
      ],
    },
    dns_client_servers: {
      label: "DNS client servers",
      mode: "powershell",
      fields: [
        { key: "interface_alias", label: "Interface alias (optional)" },
        { key: "address_family", label: "Address family (optional)", placeholder: "IPv4" },
      ],
    },
    dns_client_cache: {
      label: "DNS client cache",
      mode: "powershell",
      fields: [
        { key: "name_pattern", label: "Name filter (optional)", placeholder: "*" },
        { key: "max_results", label: "Max results", type: "number", placeholder: "1000" },
      ],
    },
    dns_cache_display: {
      label: "DNS cache (ipconfig)",
      mode: "powershell",
      fields: [],
    },
    netstat_connections: {
      label: "Netstat connections",
      mode: "powershell",
      fields: [],
    },
    tcp_connections: {
      label: "TCP connections (Get-NetTCPConnection)",
      mode: "powershell",
      fields: [
        { key: "state", label: "State (optional)", placeholder: "Established" },
        { key: "local_port", label: "Local port (optional)", type: "number" },
        { key: "remote_port", label: "Remote port (optional)", type: "number" },
      ],
    },
    list_routes: {
      label: "Routes (Get-NetRoute)",
      mode: "powershell",
      fields: [
        { key: "interface_alias", label: "Interface alias (optional)" },
        { key: "address_family", label: "Address family (optional)", placeholder: "IPv4" },
      ],
    },
    route_print: {
      label: "Route print (legacy)",
      mode: "powershell",
      fields: [],
    },
    list_ip_configurations: {
      label: "IP configuration summary",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [{ key: "interface_alias", label: "Interface alias (optional)" }],
    },
    list_ip_interfaces: {
      label: "IP interface metrics",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [
        { key: "interface_alias", label: "Interface alias (optional)" },
        { key: "address_family", label: "Address family (optional)", placeholder: "IPv4" },
      ],
    },
    list_adapter_advanced: {
      label: "Adapter advanced properties",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [{ key: "name", label: "Adapter name (optional)" }],
    },
    list_neighbors: {
      label: "On-link neighbors",
      mode: "powershell",
      fields: [
        { key: "interface_alias", label: "Interface alias (optional)" },
        { key: "address_family", label: "Address family (optional)", placeholder: "IPv4" },
      ],
    },
    arp_table: {
      label: "ARP table (arp -a)",
      mode: "powershell",
      fields: [],
    },
    firewall_profiles: {
      label: "Firewall profiles",
      mode: "powershell",
      fields: [],
    },
    firewall_rules: {
      label: "Firewall rules",
      mode: "powershell",
      fields: [
        { key: "name_pattern", label: "Name filter (optional)", placeholder: "*" },
        { key: "direction", label: "Direction (optional)", placeholder: "Inbound" },
        { key: "action", label: "Action (optional)", placeholder: "Allow" },
        { key: "enabled", label: "Enabled only", type: "checkbox" },
        { key: "profile", label: "Profile filter (optional)", placeholder: "Domain" },
      ],
    },
    firewall_ports: {
      label: "Firewall port filters",
      mode: "powershell",
      fields: [
        { key: "local_port", label: "Local port (optional)", type: "number" },
        { key: "remote_port", label: "Remote port (optional)", type: "number" },
        { key: "protocol", label: "Protocol (optional)", placeholder: "TCP" },
      ],
    },
    firewall_quick_check: {
      label: "Firewall profiles & key rules",
      mode: "powershell",
      fields: [
        { key: "local_port", label: "Local port (optional)", type: "number" },
        { key: "program", label: "Program path filter (optional)", placeholder: "*\\app.exe" },
        { key: "direction", label: "Direction (optional)", placeholder: "Inbound" },
        { key: "profile", label: "Profile filter (optional)", placeholder: "Domain" },
      ],
    },
    firewall_settings: {
      label: "Firewall settings",
      mode: "powershell",
      fields: [],
    },
    smb_test_path: {
      label: "Test SMB path",
      mode: "powershell",
      fields: [{ key: "unc_path", label: "UNC path (\\\\server\\\\share)" }],
    },
    smb_connections: {
      label: "SMB connections",
      mode: "powershell",
      fields: [],
    },
    smb_sessions: {
      label: "SMB sessions",
      mode: "powershell",
      fields: [{ key: "server", label: "Server (optional)" }],
    },
    smb_open_files: {
      label: "SMB open files",
      mode: "powershell",
      fields: [{ key: "server", label: "Server (optional)" }],
    },
    smb_client_config: {
      label: "SMB client configuration",
      mode: "powershell",
      fields: [],
    },
    smb_status: {
      label: "SMB status",
      mode: "powershell",
      fields: [{ key: "server", label: "Server (for sessions, optional)" }],
    },
    net_use: {
      label: "Net use mappings",
      mode: "powershell",
      fields: [],
    },
    kerberos_tickets: {
      label: "Kerberos tickets (klist)",
      mode: "powershell",
      fields: [],
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
  remote_workflows: {
    get_endpoint_auth_reality: {
      label: "Endpoint authentication reality check",
      mode: "powershell",
      allowed_targets: ["ssh"],
      fields: [
        { key: "lookback_hours", label: "Lookback hours", type: "number", placeholder: "24" },
        { key: "time_skew_warn_minutes", label: "Time skew warn (minutes)", type: "number", placeholder: "5" },
      ],
    },
    get_effective_policy: {
      label: "Effective policy vs intended",
      mode: "powershell",
      allowed_targets: ["ssh"],
      fields: [
        { key: "lookback_hours", label: "Lookback hours", type: "number", placeholder: "24" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "50" },
      ],
    },
    get_service_process_integrity: {
      label: "Service-to-process integrity",
      mode: "powershell",
      allowed_targets: ["ssh"],
      fields: [
        { key: "lookback_hours", label: "Lookback hours", type: "number", placeholder: "24" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "25" },
      ],
    },
    get_recent_failure_causality: {
      label: "Recent failure causality",
      mode: "powershell",
      allowed_targets: ["ssh"],
      fields: [
        { key: "lookback_hours", label: "Lookback hours", type: "number", placeholder: "24" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "50" },
      ],
    },
    get_host_network_path: {
      label: "Host-perspective network path check",
      mode: "powershell",
      allowed_targets: ["ssh"],
      fields: [
        { key: "target_host", label: "Target host", placeholder: "server.contoso.local" },
        { key: "port", label: "Port (optional)", type: "number", placeholder: "445" },
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
  topology: {
    collect_topology: {
      label: "Collect topology",
      mode: "powershell",
      fields: [
        { key: "dhcp_server", label: "DHCP server (optional)" },
        { key: "dns_server", label: "DNS server (optional)" },
        { key: "print_server", label: "Print server (optional)" },
        { key: "smb_server", label: "SMB server (optional)" },
        { key: "dns_zones", label: "DNS zones (comma-separated)" },
        { key: "record_types", label: "DNS record types (comma-separated)", placeholder: "A,AAAA" },
        { key: "include_print_jobs", label: "Include print jobs", type: "checkbox" },
        { key: "max_items", label: "Max items per source (optional)", type: "number", placeholder: "5000" },
      ],
    },
    ping_targets: {
      label: "Ping targets",
      mode: "powershell",
      fields: [
        { key: "targets", label: "Targets (comma-separated)" },
        { key: "count", label: "Count", type: "number", placeholder: "1" },
        { key: "timeout_seconds", label: "Timeout (seconds)", type: "number", placeholder: "2" },
        { key: "ipv6", label: "Use IPv6", type: "checkbox" },
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
  time: {
    time_chain: {
      label: "Time chain status",
      mode: "powershell",
      fields: [
        { key: "ntp_servers", label: "NTP servers", placeholder: "pool.ntp.org, time.windows.com" },
      ],
    },
    time_drift_history: {
      label: "Time drift history",
      mode: "local",
      fields: [
        { key: "canonical_id", label: "Subject ID (optional)" },
        { key: "limit", label: "Limit", type: "number", placeholder: "50" },
      ],
    },
  },
  certificates: {
    list_machine_certificates: {
      label: "List machine certificates",
      mode: "powershell",
      fields: [
        { key: "stores", label: "Stores", placeholder: "My, Root, CA" },
        { key: "expiring_days", label: "Expiring within days", type: "number", placeholder: "30" },
      ],
    },
    tls_probe: {
      label: "TLS trust probe",
      mode: "powershell",
      fields: [
        { key: "targets", label: "Targets", placeholder: "graph.microsoft.com, login.microsoftonline.com" },
        { key: "port", label: "Port", type: "number", placeholder: "443" },
      ],
    },
  },
  processes: {
    process_inventory: {
      label: "Process inventory",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [
        { key: "include_command_line", label: "Include command line", type: "checkbox" },
        { key: "max_items", label: "Max items", type: "number", placeholder: "200" },
      ],
    },
    service_process_map: {
      label: "Service → process map",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [{ key: "max_items", label: "Max items", type: "number", placeholder: "200" }],
    },
  },
  baselines: {
    list_golden: { label: "List golden baselines", mode: "local", fields: [] },
    set_golden: {
      label: "Set golden baseline",
      mode: "local",
      fields: [
        { key: "kind", label: "Subject kind", placeholder: "admin_host" },
        { key: "snapshot_id", label: "Snapshot ID" },
        { key: "label", label: "Label (optional)" },
      ],
    },
    compare_golden: {
      label: "Compare to golden",
      mode: "local",
      fields: [{ key: "snapshot_id", label: "Snapshot ID" }],
    },
    clear_golden: {
      label: "Clear golden baseline",
      mode: "local",
      fields: [{ key: "kind", label: "Subject kind", placeholder: "admin_host" }],
    },
  },
  eventlogs: {
    eventlog_summary: {
      label: "Event log summary",
      mode: "powershell",
      allowed_targets: ["local", "ssh"],
      fields: [
        { key: "log_names", label: "Log names", placeholder: "System, Application" },
        { key: "levels", label: "Levels", placeholder: "Error, Warning" },
        { key: "time_window_hours", label: "Lookback hours", type: "number", placeholder: "24" },
        { key: "event_ids", label: "Event IDs (comma-separated)" },
        { key: "providers", label: "Providers (comma-separated)" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "500" },
        { key: "sample_size", label: "Sample size", type: "number", placeholder: "10" },
      ],
    },
    eventlog_gpo_failures: { label: "GPO failures summary", mode: "powershell", allowed_targets: ["local", "ssh"], fields: [] },
    eventlog_print_failures: { label: "Print failures summary", mode: "powershell", allowed_targets: ["local", "ssh"], fields: [] },
    eventlog_rdp_failures: { label: "RDP/logon failures summary", mode: "powershell", allowed_targets: ["local", "ssh"], fields: [] },
    eventlog_windows_update_failures: { label: "Windows Update failures", mode: "powershell", allowed_targets: ["local", "ssh"], fields: [] },
    export_evtx: {
      label: "Export EVTX",
      mode: "powershell",
      fields: [
        { key: "log_names", label: "Log names", placeholder: "System, Application" },
        { key: "output_dir", label: "Output folder (optional)" },
      ],
    },
    import_evtx: {
      label: "Import EVTX",
      mode: "powershell",
      fields: [
        { key: "file_path", label: "EVTX file path" },
        { key: "max_events", label: "Max events", type: "number", placeholder: "500" },
        { key: "sample_size", label: "Sample size", type: "number", placeholder: "10" },
      ],
    },
  },
  registry: {
    list_watchlists: { label: "List watchlists", mode: "local", fields: [] },
    save_watchlist: {
      label: "Save watchlist",
      mode: "local",
      fields: [
        { key: "watchlist_id", label: "Watchlist ID" },
        { key: "name", label: "Name" },
        { key: "description", label: "Description" },
        { key: "paths", label: "Paths (comma-separated)" },
      ],
    },
    delete_watchlist: {
      label: "Delete watchlist",
      mode: "local",
      fields: [{ key: "watchlist_id", label: "Watchlist ID" }],
    },
    capture_watchlist: {
      label: "Capture watchlist snapshot",
      mode: "local",
      fields: [
        { key: "watchlist_id", label: "Watchlist ID", placeholder: "network.core" },
        { key: "hostname", label: "Host (optional)", placeholder: "admin_host" },
        { key: "recurse_depth", label: "Recurse depth", type: "number", placeholder: "0" },
        { key: "max_items", label: "Max items", type: "number", placeholder: "200" },
      ],
    },
    diff_watchlist: {
      label: "Diff watchlist snapshots",
      mode: "local",
      fields: [
        { key: "watchlist_id", label: "Watchlist ID (optional)", placeholder: "network.core" },
        { key: "snapshot_a", label: "Snapshot A (optional)" },
        { key: "snapshot_b", label: "Snapshot B (optional)" },
        { key: "canonical_id", label: "Subject ID (optional)", placeholder: "admin_host:admin_host" },
      ],
    },
    export_reg: {
      label: "Export .reg",
      mode: "powershell",
      fields: [
        { key: "path", label: "Registry path" },
        { key: "output_path", label: "Output path (optional)" },
      ],
    },
    save_hive: {
      label: "Save registry hive",
      mode: "powershell",
      fields: [
        { key: "hive", label: "Hive", placeholder: "HKLM\\\\SYSTEM" },
        { key: "output_path", label: "Output path (optional)" },
      ],
    },
  },
};

const UPDATE_CONTEXT_MAP = {
  exchange: {
    list_events: {
      updateAction: "update_event",
      idField: "id",
      idParam: "event_id",
      payloadKey: "updates",
      contextKeys: ["user_id"],
      allowedFields: ["subject", "importance", "showAs", "isAllDay"],
    },
  },
  onedrive: {
    list_drive_items: {
      updateAction: "update_item",
      idField: "id",
      idParam: "item_id",
      payloadKey: "updates",
      contextKeys: ["user_id"],
      allowedFields: ["name", "description"],
    },
  },
  sharepoint: {
    list_list_items: {
      updateAction: "update_list_item_fields",
      idField: "id",
      idParam: "item_id",
      payloadKey: "fields",
      contextKeys: ["site_id", "list_id"],
      allowedFields: null,
      autoValidators: true,
    },
    list_list_columns: {
      updateAction: "update_list_column",
      idField: "id",
      idParam: "column_id",
      payloadKey: "updates",
      contextKeys: ["site_id", "list_id"],
      allowedFields: ["displayName", "description", "hidden", "required"],
    },
    list_site_permissions: {
      updateAction: "update_site_permission",
      idField: "id",
      idParam: "permission_id",
      payloadKey: "updates",
      contextKeys: ["site_id"],
      allowedFields: ["roles"],
    },
  },
  teams: {
    list_channels: {
      updateAction: "update_channel",
      idField: "id",
      idParam: "channel_id",
      payloadKey: "updates",
      contextKeys: ["team_id"],
      allowedFields: ["displayName", "description"],
    },
  },
  entra: {
    list_users: {
      updateAction: "update_user",
      idField: "id",
      idParam: "user_id",
      payloadKey: "updates",
      contextKeys: [],
      allowedFields: [
        "displayName",
        "givenName",
        "surname",
        "jobTitle",
        "department",
        "officeLocation",
        "mobilePhone",
        "companyName",
        "city",
        "state",
        "country",
        "postalCode",
        "streetAddress",
        "usageLocation",
        "userPrincipalName",
      ],
      validators: {
        userPrincipalName: "email",
      },
    },
    list_groups: {
      updateAction: "update_group",
      idField: "id",
      idParam: "group_id",
      payloadKey: "updates",
      contextKeys: [],
      allowedFields: ["displayName", "description", "mailEnabled", "securityEnabled", "visibility"],
    },
    list_applications: {
      updateAction: "update_application",
      idField: "id",
      idParam: "app_id",
      payloadKey: "updates",
      contextKeys: [],
      allowedFields: ["displayName", "signInAudience", "notes"],
    },
  },
};

const READ_ONLY_SHAREPOINT_FIELDS = new Set(
  [
    "id",
    "ID",
    "contenttype",
    "contenttypeid",
    "created",
    "modified",
    "editor",
    "author",
    "createdby",
    "modifiedby",
    "attachments",
    "attachmentfiles",
    "owshiddenversion",
    "uniqueid",
    "guid",
    "fileleafref",
    "filedirref",
    "filetype",
    "filesize",
  ].map((item) => String(item).toLowerCase())
);

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
const ACTION_PACK_AUDIT_KEY = "actionPackAudit";
const ACTION_PACK_VERSION_LIMIT = 5;
const REPORT_HISTORY_KEY = "reportHistory";
const SNAPSHOT_PREFS_KEY = "snapshotPrefs";
const DRAFT_SNAPSHOTS_KEY = "draftSnapshots";
const ACTIVE_DRAFT_KEY = "draftSnapshotActive";

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
  endpoint: ["GroupPolicy"],
  domaincontroller: ["ActiveDirectory"],
  printers: ["PrintManagement", "GroupPolicy"],
  network: ["NetAdapter", "NetTCPIP", "NetSecurity", "DnsServer", "SmbShare"],
  fileserver: [],
  topology: [],
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
    id: "flagship-user-lifecycle",
    name: "User lifecycle: onboard/offboard (M365)",
    description:
      "End-to-end onboarding with verification, dry-run controls, and rollback guidance across cloud + on-prem.",
    steps: [
      {
        type: "note",
        phase: "Prep",
        label: "Dry-run + diff preview",
        note:
          "Use Dry-run to simulate the workflow. Safe (read-only) steps still execute. Use diff preview on any update steps before applying.",
      },
      {
        type: "note",
        phase: "Prep",
        label: "Required inputs",
        note:
          "Collect UPN, display name, temp password, group IDs, SKU IDs, Teams IDs, OU DN, and GPO OU DN before running.",
      },
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true, include_signins: true, include_devices: true },
        label: "Baseline audit snapshot (optional)",
        optional: true,
        safe: true,
        phase: "Verify",
      },
      {
        service: "entra",
        action: "create_user",
        label: "Create Entra user",
        phase: "Provision",
      },
      {
        service: "entra",
        action: "add_group_member",
        label: "Assign group membership",
        phase: "Provision",
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Assign licenses (PowerShell)",
        phase: "Provision",
      },
      {
        service: "onedrive",
        action: "get_user_drive_id",
        label: "Provision OneDrive",
        optional: true,
        safe: true,
        phase: "Provision",
      },
      {
        service: "exchange",
        action: "list_mail_folders",
        label: "Verify mailbox folders",
        optional: true,
        safe: true,
        phase: "Verify",
      },
      {
        service: "teams",
        action: "list_joined_teams",
        label: "Verify Teams membership (optional)",
        optional: true,
        safe: true,
        phase: "Verify",
      },
      {
        service: "localad",
        action: "create_user",
        label: "Create on-prem AD user (optional)",
        optional: true,
        defaultInclude: false,
        phase: "On-prem",
      },
      {
        service: "localad",
        action: "move_user_to_ou",
        label: "Place AD user in OU (optional)",
        optional: true,
        defaultInclude: false,
        phase: "On-prem",
      },
      {
        service: "reports",
        action: "gpo_link_audit",
        label: "Verify GPO links for OU (optional)",
        optional: true,
        defaultInclude: false,
        safe: true,
        phase: "On-prem",
      },
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true, include_signins: true, include_devices: true },
        label: "Post-check audit snapshot (optional)",
        optional: true,
        safe: true,
        phase: "Verify",
      },
      {
        type: "note",
        phase: "Evidence",
        label: "Evidence bundle export",
        note:
          "Use the Export incident bundle button on key outputs to capture evidence for tickets and audits.",
      },
      {
        type: "note",
        phase: "Rollback",
        label: "Rollback plan",
        note:
          "If validation fails, run the rollback steps below or revert changes manually in Entra/AD.",
      },
      {
        service: "entra",
        action: "remove_group_member",
        label: "Rollback: remove group membership",
        optional: true,
        defaultInclude: false,
        rollback: true,
        phase: "Rollback",
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Rollback: remove licenses (PowerShell)",
        optional: true,
        defaultInclude: false,
        rollback: true,
        phase: "Rollback",
      },
      {
        service: "localad",
        action: "disable_account",
        label: "Rollback: disable on-prem account",
        optional: true,
        defaultInclude: false,
        rollback: true,
        phase: "Rollback",
      },
    ],
  },
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
    name: "Offboard user (cloud + on-prem)",
    description: "Capture audit, disable on-prem + cloud access, remove licenses, and document changes.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
        label: "Capture user audit snapshot",
      },
      {
        service: "localad",
        action: "disable_account",
        label: "Disable on-prem account",
      },
      {
        service: "localad",
        action: "move_user_to_ou",
        label: "Move to inactive OU (optional)",
        optional: true,
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Remove licenses (PowerShell)",
      },
      {
        service: "entra",
        action: "remove_group_member",
        label: "Remove from groups (optional)",
        optional: true,
      },
    ],
  },
  {
    id: "connectivity-triage",
    name: "Connectivity triage",
    description:
      "DNS resolve, ping, port probe, traceroute, route table, and firewall profiles in one sweep.",
    bundleOnComplete: true,
    defaults: {
      stepParams: {
        "network.resolve_dns_name": { record_type: "A" },
        "network.ping_host": { count: 4, timeout_seconds: 2 },
        "network.test_port": { port: 443, information_level: "Detailed" },
        "network.trace_route": { max_hops: 20, timeout_ms: 3000 },
        "network.firewall_quick_check": { local_port: 443 },
      },
    },
    steps: [
      {
        service: "network",
        action: "resolve_dns_name",
        label: "DNS resolve",
        safe: true,
        phase: "Connectivity",
      },
      {
        service: "network",
        action: "ping_host",
        label: "Ping host",
        safe: true,
        phase: "Connectivity",
      },
      {
        service: "network",
        action: "test_port",
        label: "Test TCP port",
        safe: true,
        phase: "Connectivity",
      },
      {
        service: "network",
        action: "trace_route",
        label: "Trace route",
        safe: true,
        phase: "Path",
      },
      {
        service: "network",
        action: "list_routes",
        label: "Route table snapshot",
        safe: true,
        phase: "Host",
      },
      {
        service: "network",
        action: "firewall_quick_check",
        label: "Firewall profiles & key rules",
        safe: true,
        phase: "Host",
      },
      {
        type: "note",
        phase: "Evidence",
        label: "Incident bundle",
        note: "This pack exports a combined incident bundle when it completes.",
      },
    ],
  },
  {
    id: "dc-health-triage",
    name: "DC health triage",
    description:
      "List DCs, check replication summary, show replication partners, run dcdiag, and validate time sync.",
    bundleOnComplete: true,
    defaults: {
      stepParams: {
        "domaincontroller.time_sync_health": {},
        "domaincontroller.dc_diagnostics": { verbose: false },
      },
    },
    steps: [
      {
        service: "domaincontroller",
        action: "list_domain_controllers",
        label: "List domain controllers",
        safe: true,
        phase: "Discovery",
      },
      {
        service: "domaincontroller",
        action: "replication_health_summary",
        label: "Replication summary",
        safe: true,
        phase: "Replication",
      },
      {
        service: "domaincontroller",
        action: "show_replication_partners",
        label: "Show replication partners (auto-pick DC)",
        safe: true,
        phase: "Replication",
      },
      {
        service: "domaincontroller",
        action: "dc_diagnostics",
        label: "Run dcdiag",
        safe: true,
        phase: "Health",
      },
      {
        service: "domaincontroller",
        action: "time_sync_health",
        label: "Time sync health",
        safe: true,
        phase: "Time",
      },
      {
        type: "note",
        phase: "Evidence",
        label: "Incident bundle",
        note: "This pack exports a combined incident bundle when it completes.",
      },
    ],
  },
  {
    id: "printer-incident-triage",
    name: "Printer incident triage",
    description: "Assess printer health, validate GPO mappings, and cross-reference conflicts.",
    steps: [
      {
        service: "printers",
        action: "list_printers",
        label: "List printers and status",
      },
      {
        service: "printers",
        action: "list_gpo_printer_mappings",
        label: "List GPO printer mappings",
      },
      {
        service: "printers",
        action: "cross_reference_printers_gpo",
        label: "Cross-reference printers vs GPOs",
      },
      {
        service: "topology",
        action: "ping_targets",
        label: "Ping printer targets (optional)",
        optional: true,
      },
    ],
  },
  {
    id: "onedrive-access-triage",
    name: "User can’t access OneDrive",
    description: "Verify provisioning, resolve drive ID, and confirm site visibility.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_signins: true, include_licenses: true },
        label: "Check sign-ins and licenses",
      },
      {
        service: "onedrive",
        action: "get_user_drive_id",
        label: "Resolve OneDrive drive ID",
      },
      {
        service: "onedrive",
        action: "list_drive_items",
        label: "List root items (optional)",
        optional: true,
      },
      {
        service: "onedrive",
        action: "list_personal_sites",
        label: "Check personal site provisioning (PowerShell)",
        optional: true,
      },
    ],
  },
  {
    id: "license-reconciliation",
    name: "License reconciliation",
    description: "Audit assigned licenses and reconcile with intended SKU set.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true },
        label: "Audit current license state",
      },
      {
        service: "entra",
        action: "set_user_license",
        label: "Apply license changes (PowerShell)",
      },
      {
        service: "reports",
        action: "user_audit",
        params: { include_licenses: true },
        label: "Validate license state (optional)",
        optional: true,
      },
    ],
  },
  {
    id: "conditional-access-triage",
    name: "Conditional access troubleshooting",
    description: "Inspect sign-in activity, device posture, and group context to pinpoint CA blocks.",
    steps: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_signins: true, include_devices: true, include_licenses: true },
        label: "Review sign-ins and device posture",
      },
      {
        service: "entra",
        action: "list_group_members",
        label: "Check CA-related group membership (optional)",
        optional: true,
      },
      {
        service: "entra",
        action: "list_users",
        label: "Verify user properties (optional)",
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
  {
    id: "identity-health",
    label: "Identity health snapshots",
    actions: [
      {
        service: "reports",
        action: "user_audit",
        params: { include_groups: true, include_licenses: true, include_signins: true },
      },
      { service: "reports", action: "sign_in_summary", params: { top: 25, lookback_hours: 24 } },
      { service: "reports", action: "conditional_access_summary" },
      { service: "reports", action: "device_compliance", params: { top: 50 } },
    ],
  },
];

let currentPresetId = null;
let currentPresetSteps = [];
let sshSocket = null;
let sshConnected = false;
let topologyData = null;
let topologyPing = null;
let reportHistoryItems = [];

const ISSUE_STORAGE_KEY = "topologyIssues";
const TOPOLOGY_HISTORY_KEY = "topologyHistory";
const TOPOLOGY_HISTORY_LIMIT_KEY = "topologyHistoryLimit";
const TOPOLOGY_HISTORY_LIMITS = [5, 10, 20, 50];
const DEFAULT_TOPOLOGY_HISTORY_LIMIT = 20;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2000);
}

let activeModal = null;

function ensureAppModal() {
  let modal = document.getElementById("app-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "app-modal";
  modal.classList.add("modal");
  modal.setAttribute("role", "dialog");
  modal.setAttribute("aria-modal", "true");
  modal.setAttribute("aria-hidden", "true");
  modal.setAttribute("aria-labelledby", "app-modal-title");
  modal.setAttribute("aria-describedby", "app-modal-body");
  modal.innerHTML = `
    <div class="modal-card" role="document">
      <div class="modal-header">
        <div>
          <div class="modal-title" id="app-modal-title"></div>
          <div class="modal-subtitle" id="app-modal-subtitle"></div>
        </div>
        <div class="modal-actions">
          <button class="ghost small modal-close" id="app-modal-close" aria-label="Close">×</button>
        </div>
      </div>
      <div class="modal-body" id="app-modal-body"></div>
      <div class="modal-footer" id="app-modal-footer"></div>
    </div>
  `;
  document.body.appendChild(modal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal && activeModal?.allowOutsideClose) {
      activeModal.close("cancel");
    }
  });
  modal.querySelector("#app-modal-close").addEventListener("click", () => {
    if (activeModal) activeModal.close("cancel");
  });
  return modal;
}

function getFocusableElements(root) {
  if (!root) return [];
  return Array.from(
    root.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter((el) => !el.disabled && !el.getAttribute("aria-hidden"));
}

function openModal(config = {}) {
  const modal = ensureAppModal();
  const card = modal.querySelector(".modal-card");
  const titleEl = modal.querySelector("#app-modal-title");
  const subtitleEl = modal.querySelector("#app-modal-subtitle");
  const bodyEl = modal.querySelector("#app-modal-body");
  const footerEl = modal.querySelector("#app-modal-footer");

  titleEl.textContent = config.title || "";
  subtitleEl.textContent = config.subtitle || "";
  subtitleEl.style.display = config.subtitle ? "block" : "none";

  bodyEl.innerHTML = "";
  if (config.body) {
    if (typeof config.body === "string") {
      const message = document.createElement("div");
      message.classList.add("modal-message");
      message.textContent = config.body;
      bodyEl.appendChild(message);
    } else {
      bodyEl.appendChild(config.body);
    }
  }

  footerEl.innerHTML = "";
  card.classList.toggle("modal-small", config.size === "small");
  card.classList.toggle("modal-large", config.size === "large");

  let primaryButton = null;
  const actions = config.actions || [];
  actions.forEach((action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add(action.variant === "primary" ? "primary" : "ghost");
    if (action.variant === "primary" && action.danger) {
      button.classList.add("danger");
    }
    if (action.size === "small") button.classList.add("small");
    button.textContent = action.label;
    if (action.primary) primaryButton = button;
    button.addEventListener("click", () => {
      if (action.onClick && action.onClick() === false) return;
      const payload = action.collect ? action.collect() : null;
      activeModal?.close(action.value || action.label, payload);
    });
    footerEl.appendChild(button);
  });

  const lastFocus = document.activeElement;
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");

  const handleKeydown = (event) => {
    if (event.key === "Escape") {
      if (activeModal) activeModal.close("cancel");
      return;
    }
    if (event.key === "Enter" && primaryButton) {
      const target = event.target;
      if (target && target.tagName === "TEXTAREA") return;
      if (!primaryButton.disabled) {
        event.preventDefault();
        primaryButton.click();
      }
    }
    if (event.key === "Tab") {
      const focusable = getFocusableElements(card);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  };

  modal.addEventListener("keydown", handleKeydown);

  const close = (action, payload) => {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    modal.removeEventListener("keydown", handleKeydown);
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
    if (activeModal?.resolve) {
      activeModal.resolve({ action, payload });
    }
    activeModal = null;
  };

  activeModal = {
    resolve: null,
    close,
    allowOutsideClose: config.allowOutsideClose !== false,
  };

  const promise = new Promise((resolve) => {
    activeModal.resolve = resolve;
  });

  const focusables = getFocusableElements(card);
  const focusTarget = config.initialFocus || focusables[0] || primaryButton;
  if (focusTarget && typeof focusTarget.focus === "function") {
    focusTarget.focus();
  }

  if (config.onReady) {
    config.onReady({ modal, card, primaryButton, close });
  }

  return promise;
}

async function confirmModal({ title, subtitle, message, confirmLabel, cancelLabel, danger } = {}) {
  const result = await openModal({
    title: title || "Confirm",
    subtitle: subtitle || "",
    body: message || "",
    actions: [
      { label: cancelLabel || "Cancel", variant: "ghost", value: "cancel" },
      {
        label: confirmLabel || "Confirm",
        variant: "primary",
        value: "confirm",
        primary: true,
        danger: Boolean(danger),
      },
    ],
  });
  return result?.action === "confirm";
}

async function openFormModal({ title, subtitle, fields = [], confirmLabel, cancelLabel, size } = {}) {
  const form = document.createElement("div");
  form.classList.add("modal-form");
  const fieldMap = new Map();

  fields.forEach((field) => {
    if (field.type === "checkbox") {
      const wrapper = document.createElement("label");
      wrapper.classList.add("modal-field", "checkbox");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = Boolean(field.value);
      const span = document.createElement("span");
      span.textContent = field.label;
      wrapper.appendChild(checkbox);
      wrapper.appendChild(span);
      form.appendChild(wrapper);
      fieldMap.set(field.key, { field, input: checkbox });
      return;
    }

    const label = document.createElement("label");
    label.classList.add("modal-field");
    label.textContent = field.label;
    let input;
    if (field.type === "select") {
      input = document.createElement("select");
      (field.options || []).forEach((option) => {
        const opt = document.createElement("option");
        opt.value = option.value;
        opt.textContent = option.label;
        input.appendChild(opt);
      });
      if (field.value !== undefined && field.value !== null) {
        input.value = field.value;
      }
    } else if (field.type === "textarea") {
      input = document.createElement("textarea");
      input.rows = field.rows || 4;
      input.value = field.value || "";
    } else {
      input = document.createElement("input");
      input.type = field.type || "text";
      input.value = field.value || "";
    }
    if (field.placeholder) input.placeholder = field.placeholder;
    label.appendChild(input);
    if (field.hint) {
      const hint = document.createElement("div");
      hint.classList.add("modal-hint");
      hint.textContent = field.hint;
      label.appendChild(hint);
    }
    form.appendChild(label);
    fieldMap.set(field.key, { field, input });
  });

  let primaryButton = null;
  const updateValidity = () => {
    if (!primaryButton) return;
    const invalid = Array.from(fieldMap.values()).some(({ field, input }) => {
      if (!field.required) return false;
      if (field.type === "checkbox") return !input.checked;
      return !String(input.value || "").trim();
    });
    primaryButton.disabled = invalid;
  };

  const result = await openModal({
    title: title || "",
    subtitle: subtitle || "",
    body: form,
    size,
    actions: [
      { label: cancelLabel || "Cancel", variant: "ghost", value: "cancel" },
      {
        label: confirmLabel || "Save",
        variant: "primary",
        value: "confirm",
        primary: true,
      },
    ],
    onReady: ({ primaryButton: btn }) => {
      primaryButton = btn;
      updateValidity();
      fieldMap.forEach(({ input }) => {
        input.addEventListener("input", updateValidity);
        input.addEventListener("change", updateValidity);
      });
    },
  });

  if (result?.action !== "confirm") return null;
  const values = {};
  fieldMap.forEach(({ field, input }, key) => {
    values[key] = field.type === "checkbox" ? Boolean(input.checked) : input.value;
  });
  return values;
}

async function promptModal({ title, subtitle, label, defaultValue, placeholder, confirmLabel, cancelLabel, required, hint }) {
  const values = await openFormModal({
    title,
    subtitle,
    confirmLabel,
    cancelLabel,
    fields: [
      {
        key: "value",
        label: label || "Value",
        value: defaultValue || "",
        placeholder,
        required: Boolean(required),
        hint,
      },
    ],
  });
  if (!values) return null;
  return values.value;
}

async function selectModal({ title, subtitle, label, options = [], defaultValue, confirmLabel, cancelLabel }) {
  const values = await openFormModal({
    title,
    subtitle,
    confirmLabel,
    cancelLabel,
    fields: [
      {
        key: "selection",
        label: label || "Select",
        type: "select",
        value: defaultValue,
        options: options.map((option) =>
          typeof option === "string" ? { value: option, label: option } : option
        ),
        required: true,
      },
    ],
  });
  if (!values) return null;
  return values.selection;
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
  lastOutputStatus[service] = {
    ...(lastOutputStatus[service] || {}),
    ...(state !== undefined ? { state } : {}),
    ...(text !== undefined ? { text } : {}),
    ...(meta !== undefined ? { meta } : {}),
    ...(running !== undefined ? { running } : {}),
    updated_at: new Date().toISOString(),
  };
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

function setOutputView(service, view) {
  const panel = document.querySelector(`.output[data-output="${service}"]`);
  if (!panel) return;
  const card = panel.closest(".output-card");
  if (!card) return;
  const tab = card.querySelector(`.output-tabs .tab[data-view="${view}"]`);
  if (tab) tab.click();
}

function hideGraphStatusBanner() {
  if (!graphStatusBanner) return;
  graphStatusBanner.classList.add("hidden");
  if (graphStatusActions) {
    graphStatusActions.innerHTML = "";
  }
}

function showGraphStatusBanner(message, meta = "", actions = null) {
  if (!graphStatusBanner || !graphStatusMessage) return;
  graphStatusMessage.textContent = message || "Graph service reports degraded status.";
  if (graphStatusMeta) {
    graphStatusMeta.textContent = meta || "";
  }
  if (graphStatusActions) {
    graphStatusActions.innerHTML = "";
    if (Array.isArray(actions)) {
      actions.forEach((item) => {
        if (!item || typeof item !== "object" || !item.label || typeof item.onClick !== "function") return;
        const button = document.createElement("button");
        button.type = "button";
        button.classList.add("ghost", "small");
        if (item.danger) button.classList.add("danger");
        button.textContent = item.label;
        if (item.title) button.title = item.title;
        button.addEventListener("click", item.onClick);
        graphStatusActions.appendChild(button);
      });
    }
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

function normalizeList(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function parseSnapshotTime(value) {
  if (!value) return null;
  const ts = new Date(value);
  if (Number.isNaN(ts.getTime())) return null;
  return ts;
}

function formatSnapshotLabel(snapshot) {
  const ts = parseSnapshotTime(snapshot?.timestamp);
  const label = ts ? ts.toLocaleString() : String(snapshot?.timestamp || "Snapshot");
  const leaseCount = normalizeList(snapshot?.dhcp_leases).length;
  const dnsCount = normalizeList(snapshot?.dns_records).length;
  return `${label} · DHCP ${leaseCount} · DNS ${dnsCount}`;
}

function getSnapshotId(snapshot, index) {
  return snapshot?.timestamp || snapshot?.generated_at || `snapshot-${index}`;
}

function findSnapshotById(history, id) {
  if (!id) return null;
  const match = history.find((snap) => getSnapshotId(snap) === id);
  return match || null;
}

function findSnapshotBefore(history, hours) {
  const target = Date.now() - hours * 60 * 60 * 1000;
  let candidate = null;
  let candidateTime = 0;
  history.forEach((snap) => {
    const ts = parseSnapshotTime(snap?.timestamp || snap?.generated_at);
    if (!ts) return;
    const t = ts.getTime();
    if (t <= target && t >= candidateTime) {
      candidateTime = t;
      candidate = snap;
    }
  });
  if (!candidate && history.length) {
    candidate = history[history.length - 1];
  }
  return candidate;
}

function renderTopologyDiffSelectors(history) {
  if (!topologyDiffSelectA || !topologyDiffSelectB) return;
  const options = history.map((snap, index) => ({
    id: getSnapshotId(snap, index),
    label: formatSnapshotLabel(snap),
  }));
  const currentA = topologyDiffSelectA.value;
  const currentB = topologyDiffSelectB.value;
  topologyDiffSelectA.innerHTML = "";
  topologyDiffSelectB.innerHTML = "";
  options.forEach((opt) => {
    const optionA = document.createElement("option");
    optionA.value = opt.id;
    optionA.textContent = opt.label;
    topologyDiffSelectA.appendChild(optionA);
    const optionB = document.createElement("option");
    optionB.value = opt.id;
    optionB.textContent = opt.label;
    topologyDiffSelectB.appendChild(optionB);
  });
  if (options.length >= 2) {
    topologyDiffSelectB.value = currentB || options[0].id;
    topologyDiffSelectA.value = currentA || options[1].id;
  } else if (options.length === 1) {
    topologyDiffSelectA.value = options[0].id;
    topologyDiffSelectB.value = options[0].id;
  }
}

function renderTopologyTimeline(history) {
  if (!topologyTimelineList) return;
  topologyTimelineList.innerHTML = "";
  if (!history.length) {
    const empty = document.createElement("li");
    empty.textContent = "No topology snapshots yet.";
    topologyTimelineList.appendChild(empty);
    return;
  }
  history.forEach((snap, index) => {
    const prev = history[index + 1];
    const leaseCount = normalizeList(snap?.dhcp_leases).length;
    const dnsCount = normalizeList(snap?.dns_records).length;
    const prevLeaseCount = prev ? normalizeList(prev?.dhcp_leases).length : null;
    const prevDnsCount = prev ? normalizeList(prev?.dns_records).length : null;
    const leaseDelta =
      prevLeaseCount === null ? "" : ` (${leaseCount - prevLeaseCount >= 0 ? "+" : ""}${leaseCount - prevLeaseCount})`;
    const dnsDelta =
      prevDnsCount === null ? "" : ` (${dnsCount - prevDnsCount >= 0 ? "+" : ""}${dnsCount - prevDnsCount})`;
    const li = document.createElement("li");
    const title = document.createElement("div");
    title.textContent = parseSnapshotTime(snap?.timestamp)?.toLocaleString() || snap?.timestamp || "Snapshot";
    const meta = document.createElement("div");
    meta.classList.add("activity-meta");
    meta.textContent = `DHCP ${leaseCount}${leaseDelta} · DNS ${dnsCount}${dnsDelta}`;
    li.appendChild(title);
    li.appendChild(meta);
    topologyTimelineList.appendChild(li);
  });
}

function refreshTopologyChangeViews() {
  const history = loadTopologyHistory();
  renderTopologyDiffSelectors(history);
  renderTopologyTimeline(history);
}

function loadIssues() {
  try {
    const raw = localStorage.getItem(ISSUE_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) {
      return parsed.filter((item) => item?.user || item?.device || item?.symptom);
    }
  } catch (err) {
    return [];
  }
  return [];
}

function saveIssues(items) {
  localStorage.setItem(ISSUE_STORAGE_KEY, JSON.stringify(items || []));
}

function getTopologyHistoryLimit() {
  const raw = localStorage.getItem(TOPOLOGY_HISTORY_LIMIT_KEY);
  const parsed = Number.parseInt(raw || "", 10);
  if (TOPOLOGY_HISTORY_LIMITS.includes(parsed)) {
    return parsed;
  }
  return DEFAULT_TOPOLOGY_HISTORY_LIMIT;
}

function setTopologyHistoryLimit(value) {
  if (!TOPOLOGY_HISTORY_LIMITS.includes(value)) return;
  localStorage.setItem(TOPOLOGY_HISTORY_LIMIT_KEY, String(value));
}

function trimHistoryToLimit(history, limit) {
  if (!Array.isArray(history)) return [];
  if (!limit) return history;
  return history.slice(0, limit);
}

function loadTopologyHistory() {
  try {
    const raw = localStorage.getItem(TOPOLOGY_HISTORY_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    if (Array.isArray(parsed)) {
      const trimmed = parsed.filter((item) => item?.timestamp);
      return trimHistoryToLimit(trimmed, getTopologyHistoryLimit());
    }
  } catch (err) {
    return [];
  }
  return [];
}

function saveTopologyHistory(items) {
  localStorage.setItem(TOPOLOGY_HISTORY_KEY, JSON.stringify(items || []));
}

function storeTopologySnapshot(data) {
  if (!data) return;
  const snapshot = {
    timestamp: new Date().toISOString(),
    dhcp_server: data?.dhcp_server,
    dns_server: data?.dns_server,
    print_server: data?.print_server,
    smb_server: data?.smb_server,
    dhcp_leases: normalizeList(data?.dhcp_leases)
      .map((lease) => ({
        HostName: lease?.HostName || lease?.hostName,
        IPAddress: lease?.IPAddress || lease?.IpAddress || lease?.ip,
        ClientId: lease?.ClientId,
        LeaseExpiryTime: lease?.LeaseExpiryTime,
        ScopeId: lease?.ScopeId,
      }))
      .filter((lease) => lease.HostName || lease.IPAddress),
    dns_records: normalizeList(data?.dns_records)
      .map((record) => ({
        Zone: record?.Zone,
        HostName: record?.HostName,
        RecordType: record?.RecordType,
        RecordData: record?.RecordData,
      }))
      .filter((record) => record.HostName || record.RecordData),
  };
  const history = loadTopologyHistory();
  history.unshift(snapshot);
  const limit = getTopologyHistoryLimit();
  const trimmed = trimHistoryToLimit(history, limit);
  saveTopologyHistory(trimmed);
  refreshTopologyChangeViews();
  return snapshot;
}

async function fetchTopologyHistory() {
  const limit = getTopologyHistoryLimit();
  try {
    const res = await fetch(`/api/topology/history?limit=${limit}`);
    const data = await res.json();
    if (data && data.normalized) {
      lastNormalized[service] = data.normalized;
    }
    if (data?.ok && Array.isArray(data.data)) {
      saveTopologyHistory(trimHistoryToLimit(data.data, limit));
      refreshTopologyChangeViews();
      return data.data;
    }
  } catch (err) {
    return null;
  }
  return null;
}

async function syncTopologyHistory(snapshot) {
  if (!snapshot) return null;
  const limit = getTopologyHistoryLimit();
  try {
    const res = await fetch("/api/topology/history", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ snapshot, limit }),
    });
    const data = await res.json();
    if (data?.ok && Array.isArray(data.data)) {
      saveTopologyHistory(trimHistoryToLimit(data.data, limit));
      return data.data;
    }
  } catch (err) {
    return null;
  }
  return null;
}

function buildTopologyHistoryIndex(history) {
  const hostMap = new Map();
  const ipMap = new Map();
  if (!Array.isArray(history)) {
    return { hostMap, ipMap, count: 0, lastSnapshot: null };
  }

  const maybeUpdateHost = (key, ip, timestamp, source) => {
    if (!key || !ip || !timestamp) return;
    const normalized = String(key).toLowerCase();
    const existing = hostMap.get(normalized);
    const currentTs = existing?.last_seen ? new Date(existing.last_seen).getTime() : 0;
    const nextTs = new Date(timestamp).getTime();
    if (!existing || nextTs >= currentTs) {
      hostMap.set(normalized, {
        host: key,
        ip,
        last_seen: timestamp,
        source,
      });
    }
  };

  history.forEach((snapshot) => {
    const ts = snapshot?.timestamp;
    normalizeList(snapshot?.dhcp_leases).forEach((lease) => {
      const host = lease?.HostName;
      const ip = lease?.IPAddress || lease?.IpAddress || lease?.ip;
      maybeUpdateHost(host, ip, ts, "dhcp");
      if (ip) {
        const ipKey = String(ip).toLowerCase();
        const record = ipMap.get(ipKey) || { ip, hosts: new Set(), last_seen: ts };
        if (host) record.hosts.add(host);
        record.last_seen = ts || record.last_seen;
        ipMap.set(ipKey, record);
      }
    });

    normalizeList(snapshot?.dns_records).forEach((record) => {
      const host = record?.HostName;
      const zone = record?.Zone;
      const fqdn = host && zone ? `${host}.${zone}`.replace(/\.\./g, ".") : host;
      extractIpStrings(record?.RecordData).forEach((ip) => {
        maybeUpdateHost(fqdn, ip, ts, "dns");
        if (host) {
          maybeUpdateHost(host, ip, ts, "dns");
        }
        const ipKey = String(ip).toLowerCase();
        const entry = ipMap.get(ipKey) || { ip, hosts: new Set(), last_seen: ts };
        if (fqdn) entry.hosts.add(fqdn);
        if (host) entry.hosts.add(host);
        entry.last_seen = ts || entry.last_seen;
        ipMap.set(ipKey, entry);
      });
    });
  });

  return {
    hostMap,
    ipMap,
    count: history.length,
    lastSnapshot: history[0]?.timestamp || null,
  };
}

function findHistoryMatches(device, historyIndex, limit = 3) {
  const matches = [];
  if (!device || !historyIndex?.hostMap) return matches;
  const key = String(device).toLowerCase();
  const ipMatches = extractIpStrings(key);
  if (ipMatches.length && historyIndex.ipMap) {
    ipMatches.forEach((ip) => {
      const entry = historyIndex.ipMap.get(String(ip).toLowerCase());
      if (entry) {
        Array.from(entry.hosts || []).forEach((host) => {
          if (matches.length < limit) {
            matches.push({
              host,
              ip,
              last_seen: entry.last_seen,
              source: "dns/dhcp",
            });
          }
        });
      }
    });
  }
  const direct = historyIndex.hostMap.get(key);
  if (direct) {
    matches.push(direct);
  }
  if (matches.length < limit) {
    historyIndex.hostMap.forEach((entry, hostKey) => {
      if (matches.length >= limit) return;
      if (hostKey === key) return;
      if (hostKey.startsWith(`${key}.`) || hostKey.includes(key)) {
        matches.push(entry);
      }
    });
  }
  return matches.slice(0, limit);
}

function renderIssues() {
  if (!issueList) return;
  const issues = loadIssues();
  issueList.innerHTML = "";
  if (!issues.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No issues recorded.";
    issueList.appendChild(empty);
    return;
  }
  issues.forEach((issue, idx) => {
    const li = document.createElement("li");
    li.classList.add("issue-item");
    const detail = document.createElement("div");
    const title = document.createElement("div");
    title.textContent = `${issue.user || "Unknown user"} → ${issue.device || "Unknown device"}`;
    const meta = document.createElement("div");
    meta.classList.add("issue-meta");
    const templateLabel = symptomTemplates.find((entry) => entry.symptom_id === issue.symptom_id)?.display_name;
    meta.textContent = templateLabel ? `${templateLabel} · ${issue.symptom || ""}`.trim() : issue.symptom || "No symptom provided";
    detail.appendChild(title);
    detail.appendChild(meta);
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      const next = loadIssues().filter((_, i) => i !== idx);
      saveIssues(next);
      renderIssues();
    });
    li.appendChild(detail);
    li.appendChild(remove);
    issueList.appendChild(li);
  });
}

async function renderIncidents() {
  if (!incidentList) return;
  const incidents = await fetchIncidents();
  incidentList.innerHTML = "";
  if (!incidents.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No incidents recorded.";
    incidentList.appendChild(empty);
    return;
  }
  incidents.forEach((incident) => {
    const row = document.createElement("div");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = incident.title || incident.symptom_id || incident.incident_id;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    const when = incident.created_at ? new Date(incident.created_at).toLocaleString() : "Unknown time";
    meta.textContent = `Status: ${incident.status || "open"} · ${when}`;
    row.appendChild(title);
    row.appendChild(meta);
    incidentList.appendChild(row);
  });
  renderIncidentReportSelect();
}

async function addIssue() {
  const user = issueUserInput?.value.trim();
  const device = issueDeviceInput?.value.trim();
  const symptom = issueSymptomInput?.value.trim();
  if (!user && !device && !symptom) {
    showToast("Enter at least one field");
    return;
  }
  const symptomId = issueSymptomTemplate?.value || null;
  const incident = await createIncident({
    symptom_id: symptomId,
    title: symptom || "Incident",
    description: `${user || "Unknown user"} → ${device || "Unknown device"}`,
  });
  if (incident && incident.incident_id) {
    renderIncidents();
    activeIncidentId = incident.incident_id;
    renderIncidentReportSelect();
    loadIncidentReportFor(incident.incident_id);
  }
  const issues = loadIssues();
  const entry = {
    user,
    device,
    symptom,
    symptom_id: symptomId,
    timestamp: new Date().toISOString(),
    incident_id: incident?.incident_id || null,
  };
  issues.push(entry);
  saveIssues(issues);
  renderIssues();
  captureIncidentSnapshots(entry);
  if (issueUserInput) issueUserInput.value = "";
  if (issueDeviceInput) issueDeviceInput.value = "";
  if (issueSymptomInput) issueSymptomInput.value = "";
  if (issueSymptomTemplate) issueSymptomTemplate.value = "";
}

function extractIpStrings(text) {
  if (!text) return [];
  const matches = String(text).match(/\b(\d{1,3}\.){3}\d{1,3}\b/g);
  return matches || [];
}

function isIpAddress(value) {
  return /^\d{1,3}(\.\d{1,3}){3}$/.test(String(value || ""));
}

function extractTopologyTargets(data) {
  const targets = new Set();
  const addTarget = (value) => {
    if (!value) return;
    const raw = String(value).trim();
    if (!raw) return;
    targets.add(raw);
  };

  normalizeList(data?.dhcp_leases).forEach((lease) => {
    addTarget(lease?.HostName);
    addTarget(lease?.IPAddress || lease?.IpAddress);
  });

  normalizeList(data?.dns_records).forEach((record) => {
    const host = record?.HostName;
    const zone = record?.Zone;
    if (host && zone) {
      addTarget(`${host}.${zone}`.replace(/\.\./g, "."));
    } else if (host) {
      addTarget(host);
    }
    extractIpStrings(record?.RecordData).forEach(addTarget);
  });

  normalizeList(data?.printers).forEach((printer) => {
    extractIpStrings(printer?.PortName).forEach(addTarget);
    addTarget(printer?.ShareName);
    addTarget(printer?.Name);
  });

  normalizeList(data?.smb_sessions).forEach((session) => {
    addTarget(session?.ClientComputerName);
  });

  normalizeList(loadIssues()).forEach((issue) => {
    addTarget(issue?.device);
  });

  const historyIndex = buildTopologyHistoryIndex(loadTopologyHistory());
  normalizeList(loadIssues()).forEach((issue) => {
    const matches = findHistoryMatches(issue?.device, historyIndex, 2);
    matches.forEach((match) => {
      addTarget(match.host);
      addTarget(match.ip);
    });
  });

  return Array.from(targets).filter(Boolean);
}

function buildPingMap(pings) {
  const map = new Map();
  normalizeList(pings).forEach((entry) => {
    if (!entry) return;
    const key = entry.Target || entry.target;
    if (key) {
      map.set(String(key).toLowerCase(), entry);
    }
    if (entry.Address) {
      map.set(String(entry.Address).toLowerCase(), entry);
    }
  });
  return map;
}

function buildDeviceIpMap(data) {
  const map = new Map();
  normalizeList(data?.dhcp_leases).forEach((lease) => {
    const host = lease?.HostName;
    const ip = lease?.IPAddress || lease?.IpAddress;
    if (host && ip) {
      map.set(String(host).toLowerCase(), String(ip));
    }
  });
  normalizeList(data?.dns_records).forEach((record) => {
    const host = record?.HostName;
    const zone = record?.Zone;
    const fqdn = host && zone ? `${host}.${zone}`.replace(/\.\./g, ".") : null;
    if (host) {
      const ips = extractIpStrings(record?.RecordData);
      if (ips.length) {
        map.set(String(host).toLowerCase(), ips[0]);
        if (fqdn) {
          map.set(String(fqdn).toLowerCase(), ips[0]);
        }
      }
    }
  });
  return map;
}

function diffDhcpLeases(before, after) {
  const normalizeLease = (lease) => ({
    HostName: lease?.HostName || lease?.hostName || "",
    IPAddress: lease?.IPAddress || lease?.IpAddress || lease?.ip || "",
    ClientId: lease?.ClientId || "",
    ScopeId: lease?.ScopeId || "",
    LeaseExpiryTime: lease?.LeaseExpiryTime || "",
  });
  const beforeList = normalizeList(before).map(normalizeLease);
  const afterList = normalizeList(after).map(normalizeLease);

  const byKey = (lease) => `${lease.HostName}`.toLowerCase() + "|" + `${lease.IPAddress}`.toLowerCase();
  const beforeMap = new Map(beforeList.map((lease) => [byKey(lease), lease]));
  const afterMap = new Map(afterList.map((lease) => [byKey(lease), lease]));

  const added = [];
  const removed = [];
  afterMap.forEach((lease, key) => {
    if (!beforeMap.has(key)) added.push(lease);
  });
  beforeMap.forEach((lease, key) => {
    if (!afterMap.has(key)) removed.push(lease);
  });

  const changed = [];
  const beforeByHost = new Map();
  beforeList.forEach((lease) => {
    const hostKey = String(lease.HostName || "").toLowerCase();
    if (hostKey) beforeByHost.set(hostKey, lease);
  });
  afterList.forEach((lease) => {
    const hostKey = String(lease.HostName || "").toLowerCase();
    if (!hostKey || !beforeByHost.has(hostKey)) return;
    const prev = beforeByHost.get(hostKey);
    if (prev.IPAddress !== lease.IPAddress) {
      changed.push({
        HostName: lease.HostName,
        previous_ip: prev.IPAddress || null,
        current_ip: lease.IPAddress || null,
        previous_scope: prev.ScopeId || null,
        current_scope: lease.ScopeId || null,
      });
    }
  });

  return { added, removed, changed };
}

function diffDnsRecords(before, after) {
  const normalizeRecord = (record) => ({
    Zone: record?.Zone || "",
    HostName: record?.HostName || "",
    RecordType: record?.RecordType || "",
    RecordData: record?.RecordData || "",
  });
  const beforeList = normalizeList(before).map(normalizeRecord);
  const afterList = normalizeList(after).map(normalizeRecord);
  const keyFor = (record) =>
    `${record.Zone}`.toLowerCase() +
    "|" +
    `${record.HostName}`.toLowerCase() +
    "|" +
    `${record.RecordType}`.toLowerCase() +
    "|" +
    `${record.RecordData}`.toLowerCase();
  const beforeMap = new Map(beforeList.map((record) => [keyFor(record), record]));
  const afterMap = new Map(afterList.map((record) => [keyFor(record), record]));

  const added = [];
  const removed = [];
  afterMap.forEach((record, key) => {
    if (!beforeMap.has(key)) added.push(record);
  });
  beforeMap.forEach((record, key) => {
    if (!afterMap.has(key)) removed.push(record);
  });

  const changed = [];
  const beforeByHost = new Map();
  beforeList.forEach((record) => {
    const hostKey = `${record.Zone}|${record.HostName}|${record.RecordType}`.toLowerCase();
    if (record.HostName) beforeByHost.set(hostKey, record);
  });
  afterList.forEach((record) => {
    const hostKey = `${record.Zone}|${record.HostName}|${record.RecordType}`.toLowerCase();
    if (!beforeByHost.has(hostKey)) return;
    const prev = beforeByHost.get(hostKey);
    if (prev.RecordData !== record.RecordData) {
      changed.push({
        Zone: record.Zone,
        HostName: record.HostName,
        RecordType: record.RecordType,
        previous_data: prev.RecordData || null,
        current_data: record.RecordData || null,
      });
    }
  });

  return { added, removed, changed };
}

function buildTopologyDiffReport(snapshotA, snapshotB, windowHours = null) {
  const timestampA = snapshotA?.timestamp || snapshotA?.generated_at || null;
  const timestampB = snapshotB?.timestamp || snapshotB?.generated_at || null;
  const dhcpDiff = diffDhcpLeases(snapshotA?.dhcp_leases, snapshotB?.dhcp_leases);
  const dnsDiff = diffDnsRecords(snapshotA?.dns_records, snapshotB?.dns_records);
  return {
    generated_at: new Date().toISOString(),
    window_hours: windowHours,
    snapshot_a: {
      timestamp: timestampA,
      dhcp_count: normalizeList(snapshotA?.dhcp_leases).length,
      dns_count: normalizeList(snapshotA?.dns_records).length,
    },
    snapshot_b: {
      timestamp: timestampB,
      dhcp_count: normalizeList(snapshotB?.dhcp_leases).length,
      dns_count: normalizeList(snapshotB?.dns_records).length,
    },
    summary: {
      dhcp_added: dhcpDiff.added.length,
      dhcp_removed: dhcpDiff.removed.length,
      dhcp_changed: dhcpDiff.changed.length,
      dns_added: dnsDiff.added.length,
      dns_removed: dnsDiff.removed.length,
      dns_changed: dnsDiff.changed.length,
    },
    dhcp: dhcpDiff,
    dns: dnsDiff,
  };
}

function parseUncPath(path) {
  if (!path) return { server: null, share: null };
  const match = String(path).match(/^\\\\([^\\]+)\\([^\\]+)/);
  if (!match) return { server: null, share: null };
  return { server: match[1], share: match[2] };
}

function normalizePrinterReport(payload) {
  if (!payload) return { matches: [], printers: [], mappings: [] };
  if (Array.isArray(payload)) {
    return { matches: [], printers: payload, mappings: [] };
  }
  const matches = normalizeList(payload.matches || payload.Matches);
  const printers = normalizeList(payload.printers || payload.value || payload.Printers);
  const mappings = normalizeList(payload.gpo_printer_mappings || payload.gpoMappings || payload.GpoMappings);
  return { matches, printers, mappings };
}

function buildPrinterGpoIndex(payload) {
  const report = normalizePrinterReport(payload);
  const index = new Map();
  const servers = new Set();
  const links = [];
  report.matches.forEach((raw) => {
    if (!raw) return;
    const printerName = raw.printer_name || raw.printerName || raw.PrinterName || "";
    const shareName = raw.share_name || raw.shareName || raw.ShareName || "";
    const uncPath = raw.unc_path || raw.uncPath || raw.UncPath || "";
    const parsed = parseUncPath(uncPath);
    const server = raw.server || parsed.server || "";
    if (server) servers.add(server);
    const entry = {
      ...raw,
      printer_name: printerName,
      share_name: shareName || parsed.share || "",
      unc_path: uncPath,
      server,
      gpo_name: raw.gpo_name || raw.gpoName || raw.GpoName || "",
      gpo_id: raw.gpo_id || raw.gpoId || raw.GpoId || "",
    };
    links.push(entry);
    [printerName, shareName, entry.share_name].forEach((key) => {
      if (!key) return;
      const normalized = String(key).toLowerCase();
      const list = index.get(normalized) || [];
      list.push(entry);
      index.set(normalized, list);
    });
  });
  return { index, links, servers: Array.from(servers.values()) };
}

function normalizeNetworkAdapters(payload) {
  if (!payload) return [];
  const list = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.value)
      ? payload.value
      : payload?.InterfaceAlias || payload?.Name || payload?.InterfaceDescription
        ? [payload]
        : [];
  return list
    .map((adapter) => {
      const name = adapter?.Name || adapter?.InterfaceAlias || adapter?.InterfaceDescription;
      if (!name) return null;
      return {
        name,
        status: adapter?.Status || adapter?.MediaConnectionState || adapter?.StatusDescription,
        mac: adapter?.MacAddress || adapter?.Mac,
        index: adapter?.ifIndex || adapter?.InterfaceIndex,
        raw: adapter,
      };
    })
    .filter(Boolean);
}

function buildUserDeviceIndexFromReport(payload) {
  const index = new Map();
  if (!payload || typeof payload !== "object") return index;
  const user = payload.user;
  const devices = normalizeList(payload.devices);
  if (!user || !devices.length) return index;
  const upn = String(user.userPrincipalName || user.mail || user.id || "").toLowerCase();
  if (!upn) return index;
  const deviceNames = devices
    .map((device) => device?.displayName || device?.deviceId || device?.id)
    .filter(Boolean);
  if (deviceNames.length) {
    index.set(upn, deviceNames);
  }
  return index;
}

function generateIssueReport() {
  if (!topologyData) {
    showToast("Collect topology first");
    return;
  }
  const issues = loadIssues();
  if (!issues.length) {
    showToast("No issues recorded");
    return;
  }
  const pingMap = buildPingMap(topologyPing);
  const deviceIpMap = buildDeviceIpMap(topologyData);
  const historyIndex = buildTopologyHistoryIndex(loadTopologyHistory());
  const smbSessions = normalizeList(topologyData?.smb_sessions);
  const printJobs = normalizeList(topologyData?.print_jobs);
  const printerReport = lastOutputs["printers"];
  const printerIndex = buildPrinterGpoIndex(printerReport);
  const adapters = normalizeNetworkAdapters(lastOutputs["network"]);
  const adapterNames = adapters.map((adapter) => adapter.name);
  const reportDeviceIndex = buildUserDeviceIndexFromReport(lastOutputs["reports"]);

  const reportItems = issues.map((issue) => {
    const user = issue.user || "";
    const userKey = user.toLowerCase();
    const deviceCandidates = !issue.device && reportDeviceIndex.has(userKey) ? reportDeviceIndex.get(userKey) : [];
    const device = issue.device || deviceCandidates?.[0] || "";
    const deviceKey = device.toLowerCase();
    const resolvedIp = deviceIpMap.get(deviceKey);
    const historyMatches = findHistoryMatches(device, historyIndex, 3);
    const historyIp = historyMatches[0]?.ip || null;
    const ping =
      pingMap.get(deviceKey) ||
      (resolvedIp ? pingMap.get(String(resolvedIp).toLowerCase()) : null) ||
      (historyIp ? pingMap.get(String(historyIp).toLowerCase()) : null) ||
      null;
    const smbMatches = smbSessions.filter((session) => {
      const name = String(session?.ClientComputerName || "").toLowerCase();
      return deviceKey && name === deviceKey;
    });
    const printerMatches = printJobs.filter((job) => {
      const submitter = String(job?.Submitter || "").toLowerCase();
      return user && submitter.includes(userKey);
    });

    const printerLinks = [];
    const seenLinks = new Set();
    printerMatches.forEach((job) => {
      const printerName = job?.PrinterName || job?.printerName || "";
      if (!printerName) return;
      const key = String(printerName).toLowerCase();
      const links = printerIndex.index.get(key) || [];
      if (!links.length) {
        const entryKey = `${key}|unknown|unknown`;
        if (!seenLinks.has(entryKey)) {
          printerLinks.push({
            printer_name: printerName,
            share_name: "",
            gpo_name: "",
            gpo_id: "",
            unc_path: "",
            server: "",
          });
          seenLinks.add(entryKey);
        }
        return;
      }
      links.forEach((link) => {
        const entryKey = `${key}|${link.gpo_name}|${link.server || ""}`;
        if (seenLinks.has(entryKey)) return;
        printerLinks.push(link);
        seenLinks.add(entryKey);
      });
    });

    if (!printerLinks.length && issue.symptom && printerIndex.index.size) {
      const symptomLower = String(issue.symptom).toLowerCase();
      let added = 0;
      printerIndex.index.forEach((links, key) => {
        if (added >= 3) return;
        if (!key || !symptomLower.includes(key)) return;
        links.forEach((link) => {
          if (added >= 3) return;
          const entryKey = `${key}|${link.gpo_name}|${link.server || ""}`;
          if (seenLinks.has(entryKey)) return;
          printerLinks.push(link);
          seenLinks.add(entryKey);
          added += 1;
        });
      });
    }

    const servers = new Set();
    if (topologyData?.smb_server) servers.add(topologyData.smb_server);
    if (topologyData?.print_server) servers.add(topologyData.print_server);
    printerLinks.forEach((link) => {
      if (link?.server) servers.add(link.server);
      const parsed = parseUncPath(link?.unc_path);
      if (parsed.server) servers.add(parsed.server);
    });
    const serverList = Array.from(servers.values()).filter(Boolean);

    const paths = [];
    const base = [];
    if (user) base.push(user);
    if (device) base.push(device);
    if (printerLinks.length) {
      printerLinks.forEach((link) => {
        const chain = base.slice();
        const printerLabel = link.printer_name || link.share_name;
        if (printerLabel) chain.push(printerLabel);
        if (link.gpo_name) chain.push(link.gpo_name);
        if (link.server) chain.push(link.server);
        if (adapterNames.length) {
          chain.push(adapterNames.length > 1 ? `Adapters (${adapterNames.length})` : adapterNames[0]);
        }
        if (chain.length) paths.push(chain.join(" → "));
      });
    } else if (serverList.length) {
      serverList.forEach((server) => {
        const chain = base.slice();
        if (server) chain.push(server);
        if (adapterNames.length) {
          chain.push(adapterNames.length > 1 ? `Adapters (${adapterNames.length})` : adapterNames[0]);
        }
        if (chain.length) paths.push(chain.join(" → "));
      });
    } else if (base.length) {
      paths.push(base.join(" → "));
    }

    const timeline = [];
    if (issue.timestamp) {
      timeline.push({ timestamp: issue.timestamp, label: "Issue reported", type: "issue" });
    }
    printerMatches.forEach((job) => {
      if (!job?.TimeSubmitted) return;
      timeline.push({
        timestamp: job.TimeSubmitted,
        label: `Print job on ${job.PrinterName || "printer"}`,
        type: "print",
      });
    });
    timeline.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    return {
      user,
      device,
      symptom: issue.symptom || "",
      device_ip: resolvedIp || historyIp || null,
      device_ip_source: resolvedIp ? "current" : historyIp ? "history" : null,
      history_matches: historyMatches,
      ping,
      smb_sessions: smbMatches,
      printer_jobs: printerMatches,
      printer_gpo_links: printerLinks,
      servers: serverList,
      network_adapters: adapterNames,
      device_candidates: deviceCandidates || [],
      correlation_paths: paths,
      timeline,
    };
  });

  const reachable = reportItems.filter((item) => item.ping?.Reachable).length;
  const unreachable = reportItems.filter((item) => item.ping && item.ping.Reachable === false).length;
  const summarySets = {
    users: new Set(),
    devices: new Set(),
    printers: new Set(),
    gpos: new Set(),
    servers: new Set(),
    adapters: new Set(),
  };
  reportItems.forEach((item) => {
    if (item.user) summarySets.users.add(item.user);
    if (item.device) summarySets.devices.add(item.device);
    normalizeList(item.printer_gpo_links).forEach((link) => {
      if (link?.printer_name) summarySets.printers.add(link.printer_name);
      if (link?.gpo_name) summarySets.gpos.add(link.gpo_name);
      if (link?.server) summarySets.servers.add(link.server);
    });
    normalizeList(item.servers).forEach((server) => summarySets.servers.add(server));
    normalizeList(item.network_adapters).forEach((adapter) => summarySets.adapters.add(adapter));
  });
  const report = {
    generated_at: new Date().toISOString(),
    issue_count: issues.length,
    reachable,
    unreachable,
    smb_server: topologyData?.smb_server || null,
    print_server: topologyData?.print_server || null,
    correlation: {
      summary: {
        users: summarySets.users.size,
        devices: summarySets.devices.size,
        printers: summarySets.printers.size,
        gpos: summarySets.gpos.size,
        servers: summarySets.servers.size,
        adapters: summarySets.adapters.size,
      },
      sources: {
        topology: Boolean(topologyData),
        printers: Boolean(printerIndex.links?.length),
        network: Boolean(adapterNames.length),
        reports: Boolean(reportDeviceIndex.size),
      },
    },
    history: {
      snapshots: historyIndex.count,
      last_snapshot: historyIndex.lastSnapshot,
    },
    items: reportItems,
  };
  setOutput("topology-report", report);
  setOutputStatus("topology-report", { state: "ok", text: "Report ready", meta: "" });
  setOutputView("topology-report", "graph");
  showToast("Issue correlation report generated");
}

function getGraphPanel(service) {
  return document.querySelector(`.output-graph[data-output="${service}"]`);
}

function buildTopologyGraphData(report) {
  if (!report || !Array.isArray(report.items)) {
    return { nodes: [], edges: [], reportId: null };
  }
  const nodes = new Map();
  const edges = [];
  const addNode = (id, label, type, meta = {}) => {
    if (!id) return;
    if (!nodes.has(id)) {
      nodes.set(id, { id, label: label || id, type, meta });
    }
  };
  const addEdge = (source, target, label, type) => {
    if (!source || !target) return;
    edges.push({ source, target, label, type });
  };

  report.items.forEach((item) => {
    const userLabel = item.user || "Unknown user";
    const deviceLabel = item.device || "Unknown device";
    const userId = `user:${userLabel.toLowerCase()}`;
    const deviceId = `device:${deviceLabel.toLowerCase()}`;
    addNode(userId, userLabel, "user");
    addNode(deviceId, deviceLabel, "device", { ping: item.ping });
    addEdge(userId, deviceId, "reports", "issue");

    const serverLabels = new Set();
    normalizeList(item.servers).forEach((server) => {
      if (server) serverLabels.add(server);
    });
    if (report?.print_server) serverLabels.add(report.print_server);

    if (item.device_ip) {
      const ipId = `ip:${item.device_ip}`;
      addNode(ipId, item.device_ip, "ip");
      addEdge(deviceId, ipId, item.device_ip_source === "history" ? "IP (history)" : "IP", "ip");
    }

    normalizeList(item.printer_jobs).forEach((job) => {
      const printerName = job?.PrinterName || job?.printerName || "Printer";
      const printerId = `printer:${printerName.toLowerCase()}`;
      addNode(printerId, printerName, "printer");
      addEdge(userId, printerId, "print job", "printer");
    });

    normalizeList(item.printer_gpo_links).forEach((link) => {
      const printerLabel = link?.printer_name || link?.share_name;
      if (printerLabel) {
        const printerId = `printer:${printerLabel.toLowerCase()}`;
        addNode(printerId, printerLabel, "printer");
        addEdge(userId, printerId, "print target", "printer");
        if (link?.gpo_name) {
          const gpoId = `gpo:${link.gpo_name.toLowerCase()}`;
          addNode(gpoId, link.gpo_name, "gpo");
          addEdge(printerId, gpoId, "GPO", "gpo");
          if (link?.server) {
            const serverId = `server:${link.server.toLowerCase()}`;
            addNode(serverId, link.server, "server");
            addEdge(gpoId, serverId, "server", "server");
            serverLabels.add(link.server);
          }
        }
      }
    });

    if (normalizeList(item.smb_sessions).length) {
      const serverLabel = report?.smb_server || "SMB Server";
      const serverId = `server:${serverLabel.toLowerCase()}`;
      addNode(serverId, serverLabel, "server");
      addEdge(deviceId, serverId, "SMB", "smb");
      serverLabels.add(serverLabel);
    }

    normalizeList(item.servers).forEach((server) => {
      const serverId = `server:${String(server).toLowerCase()}`;
      addNode(serverId, server, "server");
    });

    const adapterTargets = normalizeList(item.network_adapters);
    if (adapterTargets.length) {
      const serverTarget = Array.from(serverLabels)[0] || "Local host";
      const serverId = `server:${String(serverTarget).toLowerCase()}`;
      addNode(serverId, serverTarget, "server");
      adapterTargets.forEach((adapter) => {
        const adapterLabel = String(adapter || "Adapter");
        const adapterId = `adapter:${adapterLabel.toLowerCase()}`;
        addNode(adapterId, adapterLabel, "adapter");
        addEdge(serverId, adapterId, "adapter", "adapter");
      });
    }

    normalizeList(item.history_matches).forEach((match) => {
      const historyHost = match?.host;
      const historyIp = match?.ip;
      if (historyHost) {
        const hostId = `host:${historyHost.toLowerCase()}`;
        addNode(hostId, historyHost, "history");
        addEdge(deviceId, hostId, "history host", "history");
        if (historyIp) {
          const histIpId = `ip:${historyIp}`;
          addNode(histIpId, historyIp, "ip");
          addEdge(hostId, histIpId, "history IP", "history");
        }
      }
    });
  });

  return {
    nodes: Array.from(nodes.values()),
    edges,
    reportId: report?.generated_at || null,
  };
}

function layoutGraph(nodes, edges, width, height) {
  if (!nodes.length) return;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 3;
  nodes.forEach((node, idx) => {
    const angle = (idx / nodes.length) * Math.PI * 2;
    node.x = centerX + radius * Math.cos(angle);
    node.y = centerY + radius * Math.sin(angle);
    node.vx = 0;
    node.vy = 0;
  });

  const k = Math.sqrt((width * height) / Math.max(nodes.length, 1));
  const iterations = 220;
  const damping = 0.85;
  const repulsion = 140;

  const nodeIndex = new Map(nodes.map((node) => [node.id, node]));
  for (let step = 0; step < iterations; step += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      const nodeA = nodes[i];
      for (let j = i + 1; j < nodes.length; j += 1) {
        const nodeB = nodes[j];
        const dx = nodeA.x - nodeB.x;
        const dy = nodeA.y - nodeB.y;
        const dist = Math.max(20, Math.hypot(dx, dy));
        const force = (repulsion * k * k) / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodeA.vx += fx;
        nodeA.vy += fy;
        nodeB.vx -= fx;
        nodeB.vy -= fy;
      }
    }

    edges.forEach((edge) => {
      const source = nodeIndex.get(edge.source);
      const target = nodeIndex.get(edge.target);
      if (!source || !target) return;
      const dx = source.x - target.x;
      const dy = source.y - target.y;
      const dist = Math.max(30, Math.hypot(dx, dy));
      const force = (dist * dist) / (k * 12);
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      source.vx -= fx;
      source.vy -= fy;
      target.vx += fx;
      target.vy += fy;
    });

    nodes.forEach((node) => {
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;
      node.x = Math.min(width - 20, Math.max(20, node.x));
      node.y = Math.min(height - 20, Math.max(20, node.y));
    });
  }
}

const GRAPH_LAYOUT_SCOPE = "service";
const GRAPH_LAYOUT_SERVICE_KEY = "topology-report";

function getGraphLayoutKey(reportId, scope = GRAPH_LAYOUT_SCOPE) {
  if (scope === "report") {
    if (!reportId) return null;
    return `graphLayout:${reportId}`;
  }
  return `graphLayout:${GRAPH_LAYOUT_SERVICE_KEY}`;
}

function parseGraphLayout(raw) {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return parsed;
  } catch (err) {
    return null;
  }
}

function loadGraphLayout(reportId) {
  const serviceKey = getGraphLayoutKey(reportId, "service");
  const reportKey = getGraphLayoutKey(reportId, "report");
  const serviceLayout = parseGraphLayout(localStorage.getItem(serviceKey));
  if (serviceLayout) return serviceLayout;
  return parseGraphLayout(reportKey ? localStorage.getItem(reportKey) : null);
}

function saveGraphLayout(state) {
  if (!state) return;
  const payload = {
    reportId: state.reportId || null,
    nodes: state.graphData.nodes.reduce((acc, node) => {
      acc[node.id] = { x: node.x, y: node.y };
      return acc;
    }, {}),
    view: state.viewState,
  };
  const serviceKey = getGraphLayoutKey(state.reportId, "service");
  if (serviceKey) {
    localStorage.setItem(serviceKey, JSON.stringify(payload));
  }
  const reportKey = getGraphLayoutKey(state.reportId, "report");
  if (reportKey) {
    localStorage.setItem(reportKey, JSON.stringify(payload));
  }
}

function autoFitGraph(state, width, height, padding = 40) {
  if (!state?.graphData?.nodes?.length) return;
  const nodes = state.graphData.nodes;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  nodes.forEach((node) => {
    if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
    minX = Math.min(minX, node.x);
    minY = Math.min(minY, node.y);
    maxX = Math.max(maxX, node.x);
    maxY = Math.max(maxY, node.y);
  });
  if (!Number.isFinite(minX) || !Number.isFinite(minY)) return;
  const contentWidth = Math.max(1, maxX - minX);
  const contentHeight = Math.max(1, maxY - minY);
  const availableWidth = Math.max(1, width - padding * 2);
  const availableHeight = Math.max(1, height - padding * 2);
  const scale = Math.min(availableWidth / contentWidth, availableHeight / contentHeight);
  const clampedScale = Math.min(2.5, Math.max(0.4, scale));
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  state.viewState.scale = clampedScale;
  state.viewState.translateX = width / 2 / clampedScale - centerX;
  state.viewState.translateY = height / 2 / clampedScale - centerY;
  state.graphLayer.setAttribute(
    "transform",
    `scale(${state.viewState.scale}) translate(${state.viewState.translateX},${state.viewState.translateY})`
  );
}

function buildGraphSvgStyle() {
  const rootStyle = getComputedStyle(document.documentElement);
  const text = rootStyle.getPropertyValue("--text").trim() || "#ecf4f1";
  const muted = rootStyle.getPropertyValue("--muted").trim() || "#9bb2b5";
  return `
    .graph-node text { font-size: 10px; fill: ${text}; opacity: 0.85; font-family: "Manrope", "Segoe UI", sans-serif; }
    .graph-node circle { stroke: rgba(255, 255, 255, 0.4); stroke-width: 1; }
    .graph-node.user circle { fill: rgba(71, 244, 197, 0.9); }
    .graph-node.device circle { fill: rgba(88, 158, 255, 0.9); }
    .graph-node.ip circle { fill: rgba(255, 209, 102, 0.9); }
    .graph-node.printer circle { fill: rgba(255, 146, 97, 0.9); }
    .graph-node.gpo circle { fill: rgba(255, 122, 180, 0.9); }
    .graph-node.server circle { fill: rgba(180, 120, 255, 0.9); }
    .graph-node.adapter circle { fill: rgba(102, 204, 255, 0.9); }
    .graph-node.history circle { fill: rgba(255, 255, 255, 0.55); }
    .graph-edge { stroke: rgba(255, 255, 255, 0.22); stroke-width: 1; }
    .graph-edge.history { stroke-dasharray: 4 4; stroke: rgba(255, 255, 255, 0.35); }
    .graph-node.highlight circle { stroke: ${text}; stroke-width: 2; }
    .graph-node.dimmed { opacity: 0.35; }
    .graph-node.hidden, .graph-edge.hidden { opacity: 0; }
    .graph-edge.dimmed { opacity: 0.25; }
    .graph-label-muted { fill: ${muted}; font-size: 9px; }
  `;
}

function buildGraphSvgString(state, includeBackground) {
  if (!state?.svg) return null;
  const svg = state.svg;
  const clone = svg.cloneNode(true);
  const viewBox = svg.getAttribute("viewBox") || "0 0 800 500";
  const viewParts = viewBox.split(/\s+/).map((value) => Number(value));
  const width = Number.isFinite(viewParts[2]) ? viewParts[2] : 800;
  const height = Number.isFinite(viewParts[3]) ? viewParts[3] : 500;
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  clone.setAttribute("width", width);
  clone.setAttribute("height", height);

  const style = document.createElementNS("http://www.w3.org/2000/svg", "style");
  style.textContent = buildGraphSvgStyle();

  if (includeBackground) {
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", "0");
    rect.setAttribute("y", "0");
    rect.setAttribute("width", width);
    rect.setAttribute("height", height);
    rect.setAttribute("fill", "#0b0f14");
    clone.insertBefore(rect, clone.firstChild);
  }
  clone.insertBefore(style, clone.firstChild);

  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(clone);
  return `<?xml version="1.0" encoding="UTF-8"?>\n${source}`;
}

function exportGraphSvg(state) {
  const svgString = buildGraphSvgString(state, true);
  if (!svgString) {
    showToast("Graph export unavailable");
    return;
  }
  const name = getGraphExportName(state, "svg");
  downloadTextFile(svgString, name, "image/svg+xml");
}

async function exportGraphPng(state) {
  const svgString = buildGraphSvgString(state, true);
  if (!svgString) {
    showToast("Graph export unavailable");
    return;
  }
  const viewBox = state.svg.getAttribute("viewBox") || "0 0 800 500";
  const viewParts = viewBox.split(/\s+/).map((value) => Number(value));
  const width = Number.isFinite(viewParts[2]) ? viewParts[2] : 800;
  const height = Number.isFinite(viewParts[3]) ? viewParts[3] : 500;
  const blob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = reject;
    img.src = url;
  });
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    ctx.fillStyle = "#0b0f14";
    ctx.fillRect(0, 0, width, height);
    ctx.drawImage(img, 0, 0, width, height);
  }
  URL.revokeObjectURL(url);
  const pngBlob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
  if (!pngBlob) {
    showToast("PNG export failed");
    return;
  }
  const pngUrl = URL.createObjectURL(pngBlob);
  const link = document.createElement("a");
  link.href = pngUrl;
  link.download = getGraphExportName(state, "png");
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(pngUrl);
}

function getGraphExportName(state, ext) {
  const base = sanitizeFilename(state?.reportId || "topology-graph");
  return `${base}.${ext}`;
}

function renderTopologyGraph(container, graphData) {
  if (!container) return;
  container.innerHTML = "";
  if (!graphData || !graphData.nodes.length) {
    const empty = document.createElement("div");
    empty.classList.add("graph-empty");
    empty.textContent = "No graph data available.";
    container.appendChild(empty);
    return;
  }

  const controls = document.createElement("div");
  controls.classList.add("graph-controls");
  controls.innerHTML = `
    <div class="graph-controls-left">
      <button class="ghost small" data-graph-action="reset-view">Reset view</button>
      <button class="ghost small" data-graph-action="auto-fit">Auto-fit</button>
      <button class="ghost small" data-graph-action="reset-layout">Reset layout</button>
      <button class="ghost small" data-graph-action="save-layout">Save layout</button>
    </div>
    <div class="graph-controls-right">
      <input class="graph-search" type="search" placeholder="Search nodes" />
      <button class="ghost small" data-graph-action="toggle-legend">Legend</button>
      <button class="ghost small" data-graph-action="export-svg">Export SVG</button>
      <button class="ghost small" data-graph-action="export-png">Export PNG</button>
    </div>
  `;

  const filterBar = document.createElement("div");
  filterBar.classList.add("graph-filters");
  const filterTypes = [
    { type: "user", label: "Users" },
    { type: "device", label: "Devices" },
    { type: "ip", label: "IPs" },
    { type: "printer", label: "Printers" },
    { type: "gpo", label: "GPOs" },
    { type: "server", label: "Servers" },
    { type: "adapter", label: "Adapters" },
    { type: "history", label: "History" },
  ];
  filterTypes.forEach((item) => {
    const label = document.createElement("label");
    label.classList.add("graph-filter");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = true;
    input.dataset.filterType = item.type;
    label.appendChild(input);
    label.appendChild(document.createTextNode(item.label));
    filterBar.appendChild(label);
  });

  const canvas = document.createElement("div");
  canvas.classList.add("graph-canvas");
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "graph-svg");
  canvas.appendChild(svg);

  const legend = document.createElement("div");
  legend.classList.add("graph-legend");
  const legendItems = [
    { type: "user", label: "User" },
    { type: "device", label: "Device" },
    { type: "ip", label: "IP" },
    { type: "printer", label: "Printer" },
    { type: "gpo", label: "GPO" },
    { type: "server", label: "Server" },
    { type: "adapter", label: "Adapter" },
    { type: "history", label: "History" },
  ];
  legendItems.forEach((item) => {
    const row = document.createElement("span");
    row.classList.add("legend-item");
    row.dataset.type = item.type;
    row.textContent = item.label;
    legend.appendChild(row);
  });

  container.appendChild(controls);
  container.appendChild(filterBar);
  container.appendChild(canvas);
  container.appendChild(legend);

  const { width, height } = canvas.getBoundingClientRect();
  const w = width || 520;
  const h = height || 320;
  layoutGraph(graphData.nodes, graphData.edges, w, h);

  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

  const graphLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
  graphLayer.setAttribute("class", "graph-layer");
  svg.appendChild(graphLayer);

  const viewState = {
    scale: 1,
    translateX: 0,
    translateY: 0,
  };

  const nodeIndex = new Map(graphData.nodes.map((node) => [node.id, node]));
  const nodeElements = new Map();
  const edgeElements = [];

  const applyTransform = () => {
    graphLayer.setAttribute(
      "transform",
      `scale(${viewState.scale}) translate(${viewState.translateX},${viewState.translateY})`
    );
  };

  const getGraphCoords = (event) => {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const ctm = graphLayer.getCTM();
    if (!ctm) {
      return { x: 0, y: 0 };
    }
    const inverse = ctm.inverse();
    const transformed = point.matrixTransform(inverse);
    return { x: transformed.x, y: transformed.y };
  };

  const updateNodeElement = (node) => {
    const el = nodeElements.get(node.id);
    if (!el) return;
    el.circle.setAttribute("cx", node.x);
    el.circle.setAttribute("cy", node.y);
    el.text.setAttribute("x", node.x + 12);
    el.text.setAttribute("y", node.y + 4);
  };

  const updateEdges = () => {
    edgeElements.forEach((entry) => {
      const source = nodeIndex.get(entry.edge.source);
      const target = nodeIndex.get(entry.edge.target);
      if (!source || !target) return;
      entry.line.setAttribute("x1", source.x);
      entry.line.setAttribute("y1", source.y);
      entry.line.setAttribute("x2", target.x);
      entry.line.setAttribute("y2", target.y);
    });
  };

  graphData.edges.forEach((edge) => {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    const source = nodeIndex.get(edge.source);
    const target = nodeIndex.get(edge.target);
    if (!source || !target) return;
    line.setAttribute("x1", source.x);
    line.setAttribute("y1", source.y);
    line.setAttribute("x2", target.x);
    line.setAttribute("y2", target.y);
    line.setAttribute("class", `graph-edge ${edge.type || ""}`.trim());
    graphLayer.appendChild(line);
    edgeElements.push({ edge, line });
  });

  graphData.nodes.forEach((node) => {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", `graph-node ${node.type || "unknown"}`.trim());
    group.dataset.nodeId = node.id;
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", node.x);
    circle.setAttribute("cy", node.y);
    circle.setAttribute("r", 9);
    group.appendChild(circle);
    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", node.x + 12);
    text.setAttribute("y", node.y + 4);
    text.textContent = node.label;
    group.appendChild(text);
    const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
    title.textContent = node.label;
    group.appendChild(title);
    graphLayer.appendChild(group);
    nodeElements.set(node.id, { group, circle, text });
  });

  applyTransform();

  let draggingNode = null;
  let panning = false;
  let panStart = { x: 0, y: 0, tx: 0, ty: 0 };

  graphLayer.addEventListener("pointerdown", (event) => {
    const target = event.target.closest(".graph-node");
    if (!target) return;
    const nodeId = target.dataset.nodeId;
    const node = nodeIndex.get(nodeId);
    if (!node) return;
    draggingNode = node;
    target.classList.add("dragging");
    event.preventDefault();
    event.stopPropagation();
    svg.setPointerCapture(event.pointerId);
  });

  svg.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".graph-node")) return;
    panning = true;
    panStart = {
      x: event.clientX,
      y: event.clientY,
      tx: viewState.translateX,
      ty: viewState.translateY,
    };
    canvas.classList.add("panning");
    svg.setPointerCapture(event.pointerId);
  });

  svg.addEventListener("pointermove", (event) => {
    if (draggingNode) {
      const point = getGraphCoords(event);
      draggingNode.x = point.x;
      draggingNode.y = point.y;
      updateNodeElement(draggingNode);
      updateEdges();
      return;
    }
    if (panning) {
      const dx = event.clientX - panStart.x;
      const dy = event.clientY - panStart.y;
      viewState.translateX = panStart.tx + dx;
      viewState.translateY = panStart.ty + dy;
      applyTransform();
    }
  });

  const stopInteraction = (event) => {
    if (draggingNode) {
      const el = nodeElements.get(draggingNode.id);
      if (el) {
        el.group.classList.remove("dragging");
      }
    }
    draggingNode = null;
    panning = false;
    canvas.classList.remove("panning");
    if (event?.pointerId !== undefined) {
      try {
        svg.releasePointerCapture(event.pointerId);
      } catch (err) {
        /* ignore */
      }
    }
  };

  svg.addEventListener("pointerup", stopInteraction);
  svg.addEventListener("pointercancel", stopInteraction);
  svg.addEventListener("pointerleave", stopInteraction);

  svg.addEventListener("wheel", (event) => {
    event.preventDefault();
    const delta = event.deltaY || 0;
    const zoomFactor = delta < 0 ? 1.1 : 0.9;
    const newScale = Math.min(2.5, Math.max(0.5, viewState.scale * zoomFactor));
    if (newScale === viewState.scale) return;
    const point = getGraphCoords(event);
    viewState.translateX += (viewState.scale - newScale) * point.x;
    viewState.translateY += (viewState.scale - newScale) * point.y;
    viewState.scale = newScale;
    applyTransform();
  });

  const state = {
    graphData,
    nodeIndex,
    nodeElements,
    edgeElements,
    viewState,
    svg,
    graphLayer,
    filters: new Set(filterTypes.map((item) => item.type)),
    searchQuery: "",
    reportId: graphData.reportId || null,
    legendVisible: true,
  };
  graphStates["topology-report"] = state;

  const applyStoredLayout = (layout) => {
    if (!layout) return;
    const nodePositions = layout.nodes || {};
    state.graphData.nodes.forEach((node) => {
      const saved = nodePositions[node.id];
      if (!saved) return;
      if (Number.isFinite(saved.x)) node.x = saved.x;
      if (Number.isFinite(saved.y)) node.y = saved.y;
    });
    state.graphData.nodes.forEach((node) => updateNodeElement(node));
    updateEdges();
    if (layout.view) {
      const scale = Number(layout.view.scale);
      const tx = Number(layout.view.translateX);
      const ty = Number(layout.view.translateY);
      if (Number.isFinite(scale)) state.viewState.scale = Math.min(3, Math.max(0.4, scale));
      if (Number.isFinite(tx)) state.viewState.translateX = tx;
      if (Number.isFinite(ty)) state.viewState.translateY = ty;
      applyTransform();
    }
  };

  const applyFilters = () => {
    const query = state.searchQuery;
    const allowed = state.filters;
    const visibleMap = new Map();
    state.graphData.nodes.forEach((node) => {
      const matchesType = allowed.has(node.type);
      const matchesQuery = !query || node.label.toLowerCase().includes(query);
      visibleMap.set(node.id, matchesType);
      const elements = state.nodeElements.get(node.id);
      if (!elements) return;
      elements.group.classList.toggle("hidden", !matchesType);
      elements.group.classList.toggle("dimmed", matchesType && query && !matchesQuery);
      elements.group.classList.toggle("highlight", matchesType && query && matchesQuery);
    });
    state.edgeElements.forEach(({ edge, line }) => {
      const sourceVisible = visibleMap.get(edge.source);
      const targetVisible = visibleMap.get(edge.target);
      const show = sourceVisible && targetVisible;
      line.classList.toggle("hidden", !show);
    });
  };

  const savedLayout = loadGraphLayout(state.reportId);
  if (savedLayout) {
    applyStoredLayout(savedLayout);
    if (!savedLayout.view) {
      autoFitGraph(state, w, h);
    }
  } else {
    autoFitGraph(state, w, h);
  }

  const searchInput = controls.querySelector(".graph-search");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      state.searchQuery = searchInput.value.trim().toLowerCase();
      applyFilters();
    });
  }

  filterBar.querySelectorAll("input[type=\"checkbox\"]").forEach((input) => {
    input.addEventListener("change", () => {
      const type = input.dataset.filterType;
      if (!type) return;
      if (input.checked) {
        state.filters.add(type);
      } else {
        state.filters.delete(type);
      }
      applyFilters();
    });
  });

  controls.querySelectorAll("[data-graph-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.dataset.graphAction;
      if (action === "reset-view") {
        state.viewState.scale = 1;
        state.viewState.translateX = 0;
        state.viewState.translateY = 0;
        applyTransform();
      }
      if (action === "auto-fit") {
        autoFitGraph(state, w, h);
      }
      if (action === "reset-layout") {
        layoutGraph(state.graphData.nodes, state.graphData.edges, w, h);
        state.graphData.nodes.forEach((node) => updateNodeElement(node));
        updateEdges();
      }
      if (action === "save-layout") {
        saveGraphLayout(state);
        showToast("Layout saved");
      }
      if (action === "toggle-legend") {
        state.legendVisible = !state.legendVisible;
        legend.classList.toggle("hidden", !state.legendVisible);
      }
      if (action === "export-svg") {
        exportGraphSvg(state);
      }
      if (action === "export-png") {
        await exportGraphPng(state);
      }
    });
  });

  applyFilters();
}

function renderGraph(service, parsed) {
  if (service === "topology-report") {
    const container = getGraphPanel(service);
    if (!container) return;
    const graphData = buildTopologyGraphData(parsed);
    renderTopologyGraph(container, graphData);
  }
  if (service === "incident") {
    const container = getGraphPanel(service);
    if (!container) return;
    const graph = parsed?.incident_graph;
    if (!graph || !Array.isArray(graph.nodes)) return;
    const graphData = {
      nodes: graph.nodes,
      edges: graph.edges || [],
      reportId: graph?.incident?.incident_id || null,
    };
    renderTopologyGraph(container, graphData);
  }
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
  if (step.type === "note") {
    const label = String(step.label || "Note").trim();
    if (!label) return null;
    return {
      type: "note",
      label,
      note: step.note || "",
      optional: Boolean(step.optional),
      defaultInclude: step.defaultInclude,
      phase: step.phase || "",
    };
  }
  const service = step.service;
  const action = step.action;
  if (!ACTIONS_UI?.[service]?.[action]) return null;
  return {
    service,
    action,
    label: step.label || "",
    optional: Boolean(step.optional),
    defaultInclude: step.defaultInclude,
    params: step.params || undefined,
    safe: Boolean(step.safe),
    rollback: Boolean(step.rollback),
    phase: step.phase || "",
  };
}

function normalizePackVersion(version) {
  if (!version || typeof version !== "object") return null;
  const name = String(version.name || "").trim();
  if (!name) return null;
  const steps = Array.isArray(version.steps) ? version.steps.map(normalizePackStep).filter(Boolean) : [];
  if (!steps.length) return null;
  return {
    version_id: version.version_id || version.versionId || `v-${Date.now()}`,
    saved_at: version.saved_at || version.savedAt || Date.now(),
    name,
    description: version.description || "",
    steps,
    defaults: version.defaults && typeof version.defaults === "object" ? version.defaults : undefined,
    tenant_id: version.tenant_id || version.tenantId || undefined,
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
  const createdAt = pack.created_at || pack.createdAt || null;
  const updatedAt = pack.updated_at || pack.updatedAt || createdAt || null;
  const deletedAt = pack.deleted_at || pack.deletedAt || null;
  const versions = Array.isArray(pack.versions)
    ? pack.versions.map(normalizePackVersion).filter(Boolean)
    : [];
  return {
    id,
    name,
    description: pack.description || "",
    steps,
    defaults,
    tenant_id: tenantId,
    builtin: Boolean(pack.builtin),
    created_at: createdAt,
    updated_at: updatedAt,
    deleted_at: deletedAt,
    versions,
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

function isPackDeleted(pack) {
  return Boolean(pack?.deleted_at);
}

function buildPackVersionSnapshot(pack) {
  return normalizePackVersion({
    version_id: `v-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`,
    saved_at: Date.now(),
    name: pack.name,
    description: pack.description || "",
    steps: pack.steps,
    defaults: pack.defaults,
    tenant_id: pack.tenant_id,
  });
}

function loadActionPackAudit() {
  try {
    const raw = localStorage.getItem(ACTION_PACK_AUDIT_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function saveActionPackAudit(entries) {
  localStorage.setItem(ACTION_PACK_AUDIT_KEY, JSON.stringify(entries));
}

function logActionPackAudit(action, pack, details = {}) {
  const entries = loadActionPackAudit();
  entries.unshift({
    action,
    pack_id: pack?.id || null,
    pack_name: pack?.name || null,
    timestamp: Date.now(),
    details,
  });
  saveActionPackAudit(entries.slice(0, 200));
  addActivity(`Pack ${action}: ${pack?.name || "unknown"}`);
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
  return data[packId] || { stepParams: {}, includeSteps: {}, dryRun: false };
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

function loadSnapshotPrefs() {
  try {
    const raw = localStorage.getItem(SNAPSHOT_PREFS_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (err) {
    return {};
  }
}

function getSnapshotPreference(service) {
  const prefs = loadSnapshotPrefs();
  if (prefs[service] === undefined) return true;
  return Boolean(prefs[service]);
}

function setSnapshotPreference(service, enabled) {
  const prefs = loadSnapshotPrefs();
  prefs[service] = Boolean(enabled);
  localStorage.setItem(SNAPSHOT_PREFS_KEY, JSON.stringify(prefs));
}

function loadDraftSnapshots() {
  try {
    const raw = localStorage.getItem(DRAFT_SNAPSHOTS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function saveDraftSnapshots(drafts) {
  const payload = Array.isArray(drafts) ? drafts : [];
  localStorage.setItem(DRAFT_SNAPSHOTS_KEY, JSON.stringify(payload));
}

function getActiveDraftId() {
  return localStorage.getItem(ACTIVE_DRAFT_KEY) || null;
}

function setActiveDraftId(draftId) {
  if (!draftId) {
    localStorage.removeItem(ACTIVE_DRAFT_KEY);
    activeDraftId = null;
    return;
  }
  localStorage.setItem(ACTIVE_DRAFT_KEY, draftId);
  activeDraftId = draftId;
}

function getActiveDraft() {
  if (!activeDraftId) return null;
  return (
    draftSnapshots.find((entry) => entry.id === activeDraftId && !entry.archived_at) || null
  );
}

function createDraftSnapshot({ title } = {}) {
  const now = new Date().toISOString();
  const draft = {
    id: `draft-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title: title || "New draft",
    notes: "",
    subject: null,
    profile: "core",
    entries: [],
    created_at: now,
    updated_at: now,
  };
  draftSnapshots.unshift(draft);
  setActiveDraftId(draft.id);
  saveDraftSnapshots(draftSnapshots);
  return draft;
}

function updateDraftSnapshot(draftId, updates) {
  const draft = draftSnapshots.find((entry) => entry.id === draftId);
  if (!draft) return null;
  Object.assign(draft, updates || {});
  draft.updated_at = new Date().toISOString();
  saveDraftSnapshots(draftSnapshots);
  return draft;
}

function archiveDraftSnapshot(draftId) {
  const draft = updateDraftSnapshot(draftId, { archived_at: new Date().toISOString() });
  if (!draft) return null;
  saveDraftSnapshots(draftSnapshots);
  if (activeDraftId === draftId) {
    const next = draftSnapshots.find((entry) => !entry.archived_at);
    setActiveDraftId(next ? next.id : null);
  }
  return draft;
}

function addDraftEntry(draftId, entry) {
  const draft = draftSnapshots.find((item) => item.id === draftId);
  if (!draft) return null;
  draft.entries = Array.isArray(draft.entries) ? draft.entries : [];
  draft.entries.unshift(entry);
  draft.updated_at = new Date().toISOString();
  saveDraftSnapshots(draftSnapshots);
  return draft;
}

function clearDraftEntries(draftId) {
  const draft = draftSnapshots.find((item) => item.id === draftId);
  if (!draft) return null;
  draft.entries = [];
  draft.updated_at = new Date().toISOString();
  saveDraftSnapshots(draftSnapshots);
  return draft;
}

function getActionKind(service, action) {
  if (!action) return "event";
  if (service === "reports") return "read";
  if (action.startsWith("list_") || action.startsWith("get_") || action.endsWith("_report")) return "read";
  if (
    action.startsWith("create_") ||
    action.startsWith("update_") ||
    action.startsWith("delete_") ||
    action.startsWith("add_") ||
    action.startsWith("remove_") ||
    action.startsWith("set_") ||
    action.startsWith("enable_") ||
    action.startsWith("disable_") ||
    action.startsWith("assign_") ||
    action.startsWith("link_") ||
    action.startsWith("unlink_") ||
    action.startsWith("reset_") ||
    action.startsWith("restore_")
  ) {
    return "write";
  }
  return "event";
}

function shouldDisableSnapshots(service, action) {
  if (service === "reports") return false;
  return true;
}

async function fetchSnapshots({ type, target, prefix, action, limit } = {}) {
  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (target) params.set("target", target);
  if (prefix) params.set("prefix", prefix);
  if (action) params.set("action", action);
  if (limit) params.set("limit", String(limit));
  try {
    const res = await fetch(`/api/snapshots?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || [];
  } catch (err) {
    return null;
  }
}

async function fetchSnapshotDiff(snapshotA, snapshotB) {
  if (!snapshotA || !snapshotB) return null;
  const params = new URLSearchParams();
  params.set("a", snapshotA);
  params.set("b", snapshotB);
  try {
    const res = await fetch(`/api/snapshots/diff?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return null;
    fetchSystemStatusSummary();
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function fetchSnapshotEntities() {
  try {
    const res = await fetch("/api/snapshots/entities");
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

async function fetchSnapshotHistory(canonicalId, limit = 20) {
  if (!canonicalId) return [];
  const params = new URLSearchParams();
  params.set("canonical_id", canonicalId);
  params.set("limit", String(limit));
  try {
    const res = await fetch(`/api/snapshots/history?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

async function createIncident(payload) {
  try {
    const res = await fetch("/api/incidents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload || {}),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Failed to create incident");
    return data.data;
  } catch (err) {
    showToast(err.message || "Incident creation failed");
    return null;
  }
}

async function fetchIncidents(limit = 50) {
  try {
    const res = await fetch(`/api/incidents?limit=${limit}`);
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

async function renderIncidentReportSelect() {
  if (!incidentReportSelect) return;
  const incidents = await fetchIncidents();
  incidentReportSelect.innerHTML = "";
  if (!incidents.length) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No incidents";
    incidentReportSelect.appendChild(opt);
    incidentReportSelect.disabled = true;
    return;
  }
  incidentReportSelect.disabled = false;
  incidents.forEach((incident) => {
    const option = document.createElement("option");
    option.value = incident.incident_id;
    option.textContent = incident.title || incident.symptom_id || incident.incident_id;
    incidentReportSelect.appendChild(option);
  });
  if (activeIncidentId) {
    incidentReportSelect.value = activeIncidentId;
  }
}

async function fetchIncidentGraph(incidentId) {
  if (!incidentId) return null;
  try {
    const res = await fetch(`/api/incidents/${incidentId}/graph`);
    const data = await res.json();
    if (!data.ok) return null;
    fetchSystemStatusSummary();
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function fetchIncidentTimeline(incidentId) {
  if (!incidentId) return null;
  try {
    const res = await fetch(`/api/incidents/${incidentId}/timeline`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function fetchGoldenBaselines() {
  try {
    const res = await fetch("/api/snapshots/golden");
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

async function setGoldenBaseline(kind, snapshotId, label = "") {
  try {
    const res = await fetch("/api/snapshots/golden", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind, snapshot_id: snapshotId, label }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Failed to set golden baseline");
    return data.data;
  } catch (err) {
    showToast(err.message || "Failed to set golden baseline");
    return null;
  }
}

async function compareGoldenBaseline(snapshotId) {
  if (!snapshotId) return null;
  const params = new URLSearchParams();
  params.set("snapshot_id", snapshotId);
  try {
    const res = await fetch(`/api/snapshots/golden/diff?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Golden diff failed");
      return null;
    }
    return data.data || null;
  } catch (err) {
    showToast("Golden diff failed");
    return null;
  }
}

async function fetchSnapshotEngineDiff(snapshotA, snapshotB) {
  if (!snapshotA || !snapshotB) return null;
  const params = new URLSearchParams();
  params.set("a", snapshotA);
  params.set("b", snapshotB);
  try {
    const res = await fetch(`/api/snapshots/engine/diff?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function resolveSnapshotSubject(aliasType, aliasValue) {
  if (!aliasType || !aliasValue) return null;
  const params = new URLSearchParams();
  params.set("alias_type", aliasType);
  params.set("alias_value", aliasValue);
  try {
    const res = await fetch(`/api/snapshots/resolve?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function fetchSnapshotEvents(canonicalIds, limit = 50) {
  if (!canonicalIds || !canonicalIds.length) return [];
  const params = new URLSearchParams();
  params.set("canonical_ids", canonicalIds.join(","));
  params.set("limit", String(limit));
  try {
    const res = await fetch(`/api/snapshots/events?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

async function fetchSymptomTemplates() {
  try {
    const res = await fetch("/api/symptoms");
    const data = await res.json();
    if (!data.ok) return [];
    return data.data || [];
  } catch (err) {
    return [];
  }
}

function renderSymptomTemplates() {
  if (!issueSymptomTemplate) return;
  issueSymptomTemplate.innerHTML = "";
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Manual symptom";
  issueSymptomTemplate.appendChild(defaultOption);
  symptomTemplates.forEach((template) => {
    const option = document.createElement("option");
    option.value = template.symptom_id;
    option.textContent = template.display_name || template.symptom_id;
    issueSymptomTemplate.appendChild(option);
  });
}

async function refreshSymptomTemplates() {
  symptomTemplates = await fetchSymptomTemplates();
  renderSymptomTemplates();
}

async function captureSnapshots(subjects, profile = "core", context = {}, incidentId = null) {
  if (!subjects || !subjects.length) return null;
  const incident = incidentId || activeIncidentId || null;
  try {
    const res = await fetch("/api/snapshots/capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subjects, profile, context, incident_id: incident }),
    });
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function captureIncidentSnapshots(issue) {
  if (!issue) return null;
  try {
    const res = await fetch("/api/snapshots/capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        incident: issue,
        incident_id: issue.incident_id || null,
        profile: "core",
        context: { source: "incident" },
      }),
    });
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

function deriveSubjectsFromPack(pack, stepParams) {
  const subjects = [];
  const addSubject = (kind, identifiers) => {
    if (!kind || !identifiers) return;
    subjects.push({ kind, identifiers });
  };
  if (Array.isArray(pack?.subjects)) {
    pack.subjects.forEach((subject) => {
      if (subject && typeof subject === "object") subjects.push(subject);
    });
  }
  Object.values(stepParams || {}).forEach((entry) => {
    if (!entry || typeof entry !== "object") return;
    const user = entry.user_id || entry.upn || entry.user;
    if (user) addSubject("user", { upn: user });
    const device = entry.device || entry.hostname || entry.server || entry.ip;
    if (device) {
      const aliasType = isIpAddress(device) ? "ip" : "hostname";
      addSubject("device", { [aliasType]: device });
    }
    if (entry.dc) addSubject("dc", { hostname: entry.dc });
    if (entry.dns_server) addSubject("dns_server", { hostname: entry.dns_server });
    if (entry.file_server) addSubject("file_server", { hostname: entry.file_server });
    if (entry.print_server) addSubject("print_server", { hostname: entry.print_server });
  });
  return subjects;
}

function mapReportSnapshot(entry) {
  const type = entry?.type || "";
  const action = type.startsWith("reports.") ? type.replace("reports.", "") : entry?.meta?.action || "report";
  const label = ACTIONS_UI?.reports?.[action]?.label || action;
  const timestamp = entry?.collected_at ? Date.parse(entry.collected_at) : Date.now();
  return {
    id: entry?.id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    action,
    label,
    timestamp,
    data: entry?.payload || null,
    snapshot: entry || null,
  };
}

function getReportHistoryItems() {
  return reportHistoryItems.length ? reportHistoryItems : loadReportHistory();
}

async function refreshReportHistory() {
  const snapshots = await fetchSnapshots({ prefix: "reports.", limit: 50 });
  if (!snapshots) {
    renderReportHistory();
    return;
  }
  reportHistoryItems = snapshots.map(mapReportSnapshot);
  renderReportHistory();
}

function getAllActionPacks(options = {}) {
  const includeDeleted = Boolean(options.includeDeleted);
  const packs = [...ACTION_PACKS, ...loadActionPacks()];
  return includeDeleted ? packs : packs.filter((pack) => !isPackDeleted(pack));
}

function getActionPackById(id, options = {}) {
  return getAllActionPacks({ includeDeleted: Boolean(options.includeDeleted) }).find((pack) => pack.id === id);
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

function getDeletedActionPacks() {
  return loadActionPacks().filter((pack) => isPackDeleted(pack));
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
let currentPackVersions = [];
let reportExportOptions = [];
let currentTenantId = "";
let configLocked = false;
let keychainAvailable = false;
let tenantInfoLoading = false;
let sshTargets = [];
const runnerTargetSelections = {};
let selectedPackId = null;
const BULK_CONCURRENCY_DEFAULT = 3;
const BULK_CONCURRENCY_KEY = "bulkConcurrency";
const bulkRetryButtons = {};
const bulkFailureCache = {};
const lastStructuredLists = {};
const auditState = { items: [], query: {} };
let incidentFixPackId = null;
let incidentFixPackParams = null;
let lastIncidentContext = null;

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
    label.textContent = step.label || (step.type === "note" ? "Note" : activityLabel(step.service, step.action));
    const key = document.createElement("span");
    key.textContent = step.type === "note" ? "note" : `${step.service}.${step.action}`;
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
  renderPackBuilderHowItRuns();
}

function renderPackVersionHistory() {
  if (!packVersionSelect) return;
  packVersionSelect.innerHTML = "";
  if (!currentPackVersions.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No versions yet";
    packVersionSelect.appendChild(option);
    packVersionSelect.disabled = true;
    if (packVersionRestoreButton) packVersionRestoreButton.disabled = true;
    return;
  }
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a version";
  packVersionSelect.appendChild(placeholder);
  currentPackVersions.forEach((version) => {
    const option = document.createElement("option");
    option.value = version.version_id;
    const stamp = version.saved_at ? new Date(version.saved_at).toLocaleString() : "Unknown time";
    option.textContent = `${stamp} · ${version.name}`;
    packVersionSelect.appendChild(option);
  });
  packVersionSelect.disabled = false;
  if (packVersionRestoreButton) packVersionRestoreButton.disabled = false;
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
  currentPackVersions = [];
  if (packNameInput) packNameInput.value = "";
  if (packDescriptionInput) packDescriptionInput.value = "";
  if (packDefaultsInput) packDefaultsInput.value = "";
  if (packScopeSelect) packScopeSelect.value = "global";
  renderPackSteps();
  renderPackVersionHistory();
  renderPackBuilderHowItRuns();
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
  currentPackVersions = useClone ? [] : (pack.versions || []).slice();
  if (packNameInput) packNameInput.value = useClone ? `${pack.name} (Copy)` : pack.name;
  if (packDescriptionInput) packDescriptionInput.value = pack.description || "";
  if (packDefaultsInput) {
    packDefaultsInput.value = pack.defaults ? JSON.stringify(pack.defaults, null, 2) : "";
  }
  if (packScopeSelect) {
    packScopeSelect.value = pack.tenant_id ? "tenant" : "global";
  }
  renderPackSteps();
  renderPackVersionHistory();
  renderPackBuilderHowItRuns();
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

function collectPackDefaults(options = {}) {
  if (!packDefaultsInput) return undefined;
  const raw = packDefaultsInput.value.trim();
  if (!raw) return undefined;
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch (err) {
    if (!options.silent) {
      showToast("Defaults JSON is invalid");
    }
    return null;
  }
  return null;
}

function savePackFromBuilder(options = {}) {
  const asCopy = Boolean(options.asCopy);
  const name = packNameInput?.value.trim() || "";
  if (!name) {
    showToast("Pack name is required");
    return;
  }
  if (!currentPackSteps.length) {
    showToast("Add at least one step");
    return;
  }
  const defaults = collectPackDefaults({ silent: true });
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
  const current = currentPackId ? existing.find((pack) => pack.id === currentPackId) : null;
  let id = currentPackId || idBase;
  if (asCopy || !currentPackId || currentPackBuiltin) {
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
  const now = Date.now();
  entry.created_at = current?.created_at || now;
  entry.updated_at = now;
  entry.deleted_at = current?.deleted_at || null;
  entry.versions = Array.isArray(current?.versions) ? current.versions.slice() : [];
  if (current && !asCopy) {
    const snapshot = buildPackVersionSnapshot(current);
    if (snapshot) {
      entry.versions.unshift(snapshot);
      entry.versions = entry.versions.slice(0, ACTION_PACK_VERSION_LIMIT);
    }
  } else {
    entry.versions = [];
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
  currentPackVersions = entry.versions || [];
  setActionPackPageIndex(0);
  renderActionPacks();
  renderDeletedActionPacks();
  renderPackVersionHistory();
  renderPackBuilderHowItRuns();
  const actionLabel = asCopy ? "copied" : idx >= 0 ? "updated" : "created";
  logActionPackAudit(actionLabel, entry, { source_id: current?.id || null });
  showToast(asCopy ? "Action pack copied" : "Action pack saved");
}

async function deletePackFromBuilder() {
  if (!currentPackId) {
    showToast("Select a custom pack to delete");
    return;
  }
  if (currentPackBuiltin) {
    showToast("Built-in packs cannot be deleted");
    return;
  }
  const pack = getActionPackById(currentPackId, { includeDeleted: true });
  if (!pack) {
    showToast("Pack not found");
    return;
  }
  const confirmed = await confirmPackDelete(pack);
  if (!confirmed) return;
  const ok = softDeleteActionPack(pack.id);
  if (!ok) {
    showToast("Delete failed");
    return;
  }
  resetPackBuilder();
  renderActionPacks();
  renderDeletedActionPacks();
  showToast("Action pack moved to trash");
}

async function confirmPackDelete(pack) {
  const name = pack?.name || "";
  const response = await promptModal({
    title: "Delete action pack",
    subtitle: `Type the pack name to confirm.`,
    label: "Pack name",
    placeholder: name,
    confirmLabel: "Delete pack",
    cancelLabel: "Cancel",
    required: true,
    hint: `Type "${name}" to confirm deletion.`,
  });
  if (!response) return false;
  return response.trim() === name;
}

function softDeleteActionPack(packId) {
  const existing = loadActionPacks();
  const idx = existing.findIndex((pack) => pack.id === packId);
  if (idx < 0) return false;
  const pack = existing[idx];
  existing[idx] = {
    ...pack,
    deleted_at: Date.now(),
    updated_at: Date.now(),
  };
  saveActionPacks(existing);
  const favorites = loadActionPackFavorites();
  if (favorites.has(packId)) {
    favorites.delete(packId);
    saveActionPackFavorites(favorites);
  }
  logActionPackAudit("deleted", pack);
  return true;
}

function restoreDeletedPack(packId) {
  const existing = loadActionPacks();
  const idx = existing.findIndex((pack) => pack.id === packId);
  if (idx < 0) return false;
  const pack = existing[idx];
  existing[idx] = { ...pack, deleted_at: null, updated_at: Date.now() };
  saveActionPacks(existing);
  logActionPackAudit("restored", pack);
  return true;
}

function permanentlyDeletePack(packId) {
  const existing = loadActionPacks();
  const pack = existing.find((entry) => entry.id === packId);
  saveActionPacks(existing.filter((entry) => entry.id !== packId));
  logActionPackAudit("permanently deleted", pack || { id: packId, name: packId });
  return true;
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

async function deletePresetFromBuilder() {
  if (!currentPresetId) {
    showToast("Select a custom preset to delete");
    return;
  }
  const confirmDelete = await confirmModal({
    title: "Delete report preset",
    message: "Delete this report preset?",
    confirmLabel: "Delete preset",
  });
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
      renderDeletedActionPacks();
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

function downloadTextFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType || "text/plain" });
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

async function buildParamsWithDefaults(service, action, defaults = {}) {
  const fields = ACTIONS_UI?.[service]?.[action]?.fields || [];
  const params = { ...defaults };
  let cancelled = false;
  for (const field of fields) {
    if (params[field.key] !== undefined) continue;
    if (field.type === "checkbox") {
      const confirmValue = await confirmModal({
        title: field.label,
        message: `${field.label}?`,
        confirmLabel: "Yes",
        cancelLabel: "No",
      });
      if (confirmValue) params[field.key] = true;
      continue;
    }
    const value = await promptModal({
      title: field.label,
      label: field.label,
      confirmLabel: "Add",
      cancelLabel: "Cancel",
    });
    if (value === null) {
      cancelled = true;
      break;
    }
    if (value.trim() !== "") {
      params[field.key] = value.trim();
    }
  }
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
      const filled = await buildParamsWithDefaults(step.service, step.action, params);
      if (filled === null) {
        showToast("Preset cancelled");
        return;
      }
      params = filled;
    }
    const result = await runAction(step.service, step.action, params);
    if (!result?.ok) {
      const proceed = await confirmModal({
        title: "Preset step failed",
        message: `Preset step failed: ${label}. Continue?`,
        confirmLabel: "Continue",
        cancelLabel: "Stop",
      });
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

function exportTopologyReportJson() {
  const payload = getExportPayload("topology-report");
  if (!payload) {
    showToast("No report data to export");
    return;
  }
  downloadJson(payload, "topology-report.json");
}

function exportTopologyReportCsv() {
  const payload = getExportPayload("topology-report");
  if (!payload) {
    showToast("No report data to export");
    return;
  }
  let rows = Array.isArray(payload?.items) ? payload.items : null;
  if (!rows && Array.isArray(payload)) {
    rows = payload;
  }
  if (!rows || !rows.length) {
    showToast("No tabular data to export");
    return;
  }
  const content = toCsv(rows);
  downloadTextFile(content, "topology-report.csv", "text/csv");
}

function renderActionPacks() {
  const container = document.getElementById("action-pack-list");
  if (!container) return;
  container.innerHTML = "";

  const filter = getActionPackFilter();
  const favorites = loadActionPackFavorites();
  const packs = getAllActionPacks({ includeDeleted: filter === "deleted" }).filter((pack) => {
    const tenantId = pack.tenant_id;
    if (filter === "favorites") {
      return favorites.has(pack.id);
    }
    if (filter === "deleted") {
      return isPackDeleted(pack);
    }
    if (filter === "global") {
      return !tenantId;
    }
    if (filter === "all") {
      return !isPackDeleted(pack);
    }
    if (isPackDeleted(pack)) return false;
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
    empty.textContent =
      filter === "deleted"
        ? "No deleted action packs."
        : "No action packs available. Create your first pack to get started.";
    if (filter !== "deleted") {
      const button = document.createElement("button");
      button.type = "button";
      button.classList.add("ghost", "small");
      button.textContent = "Create your first pack";
      button.addEventListener("click", () => {
        const builder = document.getElementById("action-pack-builder");
        if (builder) builder.open = true;
        packNameInput?.focus();
      });
      const wrap = document.createElement("div");
      wrap.appendChild(button);
      empty.appendChild(wrap);
    }
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
      if (step.type === "note") {
        badge.classList.add("note");
        badge.textContent = "Note";
      } else if (step.rollback) {
        badge.classList.add("rollback");
        badge.textContent = "Rollback";
      } else if (step.optional) {
        badge.classList.add("ps");
        badge.textContent = "Optional";
      } else {
        badge.classList.add("graph");
        badge.textContent = "Step";
      }
      const label = document.createElement("span");
      label.textContent = `${index + 1}. ${step.label || activityLabel(step.service, step.action)}`;
      row.appendChild(badge);
      row.appendChild(label);
      steps.appendChild(row);
    });
    card.appendChild(steps);

    if (filter === "deleted") {
      const deletedMeta = document.createElement("div");
      deletedMeta.classList.add("pack-summary");
      deletedMeta.textContent = pack.deleted_at
        ? `Deleted ${new Date(pack.deleted_at).toLocaleString()}`
        : "Deleted";
      card.appendChild(deletedMeta);
      const actions = document.createElement("div");
      actions.classList.add("action-pack-actions");
      const restore = document.createElement("button");
      restore.type = "button";
      restore.classList.add("ghost", "small");
      restore.textContent = "Restore";
      restore.addEventListener("click", () => {
        restoreDeletedPack(pack.id);
        renderActionPacks();
        renderDeletedActionPacks();
        showToast("Pack restored");
      });
      const destroy = document.createElement("button");
      destroy.type = "button";
      destroy.classList.add("ghost", "small");
      destroy.textContent = "Delete permanently";
      destroy.addEventListener("click", async () => {
        const confirmDelete = await confirmModal({
          title: "Delete permanently",
          message: `Permanently delete "${pack.name}"? This cannot be undone.`,
          confirmLabel: "Delete",
          cancelLabel: "Cancel",
          danger: true,
        });
        if (!confirmDelete) return;
        permanentlyDeletePack(pack.id);
        renderActionPacks();
        renderDeletedActionPacks();
        showToast("Pack deleted permanently");
      });
      actions.appendChild(restore);
      actions.appendChild(destroy);
      card.appendChild(actions);
      container.appendChild(card);
      return;
    }

    const summary = document.createElement("div");
    summary.classList.add("pack-summary");
    const counts = summarizePackSteps(pack);
    const packRisk = formatRiskLabel(getPackRisk(pack));
    const lastRun = getLastActionPackRun(pack.id);
    const lastRunLabel = lastRun ? `${lastRun.status || "unknown"}` : "Never run";
    summary.textContent = `${counts.total} steps · Graph(${counts.graph}) · PowerShell(${counts.powershell}) · Risk: ${packRisk} · Last run: ${lastRunLabel}`;
    card.appendChild(summary);

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
    edit.textContent = pack.builtin ? "Clone" : "Edit steps";
    edit.addEventListener("click", () => setPackBuilder(pack, { clone: pack.builtin }));
    const configure = document.createElement("button");
    configure.type = "button";
    configure.classList.add("ghost", "small");
    configure.textContent = "Configure";
    configure.addEventListener("click", () => selectActionPack(pack, { scroll: true }));
    const run = document.createElement("button");
    run.type = "button";
    run.classList.add("primary", "small", "action-pack-run");
    run.textContent = "Run pack";
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

function renderDeletedActionPacks() {
  if (!actionPackDeletedList) return;
  actionPackDeletedList.innerHTML = "";
  const deleted = getDeletedActionPacks();
  if (!deleted.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No deleted packs.";
    actionPackDeletedList.appendChild(empty);
    return;
  }
  deleted.forEach((pack) => {
    const row = document.createElement("div");
    row.classList.add("deleted-pack-row");
    const title = document.createElement("div");
    title.classList.add("deleted-pack-title");
    title.textContent = pack.name || pack.id;
    const meta = document.createElement("div");
    meta.classList.add("deleted-pack-meta");
    meta.textContent = pack.deleted_at ? `Deleted ${new Date(pack.deleted_at).toLocaleString()}` : "Deleted";
    const actions = document.createElement("div");
    actions.classList.add("deleted-pack-actions");
    const restore = document.createElement("button");
    restore.type = "button";
    restore.classList.add("ghost", "small");
    restore.textContent = "Restore";
    restore.addEventListener("click", () => {
      restoreDeletedPack(pack.id);
      renderActionPacks();
      renderDeletedActionPacks();
      showToast("Pack restored");
    });
    const destroy = document.createElement("button");
    destroy.type = "button";
    destroy.classList.add("ghost", "small");
    destroy.textContent = "Delete permanently";
    destroy.addEventListener("click", async () => {
      const confirmDelete = await confirmModal({
        title: "Delete permanently",
        message: `Permanently delete "${pack.name}"? This cannot be undone.`,
        confirmLabel: "Delete",
        cancelLabel: "Cancel",
        danger: true,
      });
      if (!confirmDelete) return;
      permanentlyDeletePack(pack.id);
      renderActionPacks();
      renderDeletedActionPacks();
      showToast("Pack deleted permanently");
    });
    actions.appendChild(restore);
    actions.appendChild(destroy);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    actionPackDeletedList.appendChild(row);
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
    const duration = entry.duration_ms ? ` · ${formatDuration(entry.duration_ms)}` : "";
    const failed = entry.failed_step ? ` · Failed: ${entry.failed_step}` : "";
    meta.textContent = `${new Date(entry.timestamp).toLocaleString()} · ${entry.status}${
      entry.dryRun ? " · dry-run" : ""
    }${duration}${failed}`;
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const rerun = document.createElement("button");
    rerun.type = "button";
    rerun.classList.add("ghost", "small");
    rerun.textContent = "Rerun";
    rerun.addEventListener("click", () => {
      const pack = getActionPackById(entry.packId);
      if (!pack) {
        showToast("Pack not found or deleted");
        return;
      }
      selectActionPack(pack, { scroll: true });
      setPackParams(pack.id, {
        stepParams: entry.stepParams || {},
        includeSteps: entry.includeSteps || {},
        dryRun: Boolean(entry.dryRun),
      });
      renderActionPackRunner(pack);
      runActionPack(pack, {
        stepParams: entry.stepParams || {},
        includeSteps: entry.includeSteps || {},
        dryRun: Boolean(entry.dryRun),
      });
    });
    const view = document.createElement("button");
    view.type = "button";
    view.classList.add("ghost", "small");
    view.textContent = "View output";
    view.addEventListener("click", () => {
      if (entry.result_summary) {
        showModal("Action pack run output", entry.result_summary, "actionpacks");
      } else {
        showToast("No output stored for this run");
      }
    });
    actions.appendChild(rerun);
    actions.appendChild(view);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    actionPackHistoryList.appendChild(row);
  });
}

function getLastActionPackRun(packId) {
  const items = loadActionPackHistory();
  return items.find((entry) => entry.packId === packId) || null;
}

function formatDuration(ms) {
  if (!Number.isFinite(ms) || ms <= 0) return "";
  const totalSeconds = Math.round(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

function summarizePackSteps(pack) {
  let graph = 0;
  let powershell = 0;
  let notes = 0;
  pack.steps.forEach((step) => {
    if (step.type === "note") {
      notes += 1;
      return;
    }
    const meta = ACTIONS_UI?.[step.service]?.[step.action];
    if (meta?.mode === "powershell") {
      powershell += 1;
    } else {
      graph += 1;
    }
  });
  const total = graph + powershell;
  return { total, graph, powershell, notes };
}

function getPackRisk(pack) {
  if (!pack || !Array.isArray(pack.steps)) return "safe";
  let level = "safe";
  const score = { safe: 0, caution: 1, danger: 2 };
  pack.steps.forEach((step) => {
    if (!step || step.type === "note") return;
    const risk = getActionRisk(step.service, step.action);
    if (score[risk] > score[level]) level = risk;
  });
  return level;
}

function getMissingInputsForStep(step, params) {
  const meta = ACTIONS_UI?.[step.service]?.[step.action];
  const fields = meta?.fields || [];
  return fields
    .filter((field) => field.type !== "checkbox" && field.required !== false)
    .filter((field) => {
      const value = params?.[field.key];
      return value === undefined || value === null || value === "";
    })
    .map((field) => field.label || field.key);
}

function buildActionPackPlan(pack, params) {
  const stepParams = params?.stepParams || {};
  const includeSteps = params?.includeSteps || {};
  const dryRun = params?.dryRun || false;
  const plan = [];
  const packContext = {};
  pack.steps.forEach((step) => {
    if (step.type === "note") {
      plan.push({
        type: "note",
        label: step.label,
        note: step.note,
        phase: step.phase || "",
        included: true,
        skipped: false,
      });
      return;
    }
    const stepKey = `${step.service}.${step.action}`;
    const defaults = getActionPackStepDefaults(pack, step) || {};
    const override = stepParams[stepKey] || {};
    const paramsResolved = applyPackAutoParams(
      step,
      { ...defaults, ...(step.params || {}), ...(override?.params || {}), ...override },
      packContext
    );
    const include = shouldIncludePackStep(step, includeSteps);
    const skipped = !include || (dryRun && !step.safe);
    const reason = !include
      ? "Excluded"
      : dryRun && !step.safe
        ? "Skipped (dry-run)"
        : "";
    const missing = getMissingInputsForStep(step, paramsResolved);
    plan.push({
      type: "step",
      stepKey,
      label: step.label || activityLabel(step.service, step.action),
      service: step.service,
      action: step.action,
      mode: ACTIONS_UI?.[step.service]?.[step.action]?.mode || "graph",
      included: include,
      skipped,
      reason,
      params: paramsResolved,
      missing,
      safe: Boolean(step.safe),
      optional: Boolean(step.optional),
      phase: step.phase || "",
    });
  });
  return plan;
}

function renderActionPackHowItRuns(pack, container, params = null) {
  if (!container) return;
  container.innerHTML = "";
  if (!pack) return;
  const header = document.createElement("div");
  header.classList.add("pack-how-title");
  header.textContent = "How it runs";
  container.appendChild(header);

  const summary = document.createElement("div");
  summary.classList.add("pack-how-summary");
  summary.textContent =
    "Action packs run steps sequentially. Each step calls Graph or PowerShell with inputs merged from defaults and the form. Failures prompt you to continue or stop.";
  container.appendChild(summary);

  const flow = document.createElement("ul");
  flow.classList.add("pack-how-flow");
  ["Inputs → step params → outputs", "Sequential execution (no parallel steps)", "Dry-run skips non-safe steps"].forEach(
    (text) => {
      const li = document.createElement("li");
      li.textContent = text;
      flow.appendChild(li);
    }
  );
  container.appendChild(flow);

  const list = document.createElement("div");
  list.classList.add("pack-how-steps");
  const plan = params ? buildActionPackPlan(pack, params) : buildActionPackPlan(pack, getPackParams(pack.id));
  plan.forEach((item) => {
    if (item.type === "note") {
      const row = document.createElement("div");
      row.classList.add("pack-how-step", "note");
      row.textContent = item.label;
      list.appendChild(row);
      return;
    }
    const row = document.createElement("div");
    row.classList.add("pack-how-step");
    const title = document.createElement("div");
    title.classList.add("pack-how-step-title");
    title.textContent = `${item.label}`;
    const meta = document.createElement("div");
    meta.classList.add("pack-how-step-meta");
    meta.textContent = `${item.service}.${item.action} · ${item.mode}`;
    if (item.phase) {
      const phase = document.createElement("span");
      phase.classList.add("pack-step-phase");
      phase.textContent = item.phase;
      meta.appendChild(phase);
    }
    row.appendChild(title);
    row.appendChild(meta);
    const fieldMeta = ACTIONS_UI?.[item.service]?.[item.action];
    if (fieldMeta?.fields?.length) {
      const inputs = document.createElement("div");
      inputs.classList.add("pack-how-inputs");
      inputs.textContent = `Inputs: ${fieldMeta.fields.map((field) => field.label || field.key).join(", ")}`;
      row.appendChild(inputs);
    }
    list.appendChild(row);
  });
  container.appendChild(list);
}

function renderActionPackLastRun(pack, container) {
  if (!container) return;
  container.innerHTML = "";
  if (!pack) return;
  const entry = getLastActionPackRun(pack.id);
  const title = document.createElement("div");
  title.classList.add("pack-last-title");
  title.textContent = "Last run";
  container.appendChild(title);
  if (!entry) {
    const note = document.createElement("div");
    note.classList.add("note");
    note.textContent = "No runs yet.";
    container.appendChild(note);
    return;
  }
  const meta = document.createElement("div");
  meta.classList.add("pack-last-meta");
  const timeText = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "Unknown time";
  const durationText = entry.duration_ms ? formatDuration(entry.duration_ms) : "";
  const failedStep = entry.failed_step ? ` · Failed: ${entry.failed_step}` : "";
  const statusLabel = entry.status || "unknown";
  meta.textContent = `${timeText} · ${statusLabel}${entry.dryRun ? " · dry-run" : ""}${durationText ? ` · ${durationText}` : ""}${failedStep}`;
  container.appendChild(meta);
  const link = document.createElement("button");
  link.type = "button";
  link.classList.add("ghost", "small");
  link.textContent = "View in history";
  link.addEventListener("click", () => {
    const historyPanel = document.getElementById("action-pack-history-panel");
    if (historyPanel && historyPanel.tagName === "DETAILS") {
      historyPanel.open = true;
    }
    const history = document.getElementById("action-pack-history");
    if (history) history.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  container.appendChild(link);
  if (entry.result_summary) {
    const view = document.createElement("button");
    view.type = "button";
    view.classList.add("ghost", "small");
    view.textContent = "View output";
    view.addEventListener("click", () => {
      showModal("Action pack run output", entry.result_summary, "actionpacks");
    });
    container.appendChild(view);
  }
}

function renderActionPackPlan(pack, params, container, { mode } = {}) {
  if (!container) return;
  container.innerHTML = "";
  if (!pack) return;
  const plan = buildActionPackPlan(pack, params);
  const heading = document.createElement("div");
  heading.classList.add("pack-plan-title");
  heading.textContent = mode === "validate" ? "Input validation" : "Preview execution plan";
  container.appendChild(heading);
  const list = document.createElement("div");
  list.classList.add("pack-plan-list");
  let missingCount = 0;
  plan.forEach((item) => {
    if (item.type !== "step") return;
    const row = document.createElement("div");
    row.classList.add("pack-plan-row");
    const title = document.createElement("div");
    title.classList.add("pack-plan-title-row");
    title.textContent = `${item.label} (${item.service}.${item.action})`;
    const meta = document.createElement("div");
    meta.classList.add("pack-plan-meta");
    meta.textContent = item.skipped ? `Skipped · ${item.reason}` : item.included ? "Included" : "Excluded";
    row.appendChild(title);
    row.appendChild(meta);
    if (item.missing.length) {
      missingCount += item.missing.length;
      const missing = document.createElement("div");
      missing.classList.add("pack-plan-missing");
      missing.textContent = `Missing inputs: ${item.missing.join(", ")}`;
      row.appendChild(missing);
    }
    if (mode !== "validate" && item.included && !item.skipped) {
      const paramsBlock = document.createElement("pre");
      paramsBlock.classList.add("pack-plan-params");
      paramsBlock.textContent = JSON.stringify(item.params || {}, null, 2);
      row.appendChild(paramsBlock);
    }
    list.appendChild(row);
  });
  if (!plan.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No steps to preview.";
    list.appendChild(empty);
  }
  if (mode === "validate") {
    const summary = document.createElement("div");
    summary.classList.add("pack-plan-summary");
    summary.textContent = missingCount
      ? `Missing ${missingCount} required input${missingCount === 1 ? "" : "s"}.`
      : "All required inputs are present.";
    container.appendChild(summary);
  }
  container.appendChild(list);
}

function renderPackBuilderHowItRuns() {
  const builderPanel = document.getElementById("pack-how-it-runs");
  if (!builderPanel) return;
  const name = packNameInput?.value.trim() || "Untitled pack";
  const description = packDescriptionInput?.value.trim() || "";
  const defaults = collectPackDefaults();
  const tempPack = normalizeActionPack({
    id: currentPackId || `builder-${Date.now()}`,
    name,
    description,
    steps: currentPackSteps,
    defaults: defaults && defaults !== null ? defaults : undefined,
    tenant_id: packScopeSelect?.value === "tenant" ? currentTenantId : undefined,
    builtin: false,
  });
  if (!tempPack) {
    builderPanel.innerHTML = "";
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "Add at least one step to preview how this pack runs.";
    builderPanel.appendChild(empty);
    return;
  }
  renderActionPackHowItRuns(tempPack, builderPanel, {
    stepParams: {},
    includeSteps: {},
    dryRun: false,
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
    if (actionPackDryRunToggle) actionPackDryRunToggle.checked = false;
    if (actionPackDryRunToggle) actionPackDryRunToggle.disabled = true;
    if (actionPackPreviewButton) actionPackPreviewButton.disabled = true;
    if (actionPackValidateButton) actionPackValidateButton.disabled = true;
    if (actionPackHowPanel) actionPackHowPanel.innerHTML = "";
    if (actionPackPlanPanel) actionPackPlanPanel.innerHTML = "";
    if (actionPackLastRun) actionPackLastRun.innerHTML = "";
    return;
  }
  if (actionPackRunnerTitle) {
    actionPackRunnerTitle.textContent = `${pack.name} · ${pack.tenant_id ? "Tenant" : "Global"}`;
  }
  if (actionPackPlanPanel) actionPackPlanPanel.innerHTML = "";
  const saved = getPackParams(pack.id);
  if (actionPackDryRunToggle) {
    actionPackDryRunToggle.checked = Boolean(saved.dryRun);
    actionPackDryRunToggle.disabled = false;
  }
  if (actionPackPreviewButton) actionPackPreviewButton.disabled = false;
  if (actionPackValidateButton) actionPackValidateButton.disabled = false;
  pack.steps.forEach((step) => {
    if (step.type === "note") {
      const noteWrap = document.createElement("div");
      noteWrap.classList.add("pack-step", "pack-step-note");
      const header = document.createElement("div");
      header.classList.add("pack-step-header");
      const title = document.createElement("div");
      title.classList.add("pack-step-title");
      title.textContent = step.label || "Note";
      const metaWrap = document.createElement("div");
      metaWrap.classList.add("pack-step-meta");
      if (step.phase) {
        const phase = document.createElement("span");
        phase.classList.add("pack-step-phase");
        phase.textContent = step.phase;
        metaWrap.appendChild(phase);
      }
      const badge = document.createElement("span");
      badge.classList.add("badge", "note");
      badge.textContent = "Note";
      metaWrap.appendChild(badge);
      header.appendChild(title);
      header.appendChild(metaWrap);
      noteWrap.appendChild(header);
      if (step.note) {
        const body = document.createElement("div");
        body.classList.add("note");
        body.textContent = step.note;
        noteWrap.appendChild(body);
      }
      actionPackRunnerSteps.appendChild(noteWrap);
      return;
    }
    const meta = ACTIONS_UI?.[step.service]?.[step.action];
    const stepKey = `${step.service}.${step.action}`;
    const defaults = getActionPackStepDefaults(pack, step) || {};
    const baseParams = { ...defaults, ...(step.params || {}), ...(saved.stepParams?.[stepKey] || {}) };
    const includeDefault =
      saved.includeSteps?.[stepKey] !== undefined
        ? saved.includeSteps?.[stepKey]
        : step.defaultInclude !== false;
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
    if (step.phase) {
      const phase = document.createElement("span");
      phase.classList.add("pack-step-phase");
      phase.textContent = step.phase;
      metaWrap.appendChild(phase);
    }
    if (step.safe) {
      const safeBadge = document.createElement("span");
      safeBadge.classList.add("badge", "graph");
      safeBadge.textContent = "Read-only";
      metaWrap.appendChild(safeBadge);
    }
    if (step.rollback) {
      const rollbackBadge = document.createElement("span");
      rollbackBadge.classList.add("badge", "rollback");
      rollbackBadge.textContent = "Rollback";
      metaWrap.appendChild(rollbackBadge);
    }
    if (step.optional) {
      const includeLabel = document.createElement("label");
      includeLabel.classList.add("field", "checkbox");
      const includeInput = document.createElement("input");
      includeInput.type = "checkbox";
      includeInput.classList.add("pack-step-include");
      includeInput.checked = includeDefault !== false;
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
  renderActionPackHowItRuns(pack, actionPackHowPanel, saved);
  renderActionPackLastRun(pack, actionPackLastRun);
}

function selectActionPack(pack, options = {}) {
  if (!pack) return;
  if (isPackDeleted(pack)) {
    showToast("Pack is deleted. Restore it to run.");
    return;
  }
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
  const dryRun = actionPackDryRunToggle ? actionPackDryRunToggle.checked : false;
  if (!actionPackRunnerSteps) return { stepParams, includeSteps, dryRun };
  actionPackRunnerSteps.querySelectorAll(".pack-step").forEach((stepEl) => {
    const stepKey = stepEl.dataset.stepKey;
    if (!stepKey) return;
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
  return { stepParams, includeSteps, dryRun };
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
  const items = getReportHistoryItems();
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
    const target = entry?.snapshot?.target || entry?.snapshot?.meta?.target;
    const timestamp = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "Unknown time";
    meta.textContent = target ? `${timestamp} · ${target}` : `${timestamp}`;
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

function setDiffLoading(metaEl, rawEl, triageEl, message = "Loading diff...") {
  if (metaEl) metaEl.textContent = message;
  if (rawEl) rawEl.textContent = "Loading...";
  if (triageEl) {
    triageEl.innerHTML = "";
    const note = document.createElement("div");
    note.classList.add("note");
    note.textContent = "Loading triage...";
    triageEl.appendChild(note);
  }
}

function cacheSnapshotDiff(canonicalId, idA, idB, diff) {
  if (!canonicalId) return;
  snapshotDiffCache.set(canonicalId, {
    a: idA,
    b: idB,
    diff,
    captured_at: Date.now(),
  });
}

function getCachedSnapshotDiff(canonicalId, idA, idB) {
  if (!canonicalId) return null;
  const cached = snapshotDiffCache.get(canonicalId);
  if (!cached) return null;
  if (cached.a === idA && cached.b === idB) return cached.diff;
  return null;
}

function cacheReportDiff(idA, idB, diff) {
  if (!idA || !idB) return;
  reportDiffCache.set(`${idA}:${idB}`, { diff, captured_at: Date.now() });
}

function getCachedReportDiff(idA, idB) {
  if (!idA || !idB) return null;
  return reportDiffCache.get(`${idA}:${idB}`)?.diff || null;
}

function buildDiffCopyText(triage) {
  if (!triage) return "";
  const lines = [];
  lines.push(triage.headline || "Snapshot Comparison Summary");
  lines.push(
    `Security-impacting: ${triage.counts?.security ?? 0}, ` +
      `Config drift: ${triage.counts?.config ?? 0}, ` +
      `Metadata: ${triage.counts?.metadata ?? 0}`
  );
  if (triage.coverage?.percent !== null && triage.coverage?.percent !== undefined) {
    lines.push(`Coverage: ${triage.coverage.percent}% (${triage.coverage.label})`);
  }
  if (triage.limitations?.length) {
    lines.push(`Coverage limitations: ${triage.limitations.join("; ")}`);
  }
  if (triage.summaryText) {
    lines.push(triage.summaryText);
  }
  return lines.join("\n");
}

function renderDiffTriage(container, diff) {
  if (!container) return;
  container.innerHTML = "";
  if (!diff) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No diff data available.";
    container.appendChild(empty);
    return;
  }
  const triageEngine = window.GraphAdminTriage;
  if (!triageEngine || !triageEngine.buildTriage) {
    const fallback = document.createElement("pre");
    fallback.classList.add("dataset-content");
    fallback.textContent = formatDiffSummary(diff);
    container.appendChild(fallback);
    return;
  }
  const triage = triageEngine.buildTriage(diff, diffImpactOverrides);
  container.dataset.copy = buildDiffCopyText(triage);

  const meaningfulOnly = container.dataset.meaningfulOnly === "true";

  const summaryCard = document.createElement("div");
  summaryCard.classList.add("diff-summary-card");

  const summaryHeader = document.createElement("div");
  summaryHeader.classList.add("diff-summary-header");
  const headline = document.createElement("div");
  headline.classList.add("diff-summary-title");
  headline.textContent = triage.headline || "Snapshot Comparison Summary";
  summaryHeader.appendChild(headline);
  summaryCard.appendChild(summaryHeader);

  const badges = document.createElement("div");
  badges.classList.add("diff-badges");
  const securityBadge = document.createElement("span");
  securityBadge.classList.add("diff-badge", "security");
  securityBadge.textContent = `Security: ${triage.counts.security}`;
  const configBadge = document.createElement("span");
  configBadge.classList.add("diff-badge", "config");
  configBadge.textContent = `Config: ${triage.counts.config}`;
  const metaBadge = document.createElement("span");
  metaBadge.classList.add("diff-badge", "meta");
  metaBadge.textContent = `Metadata: ${triage.counts.metadata}`;
  badges.appendChild(securityBadge);
  badges.appendChild(configBadge);
  badges.appendChild(metaBadge);
  summaryCard.appendChild(badges);

  const filterRow = document.createElement("label");
  filterRow.classList.add("diff-filter");
  const filterToggle = document.createElement("input");
  filterToggle.type = "checkbox";
  filterToggle.checked = meaningfulOnly;
  const filterText = document.createElement("span");
  filterText.textContent = "Show only meaningful changes";
  filterRow.appendChild(filterToggle);
  filterRow.appendChild(filterText);
  filterToggle.addEventListener("change", () => {
    container.dataset.meaningfulOnly = filterToggle.checked ? "true" : "false";
    renderDiffTriage(container, diff);
  });
  summaryCard.appendChild(filterRow);

  const coverage = document.createElement("div");
  coverage.classList.add("diff-coverage");
  const coverageText = document.createElement("div");
  if (triage.coverage?.percent !== null && triage.coverage?.percent !== undefined) {
    coverageText.textContent = `Coverage: ${triage.coverage.percent}% · ${triage.coverage.label} confidence`;
  } else {
    coverageText.textContent = "Coverage: Unknown";
  }
  coverage.appendChild(coverageText);
  summaryCard.appendChild(coverage);

  if (triage.limitations && triage.limitations.length) {
    const limitations = document.createElement("div");
    limitations.classList.add("diff-limitations");
    const title = document.createElement("div");
    title.textContent = "Coverage limitations";
    const list = document.createElement("ul");
    triage.limitations.slice(0, 6).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    });
    limitations.appendChild(title);
    limitations.appendChild(list);
    summaryCard.appendChild(limitations);
  }

  const summaryText = document.createElement("div");
  summaryText.classList.add("diff-summary-text");
  summaryText.textContent = triage.summaryText || "";
  summaryCard.appendChild(summaryText);
  container.appendChild(summaryCard);

  const groups = [
    { key: "security", label: "🔴 Security-impacting changes" },
    { key: "config", label: "🟡 Configuration drift" },
    { key: "metadata", label: "🔵 Administrative / metadata changes" },
  ];
  groups.forEach((group) => {
    if (meaningfulOnly && group.key === "metadata") {
      return;
    }
    const items = triage.groups[group.key] || [];
    const details = document.createElement("details");
    details.classList.add("diff-group");
    if (group.key !== "metadata" && items.length) {
      details.open = true;
    }
    const summary = document.createElement("summary");
    const title = document.createElement("div");
    title.classList.add("diff-group-title");
    title.textContent = group.label;
    const confidence = triage.confidenceByBucket?.[group.key];
    if (confidence) {
      const badge = document.createElement("span");
      badge.classList.add("confidence", confidence.key);
      badge.textContent = `${confidence.label} confidence`;
      title.appendChild(badge);
    }
    const count = document.createElement("span");
    count.classList.add("diff-group-count");
    count.textContent = items.length;
    summary.appendChild(title);
    summary.appendChild(count);
    details.appendChild(summary);
    const list = document.createElement("div");
    list.classList.add("diff-list");
    if (!items.length) {
      const empty = document.createElement("div");
      empty.classList.add("note");
      empty.textContent = "No changes detected.";
      list.appendChild(empty);
    } else {
      items.slice(0, 50).forEach((item) => {
        const row = document.createElement("div");
        const titleRow = document.createElement("div");
        titleRow.classList.add("diff-item-title");
        titleRow.textContent = item.summary;
        const meta = document.createElement("div");
        meta.classList.add("diff-item-meta");
        meta.textContent = item.path || "";
        row.appendChild(titleRow);
        row.appendChild(meta);
        list.appendChild(row);
      });
    }
    details.appendChild(list);
    container.appendChild(details);
  });
}

function initDiffTabs(prefix) {
  const tabsWrap = document.querySelector(`[data-diff-tabs="${prefix}"]`);
  if (!tabsWrap) return;
  const tabs = tabsWrap.querySelectorAll(".tab");
  const triage = document.getElementById(`${prefix}-diff-triage`);
  const raw = document.getElementById(`${prefix}-diff-output`);
  const setView = (view) => {
    tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.diffView === view));
    if (triage) triage.style.display = view === "triage" ? "grid" : "none";
    if (raw) raw.style.display = view === "raw" ? "block" : "none";
  };
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => setView(tab.dataset.diffView));
  });
  setView("triage");
}

function bindDiffCopy(button, container) {
  if (!button || !container) return;
  button.addEventListener("click", async () => {
    const payload = container.dataset.copy || "";
    if (!payload) {
      showToast("Summary unavailable");
      return;
    }
    try {
      await navigator.clipboard.writeText(payload);
      showToast("Summary copied");
    } catch (err) {
      showToast("Copy failed");
    }
  });
}

const helpSearchInput = document.getElementById("help-search");
const helpSearchResults = document.getElementById("help-search-results");
const helpToc = document.getElementById("help-toc");
const helpContent = document.getElementById("help-content");
const helpTitle = document.getElementById("help-title");
const helpSubtitle = document.getElementById("help-subtitle");
const helpRailLinks = document.querySelectorAll("[data-help-link]");
const HELP_MANIFEST_PATH = "docs/help/help_manifest.json";
const helpState = {
  manifest: null,
  pages: new Map(),
  index: [],
  currentPage: null,
  headingObserver: null,
};

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function slugifyHeading(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "");
}

function parseMarkdown(md) {
  const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
  const html = [];
  const headings = [];
  const idCounts = new Map();
  let inCode = false;
  let codeLang = "";
  let codeLines = [];
  let listType = null;
  let listBuffer = [];
  let tableBuffer = null;
  let callout = null;

  const flushList = () => {
    if (!listType || !listBuffer.length) return;
    const items = listBuffer.map((item) => `<li>${item}</li>`).join("");
    html.push(`<${listType}>${items}</${listType}>`);
    listType = null;
    listBuffer = [];
  };

  const flushTable = () => {
    if (!tableBuffer || tableBuffer.length < 2) {
      tableBuffer = null;
      return;
    }
    const header = tableBuffer[0];
    const rows = tableBuffer.slice(2);
    const headerCells = header.map((cell) => `<th>${cell}</th>`).join("");
    const bodyRows = rows
      .map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`)
      .join("");
    html.push(`<table><thead><tr>${headerCells}</tr></thead><tbody>${bodyRows}</tbody></table>`);
    tableBuffer = null;
  };

  const flushCallout = () => {
    if (!callout) return;
    html.push(
      `<div class="doc-callout ${callout.type}"><div class="doc-callout-title">${callout.title}</div>${callout.body}</div>`
    );
    callout = null;
  };

  const formatInline = (text) => {
    let value = escapeHtml(text);
    value = value.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    value = value.replace(/\*(.+?)\*/g, "<em>$1</em>");
    value = value.replace(/`([^`]+)`/g, "<code>$1</code>");
    value = value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    value = value.replace(/\[\[BADGE:([a-z]+)\]\]/gi, (_, kind) => {
      const key = kind.toLowerCase();
      const label = key === "powershell" ? "PowerShell" : key === "ssh" ? "SSH" : key === "local" ? "Local" : "Graph";
      return `<span class="doc-badge ${key}">${label}</span>`;
    });
    value = value.replace(/\[\[RISK:([a-z]+)\]\]/gi, (_, level) => {
      const label = level === "dangerous" ? "Dangerous" : level === "caution" ? "Caution" : "Safe";
      return `<span class="doc-badge risk ${level.toLowerCase()}">${label}</span>`;
    });
    return value;
  };

  const placeholder = (text) => {
    return text
      .replace(/<Badge\s+kind="([^"]+)"\s*\/>/gi, (_, kind) => `[[BADGE:${kind}]]`)
      .replace(/<RiskBadge\s+level="([^"]+)"\s*\/>/gi, (_, level) => `[[RISK:${level}]]`);
  };

  lines.forEach((rawLine, idx) => {
    const line = placeholder(rawLine);
    if (line.startsWith("```")) {
      if (inCode) {
        html.push(
          `<pre><code class="language-${codeLang}">${escapeHtml(codeLines.join("\n"))}</code></pre>`
        );
        inCode = false;
        codeLang = "";
        codeLines = [];
      } else {
        flushList();
        flushTable();
        flushCallout();
        inCode = true;
        codeLang = line.replace(/```/, "").trim();
      }
      return;
    }
    if (inCode) {
      codeLines.push(line);
      return;
    }

    if (tableBuffer && line.match(/^\s*\|?\s*[-:| ]+\|?\s*$/)) {
      return;
    }

    if (line.startsWith("> [!")) {
      flushList();
      flushTable();
      const match = line.match(/> \[!([A-Z]+)\]\s*(.*)/);
      const type = match ? match[1].toLowerCase() : "note";
      const title = type === "warning" ? "Warning" : type === "danger" ? "Danger" : "Note";
      callout = {
        type,
        title,
        body: match && match[2] ? `<p>${formatInline(match[2])}</p>` : "",
      };
      return;
    }
    if (line.startsWith("> ") && callout) {
      callout.body += `<p>${formatInline(line.replace(/^> /, ""))}</p>`;
      return;
    } else if (callout) {
      flushCallout();
    }

    if (!line.trim()) {
      flushList();
      flushTable();
      return;
    }

    if (line.match(/^\s*[-*]\s+/)) {
      const item = formatInline(line.replace(/^\s*[-*]\s+/, ""));
      if (listType !== "ul") {
        flushList();
        listType = "ul";
      }
      listBuffer.push(item);
      return;
    }
    if (line.match(/^\s*\d+\.\s+/)) {
      const item = formatInline(line.replace(/^\s*\d+\.\s+/, ""));
      if (listType !== "ol") {
        flushList();
        listType = "ol";
      }
      listBuffer.push(item);
      return;
    }
    flushList();

    if (line.includes("|") && lines[idx + 1] && lines[idx + 1].match(/^\s*\|?\s*[-:| ]+\|?\s*$/)) {
      const splitRow = (row) =>
        row
          .trim()
          .replace(/^\|/, "")
          .replace(/\|$/, "")
          .split("|")
          .map((cell) => formatInline(cell.trim()));
      tableBuffer = [splitRow(line), splitRow(lines[idx + 1])];
      return;
    }
    if (tableBuffer) {
      if (line.includes("|")) {
        const row = line
          .trim()
          .replace(/^\|/, "")
          .replace(/\|$/, "")
          .split("|")
          .map((cell) => formatInline(cell.trim()));
        tableBuffer.push(row);
        return;
      }
      flushTable();
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.*)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2].trim();
      const base = slugifyHeading(text);
      const count = (idCounts.get(base) || 0) + 1;
      idCounts.set(base, count);
      const id = count > 1 ? `${base}-${count}` : base;
      headings.push({ id, text, level });
      html.push(
        `<h${level} id="${id}">${formatInline(text)}<a class="help-anchor" href="#${id}" data-anchor="${id}">#</a></h${level}>`
      );
      return;
    }

    html.push(`<p>${formatInline(line)}</p>`);
  });

  flushList();
  flushTable();
  flushCallout();

  return { html: html.join("\n"), headings };
}

async function loadHelpManifest() {
  if (helpState.manifest) return helpState.manifest;
  try {
    const res = await fetch(`/${HELP_MANIFEST_PATH}`);
    if (!res.ok) throw new Error("Help manifest not found");
    const data = await res.json();
    helpState.manifest = data;
    return data;
  } catch (err) {
    return null;
  }
}

async function loadHelpPage(page) {
  if (!page || !page.path) return null;
  if (helpState.pages.has(page.id)) return helpState.pages.get(page.id);
  try {
    const res = await fetch(`/${page.path}`);
    if (!res.ok) throw new Error("Doc not found");
    const md = await res.text();
    const parsed = parseMarkdown(md);
    const wrapper = document.createElement("div");
    wrapper.innerHTML = parsed.html;
    const text = wrapper.textContent || "";
    const data = { ...page, markdown: md, html: parsed.html, headings: parsed.headings, text };
    helpState.pages.set(page.id, data);
    return data;
  } catch (err) {
    return { ...page, html: `<div class="note">Doc not found.</div>`, headings: [], text: "" };
  }
}

function groupHelpPages(pages) {
  const groups = new Map();
  pages.forEach((page) => {
    const group = page.group || "General";
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(page);
  });
  return Array.from(groups.entries());
}

function renderHelpToc(pages, currentPageId) {
  if (!helpToc) return;
  helpToc.innerHTML = "";
  const groups = groupHelpPages(pages);
  groups.forEach(([groupName, groupPages]) => {
    const details = document.createElement("details");
    details.classList.add("help-group");
    if (groupPages.some((page) => page.id === currentPageId)) {
      details.open = true;
    }
    const summary = document.createElement("summary");
    summary.innerHTML = `<span>${groupName}</span><span class="nav-caret">▾</span>`;
    details.appendChild(summary);
    const list = document.createElement("div");
    list.classList.add("help-group-links");
    groupPages.forEach((page) => {
      const link = document.createElement("button");
      link.type = "button";
      link.classList.add("help-link");
      if (page.id === currentPageId) link.classList.add("active");
      link.textContent = page.title;
      link.addEventListener("click", () => openHelpPage(page.id));
      list.appendChild(link);
      if (page.id === currentPageId && helpState.pages.has(page.id)) {
        const pageData = helpState.pages.get(page.id);
        pageData.headings.forEach((heading) => {
          if (heading.level === 1) return;
          const sub = document.createElement("button");
          sub.type = "button";
          sub.classList.add("help-link", "heading");
          sub.dataset.anchor = heading.id;
          sub.style.paddingLeft = `${heading.level * 10}px`;
          sub.textContent = heading.text;
          sub.addEventListener("click", () => openHelpPage(page.id, heading.id));
          list.appendChild(sub);
        });
      }
    });
    details.appendChild(list);
    helpToc.appendChild(details);
  });
}

function renderHelpContent(pageData) {
  if (!helpContent) return;
  helpContent.innerHTML = pageData?.html || "<div class=\"note\">Doc not found.</div>";
  if (helpTitle) helpTitle.textContent = pageData?.title || "Help Center";
  if (helpSubtitle) helpSubtitle.textContent = pageData?.description || "Documentation and how-to guidance";
  setupHelpAnchors();
  setupHelpScrollSpy(pageData?.headings || []);
}

function clearHelpHighlights() {
  if (!helpContent) return;
  helpContent.querySelectorAll("mark").forEach((mark) => {
    const parent = mark.parentNode;
    if (!parent) return;
    parent.replaceChild(document.createTextNode(mark.textContent), mark);
    parent.normalize();
  });
}

function highlightHelpMatches(query) {
  if (!helpContent || !query) return;
  clearHelpHighlights();
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(escaped, "gi");
  const nodes = helpContent.querySelectorAll("p, li");
  nodes.forEach((node) => {
    if (node.closest("pre, code")) return;
    if (!regex.test(node.textContent)) return;
    node.innerHTML = node.innerHTML.replace(regex, (match) => `<mark class="help-highlight">${match}</mark>`);
  });
}

function setupHelpAnchors() {
  if (!helpContent) return;
  helpContent.querySelectorAll("[data-anchor]").forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
      event.preventDefault();
      const id = anchor.dataset.anchor;
      if (!id) return;
      const url = `${window.location.origin}${window.location.pathname}#${id}`;
      navigator.clipboard?.writeText(url).then(() => showToast("Link copied"));
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

function setupHelpScrollSpy(headings) {
  if (!helpContent) return;
  if (helpState.headingObserver) {
    helpState.headingObserver.disconnect();
  }
  const headingEls = headings
    .map((heading) => document.getElementById(heading.id))
    .filter(Boolean);
  if (!headingEls.length) return;
  helpState.headingObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const active = helpToc?.querySelectorAll(".help-link.heading.active");
        active?.forEach((el) => el.classList.remove("active"));
        const link = helpToc?.querySelector(`.help-link[data-anchor="${entry.target.id}"]`);
        if (link) link.classList.add("active");
      });
    },
    { root: null, threshold: 0.3 }
  );
  headingEls.forEach((el) => helpState.headingObserver.observe(el));
}

function buildHelpIndex(pages) {
  helpState.index = pages.map((page) => ({
    id: page.id,
    title: page.title,
    group: page.group,
    tags: page.tags || [],
    text: page.text || "",
    headings: page.headings || [],
  }));
}

function renderHelpSearchResults(results) {
  if (!helpSearchResults) return;
  helpSearchResults.innerHTML = "";
  if (!results.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No matches.";
    helpSearchResults.appendChild(empty);
    return;
  }
  results.slice(0, 8).forEach((result) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.classList.add("ghost", "small");
    btn.textContent = `${result.title}${result.heading ? ` · ${result.heading}` : ""}`;
    btn.addEventListener("click", () => openHelpPage(result.id, result.anchor, result.highlight));
    helpSearchResults.appendChild(btn);
  });
}

function handleHelpSearch() {
  if (!helpSearchInput) return;
  const query = helpSearchInput.value.trim().toLowerCase();
  if (!query) {
    if (helpSearchResults) helpSearchResults.innerHTML = "";
    return;
  }
  const results = [];
  helpState.index.forEach((entry) => {
    if (entry.title.toLowerCase().includes(query)) {
      results.push({ id: entry.id, title: entry.title, highlight: query });
    }
    entry.headings.forEach((heading) => {
      if (heading.text.toLowerCase().includes(query)) {
        results.push({
          id: entry.id,
          title: entry.title,
          heading: heading.text,
          anchor: heading.id,
          highlight: query,
        });
      }
    });
    if (entry.text.toLowerCase().includes(query)) {
      results.push({ id: entry.id, title: entry.title, highlight: query });
    }
  });
  renderHelpSearchResults(results);
}

async function openHelpPage(pageId, anchor, highlight) {
  const manifest = await loadHelpManifest();
  if (!manifest) return;
  const pages = manifest.pages || [];
  const page = pages.find((entry) => entry.id === pageId) || pages[0];
  if (!page) return;
  const pageData = await loadHelpPage(page);
  helpState.currentPage = pageData.id;
  renderHelpContent(pageData);
  renderHelpToc(pages, helpState.currentPage);
  if (highlight) {
    highlightHelpMatches(highlight);
  }
  if (anchor) {
    const target = document.getElementById(anchor);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      target.classList.add("help-highlight");
      setTimeout(() => target.classList.remove("help-highlight"), 1200);
    }
    if (window.location.pathname.startsWith("/help")) {
      window.history.replaceState({ section: "help" }, "", `/help/${page.id}#${anchor}`);
    }
  } else if (window.location.pathname.startsWith("/help")) {
    window.history.replaceState({ section: "help" }, "", `/help/${page.id}`);
  }
}

async function initHelpCenter() {
  const manifest = await loadHelpManifest();
  if (!manifest || !manifest.pages) {
    if (helpContent) {
      helpContent.innerHTML = '<div class="note">Help content is unavailable.</div>';
    }
    return;
  }
  const pages = manifest.pages;
  const pathParts = window.location.pathname.split("/").filter(Boolean);
  const pageIdFromPath = pathParts[0] === "help" ? pathParts[1] : null;
  const hashAnchor = window.location.hash ? window.location.hash.replace("#", "") : "";
  const initialPage = pages.find((entry) => entry.id === pageIdFromPath) || pages[0];
  await Promise.all(pages.map((page) => loadHelpPage(page)));
  buildHelpIndex([...helpState.pages.values()]);
  await openHelpPage(initialPage.id, hashAnchor || null);
  if (helpSearchInput) {
    helpSearchInput.addEventListener("input", handleHelpSearch);
  }
  helpRailLinks.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.helpLink || "";
      if (!target) return;
      const [pageId, anchor] = target.split("#");
      openHelpPage(pageId, anchor);
      setSection("help");
    });
  });
}

if (typeof window !== "undefined") {
  window.GraphAdminHelp = {
    parseMarkdown,
    slugifyHeading,
  };
}

function formatSnapshotQuality(quality) {
  if (!quality || typeof quality !== "object") return "No quality data.";
  const payload = {
    completeness: quality.completeness ?? quality.overall,
    sections: quality.sections || {},
    gaps: quality.gaps || [],
    warnings: quality.warnings || [],
  };
  return JSON.stringify(payload, null, 2);
}

function getDraftStatusLabel(status) {
  if (status === "success") return "Success";
  if (status === "failed") return "Failed";
  if (status === "canceled") return "Canceled";
  return "Unknown";
}

function buildDraftStatusBadge(status) {
  const badge = document.createElement("span");
  badge.classList.add("draft-status-badge");
  const normalized = status || "unknown";
  badge.classList.add(normalized);
  badge.textContent = getDraftStatusLabel(normalized);
  return badge;
}

function hasDraftableResult(service) {
  const meta = lastRunMeta[service];
  if (!meta) return false;
  if (meta.ended_at) return true;
  if (meta.ok !== undefined) return true;
  if (meta.error || meta.cancelled) return true;
  return false;
}

function buildDraftEntryFromService(service) {
  const meta = lastRunMeta[service] || {};
  const output = lastOutputs[service];
  let raw = getOutputPanel(service)?.textContent || "";
  const rawParsed = tryParseJson(raw);
  if (rawParsed) {
    raw = JSON.stringify(sanitizeParams(rawParsed), null, 2);
  } else if (typeof raw === "string" && raw.length > 4000) {
    raw = `${raw.slice(0, 4000)}…`;
  }
  const status = meta.cancelled ? "canceled" : meta.ok ? "success" : "failed";
  return {
    entry_id: `entry-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    timestamp: new Date().toISOString(),
    service,
    action_id: meta.action || null,
    action_label: meta.label || resolveActionLabel(service, meta.action) || meta.action || service,
    mode: meta.mode || null,
    execution_target: meta.execution_target || null,
    parameters: sanitizeParams(meta.params || {}),
    result_status: status,
    error_summary: meta.error || meta.hint || null,
    output: sanitizeParams(output),
    output_raw: raw,
    meta: {
      request_id: meta.request_id || null,
      elapsed_ms: meta.elapsed_ms || null,
    },
  };
}

function renderDraftEntries(draft) {
  if (!draftEntriesList) return;
  draftEntriesList.innerHTML = "";
  const entries = draft?.entries || [];
  if (draftEmptyNote) {
    draftEmptyNote.style.display = entries.length ? "none" : "block";
  }
  entries.forEach((entry) => {
    const li = document.createElement("li");
    li.classList.add("draft-entry");
    const header = document.createElement("div");
    header.classList.add("draft-entry-header");
    const titleWrap = document.createElement("div");
    const title = document.createElement("div");
    title.classList.add("draft-entry-title");
    title.textContent = entry.action_label || `${entry.service}.${entry.action_id || "action"}`;
    const meta = document.createElement("div");
    meta.classList.add("draft-entry-meta");
    const timestamp = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "Unknown time";
    const targetLabel = entry.execution_target ? formatSshTargetLabel(entry.execution_target) : "Local";
    meta.textContent = `${formatServiceLabel(entry.service)} · ${timestamp} · ${targetLabel}`;
    titleWrap.appendChild(title);
    titleWrap.appendChild(meta);
    const badge = buildDraftStatusBadge(entry.result_status);
    const actions = document.createElement("div");
    actions.classList.add("draft-entry-actions");
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.classList.add("ghost", "small");
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => {
      const draftId = draft?.id;
      if (!draftId) return;
      const remaining = (draft.entries || []).filter((item) => item.entry_id !== entry.entry_id);
      updateDraftSnapshot(draftId, { entries: remaining });
      renderDraftSnapshots();
    });
    actions.appendChild(removeBtn);
    header.appendChild(titleWrap);
    header.appendChild(badge);
    header.appendChild(actions);
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = entry.error_summary ? `Details · ${entry.error_summary}` : "View output";
    const pre = document.createElement("pre");
    const outputPayload = entry.output || entry.output_raw || entry;
    pre.textContent = typeof outputPayload === "string" ? outputPayload : JSON.stringify(outputPayload, null, 2);
    details.appendChild(summary);
    details.appendChild(pre);
    li.appendChild(header);
    li.appendChild(details);
    draftEntriesList.appendChild(li);
  });
}

function readDraftSubjectFromInputs() {
  if (!draftSubjectKind || !draftSubjectValue) return null;
  const kind = draftSubjectKind.value || "user";
  const identifier = draftSubjectValue.value.trim();
  const displayName = draftSubjectName?.value.trim();
  const identifiers = {};
  if (identifier) {
    if (kind === "user") {
      identifiers.upn = identifier;
    } else {
      const aliasType = isIpAddress(identifier) ? "ip" : "hostname";
      identifiers[aliasType] = identifier;
    }
  }
  const subject = { kind, identifiers };
  if (displayName) subject.display_name = displayName;
  return subject;
}

function syncDraftFields(draft) {
  if (!draft) return;
  if (draftTitleInput) draftTitleInput.value = draft.title || "";
  if (draftNotesInput) draftNotesInput.value = draft.notes || "";
  if (draftProfileSelect) draftProfileSelect.value = draft.profile || "core";
  if (draftSubjectKind) draftSubjectKind.value = draft.subject?.kind || "user";
  if (draftSubjectValue) {
    const identifiers = draft.subject?.identifiers || {};
    const value =
      identifiers.upn ||
      identifiers.hostname ||
      identifiers.ip ||
      identifiers.fqdn ||
      identifiers.objectId ||
      "";
    draftSubjectValue.value = value;
  }
  if (draftSubjectName) draftSubjectName.value = draft.subject?.display_name || "";
}

function renderDraftSnapshots() {
  if (!draftSelect) return;
  draftSelect.innerHTML = "";
  const drafts = (draftSnapshots || []).filter((entry) => !entry.archived_at);
  if (!drafts.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No drafts yet";
    draftSelect.appendChild(option);
    draftSelect.disabled = true;
    if (draftFinalizeButton) draftFinalizeButton.disabled = true;
    if (draftClearButton) draftClearButton.disabled = true;
    renderDraftEntries(null);
    return;
  }
  draftSelect.disabled = false;
  drafts.forEach((entry) => {
    const option = document.createElement("option");
    option.value = entry.id;
    option.textContent = entry.title || "Draft snapshot";
    draftSelect.appendChild(option);
  });
  const active = getActiveDraft() || drafts[0];
  if (active && activeDraftId !== active.id) {
    setActiveDraftId(active.id);
  }
  if (active) {
    draftSelect.value = active.id;
    syncDraftFields(active);
    renderDraftEntries(active);
    const hasEntries = Array.isArray(active.entries) && active.entries.length > 0;
    if (draftFinalizeButton) draftFinalizeButton.disabled = !hasEntries;
    if (draftClearButton) draftClearButton.disabled = !hasEntries;
  }
}

function updateDraftFromInputs() {
  const draft = getActiveDraft();
  if (!draft) return;
  const updates = {
    title: draftTitleInput?.value.trim() || draft.title,
    notes: draftNotesInput?.value || "",
    profile: draftProfileSelect?.value || draft.profile || "core",
    subject: readDraftSubjectFromInputs(),
  };
  updateDraftSnapshot(draft.id, updates);
  const option = draftSelect?.querySelector(`option[value="${draft.id}"]`);
  if (option) {
    option.textContent = updates.title || "Draft snapshot";
  }
}

async function addLatestResultToDraft(service) {
  if (!hasDraftableResult(service)) {
    showToast("Run an action first to add its result to a draft.");
    return;
  }
  if (!draftSnapshots.length) {
    createDraftSnapshot({ title: `${formatServiceLabel(service)} draft` });
  }
  const draft = getActiveDraft() || draftSnapshots.find((entry) => !entry.archived_at);
  if (!draft) return;
  const entry = buildDraftEntryFromService(service);
  addDraftEntry(draft.id, entry);
  renderDraftSnapshots();
  showToast("Added result to draft");
}

function updateRunnerDraftButton(service) {
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;
  const button = form.querySelector(".runner-draft");
  if (!button) return;
  const enabled = hasDraftableResult(service);
  button.disabled = !enabled;
  button.title = enabled ? "Add latest result to draft" : "Run an action first to add its result";
}

async function finalizeDraftSnapshot() {
  const draft = getActiveDraft();
  if (!draft) {
    showToast("Create a draft first");
    return;
  }
  const subject = readDraftSubjectFromInputs();
  const kind = subject?.kind || draft.subject?.kind || "user";
  const identifier = subject?.identifiers && Object.values(subject.identifiers).find(Boolean);
  if (!identifier && kind !== "admin_host") {
    showToast("Enter an identifier before finalizing");
    return;
  }
  const entries = draft.entries || [];
  if (!entries.length) {
    showToast("Add at least one result to finalize");
    return;
  }
  const payload = {
    draft: {
      ...draft,
      subject: subject || draft.subject,
      profile: draftProfileSelect?.value || draft.profile || "core",
    },
    subject: subject || draft.subject,
    profile: draftProfileSelect?.value || draft.profile || "core",
    incident_id: activeIncidentId || null,
  };
  try {
    const res = await fetch("/api/snapshots/finalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Finalize snapshot failed");
      return;
    }
    archiveDraftSnapshot(draft.id);
    renderDraftSnapshots();
    await refreshSnapshotEntities();
    await refreshSnapshotHistory();
    showToast("Snapshot finalized");
  } catch (err) {
    showToast("Finalize snapshot failed");
  }
}

async function fetchIncident(incidentId) {
  if (!incidentId) return null;
  try {
    const res = await fetch(`/api/incidents/${incidentId}`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function fetchIncidentReport(incidentId) {
  if (!incidentId) return null;
  try {
    const res = await fetch(`/api/incidents/${incidentId}/report`);
    const data = await res.json();
    if (!data.ok) return null;
    return data.data || null;
  } catch (err) {
    return null;
  }
}

async function saveIncidentReport(incidentId, report) {
  if (!incidentId) return null;
  try {
    const res = await fetch(`/api/incidents/${incidentId}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "Save failed");
    return data.data || null;
  } catch (err) {
    showToast(err.message || "Report save failed");
    return null;
  }
}

function buildDefaultIncidentReport(incident) {
  return {
    incident_id: incident?.incident_id || null,
    title: incident?.title || "Incident report",
    customer: "",
    reported_by: "",
    severity: "",
    status: incident?.status || "open",
    reported_at: incident?.created_at || "",
    resolved_at: "",
    summary_reported: incident?.description || "",
    summary_actual: "",
    root_cause: "",
    resolution: "",
    validation: "",
    preventive_actions: "",
    affected: "",
    impact_window: { start: incident?.time_window_start || "", end: incident?.time_window_end || "" },
    timeline: [],
    evidence_refs: [],
    attachments: [],
    template_id: "default",
  };
}

function applyIncidentReportToForm(report) {
  if (!report) return;
  if (incidentReportTitle) incidentReportTitle.value = report.title || "";
  if (incidentReportClient) incidentReportClient.value = report.customer || "";
  if (incidentReportReportedBy) incidentReportReportedBy.value = report.reported_by || "";
  if (incidentReportSeverity) incidentReportSeverity.value = report.severity || "";
  if (incidentReportStatus) incidentReportStatus.value = report.status || "open";
  if (incidentReportReportedAt) incidentReportReportedAt.value = report.reported_at || "";
  if (incidentReportResolvedAt) incidentReportResolvedAt.value = report.resolved_at || "";
  if (incidentReportImpactStart) incidentReportImpactStart.value = report.impact_window?.start || "";
  if (incidentReportImpactEnd) incidentReportImpactEnd.value = report.impact_window?.end || "";
  if (incidentReportSummaryReported) incidentReportSummaryReported.value = report.summary_reported || "";
  if (incidentReportSummaryActual) incidentReportSummaryActual.value = report.summary_actual || "";
  if (incidentReportRootCause) incidentReportRootCause.value = report.root_cause || "";
  if (incidentReportResolution) incidentReportResolution.value = report.resolution || "";
  if (incidentReportValidation) incidentReportValidation.value = report.validation || "";
  if (incidentReportPreventive) incidentReportPreventive.value = report.preventive_actions || "";
  if (incidentReportAffected) incidentReportAffected.value = report.affected || "";
}

function collectIncidentReportForm() {
  const report = incidentReport || {};
  return {
    ...report,
    title: incidentReportTitle?.value.trim() || report.title || "Incident report",
    customer: incidentReportClient?.value.trim() || "",
    reported_by: incidentReportReportedBy?.value.trim() || "",
    severity: incidentReportSeverity?.value || "",
    status: incidentReportStatus?.value || report.status || "open",
    reported_at: incidentReportReportedAt?.value || report.reported_at || "",
    resolved_at: incidentReportResolvedAt?.value || report.resolved_at || "",
    summary_reported: incidentReportSummaryReported?.value || "",
    summary_actual: incidentReportSummaryActual?.value || "",
    root_cause: incidentReportRootCause?.value || "",
    resolution: incidentReportResolution?.value || "",
    validation: incidentReportValidation?.value || "",
    preventive_actions: incidentReportPreventive?.value || "",
    affected: incidentReportAffected?.value || "",
    impact_window: {
      start: incidentReportImpactStart?.value || report.impact_window?.start || "",
      end: incidentReportImpactEnd?.value || report.impact_window?.end || "",
    },
    template_id: report.template_id || "default",
  };
}

function renderIncidentReportTimeline(report) {
  if (!incidentReportTimeline) return;
  incidentReportTimeline.innerHTML = "";
  const timeline = report?.timeline || [];
  if (!timeline.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No timeline entries yet.";
    incidentReportTimeline.appendChild(empty);
    return;
  }
  timeline.forEach((entry, index) => {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = entry.label || entry.summary || "Timeline entry";
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "Unknown time";
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const up = document.createElement("button");
    up.type = "button";
    up.classList.add("ghost", "small");
    up.textContent = "Up";
    up.disabled = index === 0;
    up.addEventListener("click", () => {
      const items = [...timeline];
      const temp = items[index - 1];
      items[index - 1] = items[index];
      items[index] = temp;
      incidentReport.timeline = items;
      renderIncidentReportTimeline(incidentReport);
    });
    const down = document.createElement("button");
    down.type = "button";
    down.classList.add("ghost", "small");
    down.textContent = "Down";
    down.disabled = index === timeline.length - 1;
    down.addEventListener("click", () => {
      const items = [...timeline];
      const temp = items[index + 1];
      items[index + 1] = items[index];
      items[index] = temp;
      incidentReport.timeline = items;
      renderIncidentReportTimeline(incidentReport);
    });
    const edit = document.createElement("button");
    edit.type = "button";
    edit.classList.add("ghost", "small");
    edit.textContent = "Edit";
    edit.addEventListener("click", async () => {
      const values = await openFormModal({
        title: "Edit timeline entry",
        fields: [
          {
            key: "label",
            label: "Timeline entry label",
            value: entry.label || "",
            required: true,
          },
          {
            key: "timestamp",
            label: "Timestamp (ISO or local)",
            value: entry.timestamp || "",
          },
        ],
        confirmLabel: "Save entry",
        cancelLabel: "Cancel",
      });
      if (!values) return;
      const updated = {
        ...entry,
        label: values.label || entry.label,
        timestamp: values.timestamp || entry.timestamp,
      };
      const items = [...timeline];
      items[index] = updated;
      incidentReport.timeline = items;
      renderIncidentReportTimeline(incidentReport);
    });
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      const items = timeline.filter((_, idx) => idx !== index);
      incidentReport.timeline = items;
      renderIncidentReportTimeline(incidentReport);
    });
    actions.appendChild(up);
    actions.appendChild(down);
    actions.appendChild(edit);
    actions.appendChild(remove);
    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(actions);
    incidentReportTimeline.appendChild(row);
  });
}

function buildEvidenceCandidates(incident, timelineData) {
  const candidates = [];
  const addCandidate = (item) => {
    if (!item) return;
    candidates.push(item);
  };
  draftSnapshots.forEach((draft) => {
    (draft.entries || []).forEach((entry) => {
      addCandidate({
        type: "draft_entry",
        id: `${draft.id}:${entry.entry_id}`,
        label: entry.action_label || entry.service,
        timestamp: entry.timestamp,
        summary: entry.error_summary || entry.result_status,
        payload: entry,
      });
    });
  });
  Object.entries(lastRunMeta).forEach(([service, meta]) => {
    if (!meta?.ended_at) return;
    addCandidate({
      type: "run",
      id: `run:${service}:${meta.ended_at}`,
      label: meta.label || `${service}.${meta.action}`,
      timestamp: meta.ended_at,
      summary: meta.ok ? "Success" : meta.error || "Failed",
      payload: { meta, output: sanitizeParams(lastOutputs[service]) },
    });
  });
  loadActionPackHistory().forEach((entry) => {
    addCandidate({
      type: "action_pack_run",
      id: `pack:${entry.packId}:${entry.timestamp}`,
      label: entry.pack_name || entry.packId,
      timestamp: new Date(entry.timestamp).toISOString(),
      summary: entry.status,
      payload: entry,
    });
  });
  (incident?.snapshots || []).forEach((snapId) => {
    addCandidate({
      type: "snapshot",
      id: `snapshot:${snapId}`,
      label: `Snapshot ${snapId}`,
      timestamp: null,
      summary: "Snapshot captured",
      payload: { snapshot_id: snapId },
    });
  });
  if (timelineData?.events) {
    (timelineData.events || []).forEach((evt) => {
      addCandidate({
        type: "event",
        id: evt.event_id || evt.id || `${evt.kind}:${evt.time}`,
        label: evt.kind || "Event",
        timestamp: evt.time || evt.timestamp,
        summary: evt.kind || "",
        payload: evt,
      });
    });
  }
  snapshotDiffCache.forEach((entry, key) => {
    addCandidate({
      type: "diff",
      id: `diff:${key}:${entry.a}:${entry.b}`,
      label: `Snapshot diff ${entry.a} → ${entry.b}`,
      timestamp: new Date(entry.captured_at || Date.now()).toISOString(),
      summary: "Snapshot diff",
      payload: entry.diff,
    });
  });
  reportDiffCache.forEach((entry, key) => {
    addCandidate({
      type: "diff",
      id: `report-diff:${key}`,
      label: "Report diff",
      timestamp: new Date(entry.captured_at || Date.now()).toISOString(),
      summary: "Report diff",
      payload: entry.diff,
    });
  });
  return candidates;
}

function renderIncidentEvidence(report, candidates) {
  if (!incidentReportEvidence) return;
  incidentReportEvidence.innerHTML = "";
  if (!candidates.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No evidence available yet.";
    incidentReportEvidence.appendChild(empty);
    return;
  }
  const selectedIds = new Set((report?.evidence_refs || []).map((item) => item.id));
  candidates.forEach((item) => {
    const row = document.createElement("div");
    row.classList.add("evidence-item");
    const header = document.createElement("div");
    header.classList.add("evidence-header");
    const titleWrap = document.createElement("div");
    const title = document.createElement("div");
    title.classList.add("evidence-title");
    title.textContent = item.label || item.type;
    const meta = document.createElement("div");
    meta.classList.add("evidence-meta");
    const when = item.timestamp ? new Date(item.timestamp).toLocaleString() : "No timestamp";
    meta.textContent = `${item.type.replace("_", " ")} · ${when}`;
    titleWrap.appendChild(title);
    titleWrap.appendChild(meta);
    const actions = document.createElement("div");
    actions.classList.add("evidence-actions");
    const toggle = document.createElement("input");
    toggle.type = "checkbox";
    toggle.checked = selectedIds.has(item.id);
    toggle.addEventListener("change", () => {
      const refs = report.evidence_refs || [];
      if (toggle.checked) {
        refs.push({
          type: item.type,
          id: item.id,
          label: item.label,
          timestamp: item.timestamp,
          summary: item.summary,
          raw_payload_ref: sanitizeParams(item.payload),
        });
      } else {
        const idx = refs.findIndex((ref) => ref.id === item.id);
        if (idx >= 0) refs.splice(idx, 1);
      }
      report.evidence_refs = refs;
    });
    const summary = document.createElement("span");
    summary.textContent = item.summary || "";
    actions.appendChild(summary);
    actions.appendChild(toggle);
    header.appendChild(titleWrap);
    header.appendChild(actions);
    row.appendChild(header);
    incidentReportEvidence.appendChild(row);
  });
}

async function refreshIncidentReportEvidence(report) {
  if (!report || !incidentReportEvidence) return;
  const incident = report.incident_id ? await fetchIncident(report.incident_id) : null;
  const timelineData = report.incident_id ? await fetchIncidentTimeline(report.incident_id) : null;
  const candidates = buildEvidenceCandidates(incident, timelineData);
  renderIncidentEvidence(report, candidates);
  return candidates;
}

async function loadIncidentReportFor(incidentId) {
  if (!incidentId) return;
  const incident = await fetchIncident(incidentId);
  const existing = await fetchIncidentReport(incidentId);
  incidentReport = existing || buildDefaultIncidentReport(incident);
  incidentReport.timeline = incidentReport.timeline || [];
  incidentReport.evidence_refs = incidentReport.evidence_refs || [];
  incidentReport.incident_id = incidentId;
  applyIncidentReportToForm(incidentReport);
  renderIncidentReportTimeline(incidentReport);
  await refreshIncidentReportEvidence(incidentReport);
}

async function previewIncidentReport(format) {
  if (!incidentReportPreviewOutput) return;
  if (!incidentReport?.incident_id) {
    showToast("Select an incident first");
    return;
  }
  const redaction = incidentReportRedaction?.value || "internal";
  const report = collectIncidentReportForm();
  report.timeline = incidentReport.timeline || [];
  report.evidence_refs = incidentReport.evidence_refs || [];
  incidentReport = { ...incidentReport, ...report };
  try {
    const res = await fetch(`/api/incidents/${incidentReport.incident_id}/report/render`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ format, redaction, report }),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Report render failed");
      return;
    }
    if (format === "pdf") {
      const url = data.data?.url || data.data?.artifact_url;
      if (url) window.open(url, "_blank");
      return;
    }
    incidentReportPreviewOutput.textContent = data.data?.content || "";
  } catch (err) {
    showToast("Report render failed");
  }
}

function snapshotLabel(snapshot) {
  const ts = snapshot?.captured_at || snapshot?.capturedAt || snapshot?.timestamp;
  const date = ts ? new Date(ts) : null;
  const label = date && !Number.isNaN(date.getTime()) ? date.toLocaleString() : ts || "Snapshot";
  const profile = snapshot?.profile ? ` · ${snapshot.profile}` : "";
  return `${label}${profile}`;
}

function renderSnapshotEntities() {
  if (!snapshotSubjectSelect) return;
  snapshotSubjectSelect.innerHTML = "";
  if (!snapshotEntities.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No subjects yet";
    snapshotSubjectSelect.appendChild(option);
    return;
  }
  snapshotEntities.forEach((entity) => {
    const option = document.createElement("option");
    option.value = entity.canonical_id;
    const name = entity.display_name || entity.canonical_id;
    option.textContent = `${name} (${entity.kind})`;
    snapshotSubjectSelect.appendChild(option);
  });
}

function renderSnapshotHistory() {
  if (!snapshotHistoryList) return;
  snapshotHistoryList.innerHTML = "";
  if (!snapshotHistoryItems.length) {
    const empty = document.createElement("li");
    empty.classList.add("history-empty");
    empty.textContent = "No snapshots captured yet.";
    snapshotHistoryList.appendChild(empty);
    return;
  }
  snapshotHistoryItems.forEach((snap) => {
    const li = document.createElement("li");
    li.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    const label = snapshotLabel(snap);
    const kind = snap?.subject?.kind;
    const golden = goldenBaselines.find((entry) => entry.kind === kind);
    const isGolden = golden && golden.snapshot_id === snap.snapshot_id;
    title.textContent = label;
    if (isGolden) {
      const badge = document.createElement("span");
      badge.classList.add("badge");
      badge.textContent = "Golden";
      title.appendChild(badge);
    }
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    const completeness = snap?.quality?.completeness ?? snap?.quality?.overall;
    const gapCount = Array.isArray(snap?.quality?.gaps) ? snap.quality.gaps.length : 0;
    const warnCount = Array.isArray(snap?.quality?.warnings) ? snap.quality.warnings.length : 0;
    meta.textContent = `Completeness: ${completeness != null ? Math.round(completeness * 100) : "—"}% · Gaps: ${gapCount} · Warnings: ${warnCount}`;
    const actions = document.createElement("div");
    actions.classList.add("history-actions");
    const exportBtn = document.createElement("button");
    exportBtn.type = "button";
    exportBtn.classList.add("ghost", "small");
    exportBtn.textContent = "Export JSON";
    exportBtn.addEventListener("click", () => {
      const name = sanitizeFilename(`${snap.snapshot_id || "snapshot"}.json`);
      downloadJson(snap, name);
    });
    actions.appendChild(exportBtn);
    if (kind && !isGolden) {
      const setBtn = document.createElement("button");
      setBtn.type = "button";
      setBtn.classList.add("ghost", "small");
      setBtn.textContent = "Set golden";
      setBtn.addEventListener("click", async () => {
        const labelText = await promptModal({
          title: "Golden baseline label",
          subtitle: "Optional label for this golden baseline.",
          label: "Label (optional)",
          defaultValue: kind,
          confirmLabel: "Set baseline",
          cancelLabel: "Skip label",
        });
        await setGoldenBaseline(kind, snap.snapshot_id, labelText || "");
        goldenBaselines = await fetchGoldenBaselines();
        renderSnapshotHistory();
      });
      actions.appendChild(setBtn);
    }
    if (kind && golden && golden.snapshot_id) {
      const compareBtn = document.createElement("button");
      compareBtn.type = "button";
      compareBtn.classList.add("ghost", "small");
      compareBtn.textContent = "Compare golden";
      compareBtn.addEventListener("click", async () => {
        setDiffLoading(snapshotDiffMeta, snapshotDiffOutput, snapshotDiffTriage, "Golden diff running...");
        const diff = await compareGoldenBaseline(snap.snapshot_id);
        if (snapshotDiffMeta) {
          snapshotDiffMeta.textContent = diff ? "Golden diff generated" : "Golden diff failed";
        }
        if (snapshotDiffOutput) {
          snapshotDiffOutput.textContent = formatDiffSummary(diff?.diff || diff || {});
        }
        if (snapshotDiffTriage) {
          renderDiffTriage(snapshotDiffTriage, diff?.diff || diff || {});
        }
      });
      actions.appendChild(compareBtn);
    }
    li.appendChild(title);
    li.appendChild(meta);
    li.appendChild(actions);
    snapshotHistoryList.appendChild(li);
  });
}

function updateSnapshotDiffOptions() {
  if (!snapshotDiffSelectA || !snapshotDiffSelectB) return;
  snapshotDiffSelectA.innerHTML = "";
  snapshotDiffSelectB.innerHTML = "";
  snapshotHistoryItems.forEach((snap) => {
    const id = snap.snapshot_id || snap.snapshotId;
    if (!id) return;
    const label = snapshotLabel(snap);
    const optA = document.createElement("option");
    optA.value = id;
    optA.textContent = label;
    const optB = document.createElement("option");
    optB.value = id;
    optB.textContent = label;
    snapshotDiffSelectA.appendChild(optA);
    snapshotDiffSelectB.appendChild(optB);
  });
}

async function refreshSnapshotEntities() {
  snapshotEntities = await fetchSnapshotEntities();
  renderSnapshotEntities();
  if (snapshotSubjectSelect && snapshotEntities.length) {
    if (!snapshotSubjectSelect.value) {
      snapshotSubjectSelect.value = snapshotEntities[0].canonical_id;
    }
  }
}

async function refreshSnapshotHistory() {
  const canonicalId = snapshotSubjectSelect?.value;
  if (!canonicalId) {
    snapshotHistoryItems = [];
    renderSnapshotHistory();
    return;
  }
  goldenBaselines = await fetchGoldenBaselines();
  snapshotHistoryItems = await fetchSnapshotHistory(canonicalId, 20);
  renderSnapshotHistory();
  updateSnapshotDiffOptions();
  if (snapshotQualityMeta) {
    snapshotQualityMeta.textContent = canonicalId;
  }
  if (snapshotQualityOutput) {
    const latest = snapshotHistoryItems[0];
    snapshotQualityOutput.textContent = formatSnapshotQuality(latest?.quality);
  }
}

async function runSnapshotDiff() {
  if (!snapshotDiffSelectA || !snapshotDiffSelectB) return;
  const idA = snapshotDiffSelectA.value;
  const idB = snapshotDiffSelectB.value;
  if (!idA || !idB) {
    if (snapshotDiffMeta) snapshotDiffMeta.textContent = "Select two snapshots to compare.";
    if (snapshotDiffOutput) snapshotDiffOutput.textContent = "";
    return;
  }
  setDiffLoading(snapshotDiffMeta, snapshotDiffOutput, snapshotDiffTriage, "Diff running...");
  const canonicalId = snapshotSubjectSelect?.value || "global";
  const cached = getCachedSnapshotDiff(canonicalId, idA, idB);
  const diff = cached || (await fetchSnapshotEngineDiff(idA, idB));
  if (diff && !cached) {
    cacheSnapshotDiff(canonicalId, idA, idB, diff);
  }
  if (snapshotDiffMeta) {
    snapshotDiffMeta.textContent = diff ? "Diff generated" : "Diff failed";
  }
  if (snapshotDiffOutput) {
    snapshotDiffOutput.textContent = formatDiffSummary(diff || {});
  }
  if (snapshotDiffTriage) {
    renderDiffTriage(snapshotDiffTriage, diff);
  }
}

function getDiffKey(item) {
  if (!item || typeof item !== "object") return null;
  return (
    item.id ||
    item.userPrincipalName ||
    item.mail ||
    item.name ||
    item.displayName ||
    item.ipAddress ||
    item.IPAddress ||
    item.address ||
    item.Address ||
    item.hostName ||
    item.HostName ||
    item.deviceId ||
    item.deviceName ||
    null
  );
}

function parseIncidentDate(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date;
}

function getIncidentTimeframe() {
  const now = new Date();
  const lookback = Number.parseInt(incidentLookbackInput?.value || "24", 10);
  const startInput = parseIncidentDate(incidentStartInput?.value);
  const endInput = parseIncidentDate(incidentEndInput?.value);
  const end = endInput || now;
  const start = startInput || new Date(end.getTime() - Math.max(1, lookback || 24) * 60 * 60 * 1000);
  return {
    start,
    end,
    lookback_hours: lookback || 24,
    label: `${start.toLocaleString()} → ${end.toLocaleString()}`,
  };
}

async function runReportTask(action, params) {
  const payload = { ...(params || {}) };
  if (shouldDisableSnapshots("reports", action)) {
    payload._snapshot = false;
  }
  payload._ui_request_id = generateUiRequestId();
  const res = await fetch("/api/task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service: "reports", action, params: payload }),
  });
  const data = await res.json();
  if (data.ok) {
    refreshReportHistory();
  }
  return data;
}

function extractUserKey(report) {
  const user = report?.user || {};
  return user.id || user.userPrincipalName || user.mail || user.displayName || null;
}

function findPreviousUserAudit(history, userKey, beforeTs) {
  if (!userKey) return null;
  const before = Number.isFinite(beforeTs) ? beforeTs : Date.now();
  return history.find((entry) => {
    if (entry.action !== "user_audit") return false;
    if (!entry.data) return false;
    const key = extractUserKey(entry.data);
    return key === userKey && entry.timestamp < before;
  });
}

function diffByKey(current, previous, keyFn, labelFn) {
  const currentMap = new Map();
  const prevMap = new Map();
  normalizeList(current).forEach((item) => {
    const key = keyFn(item);
    if (!key) return;
    currentMap.set(key, { key, label: labelFn(item) || key, raw: item });
  });
  normalizeList(previous).forEach((item) => {
    const key = keyFn(item);
    if (!key) return;
    prevMap.set(key, { key, label: labelFn(item) || key, raw: item });
  });
  const added = [];
  const removed = [];
  currentMap.forEach((item, key) => {
    if (!prevMap.has(key)) added.push(item);
  });
  prevMap.forEach((item, key) => {
    if (!currentMap.has(key)) removed.push(item);
  });
  return { added, removed };
}

function summarizeSignIns(signIns, start, end) {
  const filtered = normalizeList(signIns).filter((entry) => {
    const ts = parseIncidentDate(entry?.createdDateTime);
    if (!ts) return false;
    return ts >= start && ts <= end;
  });
  const failures = [];
  const errorCodes = {};
  const caStatus = {};
  filtered.forEach((entry) => {
    const status = entry?.status || {};
    const errorCode = status.errorCode;
    const ca = entry?.conditionalAccessStatus || "unknown";
    caStatus[ca] = (caStatus[ca] || 0) + 1;
    if (errorCode && errorCode !== 0) {
      errorCodes[String(errorCode)] = (errorCodes[String(errorCode)] || 0) + 1;
      failures.push(entry);
    }
  });
  const latestFailure = failures[0] || null;
  return {
    count: filtered.length,
    failures: failures.length,
    conditional_access: caStatus,
    error_codes: errorCodes,
    latest_failure: latestFailure,
  };
}

function summarizeTopologyDiff(start, end) {
  const history = loadTopologyHistory();
  if (!history.length) return null;
  const within = history
    .map((snap) => ({ snap, ts: parseSnapshotTime(snap?.timestamp || snap?.generated_at) }))
    .filter((entry) => entry.ts && entry.ts >= start && entry.ts <= end)
    .sort((a, b) => a.ts - b.ts);
  if (within.length < 2) return null;
  const earliest = within[0].snap;
  const latest = within[within.length - 1].snap;
  const report = buildTopologyDiffReport(earliest, latest, null);
  return report;
}

function chooseIncidentFixPack(signals) {
  const errorCodes = signals?.signins?.error_codes || {};
  const caStatus = signals?.signins?.conditional_access || {};
  const hasCaFailure = (caStatus.failure || 0) > 0 || Object.keys(errorCodes).some((code) => code.startsWith("53"));
  const licenseRemoved = (signals?.licenses?.removed || []).length > 0;
  if (hasCaFailure) return "conditional-access-triage";
  if (licenseRemoved) return "license-reconciliation";
  if ((signals?.groups?.removed || []).length > 0) return "onboard-user";
  return "flagship-user-lifecycle";
}

function buildIncidentAnalysis(signals, context) {
  const errorCodes = signals?.signins?.error_codes || {};
  const caStatus = signals?.signins?.conditional_access || {};
  const latestFailure = signals?.signins?.latest_failure;
  const likelyCa = (caStatus.failure || 0) > 0 || Object.keys(errorCodes).some((code) => code.startsWith("53"));
  const disabled = Object.keys(errorCodes).includes("50057");
  const badPassword = Object.keys(errorCodes).includes("50126");
  const licenseRemoved = (signals?.licenses?.removed || []).length > 0;
  const groupRemoved = (signals?.groups?.removed || []).length > 0;
  const mostLikely = disabled
    ? "User account disabled"
    : likelyCa
      ? "Conditional Access policy blocked sign-ins"
      : badPassword
        ? "Invalid credentials"
        : licenseRemoved
          ? "License removed or expired"
          : groupRemoved
            ? "Group membership change"
            : signals?.graph?.summary?.state === "warn"
              ? "Microsoft Graph service degradation"
              : "No obvious blocker detected";

  const changed = [];
  if (licenseRemoved) {
    changed.push(`Licenses removed: ${signals.licenses.removed.map((l) => l.label).join(", ")}`);
  }
  if ((signals?.licenses?.added || []).length) {
    changed.push(`Licenses added: ${signals.licenses.added.map((l) => l.label).join(", ")}`);
  }
  if (groupRemoved) {
    changed.push(`Groups removed: ${signals.groups.removed.map((g) => g.label).join(", ")}`);
  }
  if ((signals?.groups?.added || []).length) {
    changed.push(`Groups added: ${signals.groups.added.map((g) => g.label).join(", ")}`);
  }
  if (signals?.topology?.summary) {
    const topo = signals.topology.summary;
    changed.push(`Topology changes: DHCP +${topo.dhcp_added} / DNS +${topo.dns_added}`);
  }
  if (latestFailure?.createdDateTime) {
    changed.push(`Latest failure: ${latestFailure.createdDateTime}`);
  }

  const nextChecks = [];
  if (likelyCa) {
    nextChecks.push("Review Conditional Access policy results for the user and device.");
    nextChecks.push("Confirm device compliance state and MFA requirements.");
  }
  if (licenseRemoved) {
    nextChecks.push("Reassign required license SKU and re-test sign-in.");
  }
  if (groupRemoved) {
    nextChecks.push("Validate group membership required for app access.");
  }
  if (badPassword) {
    nextChecks.push("Reset password or verify credential cache on device.");
  }
  if (!nextChecks.length) {
    nextChecks.push("Review sign-in errors and confirm directory properties.");
    nextChecks.push("Check service health dashboard for tenant incidents.");
  }

  const recommendedPackId = chooseIncidentFixPack(signals);
  const pack = getActionPackById(recommendedPackId);
  return {
    most_likely_cause: mostLikely,
    what_changed_right_before_failure: changed,
    suggested_next_checks: nextChecks,
    recommended_fix_pack: pack ? { id: pack.id, name: pack.name } : null,
  };
}

function buildIncidentReport(context, reportData, signals, analysis) {
  return {
    generated_at: new Date().toISOString(),
    inputs: context,
    report: reportData || null,
    signals,
    analysis,
  };
}

function setIncidentFixPack(packId, params) {
  incidentFixPackId = packId || null;
  incidentFixPackParams = params || null;
  if (incidentRunFixButton) {
    if (incidentFixPackId) {
      const pack = getActionPackById(incidentFixPackId);
      incidentRunFixButton.disabled = !pack;
      incidentRunFixButton.textContent = pack ? `Run fix pack: ${pack.name}` : "Run fix pack";
    } else {
      incidentRunFixButton.disabled = true;
      incidentRunFixButton.textContent = "Run fix pack";
    }
  }
}

function buildIncidentPackParams(pack, context) {
  if (!pack) return null;
  const saved = getPackParams(pack.id);
  const stepParams = { ...(saved.stepParams || {}) };
  pack.steps.forEach((step) => {
    if (!step.service || !step.action) return;
    const key = `${step.service}.${step.action}`;
    const meta = ACTIONS_UI?.[step.service]?.[step.action];
    if (!meta) return;
    stepParams[key] = stepParams[key] || {};
    meta.fields?.forEach((field) => {
      if (stepParams[key]?.[field.key] !== undefined) return;
      const fieldKey = field.key.toLowerCase();
      if (context.user && (fieldKey.includes("user") || fieldKey.includes("upn"))) {
        stepParams[key][field.key] = context.user;
      }
      if (context.device && fieldKey.includes("device")) {
        stepParams[key][field.key] = context.device;
      }
    });
  });
  return {
    stepParams,
    includeSteps: saved.includeSteps || {},
    dryRun: saved.dryRun || false,
  };
}

async function runIncidentWorkspace() {
  const user = incidentUserInput?.value.trim() || "";
  const device = incidentDeviceInput?.value.trim() || "";
  const symptom = incidentSymptomInput?.value.trim() || "";
  if (!user && !device) {
    showToast("Enter a user or device");
    return;
  }
  const timeframe = getIncidentTimeframe();
  const incident = await createIncident({
    symptom_id: null,
    title: symptom || "Incident workspace",
    description: `${user || "Unknown user"} → ${device || "Unknown device"}`,
  });
  if (incident?.incident_id) {
    activeIncidentId = incident.incident_id;
    renderIncidentReportSelect();
    loadIncidentReportFor(incident.incident_id);
  }
  if (incident?.incident_id) {
    await captureIncidentSnapshots({
      user,
      device,
      symptom,
      symptom_id: null,
      timestamp: new Date().toISOString(),
      incident_id: incident.incident_id,
    });
  }
  const context = {
    user,
    device,
    symptom,
    incident_id: incident?.incident_id || null,
    timeframe: {
      start: timeframe.start.toISOString(),
      end: timeframe.end.toISOString(),
      lookback_hours: timeframe.lookback_hours,
      label: timeframe.label,
    },
  };
  lastIncidentContext = context;
  setOutput("incident", "Running incident workspace...");
  setOutputStatus("incident", {
    state: "running",
    text: "Incident workspace running",
    meta: "Collecting signals",
    running: true,
  });
  try {
    let reportData = null;
    if (user) {
      const reportResponse = await runReportTask("user_audit", {
        user_id: user,
        include_groups: true,
        include_licenses: true,
        include_signins: true,
        include_devices: true,
      });
      if (!reportResponse.ok) {
        throw new Error(reportResponse.error || "User audit failed");
      }
      reportData = reportResponse.data;
      addReportHistory({
        id: `report-${Date.now()}-${Math.random().toString(16).slice(2)}`,
        action: "user_audit",
        label: "User audit (incident)",
        timestamp: Date.now(),
        params: { user_id: user },
        data: reportData,
      });
      await refreshReportHistory();
    }

    const history = getReportHistoryItems();
    const userKey = extractUserKey(reportData);
    const previous = findPreviousUserAudit(history, userKey, Date.now());
    const groupDiff = diffByKey(
      reportData?.memberOf,
      previous?.data?.memberOf,
      (item) => item?.id || item?.displayName,
      (item) => item?.displayName || item?.id
    );
    const licenseDiff = diffByKey(
      reportData?.licenses,
      previous?.data?.licenses,
      (item) => item?.skuId || item?.skuPartNumber,
      (item) => item?.skuPartNumber || item?.skuId
    );

    const signInSummary = summarizeSignIns(reportData?.signIns, timeframe.start, timeframe.end);
    const deviceSummary = {
      count: normalizeList(reportData?.devices).length,
      devices: normalizeList(reportData?.devices).slice(0, 5),
    };

    const graphCheck = await runSystemTask("graph_check", {});
    const graphChecks = graphCheck?.data?.checks || {};
    const graphSummary = summarizeGraphCheck({ ok: graphCheck?.data?.ok, checks: graphChecks });
    const graphExplain = explainGraphHealth({ graph: { checks: graphChecks } });

    const topologyDiff = summarizeTopologyDiff(timeframe.start, timeframe.end);
    const topologySummary = topologyDiff
      ? {
          dhcp_added: topologyDiff?.dhcp?.added?.length || 0,
          dhcp_removed: topologyDiff?.dhcp?.removed?.length || 0,
          dns_added: topologyDiff?.dns?.added?.length || 0,
          dns_removed: topologyDiff?.dns?.removed?.length || 0,
        }
      : null;

    const issues = loadIssues();
    const matchingIssues = issues.filter(
      (issue) =>
        (user && issue.user && issue.user.toLowerCase() === user.toLowerCase()) ||
        (device && issue.device && issue.device.toLowerCase() === device.toLowerCase())
    );

    const signals = {
      signins: signInSummary,
      groups: groupDiff,
      licenses: licenseDiff,
      devices: deviceSummary,
      graph: {
        summary: graphSummary,
        checks: graphChecks,
        explanation: graphExplain,
      },
      topology: topologyDiff
        ? {
            summary: topologySummary,
            diff: topologyDiff,
          }
        : null,
      endpoint_narrative: matchingIssues.length ? matchingIssues : null,
    };

    const analysis = buildIncidentAnalysis(signals, context);
    const report = buildIncidentReport(context, reportData, signals, analysis);
    if (incident?.incident_id) {
      const incidentGraph = await fetchIncidentGraph(incident.incident_id);
      const incidentTimeline = await fetchIncidentTimeline(incident.incident_id);
      report.incident_graph = incidentGraph;
      report.incident_timeline = incidentTimeline;
    }
    setOutput("incident", report);
    setOutputStatus("incident", {
      state: "ok",
      text: "Incident workspace ready",
      meta: "Signals collected",
      running: false,
    });
    setIncidentFixPack(analysis?.recommended_fix_pack?.id, context);
    return report;
  } catch (err) {
    setOutput("incident", `Error: ${err.message}`);
    setOutputStatus("incident", {
      state: "fail",
      text: "Incident workspace failed",
      meta: err.message || "Error",
      running: false,
    });
    setIncidentFixPack(null, null);
  }
  return null;
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
  const objA = a || {};
  const objB = b || {};
  const keys = new Set([...Object.keys(objA), ...Object.keys(objB)]);
  const added = [];
  const removed = [];
  const changed = [];
  keys.forEach((key) => {
    if (!(key in objA)) {
      added.push({ path: key, value: objB[key] });
    } else if (!(key in objB)) {
      removed.push({ path: key, value: objA[key] });
    } else if (JSON.stringify(objA[key]) !== JSON.stringify(objB[key])) {
      changed.push({ path: key, before: objA[key], after: objB[key] });
    }
  });
  return { added, removed, changed };
}

function diffJson(a, b, path = "", depth = 0, maxDepth = 4) {
  const diff = { added: [], removed: [], changed: [] };
  if (depth > maxDepth) {
    if (JSON.stringify(a) !== JSON.stringify(b)) {
      diff.changed.push({ path, before: a, after: b });
    }
    return diff;
  }
  const aIsArray = Array.isArray(a);
  const bIsArray = Array.isArray(b);
  if (aIsArray || bIsArray) {
    const arrA = Array.isArray(a) ? a : [];
    const arrB = Array.isArray(b) ? b : [];
    const mapA = new Map();
    const mapB = new Map();
    let hasStableKey = false;
    arrA.forEach((item, idx) => {
      const key = getDiffKey(item);
      if (key) hasStableKey = true;
      mapA.set(key || `idx-${idx}`, item);
    });
    arrB.forEach((item, idx) => {
      const key = getDiffKey(item);
      if (key) hasStableKey = true;
      mapB.set(key || `idx-${idx}`, item);
    });
    mapB.forEach((value, key) => {
      if (!mapA.has(key)) {
        diff.added.push({ path, key, value });
      } else {
        const before = mapA.get(key);
        if (JSON.stringify(before) !== JSON.stringify(value)) {
          diff.changed.push({ path, key, before, after: value });
        }
      }
    });
    mapA.forEach((value, key) => {
      if (!mapB.has(key)) {
        diff.removed.push({ path, key, value });
      }
    });
    if (!hasStableKey && arrA.length !== arrB.length) {
      diff.changed.push({ path, before: arrA.length, after: arrB.length });
    }
    return diff;
  }
  if (a && b && typeof a === "object" && typeof b === "object") {
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
    keys.forEach((key) => {
      const nextPath = path ? `${path}.${key}` : key;
      if (!(key in a)) {
        diff.added.push({ path: nextPath, value: b[key] });
      } else if (!(key in b)) {
        diff.removed.push({ path: nextPath, value: a[key] });
      } else if (typeof a[key] === "object" && typeof b[key] === "object") {
        const inner = diffJson(a[key], b[key], nextPath, depth + 1, maxDepth);
        diff.added.push(...inner.added);
        diff.removed.push(...inner.removed);
        diff.changed.push(...inner.changed);
      } else if (JSON.stringify(a[key]) !== JSON.stringify(b[key])) {
        diff.changed.push({ path: nextPath, before: a[key], after: b[key] });
      }
    });
    return diff;
  }
  if (JSON.stringify(a) !== JSON.stringify(b)) {
    diff.changed.push({ path, before: a, after: b });
  }
  return diff;
}

function buildReportDiff(a, b) {
  const diff = diffJson(a, b);
  const summary = {
    added: diff.added.length,
    removed: diff.removed.length,
    changed: diff.changed.length,
  };
  return {
    type: "json",
    summary,
    details: {
      added: diff.added.slice(0, 10),
      removed: diff.removed.slice(0, 10),
      changed: diff.changed.slice(0, 10),
    },
  };
}

async function runReportDiff() {
  if (!reportDiffSelectA || !reportDiffSelectB) return;
  const idA = reportDiffSelectA.value;
  const idB = reportDiffSelectB.value;
  if (!idA || !idB) {
    if (reportDiffMeta) reportDiffMeta.textContent = "Select two runs to compare.";
    if (reportDiffOutput) reportDiffOutput.textContent = "";
    return;
  }
  setDiffLoading(reportDiffMeta, reportDiffOutput, reportDiffTriage, "Diff running...");
  const items = getReportHistoryItems();
  const entryA = items.find((entry) => entry.id === idA);
  const entryB = items.find((entry) => entry.id === idB);
  if (!entryA || !entryB) return;
  const cached = getCachedReportDiff(idA, idB);
  const diff = cached || (await fetchSnapshotDiff(idA, idB)) || buildReportDiff(entryA.data, entryB.data);
  if (!cached) {
    cacheReportDiff(idA, idB, diff);
  }
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
  if (reportDiffTriage) {
    renderDiffTriage(reportDiffTriage, diff);
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
    cfgAllowRemoteDangerous,
    sshTargetNameInput,
    sshTargetHostInput,
    sshTargetUserInput,
    sshTargetPortInput,
    sshTargetKeyInput,
    sshTargetTagsInput,
    sshTargetStrictInput,
    sshTargetSaveButton,
    sshTargetClearButton,
    profileSaveButton,
    profileApplyButton,
    profileDeleteButton,
    profileExportButton,
    profileImportButton,
    configImportButton,
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
      body: JSON.stringify({ service: "system", action: "tenant_info", params: { _ui_request_id: generateUiRequestId() } }),
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

function parseCsvList(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter(Boolean);
  return String(value)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatCsvList(list) {
  if (!Array.isArray(list)) return "";
  return list.filter(Boolean).join(", ");
}

function parseZoneMap(value) {
  if (!value) return [];
  const lines = String(value)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const entries = [];
  lines.forEach((line) => {
    const parts = line.split(",").map((part) => part.trim()).filter(Boolean);
    if (!parts.length) return;
    const [subnet, zone, site] = parts;
    if (subnet) {
      entries.push({ subnet, zone: zone || null, site: site || null });
    }
  });
  return entries;
}

function formatZoneMap(entries) {
  if (!Array.isArray(entries)) return "";
  return entries
    .map((entry) => {
      const subnet = entry.subnet || "";
      const zone = entry.zone || "";
      const site = entry.site || "";
      return [subnet, zone, site].filter(Boolean).join(", ");
    })
    .filter(Boolean)
    .join("\n");
}

function parseDiffImpactOverrides(text) {
  const overrides = {};
  if (!text) return overrides;
  String(text)
    .split("\n")
    .forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) return;
      const parts = trimmed.split("=");
      if (parts.length < 2) return;
      const key = parts[0].trim();
      const value = parts.slice(1).join("=").trim().toLowerCase();
      if (!key || !value) return;
      overrides[key] = value;
    });
  return overrides;
}

function formatDiffImpactOverrides(overrides) {
  if (!overrides || typeof overrides !== "object") return "";
  return Object.entries(overrides)
    .map(([key, value]) => `${key} = ${value}`)
    .join("\n");
}

function generateTargetId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `target-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function generateUiRequestId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `ui-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

function normalizeSshTargets(list) {
  const targets = Array.isArray(list) ? list : [];
  return targets
    .filter((item) => item && typeof item === "object" && item.host)
    .map((item) => ({
      id: item.id || generateTargetId(),
      name: item.name || "",
      host: item.host,
      user: item.user || "",
      port: Number.parseInt(item.port, 10) || 22,
      key_path: item.key_path || "",
      strict_host_key_checking: item.strict_host_key_checking !== false,
      tags: Array.isArray(item.tags)
        ? item.tags.filter(Boolean)
        : parseCsvList(item.tags || ""),
    }));
}

function setSshTargets(list) {
  sshTargets = normalizeSshTargets(list);
  renderSshTargets();
  refreshRunnerTargets();
}

function formatSshTargetLabel(target) {
  if (!target) return "Local machine";
  if (target.type === "local") return "Local machine";
  const host = target.host || "unknown";
  const user = target.user ? `${target.user}@` : "";
  const port = target.port ? `:${target.port}` : "";
  return `ssh://${user}${host}${port}`;
}

function readSshTargetForm() {
  return {
    id: sshTargetIdInput?.value || "",
    name: sshTargetNameInput?.value.trim() || "",
    host: sshTargetHostInput?.value.trim() || "",
    user: sshTargetUserInput?.value.trim() || "",
    port: Number.parseInt(sshTargetPortInput?.value || "22", 10) || 22,
    key_path: sshTargetKeyInput?.value.trim() || "",
    strict_host_key_checking: sshTargetStrictInput ? sshTargetStrictInput.checked : true,
    tags: parseCsvList(sshTargetTagsInput?.value || ""),
  };
}

function clearSshTargetForm() {
  if (sshTargetIdInput) sshTargetIdInput.value = "";
  if (sshTargetNameInput) sshTargetNameInput.value = "";
  if (sshTargetHostInput) sshTargetHostInput.value = "";
  if (sshTargetUserInput) sshTargetUserInput.value = "";
  if (sshTargetPortInput) sshTargetPortInput.value = "22";
  if (sshTargetKeyInput) sshTargetKeyInput.value = "";
  if (sshTargetTagsInput) sshTargetTagsInput.value = "";
  if (sshTargetStrictInput) sshTargetStrictInput.checked = true;
}

async function persistSshTargets() {
  if (configLocked) {
    showToast("Config is locked");
    return;
  }
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ssh_targets: sshTargets }),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Failed to save targets");
      return;
    }
    showToast("Remote targets saved");
    await fetchConfig();
  } catch (err) {
    showToast("Failed to save targets");
  }
}

function renderSshTargets() {
  if (!sshTargetList) return;
  sshTargetList.innerHTML = "";
  if (!sshTargets.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No remote targets configured.";
    sshTargetList.appendChild(empty);
    return;
  }
  sshTargets.forEach((target) => {
    const row = document.createElement("div");
    row.classList.add("target-row");
    const meta = document.createElement("div");
    meta.classList.add("target-meta");
    const title = document.createElement("div");
    title.classList.add("target-title");
    title.textContent = target.name || target.host;
    const subtitle = document.createElement("div");
    subtitle.classList.add("target-subtitle");
    const tags = target.tags?.length ? ` • ${target.tags.join(", ")}` : "";
    subtitle.textContent = `${formatSshTargetLabel({ type: "ssh", ...target })}${tags}`;
    meta.appendChild(title);
    meta.appendChild(subtitle);
    const actions = document.createElement("div");
    actions.classList.add("target-actions");
    const edit = document.createElement("button");
    edit.type = "button";
    edit.classList.add("ghost", "small");
    edit.textContent = "Edit";
    edit.addEventListener("click", () => {
      if (sshTargetIdInput) sshTargetIdInput.value = target.id;
      if (sshTargetNameInput) sshTargetNameInput.value = target.name || "";
      if (sshTargetHostInput) sshTargetHostInput.value = target.host || "";
      if (sshTargetUserInput) sshTargetUserInput.value = target.user || "";
      if (sshTargetPortInput) sshTargetPortInput.value = String(target.port || 22);
      if (sshTargetKeyInput) sshTargetKeyInput.value = target.key_path || "";
      if (sshTargetTagsInput) sshTargetTagsInput.value = (target.tags || []).join(", ");
      if (sshTargetStrictInput) sshTargetStrictInput.checked = target.strict_host_key_checking !== false;
      document.getElementById("ssh-targets-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    const test = document.createElement("button");
    test.type = "button";
    test.classList.add("ghost", "small");
    test.textContent = "Test";
    test.addEventListener("click", () => testSshTarget(target));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.classList.add("ghost", "small");
    remove.textContent = "Delete";
    remove.addEventListener("click", async () => {
      sshTargets = sshTargets.filter((entry) => entry.id !== target.id);
      renderSshTargets();
      refreshRunnerTargets();
      await persistSshTargets();
    });
    actions.appendChild(edit);
    actions.appendChild(test);
    actions.appendChild(remove);
    row.appendChild(meta);
    row.appendChild(actions);
    sshTargetList.appendChild(row);
  });
}

async function testSshTarget(target) {
  const execTarget = { type: "ssh", ...target };
  const result = await runSystemTask("ssh_test", { target: execTarget });
  if (!result?.ok) {
    showToast(result?.error || "SSH test failed");
    return;
  }
  const data = result.data || result;
  const host = data?.checks?.hostname || target.host;
  const osInfo = data?.checks?.os || "unknown OS";
  showToast(`SSH OK: ${host} (${osInfo})`);
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
    time_thresholds: {
      warn_ms: Number.parseInt(cfgTimeWarn?.value || "", 10) || undefined,
      high_ms: Number.parseInt(cfgTimeHigh?.value || "", 10) || undefined,
    },
    ntp_servers: parseCsvList(cfgNtpServers?.value || ""),
    cert_stores: parseCsvList(cfgCertStores?.value || ""),
    cert_expiring_days: Number.parseInt(cfgCertExpiring?.value || "", 10) || undefined,
    tls_endpoints: parseCsvList(cfgTlsEndpoints?.value || ""),
    latency_endpoints: parseCsvList(cfgLatencyEndpoints?.value || ""),
    dns_probe_targets: parseCsvList(cfgDnsProbeTargets?.value || ""),
    dns_resolvers: parseCsvList(cfgDnsResolvers?.value || ""),
    enable_public_resolvers: Boolean(cfgPublicResolvers?.checked),
    process_include_command_line: Boolean(cfgProcessCmdline?.checked),
    process_max_items: Number.parseInt(cfgProcessMax?.value || "", 10) || undefined,
    zone_map: parseZoneMap(cfgZoneMap?.value || ""),
    diff_impact_overrides: parseDiffImpactOverrides(cfgDiffImpactOverrides?.value || ""),
    mock_mode: Boolean(cfgMockMode?.checked),
    allow_remote_dangerous: Boolean(cfgAllowRemoteDangerous?.checked),
    ssh_targets: sshTargets,
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
  if (cfgTimeWarn) cfgTimeWarn.value = config.time_thresholds?.warn_ms ?? "";
  if (cfgTimeHigh) cfgTimeHigh.value = config.time_thresholds?.high_ms ?? "";
  if (cfgNtpServers) cfgNtpServers.value = formatCsvList(config.ntp_servers);
  if (cfgCertStores) cfgCertStores.value = formatCsvList(config.cert_stores);
  if (cfgCertExpiring) cfgCertExpiring.value = config.cert_expiring_days ?? "";
  if (cfgTlsEndpoints) cfgTlsEndpoints.value = formatCsvList(config.tls_endpoints);
  if (cfgLatencyEndpoints) cfgLatencyEndpoints.value = formatCsvList(config.latency_endpoints);
  if (cfgDnsProbeTargets) cfgDnsProbeTargets.value = formatCsvList(config.dns_probe_targets);
  if (cfgDnsResolvers) cfgDnsResolvers.value = formatCsvList(config.dns_resolvers);
  if (cfgPublicResolvers) cfgPublicResolvers.checked = Boolean(config.enable_public_resolvers);
  if (cfgProcessCmdline) cfgProcessCmdline.checked = Boolean(config.process_include_command_line);
  if (cfgProcessMax) cfgProcessMax.value = config.process_max_items ?? "";
  if (cfgZoneMap) cfgZoneMap.value = formatZoneMap(config.zone_map);
  if (cfgDiffImpactOverrides) {
    cfgDiffImpactOverrides.value = formatDiffImpactOverrides(config.diff_impact_overrides);
  }
  if (cfgMockMode) cfgMockMode.checked = Boolean(config.mock_mode);
  if (cfgAllowRemoteDangerous) cfgAllowRemoteDangerous.checked = Boolean(config.allow_remote_dangerous);
  setSshTargets(config.ssh_targets || []);
  if (!config.client_secret && cfgClientSecret.placeholder.includes("set")) {
    cfgClientSecret.placeholder = "Enter to update";
  }
}

async function exportEncryptedConfig() {
  const passphrase = configPassphraseInput?.value.trim() || "";
  if (!passphrase && !keychainAvailable) {
    showToast("Passphrase required (keychain unavailable)");
    return;
  }
  try {
    const res = await fetch("/api/config/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        passphrase: passphrase || null,
        use_keychain: !passphrase,
      }),
    });
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Export failed");
      return;
    }
    const filename = `graph-admin-config-${sanitizeFilename(currentTenantId || "export")}.json`;
    downloadJson(data.data, filename);
    showToast("Encrypted config exported");
  } catch (err) {
    showToast("Export failed");
  }
}

function importEncryptedConfigFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const parsed = JSON.parse(reader.result);
      const passphrase = configPassphraseInput?.value.trim() || "";
      if (!passphrase && !keychainAvailable) {
        showToast("Passphrase required (keychain unavailable)");
        return;
      }
      const res = await fetch("/api/config/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          payload: parsed,
          passphrase: passphrase || null,
        }),
      });
      const data = await res.json();
      if (!data.ok) {
        showToast(data.error || "Import failed");
        return;
      }
      await fetchConfig();
      await fetchStatus();
      showToast("Config imported");
    } catch (err) {
      showToast("Import failed");
    }
  };
  reader.readAsText(file);
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

function renderAuditServiceOptions() {
  if (!auditServiceSelect) return;
  const services = Object.keys(ACTIONS_UI || {}).sort();
  auditServiceSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Any";
  auditServiceSelect.appendChild(placeholder);
  services.forEach((service) => {
    const option = document.createElement("option");
    option.value = service;
    option.textContent = formatServiceLabel(service);
    auditServiceSelect.appendChild(option);
  });
}

function buildAuditQuery() {
  return {
    service: auditServiceSelect?.value || "",
    action: auditActionInput?.value.trim() || "",
    ok: auditStatusSelect?.value || "",
    user: auditUserInput?.value.trim() || "",
    query: auditQueryInput?.value.trim() || "",
    since: auditSinceInput?.value || "",
    until: auditUntilInput?.value || "",
    limit: auditLimitSelect?.value || "200",
  };
}

function renderAuditTable(items) {
  if (!auditTableBody) return;
  auditTableBody.innerHTML = "";
  if (!items || !items.length) {
    if (auditEmptyNote) auditEmptyNote.style.display = "block";
    return;
  }
  if (auditEmptyNote) auditEmptyNote.style.display = "none";
  items.forEach((entry) => {
    const row = document.createElement("tr");
    const timestamp = document.createElement("td");
    timestamp.textContent = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "";
    const user = document.createElement("td");
    user.textContent = entry.user || "";
    const service = document.createElement("td");
    service.textContent = entry.service || "";
    const action = document.createElement("td");
    action.textContent = entry.action || "";
    const itemId = document.createElement("td");
    itemId.textContent = entry.item_id || "";
    const status = document.createElement("td");
    status.textContent = entry.ok ? "OK" : "Failed";
    status.classList.add(entry.ok ? "ok" : "warn");
    const detailTd = document.createElement("td");
    const viewBtn = document.createElement("button");
    viewBtn.type = "button";
    viewBtn.classList.add("ghost", "small");
    viewBtn.textContent = "View";
    viewBtn.addEventListener("click", () => showModal("Audit entry", entry, "audit"));
    detailTd.appendChild(viewBtn);

    row.appendChild(timestamp);
    row.appendChild(user);
    row.appendChild(service);
    row.appendChild(action);
    row.appendChild(itemId);
    row.appendChild(status);
    row.appendChild(detailTd);
    auditTableBody.appendChild(row);
  });
}

async function fetchAuditLogs() {
  const query = buildAuditQuery();
  auditState.query = query;
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  try {
    const res = await fetch(`/api/audit?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) {
      showToast(data.error || "Audit log load failed");
      return;
    }
    const items = data.data?.items || [];
    auditState.items = items;
    renderAuditTable(items);
  } catch (err) {
    showToast("Audit log load failed");
  }
}

function exportAuditJson() {
  const items = auditState.items || [];
  downloadJson(items, "audit-log.json");
}

function exportAuditCsv() {
  const items = auditState.items || [];
  const headers = ["timestamp", "user", "host", "service", "action", "item_id", "ok", "error"];
  const rows = [headers.join(",")];
  items.forEach((item) => {
    const row = headers.map((key) => {
      const value = item?.[key];
      if (value === undefined || value === null) return "";
      const text = String(value).replace(/"/g, '""');
      return `"${text}"`;
    });
    rows.push(row.join(","));
  });
  downloadTextFile(rows.join("\n"), "audit-log.csv", "text/csv");
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

async function runSystemTask(action, params, target) {
  const payload = { ...(params || {}) };
  payload._ui_request_id = generateUiRequestId();
  const res = await fetch("/api/task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service: "system", action, params: payload, target }),
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
    fetchSystemStatusSummary();
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

async function runSecurityPosture() {
  setOutput("security", "Running...");
  setOutputStatus("security", {
    state: "running",
    text: "Security posture running",
    meta: "Collecting permissions and boundaries",
    running: true,
  });
  try {
    const response = await runSystemTask("security_posture", {});
    if (!response.ok) {
      setOutput("security", response);
      setOutputStatus("security", {
        state: "fail",
        text: "Security posture failed",
        meta: response.error || "Error",
        running: false,
      });
      return;
    }
    setOutput("security", response.data);
    setOutputStatus("security", {
      state: "ok",
      text: "Security posture ready",
      meta: "Report generated",
      running: false,
    });
  } catch (err) {
    setOutput("security", `Error: ${err.message}`);
    setOutputStatus("security", {
      state: "fail",
      text: "Security posture error",
      meta: err.message || "Error",
      running: false,
    });
  }
}

async function runSmokeTest() {
  if (smokeTestButton) {
    smokeTestButton.disabled = true;
    smokeTestButton.textContent = "Running...";
  }
  const healthCard = document.getElementById("health-card");
  if (healthCard) healthCard.classList.add("loading");
  if (healthSpinner) healthSpinner.classList.add("active");
  if (healthStatusText) {
    healthStatusText.textContent = `Smoke test started ${new Date().toLocaleTimeString()}`;
  }
  if (healthBreakdown) {
    healthBreakdown.open = true;
  }
  resetHealthBreakdown();
  setOutputStatus("health", {
    state: "running",
    text: "Smoke test running",
    meta: "",
    running: true,
  });
  startOutputTimer("health", "Smoke test");
  setHealthProgress([
    { label: "Graph", text: "Running smoke test", state: "warn" },
    { label: "PowerShell", text: "Pending", state: "warn" },
  ]);
  setOutput("health", "Running smoke test... Please wait.");
  try {
    const response = await runSystemTask("smoke_test", { services: GRAPH_HEALTH_SERVICES });
    if (!response.ok) {
      throw new Error(response.error || "Smoke test failed");
    }
    const report = response.data || {};
    const graphChecks = report.graph?.checks || {};
    const psData = report.powershell || { ok: false, modules: {} };

    Object.entries(graphChecks).forEach(([service, check]) => {
      const label = formatServiceLabel(service);
      const status = Number(check?.status || 0);
      const latencyMs = Number(check?.latency_ms ?? check?.latencyMs);
      const sla = getLatencySla(Number.isFinite(latencyMs) ? latencyMs : undefined, check?.ok);
      let statusLabel = "Failed";
      let statusState = "fail";
      let statusMeta = "";
      if (check?.ok) {
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
    });

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

    const graphSummary = summarizeGraphCheck({ ok: report.graph?.ok, checks: graphChecks });
    const psSummary = summarizePowerShellCheck(psData);
    setHealthProgress([
      { label: "Graph", text: graphSummary.text, state: graphSummary.state },
      { label: "PowerShell", text: psSummary.text, state: psSummary.state },
    ]);

    setOutput("health", report);
    addActivity("Ran: Smoke test");
    const finalState =
      graphSummary.state === "fail" || psSummary.state === "fail"
        ? "fail"
        : graphSummary.state === "warn" || psSummary.state === "warn"
          ? "warn"
          : "ok";
    const elapsed = outputStartTimes.has("health")
      ? formatElapsed(performance.now() - outputStartTimes.get("health"))
      : "";
    setOutputStatus("health", {
      state: finalState,
      text: "Smoke test complete",
      meta: elapsed ? `Duration ${elapsed}` : "",
      running: false,
    });
    if (healthStatusText) {
      healthStatusText.textContent = finalState === "ok" ? "Smoke test complete" : "Smoke test completed with issues";
    }
    showToast("Smoke test complete");
  } catch (err) {
    setOutput("health", `Error: ${err.message}`);
    addActivity("Smoke test error");
    if (healthStatusText) healthStatusText.textContent = "Smoke test error";
    setHealthProgress([
      { label: "Graph", text: "Error", state: "fail" },
      { label: "PowerShell", text: "Error", state: "fail" },
    ]);
    upsertHealthListItem(healthGraphList, "graph-error", "Graph", "Error", "fail", err.message);
    upsertHealthListItem(healthPowerShellList, "ps-error", "PowerShell", "Error", "fail", err.message);
    setOutputStatus("health", {
      state: "fail",
      text: "Smoke test error",
      meta: err.message || "Error",
      running: false,
    });
  } finally {
    stopOutputTimer("health");
    if (smokeTestButton) {
      smokeTestButton.disabled = false;
      smokeTestButton.textContent = "Run smoke test";
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

async function preflightAction(service, action, target) {
  if (service === "system") return { ok: true };
  const response = await runSystemTask("action_preflight", { service, action, target });
  if (response?.ok && response.data) {
    return response.data;
  }
  const errorText = String(response?.error || "");
  const fallbackAllowed = errorText.includes("Unknown action") || errorText.includes("action_preflight");
  if (!fallbackAllowed) {
    return { ok: false, data: response };
  }
  const meta = ACTIONS_UI?.[service]?.[action];
  if (!meta) return { ok: true };
  if (target && target.type === "ssh") {
    return { ok: true, warning: { message: "Remote preflight skipped for SSH targets." } };
  }
  const targetService = meta.preflightService || service;
  if (meta.mode === "powershell") {
    return preflightPowerShell(targetService);
  }
  if (meta.mode === "graph") {
    return preflightGraph(targetService);
  }
  return { ok: true };
}

function formatPreflightDiagnostics(details) {
  const diagnostics = Array.isArray(details?.diagnostics) ? details.diagnostics : [];
  if (!diagnostics.length) return null;
  return diagnostics
    .map((diag) => diag?.message || diag?.type || "Preflight diagnostic")
    .filter(Boolean)
    .join("\n");
}

function handlePreflightFailure(service, action, details) {
  const label = activityLabel(service, action);
  const summary = formatPreflightDiagnostics(details);
  setOutput(service, {
    ok: false,
    error: "Preflight failed",
    summary,
    diagnostics: details?.diagnostics || null,
    checks: details?.checks || null,
    capability: details?.capability || null,
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

function shouldIncludePackStep(step, includeSteps) {
  if (!step.optional) return true;
  const stepKey = `${step.service}.${step.action}`;
  if (includeSteps?.[stepKey] !== undefined) {
    return includeSteps[stepKey] !== false;
  }
  if (step.defaultInclude === false) return false;
  return true;
}

function resolveFirstDomainController(context) {
  const list = context["domaincontroller.list_domain_controllers"];
  if (Array.isArray(list) && list.length) {
    const entry = list.find((row) => row?.hostname || row?.HostName || row?.name);
    if (entry) {
      return entry.hostname || entry.HostName || entry.name;
    }
  }
  const nltest = context["domaincontroller.list_dcs_nltest"];
  if (Array.isArray(nltest) && nltest.length) {
    const entry = nltest.find((row) => row?.hostname || row?.name);
    if (entry) return entry.hostname || entry.name;
  }
  return null;
}

function applyPackAutoParams(step, params, context) {
  const resolved = { ...(params || {}) };
  if (step?.service === "domaincontroller" && step?.action === "show_replication_partners") {
    if (!resolved.dc) {
      const dc = resolveFirstDomainController(context);
      if (dc) {
        resolved.dc = dc;
      }
    }
  }
  return resolved;
}

async function runActionPack(pack, options = {}) {
  if (actionPackState.has(pack.id)) {
    showToast("Action pack already running");
    return;
  }
  const stepParams = options.stepParams || getPackParams(pack.id).stepParams || {};
  const includeSteps = options.includeSteps || getPackParams(pack.id).includeSteps || {};
  const dryRun = options.dryRun ?? getPackParams(pack.id).dryRun ?? false;
  const state = { cancelled: false, controller: null };
  actionPackState.set(pack.id, state);
  setActionPackRunning(pack.id, true);
  const packStart = performance.now();
  let hadFailures = false;
  let stoppedEarly = false;
  let failedStep = null;
  const packResults = [];
  const runParamsSnapshot = { stepParams, includeSteps, dryRun };
  const packContext = {};
  const packSubjects = deriveSubjectsFromPack(pack, stepParams);
  if (packSubjects.length) {
    await captureSnapshots(packSubjects, "core", {
      source: "action_pack",
      pack_id: pack.id,
      pack_name: pack.name,
      phase: "pre",
    });
  }
  for (const step of pack.steps) {
    if (state.cancelled) {
      addActivity(`Cancelled pack: ${pack.name}`);
      showToast("Action pack cancelled");
      break;
    }
    if (step.type === "note") {
      addActivity(`Note: ${step.label || pack.name}`);
      continue;
    }
    const label = step.label || activityLabel(step.service, step.action);
    if (!shouldIncludePackStep(step, includeSteps)) {
      addActivity(`Skipped: ${label}`);
      continue;
    }
    if (dryRun && !step.safe) {
      addActivity(`Dry-run: skipped ${label}`);
      continue;
    }
    const stepKey = `${step.service}.${step.action}`;
    const override = stepParams[stepKey] || {};
    const defaults = getActionPackStepDefaults(pack, step) || {};
    const params = { ...defaults, ...(step.params || {}), ...(override?.params || {}), ...override };
    const resolvedParams = applyPackAutoParams(step, params, packContext);
    const controller = new AbortController();
    state.controller = controller;
    const startedAt = performance.now();
    const result = await runAction(step.service, step.action, resolvedParams, {
      controller,
      track: false,
    });
    const elapsedMs = performance.now() - startedAt;
    const artifact = extractArtifact(result?.data);
    packResults.push({
      service: step.service,
      action: step.action,
      label,
      params: resolvedParams,
      ok: Boolean(result?.ok),
      data: result?.ok ? result.data : null,
      error: result?.ok ? null : result?.data || result?.error || null,
      elapsed_ms: Math.round(elapsedMs),
      artifact: artifact || null,
    });
    if (result?.ok) {
      packContext[`${step.service}.${step.action}`] = result.data;
    }
    if (state.cancelled || result?.cancelled) {
      addActivity(`Cancelled pack: ${pack.name}`);
      showToast("Action pack cancelled");
      break;
    }
    if (!result?.ok) {
      hadFailures = true;
      if (!failedStep) failedStep = label;
      const continueRun = await confirmModal({
        title: "Step failed",
        message: `Step failed: ${label}. Continue?`,
        confirmLabel: "Continue",
        cancelLabel: "Stop",
      });
      if (!continueRun) {
        showToast("Action pack stopped");
        stoppedEarly = true;
        break;
      }
    }
  }
  if (!state.cancelled && packSubjects.length) {
    await captureSnapshots(packSubjects, "core", {
      source: "action_pack",
      pack_id: pack.id,
      pack_name: pack.name,
      phase: "post",
    });
  }
  actionPackState.delete(pack.id);
  setActionPackRunning(pack.id, false);
  const status = state.cancelled
    ? "cancelled"
    : dryRun
      ? "dry-run"
      : stoppedEarly
        ? "stopped"
        : hadFailures
          ? "completed-with-errors"
          : "completed";
  const durationMs = Math.round(performance.now() - packStart);
  const resultSummary = packResults.map((entry) => ({
    service: entry.service,
    action: entry.action,
    label: entry.label,
    ok: entry.ok,
    elapsed_ms: entry.elapsed_ms,
    error: entry.ok ? null : entry.error || "Step failed",
  }));
  addActionPackHistory({
    packId: pack.id,
    pack_name: pack.name,
    timestamp: Date.now(),
    status,
    duration_ms: durationMs,
    failed_step: failedStep,
    result_summary: resultSummary,
    stepParams: runParamsSnapshot.stepParams,
    includeSteps: runParamsSnapshot.includeSteps,
    dryRun: runParamsSnapshot.dryRun,
  });
  if (selectedPackId === pack.id) {
    renderActionPackLastRun(pack, actionPackLastRun);
  }
  renderActionPacks();
  if (!state.cancelled) {
    showToast(dryRun ? "Action pack dry-run completed" : "Action pack completed");
  }
  if (!state.cancelled && pack.bundleOnComplete && packResults.length) {
    exportActionPackBundle(pack, packResults, runParamsSnapshot, status);
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
    if (grid.dataset.skipTiles === "true") return;
    applyTileLayout(grid);
    grid.querySelectorAll(".card").forEach((card) => {
      card.classList.add("tile");
      setupTileControls(card);
    });
    setupTileDragging(grid);
  });
}

const WORKSPACE_STORAGE_KEY = "gas.workspaces";
const ACTIVE_WORKSPACE_KEY = "gas.active_workspace";

const WORKSPACE_TILE_OVERRIDES = {
  "status.summary": {
    title: "System status",
    description: "Completeness, warnings, and readiness signals.",
    category: "Observe",
    capabilities: ["Graph", "PowerShell"],
    risk: "safe",
    source_panel: "dashboard",
  },
  "snapshots.recent": {
    title: "Recent snapshots",
    description: "Latest captures and subjects.",
    category: "Observe",
    capabilities: ["Local"],
    risk: "safe",
    source_panel: "dashboard",
  },
  "incidents.ledger": {
    title: "Incident ledger",
    description: "Latest incidents captured in the backend.",
    category: "Observe",
    capabilities: ["Local"],
    risk: "safe",
    source_panel: "incidents",
  },
  "incidents.intake": {
    title: "Incident intake",
    description: "Create an incident and run workspace triage.",
    category: "Act",
    capabilities: ["Graph", "PowerShell"],
    risk: "caution",
    source_panel: "incidents",
  },
  "snapshots.history": {
    title: "Snapshot history",
    description: "Per-subject snapshot timeline and quality.",
    category: "Analyze",
    capabilities: ["Local"],
    risk: "safe",
    source_panel: "reports",
  },
  "entra.user_lookup": {
    title: "Entra user lookup",
    description: "Fetch a user by UPN or ID.",
    category: "Observe",
    capabilities: ["Graph"],
    risk: "safe",
    source_panel: "entra",
  },
};

const TILE_CATEGORY_LABELS = {
  observe: "Observe",
  analyze: "Analyze",
  act: "Act",
  configure: "Configure",
  learn: "Help",
};
const TILE_CATEGORY_ORDER = ["Observe", "Act", "Analyze", "Configure", "Help", "Other"];

const GRAPH_PANELS = new Set([
  "exchange",
  "onedrive",
  "sharepoint",
  "teams",
  "entra",
  "azure",
  "defender",
  "powerplatform",
  "purview",
]);

const POWERSHELL_PANELS = new Set([
  "localad",
  "endpoint",
  "domaincontroller",
  "printers",
  "network",
  "fileserver",
  "eventlogs",
  "registry",
  "time",
  "certificates",
  "processes",
  "baselines",
  "remote_workflows",
]);

const SSH_PANELS = new Set(["ssh", "remote_workflows"]);

function normalizeWorkspaceKey(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function inferCapabilities(panel) {
  const caps = new Set();
  if (GRAPH_PANELS.has(panel)) caps.add("Graph");
  if (POWERSHELL_PANELS.has(panel)) caps.add("PowerShell");
  if (SSH_PANELS.has(panel)) caps.add("SSH");
  if (!caps.size) caps.add("Local");
  return Array.from(caps);
}

function inferRisk(modeKey) {
  if (modeKey === "act") return "caution";
  if (modeKey === "configure") return "caution";
  return "safe";
}

function buildTileRegistry() {
  const registry = {};
  const used = new Set();
  const counts = {};
  document.querySelectorAll(".card[data-panel]").forEach((card) => {
    if (card.closest(".workspace-grid")) return;
    const panel = card.dataset.panel || "dashboard";
    const title = card.querySelector(".card-title")?.textContent?.trim() || panel;
    const description = card.querySelector(".card-subtitle")?.textContent?.trim() || "";
    const explicit = card.dataset.workspaceBlock || card.id || "";
    const base = explicit || `${panel}.${normalizeWorkspaceKey(title) || "tile"}`;
    const nextCount = (counts[base] || 0) + 1;
    counts[base] = nextCount;
    const id = used.has(base) || nextCount > 1 ? `${base}.${nextCount}` : base;
    used.add(id);
    card.dataset.workspaceBlock = id;
    const modeKey = MODE_MAP[panel] || "observe";
    registry[id] = {
      id,
      title: title || panel,
      description: description || "",
      category: TILE_CATEGORY_LABELS[modeKey] || "Other",
      capabilities: inferCapabilities(panel),
      risk: inferRisk(modeKey),
      source_panel: panel,
      source_card_id: card.id || null,
      config_sensitive: modeKey === "configure",
      workspace_allowed: true,
    };
  });
  Object.entries(WORKSPACE_TILE_OVERRIDES).forEach(([id, override]) => {
    registry[id] = { ...(registry[id] || {}), ...override, id };
  });
  return registry;
}

const TILE_REGISTRY = buildTileRegistry();

function getWorkspaceBlock(blockType) {
  return TILE_REGISTRY[blockType] || null;
}

function listWorkspaceBlocks() {
  return Object.values(TILE_REGISTRY).filter((block) => block && block.workspace_allowed !== false);
}

async function addWorkspaceTileFromBlock(block, options = {}) {
  if (!block) return;
  if (block.risk === "dangerous") {
    const ok = await confirmModal({
      title: "Add dangerous tile?",
      message: "This tile can run risky or destructive actions. Add it to the workspace?",
      confirmLabel: "Add anyway",
      cancelLabel: "Cancel",
      danger: true,
    });
    if (!ok) return;
  }
  const blockParams = { ...(options.block_params || {}) };
  if (block.config_sensitive && !("read_only" in blockParams)) {
    blockParams.read_only = true;
  }
  addWorkspaceTile(block.id, { ...options, block_params: blockParams });
}

const WORKSPACE_TEMPLATES = [
  {
    id: "workspace-user-issues",
    name: "User issues workspace",
    description: "Incident intake plus snapshot and Entra context.",
    tiles: ["incidents.intake", "incidents.ledger", "snapshots.recent", "entra.user_lookup", "status.summary"],
  },
  {
    id: "workspace-endpoint-triage",
    name: "Network/endpoint triage",
    description: "Snapshot visibility and system readiness.",
    tiles: ["status.summary", "snapshots.recent", "incidents.ledger"],
  },
  {
    id: "workspace-cloud-identity",
    name: "Cloud identity & access",
    description: "Entra lookup with incident context.",
    tiles: ["entra.user_lookup", "incidents.ledger", "status.summary"],
  },
];

function generateWorkspaceId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `workspace-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function generateWorkspaceTileId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `tile-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`;
}

function loadWorkspaces() {
  try {
    const raw = localStorage.getItem(WORKSPACE_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    return [];
  }
}

function saveWorkspaces(workspaces) {
  localStorage.setItem(WORKSPACE_STORAGE_KEY, JSON.stringify(workspaces || []));
}

function getActiveWorkspaceId() {
  return localStorage.getItem(ACTIVE_WORKSPACE_KEY) || "";
}

function setActiveWorkspaceId(id) {
  if (id) {
    localStorage.setItem(ACTIVE_WORKSPACE_KEY, id);
  } else {
    localStorage.removeItem(ACTIVE_WORKSPACE_KEY);
  }
}

function getWorkspaceById(id) {
  return loadWorkspaces().find((workspace) => workspace.id === id) || null;
}

function upsertWorkspace(workspace) {
  const list = loadWorkspaces();
  const idx = list.findIndex((item) => item.id === workspace.id);
  const next = { ...workspace, updated_at: new Date().toISOString() };
  if (idx >= 0) {
    list[idx] = next;
  } else {
    list.push(next);
  }
  saveWorkspaces(list);
  return next;
}

function deleteWorkspace(id) {
  const list = loadWorkspaces().filter((item) => item.id !== id);
  saveWorkspaces(list);
}

function buildWorkspaceFromTemplate(template) {
  const now = new Date().toISOString();
  const tiles = template.tiles.map((block) => ({
    tile_id: generateWorkspaceTileId(),
    block_type: block,
    block_params: {},
    pinned_state: null,
  }));
  return {
    id: generateWorkspaceId(),
    name: template.name,
    description: template.description || "",
    created_at: now,
    updated_at: now,
    layout: { order: tiles.map((tile) => tile.tile_id), spans: {} },
    tiles,
  };
}

function createWorkspace(name = "New workspace") {
  const now = new Date().toISOString();
  return {
    id: generateWorkspaceId(),
    name,
    description: "",
    created_at: now,
    updated_at: now,
    layout: { order: [], spans: {} },
    tiles: [],
  };
}

async function getSystemStatusSummaryData() {
  try {
    const res = await fetch("/api/status/summary");
    return await res.json();
  } catch (err) {
    return null;
  }
}

function renderWorkspaceSelect() {
  if (!workspaceSelect) return;
  const workspaces = loadWorkspaces();
  workspaceSelect.innerHTML = "";
  if (!workspaces.length) {
    workspaceSelect.innerHTML = "";
    setActiveWorkspaceId("");
    return;
  }
  workspaces.forEach((workspace) => {
    const option = document.createElement("option");
    option.value = workspace.id;
    option.textContent = workspace.name || "Untitled workspace";
    workspaceSelect.appendChild(option);
  });
  const activeId = getActiveWorkspaceId();
  if (activeId && workspaces.some((item) => item.id === activeId)) {
    workspaceSelect.value = activeId;
  } else if (workspaces.length) {
    workspaceSelect.value = workspaces[0].id;
    setActiveWorkspaceId(workspaces[0].id);
  }
}

function renderWorkspaceTemplates() {
  if (!workspaceTemplates) return;
  workspaceTemplates.innerHTML = "";
  WORKSPACE_TEMPLATES.forEach((template) => {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.add("ghost", "small");
    button.textContent = template.name;
    button.addEventListener("click", () => {
      const workspace = buildWorkspaceFromTemplate(template);
      upsertWorkspace(workspace);
      setActiveWorkspaceId(workspace.id);
      renderWorkspaces();
      showToast("Workspace created");
    });
    workspaceTemplates.appendChild(button);
  });
}

function renderWorkspaceEmptyState() {
  if (!workspaceEmpty) return;
  const workspaces = loadWorkspaces();
  workspaceEmpty.classList.toggle("active", !workspaces.length);
  if (workspaceGrid) {
    workspaceGrid.style.display = workspaces.length ? "grid" : "none";
  }
}

function setWorkspaceTileSpan(card, span) {
  card.classList.remove("span-1", "span-2", "span-3");
  card.classList.add(`span-${span}`);
  const resizeButton = card.querySelector(".tile-resize");
  if (resizeButton) resizeButton.textContent = `${span}/3`;
  persistWorkspaceLayout();
}

function persistWorkspaceLayout() {
  if (!workspaceGrid) return;
  const activeId = getActiveWorkspaceId();
  if (!activeId) return;
  const workspace = getWorkspaceById(activeId);
  if (!workspace) return;
  const order = [];
  const spans = {};
  workspaceGrid.querySelectorAll(".workspace-tile").forEach((card) => {
    const tileId = card.dataset.tileId;
    if (!tileId) return;
    order.push(tileId);
    spans[tileId] = Number(card.className.match(/span-(\d)/)?.[1] || 1);
  });
  workspace.layout = { order, spans };
  upsertWorkspace(workspace);
}

function applyWorkspaceLayout(workspace) {
  if (!workspaceGrid || !workspace) return;
  const cards = Array.from(workspaceGrid.querySelectorAll(".workspace-tile"));
  const map = new Map(cards.map((card) => [card.dataset.tileId, card]));
  const ordered = [];
  (workspace.layout?.order || []).forEach((tileId) => {
    const card = map.get(tileId);
    if (card) {
      ordered.push(card);
      map.delete(tileId);
    }
  });
  map.forEach((card) => ordered.push(card));
  ordered.forEach((card) => {
    workspaceGrid.appendChild(card);
    const span = workspace.layout?.spans?.[card.dataset.tileId] || getInitialSpan(card);
    card.classList.add("tile");
    setWorkspaceTileSpan(card, span);
  });
}

function setupWorkspaceTileControls(card) {
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
  const span = getInitialSpan(card);
  resize.textContent = `${span}/3`;
  resize.addEventListener("click", () => {
    const current = Number(card.className.match(/span-(\d)/)?.[1] || span);
    const next = current === 3 ? 1 : current + 1;
    setWorkspaceTileSpan(card, next);
  });

  controls.appendChild(handle);
  controls.appendChild(resize);

  const header = card.querySelector(".card-header");
  if (header) {
    let actions = header.querySelector(".card-actions");
    if (!actions) {
      actions = document.createElement("div");
      actions.classList.add("card-actions");
      header.appendChild(actions);
    }
    controls.classList.add("inline");
    actions.appendChild(controls);
  } else {
    card.appendChild(controls);
  }
}

function setupWorkspaceDragging() {
  if (!workspaceGrid) return;
  if (!workspaceGrid.dataset.dragBound) {
    workspaceGrid.dataset.dragBound = "true";
    workspaceGrid.addEventListener("dragover", (event) => {
      event.preventDefault();
      const dragging = workspaceGrid._dragging;
      if (!dragging) return;
      const target = event.target.closest(".workspace-tile");
      if (!target || target === dragging) return;
      const rect = target.getBoundingClientRect();
      const before = event.clientY < rect.top + rect.height / 2;
      workspaceGrid.insertBefore(dragging, before ? target : target.nextSibling);
    });
    workspaceGrid.addEventListener("drop", (event) => {
      event.preventDefault();
      if (workspaceGrid._dragging) {
        persistWorkspaceLayout();
      }
    });
  }
  workspaceGrid.querySelectorAll(".workspace-tile").forEach((card) => {
    card.setAttribute("draggable", "false");
    const handle = card.querySelector(".tile-handle");
    if (!handle) return;
    if (handle.dataset.dragBound === "true") return;
    handle.dataset.dragBound = "true";
    handle.setAttribute("draggable", "true");
    handle.addEventListener("dragstart", (event) => {
      workspaceGrid._dragging = card;
      card.classList.add("dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.dataset.tileId || "");
      event.dataTransfer.setDragImage(card, 20, 20);
    });
    handle.addEventListener("dragend", () => {
      if (workspaceGrid._dragging) {
        workspaceGrid._dragging.classList.remove("dragging");
        workspaceGrid._dragging = null;
      }
    });
  });
}

async function renderWorkspaceStatus(container) {
  const payload = await getSystemStatusSummaryData();
  container.innerHTML = "";
  const data =
    payload && typeof payload === "object" && payload.ok !== undefined && payload.data
      ? payload.data
      : payload;
  if (!data || typeof data !== "object") {
    container.textContent = "Status summary unavailable.";
    return;
  }
  const grid = document.createElement("div");
  grid.classList.add("status-grid");
  const items = [
    [
      "Completeness",
      data.completeness_percent !== null && data.completeness_percent !== undefined
        ? `${data.completeness_percent}%`
        : "--",
    ],
    ["Warnings", data.warnings_count ?? 0],
    ["Last snapshot", formatRelativeTime(data.last_snapshot_at)],
    ["Graph readiness", data.graph_ready ? "Ready" : "Not ready"],
    ["PowerShell readiness", data.powershell_ready ? "Ready" : "Not ready"],
  ];
  items.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.classList.add("status-item");
    const l = document.createElement("div");
    l.classList.add("status-label");
    l.textContent = label;
    const v = document.createElement("div");
    v.classList.add("status-value");
    v.textContent = value;
    item.appendChild(l);
    item.appendChild(v);
    grid.appendChild(item);
  });
  container.appendChild(grid);
}

async function renderWorkspaceRecentSnapshots(container) {
  const data = await getSystemStatusSummaryData();
  container.innerHTML = "";
  if (!data || !Array.isArray(data.recent_snapshots) || !data.recent_snapshots.length) {
    const note = document.createElement("div");
    note.classList.add("note");
    note.textContent = "No snapshots captured yet.";
    container.appendChild(note);
    return;
  }
  const list = document.createElement("ul");
  list.classList.add("history-list");
  data.recent_snapshots.forEach((snap) => {
    const item = document.createElement("li");
    item.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = snap.label || snap.kind || snap.canonical_id;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = snap.captured_at ? new Date(snap.captured_at).toLocaleString() : "";
    item.appendChild(title);
    item.appendChild(meta);
    list.appendChild(item);
  });
  container.appendChild(list);
}

async function renderWorkspaceIncidentLedger(container) {
  container.innerHTML = "";
  const incidents = await fetchIncidents();
  if (!incidents.length) {
    const note = document.createElement("div");
    note.classList.add("note");
    note.textContent = "No incidents recorded.";
    container.appendChild(note);
    return;
  }
  const list = document.createElement("div");
  list.classList.add("history-list");
  incidents.slice(0, 6).forEach((incident) => {
    const row = document.createElement("div");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = incident.title || incident.symptom_id || incident.incident_id;
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    const when = incident.created_at ? new Date(incident.created_at).toLocaleString() : "Unknown time";
    meta.textContent = `Status: ${incident.status || "open"} · ${when}`;
    row.appendChild(title);
    row.appendChild(meta);
    list.appendChild(row);
  });
  container.appendChild(list);
}

function renderWorkspaceIncidentIntake(container) {
  container.innerHTML = "";
  const form = document.createElement("div");
  form.classList.add("workspace-intake");
  form.innerHTML = `
    <label>
      User
      <input type="text" class="workspace-incident-user" placeholder="user@contoso.com" />
    </label>
    <label>
      Device
      <input type="text" class="workspace-incident-device" placeholder="DEVICE-01" />
    </label>
    <label class="workspace-wide">
      Symptom
      <input type="text" class="workspace-incident-symptom" placeholder="Describe the issue" />
    </label>
  `;
  const actions = document.createElement("div");
  actions.classList.add("runner-actions");
  const openBtn = document.createElement("button");
  openBtn.type = "button";
  openBtn.classList.add("ghost", "small");
  openBtn.textContent = "Open incident workspace";
  const runBtn = document.createElement("button");
  runBtn.type = "button";
  runBtn.classList.add("primary", "small");
  runBtn.textContent = "Run workspace";
  actions.appendChild(openBtn);
  actions.appendChild(runBtn);
  container.appendChild(form);
  container.appendChild(actions);

  const userInput = form.querySelector(".workspace-incident-user");
  const deviceInput = form.querySelector(".workspace-incident-device");
  const symptomInput = form.querySelector(".workspace-incident-symptom");

  openBtn.addEventListener("click", () => {
    if (incidentUserInput) incidentUserInput.value = userInput.value;
    if (incidentDeviceInput) incidentDeviceInput.value = deviceInput.value;
    if (incidentSymptomInput) incidentSymptomInput.value = symptomInput.value;
    setSection("incidents", { scrollTarget: "incident-workspace" });
  });

  runBtn.addEventListener("click", () => {
    if (incidentUserInput) incidentUserInput.value = userInput.value;
    if (incidentDeviceInput) incidentDeviceInput.value = deviceInput.value;
    if (incidentSymptomInput) incidentSymptomInput.value = symptomInput.value;
    setSection("incidents", { scrollTarget: "incident-workspace" });
    runIncidentWorkspace();
  });
}

async function renderWorkspaceSnapshotHistory(container, tile) {
  container.innerHTML = "";
  const subjectSelect = document.createElement("select");
  subjectSelect.classList.add("workspace-subject-select");
  const entities = await fetchSnapshotEntities();
  if (!entities.length) {
    const note = document.createElement("div");
    note.classList.add("note");
    note.textContent = "No snapshot subjects yet.";
    container.appendChild(note);
    return;
  }
  entities.forEach((entity) => {
    const option = document.createElement("option");
    option.value = entity.canonical_id;
    option.textContent = entity.display_name || entity.canonical_id;
    subjectSelect.appendChild(option);
  });
  const saved = tile.block_params?.canonical_id;
  if (saved && entities.some((entity) => entity.canonical_id === saved)) {
    subjectSelect.value = saved;
  }
  container.appendChild(subjectSelect);
  const list = document.createElement("div");
  list.classList.add("history-list");
  container.appendChild(list);

  const renderHistory = async (canonicalId) => {
    list.innerHTML = "";
    const items = await fetchSnapshotHistory(canonicalId, 5);
    if (!items.length) {
      const note = document.createElement("div");
      note.classList.add("note");
      note.textContent = "No snapshots for this subject.";
      list.appendChild(note);
      return;
    }
    items.forEach((snap) => {
      const row = document.createElement("div");
      row.classList.add("history-item");
      const title = document.createElement("div");
      title.classList.add("history-title");
      title.textContent = snap.profile || snap.snapshot_id;
      const meta = document.createElement("div");
      meta.classList.add("history-meta");
      meta.textContent = snap.captured_at ? new Date(snap.captured_at).toLocaleString() : "";
      row.appendChild(title);
      row.appendChild(meta);
      list.appendChild(row);
    });
  };

  subjectSelect.addEventListener("change", () => {
    const value = subjectSelect.value;
    tile.block_params = { ...(tile.block_params || {}), canonical_id: value };
    updateWorkspaceTile(tile.tile_id, { block_params: tile.block_params });
    renderHistory(value);
  });
  renderHistory(subjectSelect.value);
}

async function renderWorkspaceEntraLookup(container, tile) {
  container.innerHTML = "";
  const form = document.createElement("div");
  form.classList.add("workspace-intake");
  form.innerHTML = `
    <label class="workspace-wide">
      User UPN or ID
      <input type="text" class="workspace-entra-user" placeholder="user@contoso.com" />
    </label>
  `;
  const actions = document.createElement("div");
  actions.classList.add("runner-actions");
  const runBtn = document.createElement("button");
  runBtn.type = "button";
  runBtn.classList.add("primary", "small");
  runBtn.textContent = "Lookup user";
  actions.appendChild(runBtn);
  const output = document.createElement("pre");
  output.classList.add("output");
  container.appendChild(form);
  container.appendChild(actions);
  container.appendChild(output);

  const input = form.querySelector(".workspace-entra-user");
  if (tile.block_params?.user_id) input.value = tile.block_params.user_id;

  runBtn.addEventListener("click", async () => {
    const userId = input.value.trim();
    if (!userId) {
      showToast("Enter a user identifier");
      return;
    }
    tile.block_params = { ...(tile.block_params || {}), user_id: userId };
    updateWorkspaceTile(tile.tile_id, { block_params: tile.block_params });
    output.textContent = "Loading...";
    try {
      const res = await fetch("/api/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service: "entra", action: "get_user", params: { id: userId, _ui_request_id: generateUiRequestId() } }),
      });
      const data = await res.json();
      output.textContent = JSON.stringify(data.data || data, null, 2);
    } catch (err) {
      output.textContent = "Lookup failed.";
    }
  });
}

function findWorkspaceSourceCard(block) {
  if (!block) return null;
  if (block.source_card_id) {
    const byId = document.getElementById(block.source_card_id);
    if (byId) return byId;
  }
  if (block.id) {
    const byBlock = document.querySelector(`.card[data-workspace-block="${block.id}"]`);
    if (byBlock) return byBlock;
  }
  if (block.source_panel) {
    return document.querySelector(`.card[data-panel="${block.source_panel}"]`) || null;
  }
  return null;
}

function sanitizeWorkspaceClone(clone, block, tile) {
  clone.classList.add("workspace-embed");
  clone.classList.remove("tile");
  clone.removeAttribute("id");
  clone.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
  clone.querySelectorAll(".tile-controls").forEach((el) => el.remove());
  clone.querySelectorAll(".card-actions").forEach((el) => el.remove());
  const header = clone.querySelector(".card-header");
  if (header) header.remove();
  clone.querySelectorAll("[data-workspace-block]").forEach((el) => el.removeAttribute("data-workspace-block"));
  const readonly = block?.config_sensitive || tile?.block_params?.read_only;
  clone.querySelectorAll("button, input, select, textarea").forEach((el) => {
    el.disabled = true;
    el.setAttribute("aria-disabled", "true");
  });
  if (readonly) {
    const banner = document.createElement("div");
    banner.classList.add("workspace-readonly-banner");
    banner.textContent = "Read-only in Workspaces. Use Settings to edit configuration.";
    clone.prepend(banner);
  } else {
    const banner = document.createElement("div");
    banner.classList.add("workspace-readonly-banner");
    banner.textContent = "Preview only. Open the source panel for live controls.";
    clone.prepend(banner);
  }
}

function renderWorkspaceTile(tile) {
  const block = getWorkspaceBlock(tile.block_type);
  if (!block) return null;
  const card = document.createElement("div");
  card.classList.add("card", "workspace-tile");
  card.dataset.tileId = tile.tile_id;
  const header = document.createElement("div");
  header.classList.add("card-header");
  const titleWrap = document.createElement("div");
  const title = document.createElement("div");
  title.classList.add("card-title");
  title.textContent = tile.title || block.title;
  const subtitle = document.createElement("div");
  subtitle.classList.add("card-subtitle");
  subtitle.textContent = block.description;
  titleWrap.appendChild(title);
  titleWrap.appendChild(subtitle);
  const actions = document.createElement("div");
  actions.classList.add("card-actions");
  if (block.source_panel) {
    const open = document.createElement("button");
    open.type = "button";
    open.classList.add("ghost", "small");
    open.textContent = "Open";
    open.addEventListener("click", () => {
      setSection(block.source_panel, { scrollTarget: block.source_card_id || null });
    });
    actions.appendChild(open);
  }
  const remove = document.createElement("button");
  remove.type = "button";
  remove.classList.add("ghost", "small");
  remove.textContent = "Remove";
  remove.addEventListener("click", () => removeWorkspaceTile(tile.tile_id));
  actions.appendChild(remove);
  header.appendChild(titleWrap);
  header.appendChild(actions);
  card.appendChild(header);
  const body = document.createElement("div");
  body.classList.add("workspace-tile-body");
  card.appendChild(body);

  const render = async () => {
    if (tile.block_type === "status.summary") {
      await renderWorkspaceStatus(body);
      return;
    }
    if (tile.block_type === "snapshots.recent") {
      await renderWorkspaceRecentSnapshots(body);
      return;
    }
    if (tile.block_type === "incidents.ledger") {
      await renderWorkspaceIncidentLedger(body);
      return;
    }
    if (tile.block_type === "incidents.intake") {
      renderWorkspaceIncidentIntake(body);
      return;
    }
    if (tile.block_type === "snapshots.history") {
      await renderWorkspaceSnapshotHistory(body, tile);
      return;
    }
    if (tile.block_type === "entra.user_lookup") {
      await renderWorkspaceEntraLookup(body, tile);
      return;
    }
    const source = findWorkspaceSourceCard(block);
    if (!source) {
      body.textContent = "Tile preview unavailable.";
      return;
    }
    const clone = source.cloneNode(true);
    sanitizeWorkspaceClone(clone, block, tile);
    body.appendChild(clone);
  };
  render();
  return card;
}

function updateWorkspaceTile(tileId, updates) {
  const activeId = getActiveWorkspaceId();
  if (!activeId) return;
  const workspace = getWorkspaceById(activeId);
  if (!workspace) return;
  const tile = workspace.tiles.find((item) => item.tile_id === tileId);
  if (!tile) return;
  Object.assign(tile, updates);
  upsertWorkspace(workspace);
}

function renderWorkspaceGrid() {
  if (!workspaceGrid) return;
  workspaceGrid.innerHTML = "";
  const activeId = getActiveWorkspaceId();
  const workspace = activeId ? getWorkspaceById(activeId) : null;
  if (!workspace) return;
  workspace.tiles.forEach((tile) => {
    const card = renderWorkspaceTile(tile);
    if (!card) return;
    const span = workspace.layout?.spans?.[tile.tile_id] || 1;
    card.classList.add(`span-${span}`);
    workspaceGrid.appendChild(card);
    setupWorkspaceTileControls(card);
  });
  applyWorkspaceLayout(workspace);
  setupWorkspaceDragging();
}

function renderWorkspaces() {
  renderWorkspaceSelect();
  renderWorkspaceTemplates();
  renderWorkspaceEmptyState();
  renderWorkspaceGrid();
}

function addWorkspaceTile(blockType, options = {}) {
  const activeId = getActiveWorkspaceId();
  if (!activeId) return;
  const workspace = getWorkspaceById(activeId);
  if (!workspace) return;
  const tile = {
    tile_id: generateWorkspaceTileId(),
    block_type: blockType,
    block_params: options.block_params || {},
    pinned_state: options.pinned_state || null,
    title: options.title || null,
  };
  workspace.tiles.push(tile);
  workspace.layout = workspace.layout || { order: [], spans: {} };
  workspace.layout.order.push(tile.tile_id);
  upsertWorkspace(workspace);
  renderWorkspaces();
}

function removeWorkspaceTile(tileId) {
  const activeId = getActiveWorkspaceId();
  if (!activeId) return;
  const workspace = getWorkspaceById(activeId);
  if (!workspace) return;
  workspace.tiles = workspace.tiles.filter((tile) => tile.tile_id !== tileId);
  workspace.layout = workspace.layout || { order: [], spans: {} };
  workspace.layout.order = (workspace.layout.order || []).filter((id) => id !== tileId);
  delete workspace.layout.spans?.[tileId];
  upsertWorkspace(workspace);
  renderWorkspaces();
}

function openWorkspacePalette() {
  if (!getActiveWorkspaceId()) {
    showToast("Create a workspace first");
    return;
  }
  const modal = ensureWorkspacePaletteModal();
  modal.classList.add("open");
  renderWorkspacePalette(modal);
}

function ensureWorkspacePaletteModal() {
  let modal = document.getElementById("workspace-palette-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "workspace-palette-modal";
  modal.classList.add("modal");
  modal.innerHTML = `
    <div class="modal-card workspace-modal">
      <div class="modal-header">
        <div class="modal-title">Add tile</div>
        <div class="modal-actions">
          <button class="ghost small" id="workspace-palette-close">Close</button>
        </div>
      </div>
      <div class="modal-toolbar workspace-palette-toolbar">
        <input id="workspace-palette-search" type="search" placeholder="Search tiles..." />
        <select id="workspace-palette-category">
          <option value="">All categories</option>
        </select>
        <select id="workspace-palette-capability">
          <option value="">All capabilities</option>
          <option value="Graph">Graph</option>
          <option value="PowerShell">PowerShell</option>
          <option value="SSH">SSH</option>
          <option value="Local">Local</option>
        </select>
        <select id="workspace-palette-risk">
          <option value="">All risk levels</option>
          <option value="safe">Safe</option>
          <option value="caution">Caution</option>
          <option value="dangerous">Dangerous</option>
        </select>
      </div>
      <div class="modal-body">
        <div class="workspace-palette-list" id="workspace-palette-list"></div>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) modal.classList.remove("open");
  });
  modal.querySelector("#workspace-palette-close").addEventListener("click", () => {
    modal.classList.remove("open");
  });
  return modal;
}

function renderWorkspacePalette(modal) {
  const list = modal.querySelector("#workspace-palette-list");
  const searchInput = modal.querySelector("#workspace-palette-search");
  const categorySelect = modal.querySelector("#workspace-palette-category");
  const capabilitySelect = modal.querySelector("#workspace-palette-capability");
  const riskSelect = modal.querySelector("#workspace-palette-risk");
  const query = (searchInput?.value || "").toLowerCase();
  const categoryFilter = (categorySelect?.value || "").toLowerCase();
  const capabilityFilter = (capabilitySelect?.value || "").toLowerCase();
  const riskFilter = (riskSelect?.value || "").toLowerCase();
  list.innerHTML = "";
  const grouped = {};
  const blocks = listWorkspaceBlocks().sort((a, b) => {
    const orderA = TILE_CATEGORY_ORDER.indexOf(a.category || "Other");
    const orderB = TILE_CATEGORY_ORDER.indexOf(b.category || "Other");
    if (orderA !== orderB) return orderA - orderB;
    return (a.title || "").localeCompare(b.title || "");
  });
  blocks.forEach((block) => {
    const haystack = `${block.title} ${block.description} ${block.id}`.toLowerCase();
    if (query && !haystack.includes(query)) {
      return;
    }
    if (categoryFilter && (block.category || "").toLowerCase() !== categoryFilter) {
      return;
    }
    if (capabilityFilter && !(block.capabilities || []).some((cap) => cap.toLowerCase() === capabilityFilter)) {
      return;
    }
    if (riskFilter && (block.risk || "safe") !== riskFilter) {
      return;
    }
    const category = block.category || "Other";
    grouped[category] = grouped[category] || [];
    grouped[category].push(block);
  });
  const rendered = new Set();
  TILE_CATEGORY_ORDER.forEach((category) => {
    const blocksForCategory = grouped[category];
    if (!blocksForCategory || !blocksForCategory.length) return;
    const heading = document.createElement("div");
    heading.classList.add("workspace-palette-heading");
    heading.textContent = category;
    list.appendChild(heading);
    blocksForCategory.forEach((block) => {
      const row = document.createElement("div");
      row.classList.add("workspace-block-row");
      const meta = document.createElement("div");
      meta.classList.add("workspace-block-meta");
      const title = document.createElement("div");
      title.classList.add("workspace-block-title");
      title.textContent = block.title;
      const desc = document.createElement("div");
      desc.classList.add("workspace-block-desc");
      desc.textContent = block.description;
      meta.appendChild(title);
      meta.appendChild(desc);
      const badges = document.createElement("div");
      badges.classList.add("workspace-block-badges");
      (block.capabilities || []).forEach((cap) => {
        const badge = document.createElement("span");
        badge.classList.add("badge");
        badge.textContent = cap;
        badges.appendChild(badge);
      });
      const risk = document.createElement("span");
      risk.classList.add("badge", "risk", `risk-${block.risk || "safe"}`);
      risk.textContent = formatRiskLabel(block.risk || "safe");
      badges.appendChild(risk);
      const add = document.createElement("button");
      add.type = "button";
      add.classList.add("ghost", "small");
      add.textContent = "Add";
      add.addEventListener("click", async () => {
        await addWorkspaceTileFromBlock(block);
        modal.classList.remove("open");
      });
      row.appendChild(meta);
      row.appendChild(badges);
      row.appendChild(add);
      list.appendChild(row);
    });
    rendered.add(category);
  });
  Object.entries(grouped).forEach(([category, blocksForCategory]) => {
    if (rendered.has(category)) return;
    const heading = document.createElement("div");
    heading.classList.add("workspace-palette-heading");
    heading.textContent = category;
    list.appendChild(heading);
    blocksForCategory.forEach((block) => {
      const row = document.createElement("div");
      row.classList.add("workspace-block-row");
      const meta = document.createElement("div");
      meta.classList.add("workspace-block-meta");
      const title = document.createElement("div");
      title.classList.add("workspace-block-title");
      title.textContent = block.title;
      const desc = document.createElement("div");
      desc.classList.add("workspace-block-desc");
      desc.textContent = block.description;
      meta.appendChild(title);
      meta.appendChild(desc);
      const badges = document.createElement("div");
      badges.classList.add("workspace-block-badges");
      (block.capabilities || []).forEach((cap) => {
        const badge = document.createElement("span");
        badge.classList.add("badge");
        badge.textContent = cap;
        badges.appendChild(badge);
      });
      const risk = document.createElement("span");
      risk.classList.add("badge", "risk", `risk-${block.risk || "safe"}`);
      risk.textContent = formatRiskLabel(block.risk || "safe");
      badges.appendChild(risk);
      const add = document.createElement("button");
      add.type = "button";
      add.classList.add("ghost", "small");
      add.textContent = "Add";
      add.addEventListener("click", async () => {
        await addWorkspaceTileFromBlock(block);
        modal.classList.remove("open");
      });
      row.appendChild(meta);
      row.appendChild(badges);
      row.appendChild(add);
      list.appendChild(row);
    });
  });
  if (categorySelect && !categorySelect.dataset.bound) {
    categorySelect.dataset.bound = "true";
    const allCategories = Array.from(new Set(listWorkspaceBlocks().map((b) => b.category || "Other")));
    const ordered = [
      ...TILE_CATEGORY_ORDER.filter((cat) => allCategories.includes(cat)),
      ...allCategories.filter((cat) => !TILE_CATEGORY_ORDER.includes(cat)),
    ];
    categorySelect.innerHTML = `<option value="">All categories</option>${ordered
      .map((cat) => `<option value="${cat.toLowerCase()}">${cat}</option>`)
      .join("")}`;
  }
  const bindFilter = (el) => {
    if (!el || el.dataset.bound === "true") return;
    el.dataset.bound = "true";
    el.addEventListener("input", () => renderWorkspacePalette(modal));
    el.addEventListener("change", () => renderWorkspacePalette(modal));
  };
  bindFilter(searchInput);
  bindFilter(categorySelect);
  bindFilter(capabilitySelect);
  bindFilter(riskSelect);
  if (!list.innerHTML) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No tiles match the current filters.";
    list.appendChild(empty);
  }
}

function ensureWorkspacePinModal() {
  let modal = document.getElementById("workspace-pin-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "workspace-pin-modal";
  modal.classList.add("modal");
  modal.innerHTML = `
    <div class="modal-card workspace-modal">
      <div class="modal-header">
        <div class="modal-title">Pin to workspace</div>
        <div class="modal-actions">
          <button class="ghost small" id="workspace-pin-close">Close</button>
        </div>
      </div>
      <div class="modal-body">
        <label class="modal-field">
          Workspace
          <select id="workspace-pin-select"></select>
        </label>
        <label class="modal-field">
          Tile name (optional)
          <input id="workspace-pin-title" type="text" placeholder="Optional custom name" />
        </label>
        <div class="runner-actions">
          <button class="primary small" id="workspace-pin-confirm">Add tile</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) modal.classList.remove("open");
  });
  modal.querySelector("#workspace-pin-close").addEventListener("click", () => {
    modal.classList.remove("open");
  });
  return modal;
}

function openWorkspacePinModal(blockType, defaultTitle = "") {
  const workspaces = loadWorkspaces();
  if (!workspaces.length) {
    showToast("Create a workspace first");
    return;
  }
  const block = getWorkspaceBlock(blockType);
  if (!block) {
    showToast("Tile unavailable");
    return;
  }
  const modal = ensureWorkspacePinModal();
  const select = modal.querySelector("#workspace-pin-select");
  const titleInput = modal.querySelector("#workspace-pin-title");
  const confirm = modal.querySelector("#workspace-pin-confirm");
  select.innerHTML = "";
  workspaces.forEach((workspace) => {
    const option = document.createElement("option");
    option.value = workspace.id;
    option.textContent = workspace.name || "Untitled workspace";
    select.appendChild(option);
  });
  const activeId = getActiveWorkspaceId();
  if (activeId) select.value = activeId;
  titleInput.value = defaultTitle || "";
  confirm.onclick = async () => {
    const workspaceId = select.value;
    if (!workspaceId) {
      showToast("Select a workspace");
      return;
    }
    const workspace = getWorkspaceById(workspaceId);
    if (!workspace) return;
    const blockParams = {};
    if (block.config_sensitive) {
      blockParams.read_only = true;
    }
    const tile = {
      tile_id: generateWorkspaceTileId(),
      block_type: blockType,
      block_params: blockParams,
      pinned_state: { source: "pin" },
      title: titleInput.value.trim() || null,
    };
    if (block.risk === "dangerous") {
      const ok = await confirmModal({
        title: "Pin dangerous tile?",
        message: "This tile can run risky or destructive actions. Pin it anyway?",
        confirmLabel: "Pin anyway",
        cancelLabel: "Cancel",
        danger: true,
      });
      if (!ok) return;
    }
    workspace.tiles.push(tile);
    workspace.layout = workspace.layout || { order: [], spans: {} };
    workspace.layout.order.push(tile.tile_id);
    upsertWorkspace(workspace);
    if (workspaceId === activeId) {
      renderWorkspaces();
    }
    modal.classList.remove("open");
    showToast("Tile pinned to workspace");
  };
  modal.classList.add("open");
}

function setupWorkspacePinButtons() {
  document.querySelectorAll("[data-workspace-block]").forEach((card) => {
    if (card.dataset.pinBound === "true") return;
    if (card.closest(".workspace-grid")) return;
    const blockType = card.dataset.workspaceBlock;
    const block = getWorkspaceBlock(blockType);
    if (!block) return;
    const header = card.querySelector(".card-header");
    if (!header) return;
    let actions = header.querySelector(".card-actions");
    if (!actions) {
      actions = document.createElement("div");
      actions.classList.add("card-actions");
      header.appendChild(actions);
    }
    const pin = document.createElement("button");
    pin.type = "button";
    pin.classList.add("ghost", "small");
    pin.textContent = "Pin";
    pin.addEventListener("click", () => openWorkspacePinModal(blockType, block.title));
    actions.appendChild(pin);
    card.dataset.pinBound = "true";
  });
}

function setSection(section, opts = {}) {
  const resolved = SECTION_ALIASES[section] || section;
  updateModeHeader(section, resolved);
  navLinks.forEach((link) => link.classList.toggle("active", link.dataset.section === section));
  const activeLink = document.querySelector(`.nav-link.active[data-section="${section}"]`);
  if (activeLink) {
    const group = activeLink.closest(".nav-group");
    if (group && !group.classList.contains("open")) {
      group.classList.add("open");
    }
    if (navList) {
      requestAnimationFrame(() => {
        activeLink.scrollIntoView({ behavior: "smooth", block: "nearest" });
        updateNavShadows();
      });
    }
  }
  panels.forEach((panel) => {
    if (panel.dataset.panel === resolved) {
      panel.style.display = panel.dataset.display || "flex";
    } else {
      panel.style.display = "none";
    }
  });
  pageTitle.textContent =
    serviceLabels?.[section] ||
    serviceLabels?.[resolved] ||
    section.charAt(0).toUpperCase() + section.slice(1);
  pageSubtitle.textContent = subtitles[section] || subtitles[resolved] || "";
  updateRouteForSection(section);
  sidebar.classList.remove("open");
  if (opts.scrollTarget) {
    const target = document.getElementById(opts.scrollTarget);
    if (target) {
      setTimeout(() => {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 0);
    }
  }
}

function updateModeHeader(section, resolvedSection) {
  if (!modePill || !modeTitle || !modeSubtitle) return;
  const modeKey = MODE_MAP[section] || MODE_MAP[resolvedSection] || "observe";
  const meta = MODE_META[modeKey] || MODE_META.observe;
  modePill.textContent = meta.label;
  modePill.className = `mode-pill ${modeKey}`;
  modeTitle.textContent = meta.label;
  modeSubtitle.textContent = meta.subtitle;
}

function updateRouteForSection(section) {
  if (!window.history || !window.history.pushState) return;
  if (section === "help") {
    if (!window.location.pathname.startsWith("/help")) {
      window.history.pushState({ section }, "", "/help");
    }
    return;
  }
  if (section === "workspaces") {
    if (!window.location.pathname.startsWith("/workspaces")) {
      window.history.pushState({ section }, "", "/workspaces");
    }
    return;
  }
  if (window.location.pathname.startsWith("/help") || window.location.pathname.startsWith("/workspaces")) {
    window.history.pushState({ section }, "", "/");
  }
}

function resolveSectionFromPath() {
  if (window.location.pathname.startsWith("/help")) return "help";
  if (window.location.pathname.startsWith("/workspaces")) return "workspaces";
  return "dashboard";
}

function updateNavShadows() {
  if (!navList) return;
  const { scrollTop, scrollHeight, clientHeight } = navList;
  const atTop = scrollTop <= 1;
  const atBottom = scrollTop + clientHeight >= scrollHeight - 1;
  navList.classList.toggle("shadow-top", !atTop);
  navList.classList.toggle("shadow-bottom", !atBottom);
}

async function fetchStatus() {
  if (!statusBadge) return;
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    statusBadge.classList.remove("ok", "warn");
    if (data.graph_configured) {
      // Configured != authenticated; use health check for a full readiness report.
      statusBadge.textContent = "Graph configured";
      statusBadge.classList.add("ok");
    } else {
      statusBadge.textContent = "Graph missing env";
      statusBadge.classList.add("warn");
    }
  } catch (err) {
    statusBadge.classList.remove("ok", "warn");
    statusBadge.textContent = "API offline";
    statusBadge.classList.add("warn");
  }
}

async function fetchSystemStatusSummary() {
  try {
    const res = await fetch("/api/status/summary");
    const data = await res.json();
    renderSystemStatusSummary(data);
  } catch (err) {
    if (statusCompleteness) statusCompleteness.textContent = "--";
    if (statusWarnings) statusWarnings.textContent = "--";
    if (statusWarningSummary) statusWarningSummary.textContent = "Status summary unavailable.";
  }
}

function formatRelativeTime(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function buildCoverageLimitations(summary) {
  const warnings = summary?.warnings || [];
  const gaps = summary?.gaps || [];
  const combined = [...warnings, ...gaps];
  const seen = new Set();
  const limitations = [];
  combined.forEach((entry) => {
    const probe = entry?.probe || entry?.id || entry?.name;
    const key = probe || entry?.message || JSON.stringify(entry || {});
    if (seen.has(key)) return;
    seen.add(key);
    const mapped = mapCoverageLimitation(probe, entry?.message);
    limitations.push(mapped);
  });
  return limitations;
}

function mapCoverageLimitation(probeId, message) {
  const normalizeReason = (value) => {
    if (typeof value !== "string") return "";
    let reason = value.trim();
    if (!reason) return "";
    reason = reason
      .replace(/Graph request handler not configured/gi, "Graph handler not configured")
      .replace(/PowerShell \\(pwsh\\) not found/gi, "PowerShell not available");
    if (!reason.endsWith(".")) reason = `${reason}.`;
    return reason;
  };

  const map = {
    "identity.user_core": {
      label: "Identity data unavailable",
      detail: "User identity details were not collected, so identity checks are incomplete.",
    },
    "authz.user_groups_core": {
      label: "Group membership not evaluated",
      detail: "Group membership checks were skipped; access decisions may be incomplete.",
    },
    "authz.user_licenses_core": {
      label: "License state not evaluated",
      detail: "License assignment could not be confirmed, so feature access may be unclear.",
    },
    "authz.signin_summary_24h": {
      label: "Sign-in summary not evaluated",
      detail: "Recent sign-in failures were not checked; authentication issues may be hidden.",
    },
    "authz.ca_block_summary_24h": {
      label: "Conditional access not evaluated",
      detail: "Conditional access blocks were not evaluated; policy impact is unknown.",
    },
  };
  if (probeId && map[probeId]) {
    const reason = normalizeReason(message);
    const label = reason ? `${map[probeId].label} (${reason})` : map[probeId].label;
    const detail = reason ? `${map[probeId].detail} Reason: ${reason}` : map[probeId].detail;
    return { probe: probeId, label, detail };
  }
  return {
    probe: probeId || "unknown",
    label: probeId ? `Coverage limitation: ${probeId}` : "Coverage limitation",
    detail: message || "Coverage limitation detected; details unavailable.",
  };
}

function renderSystemStatusSummary(summary) {
  if (!summary) return;
  if (statusCompleteness) {
    statusCompleteness.textContent =
      summary.completeness_percent !== null && summary.completeness_percent !== undefined
        ? `${summary.completeness_percent}%`
        : "--";
  }
  if (statusWarnings) {
    statusWarnings.textContent = summary.warnings_count ?? 0;
  }
  const limitations = buildCoverageLimitations(summary);
  if (statusWarningSummary) {
    statusWarningSummary.textContent = limitations.length
      ? limitations[0].label
      : "No coverage limitations detected.";
  }
  if (statusLastSnapshot) {
    statusLastSnapshot.textContent = formatRelativeTime(summary.last_snapshot_at);
  }
  if (statusGraphReady) {
    // "Ready" implies successful auth/control calls; this is a config-level indicator.
    statusGraphReady.textContent = summary.graph_ready ? "Configured" : "Not configured";
  }
  if (statusPsReady) {
    statusPsReady.textContent = summary.powershell_ready ? "Ready" : "Missing modules";
  }
  renderRecentSnapshots(summary.recent_snapshots || []);
  renderCoverageLimitations(limitations);
}

function renderRecentSnapshots(items) {
  if (!recentSnapshotsList) return;
  recentSnapshotsList.innerHTML = "";
  if (!items || !items.length) {
    const empty = document.createElement("li");
    empty.classList.add("note");
    empty.textContent = "No snapshots captured yet.";
    recentSnapshotsList.appendChild(empty);
    return;
  }
  items.slice(0, 5).forEach((item) => {
    const row = document.createElement("li");
    row.classList.add("history-item");
    const title = document.createElement("div");
    title.classList.add("history-title");
    title.textContent = item.display_name || item.canonical_id || item.kind || "Snapshot";
    const meta = document.createElement("div");
    meta.classList.add("history-meta");
    meta.textContent = `${formatRelativeTime(item.captured_at)} · ${item.profile || "core"}`;
    row.appendChild(title);
    row.appendChild(meta);
    recentSnapshotsList.appendChild(row);
  });
}

function renderCoverageLimitations(limitations) {
  const container = document.getElementById("health-limitations");
  if (!container) return;
  container.innerHTML = "";
  if (!limitations.length) {
    const empty = document.createElement("div");
    empty.classList.add("note");
    empty.textContent = "No coverage limitations detected.";
    container.appendChild(empty);
    return;
  }
  limitations.forEach((item) => {
    const row = document.createElement("div");
    row.classList.add("limitation-row");
    const title = document.createElement("div");
    title.classList.add("limitation-title");
    title.textContent = item.label;
    const detail = document.createElement("div");
    detail.classList.add("limitation-detail");
    detail.textContent = item.detail;
    row.appendChild(title);
    row.appendChild(detail);
    container.appendChild(row);
  });
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
    if (cfgTimeWarn) cfgTimeWarn.value = data.time_thresholds?.warn_ms ?? "";
    if (cfgTimeHigh) cfgTimeHigh.value = data.time_thresholds?.high_ms ?? "";
    if (cfgNtpServers) cfgNtpServers.value = formatCsvList(data.ntp_servers);
    if (cfgCertStores) cfgCertStores.value = formatCsvList(data.cert_stores);
    if (cfgCertExpiring) cfgCertExpiring.value = data.cert_expiring_days ?? "";
    if (cfgTlsEndpoints) cfgTlsEndpoints.value = formatCsvList(data.tls_endpoints);
    if (cfgLatencyEndpoints) cfgLatencyEndpoints.value = formatCsvList(data.latency_endpoints);
    if (cfgDnsProbeTargets) cfgDnsProbeTargets.value = formatCsvList(data.dns_probe_targets);
    if (cfgDnsResolvers) cfgDnsResolvers.value = formatCsvList(data.dns_resolvers);
    diffImpactOverrides = data.diff_impact_overrides || {};
    if (cfgDiffImpactOverrides) {
      cfgDiffImpactOverrides.value = formatDiffImpactOverrides(diffImpactOverrides);
    }
    if (cfgPublicResolvers) cfgPublicResolvers.checked = Boolean(data.enable_public_resolvers);
    if (cfgProcessCmdline) cfgProcessCmdline.checked = Boolean(data.process_include_command_line);
    if (cfgProcessMax) cfgProcessMax.value = data.process_max_items ?? "";
    if (cfgZoneMap) cfgZoneMap.value = formatZoneMap(data.zone_map);
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
    fetchSystemStatusSummary();
  } catch (err) {
    showToast("Failed to load config");
  }
}

async function saveConfig() {
  if (configLocked) {
    showToast("Config is locked. Disable the lock to update.");
    return;
  }
  const payload = getConfigPayloadFromForm();
  payload.reload = true;
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

function getExplainPanel(service) {
  return document.querySelector(`.output-explain[data-output="${service}"]`);
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
  const { preferredKey } = options;
  const candidates = getArrayCandidates(data);
  const keys = Object.keys(candidates);
  if (!keys.length) return null;
  if (preferredKey && candidates[preferredKey]) {
    return candidates[preferredKey];
  }
  if (keys.length === 1) return candidates[keys[0]];
  return null;
}

async function selectExportArrayWithModal(data, options = {}) {
  const { preferredKey } = options;
  const candidates = getArrayCandidates(data);
  const keys = Object.keys(candidates);
  if (!keys.length) return null;
  if (preferredKey && candidates[preferredKey]) {
    return candidates[preferredKey];
  }
  if (keys.length === 1) return candidates[keys[0]];
  const choice = await selectModal({
    title: "Select dataset to export",
    label: "Dataset",
    options: keys.map((key) => ({ value: key, label: key })),
    defaultValue: keys[0],
    confirmLabel: "Select",
    cancelLabel: "Cancel",
  });
  if (!choice) return null;
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
  let status = data.status_code || data.status || data.statusCode;
  let requestId = data.request_id || data.requestId;
  const failureSource = data.failure_source || data.failureSource || data.failure_origin || data.failureOrigin || null;
  const failureOutcome = data.failure_outcome || data.failureOutcome || null;
  const failureOrigin = data.failure_origin || data.failureOrigin || null;
  const errorClass = data.error_class || data.errorClass || null;
  const method = data.method || null;
  const url = data.url || null;
  const path = data.path || null;
  const params = data.params || null;
  const tenantId = data.tenant_id || data.tenantId || null;
  const uiRequestId = data.ui_request_id || data.uiRequestId || null;
  const correlationId = data.correlation_id || data.correlationId || null;
  const durationMs = data.duration_ms || data.durationMs || null;
  const queueWaitMs = data.queue_wait_ms || data.queueWaitMs || null;
  const timestamp = data.timestamp || null;
  const diagnostics = data.diagnostics || null;
  const retry = data.retry || null;
  const rawGraph = data.raw_graph || data.rawGraph || null;
  const normalized = data.normalized || null;
  const circuit = data.circuit || null;
  const routeGroup = data.route_group || data.routeGroup || data.request?.route_group || data.request?.routeGroup || null;
  let code = data.code || data.error_code;
  let message = (normalized && normalized.error_summary) || data.error || data.message;
  let hint = data.hint;
  let detail = data.detail;
  const rateLimit = data.rate_limit || data.rateLimit;
  const suggestedWait = data.suggested_wait_seconds || data.retry_after;
  if (detail && typeof detail === "object" && detail.error) {
    const err = detail.error;
    code = code || err.code;
    message = message || err.message;
    if (!requestId && err.innerError) {
      requestId = err.innerError["request-id"] || err.innerError["client-request-id"] || requestId;
    }
  }
  if (!code && rawGraph && typeof rawGraph === "object") {
    const bodyJson = rawGraph.body_json;
    if (bodyJson && typeof bodyJson === "object" && bodyJson.error) {
      code = bodyJson.error.code || code;
    }
  }
  if (!requestId && rawGraph && typeof rawGraph === "object") {
    const headers = rawGraph.headers || {};
    if (headers && typeof headers === "object") {
      requestId = headers["request-id"] || headers["Request-Id"] || headers["requestId"] || requestId;
    }
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
    correlationId,
    uiRequestId,
    failureSource,
    failureOutcome,
    failureOrigin,
    errorClass,
    method,
    url,
    path,
    params,
    tenantId,
    durationMs,
    queueWaitMs,
    timestamp,
    diagnostics,
    retry,
    rawGraph,
    normalized,
    circuit,
    routeGroup,
    detail,
    rateLimit,
    suggestedWait,
    raw: data,
  };
}

function extractErrorText(meta) {
  if (!meta) return "";
  const parts = [];
  if (meta.message) parts.push(String(meta.message));
  if (meta.code) parts.push(String(meta.code));
  if (meta.hint) parts.push(String(meta.hint));
  if (typeof meta.detail === "string") {
    parts.push(meta.detail);
  } else if (meta.detail && typeof meta.detail === "object") {
    if (meta.detail.error) {
      const err = meta.detail.error;
      if (err.message) parts.push(String(err.message));
      if (err.details) parts.push(String(err.details));
    }
    if (meta.detail.meta?.non_terminating_errors) {
      try {
        parts.push(JSON.stringify(meta.detail.meta.non_terminating_errors));
      } catch (err) {
        // ignore JSON errors
      }
    }
    try {
      parts.push(JSON.stringify(meta.detail));
    } catch (err) {
      // ignore JSON errors
    }
  }
  return parts.join(" ").toLowerCase();
}

function buildTriage(meta) {
  if (!meta) return null;
  const recommendations = [];
  const status = Number(meta.status || 0);
  const code = String(meta.code || "");
  const message = String(meta.message || "");
  const errorText = extractErrorText(meta);

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
  if (errorText.includes("module") && (errorText.includes("not found") || errorText.includes("could not be loaded"))) {
    recommendations.push("Install or import the missing PowerShell module, then retry.");
  }
  if (errorText.includes("access is denied") || errorText.includes("unauthorized")) {
    recommendations.push("Run with elevated privileges or ensure the account has required rights.");
  }
  if (errorText.includes("rpc server is unavailable")) {
    recommendations.push("Check RPC service status and firewall rules between client and target.");
  }
  if (errorText.includes("dns") && (errorText.includes("failed") || errorText.includes("not found") || errorText.includes("nxdomain"))) {
    recommendations.push("Verify DNS records and server reachability, then retry.");
  }
  if (errorText.includes("no such host")) {
    recommendations.push("Verify the hostname and DNS resolution.");
  }
  if (errorText.includes("connection refused") || errorText.includes("actively refused")) {
    recommendations.push("Check the target service is listening and firewall rules allow the connection.");
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

function isSensitiveKey(key) {
  const normalized = String(key || "").toLowerCase();
  if (!normalized) return false;
  if (SENSITIVE_PARAM_KEYS.has(normalized)) return true;
  if (normalized.includes("password") || normalized.includes("passphrase")) return true;
  if (normalized.includes("secret") || normalized.includes("token")) return true;
  if (normalized.includes("credential")) return true;
  if (normalized.includes("private") && normalized.includes("key")) return true;
  if (normalized.endsWith("_key") || normalized.endsWith("apikey")) return true;
  return false;
}

function sanitizeParams(value, depth = 0) {
  if (value === null || value === undefined) return value;
  if (depth > 6) return "[truncated]";
  if (Array.isArray(value)) {
    return value.map((entry) => sanitizeParams(entry, depth + 1));
  }
  if (typeof value === "object") {
    const result = {};
    Object.entries(value).forEach(([key, val]) => {
      if (isSensitiveKey(key)) {
        result[key] = "[redacted]";
      } else {
        result[key] = sanitizeParams(val, depth + 1);
      }
    });
    return result;
  }
  return value;
}

function buildIncidentContext(params) {
  const safeParams = sanitizeParams(params || {});
  const highlights = {};
  const keywords = [
    "user",
    "mailbox",
    "group",
    "team",
    "site",
    "list",
    "drive",
    "device",
    "host",
    "server",
    "printer",
    "queue",
    "ou",
    "gpo",
    "domain",
    "tenant",
    "subscription",
    "ip",
    "dns",
    "share",
    "unc",
  ];
  Object.entries(safeParams).forEach(([key, value]) => {
    const normalized = String(key || "").toLowerCase();
    if (keywords.some((needle) => normalized.includes(needle))) {
      highlights[key] = value;
    }
  });
  return { params: safeParams, highlights };
}

function collectSnapshotCandidates(meta, context) {
  const candidates = [];
  const addCandidate = (aliasType, value, kind) => {
    if (!aliasType || !value) return;
    const trimmed = String(value).trim();
    if (!trimmed) return;
    candidates.push({ aliasType, value: trimmed, kind: kind || null });
  };
  const params = meta?.params || {};
  const highlights = context?.highlights || {};
  const sources = [params, highlights];
  sources.forEach((source) => {
    Object.entries(source || {}).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") return;
      const normalized = String(key || "").toLowerCase();
      const values = Array.isArray(value) ? value : [value];
      values.forEach((entry) => {
        const text = typeof entry === "string" ? entry : String(entry);
        if (!text) return;
        if (normalized.includes("user") || normalized.includes("upn") || normalized.includes("mailbox")) {
          addCandidate("upn", text, "user");
          return;
        }
        if (normalized.includes("dc")) {
          addCandidate("hostname", text, "dc");
          return;
        }
        if (normalized.includes("dns")) {
          addCandidate("hostname", text, "dns_server");
          return;
        }
        if (normalized.includes("dhcp")) {
          addCandidate("hostname", text, "dhcp_server");
          return;
        }
        if (normalized.includes("file") || normalized.includes("share") || normalized.includes("smb")) {
          addCandidate("hostname", text, "file_server");
          return;
        }
        if (normalized.includes("print") || normalized.includes("printer")) {
          addCandidate("hostname", text, "print_server");
          return;
        }
        if (normalized.includes("device") || normalized.includes("host") || normalized.includes("server")) {
          addCandidate(isIpAddress(text) ? "ip" : "hostname", text, "device");
          return;
        }
        if (normalized.includes("ip")) {
          addCandidate("ip", text, "device");
          return;
        }
      });
    });
  });
  return candidates;
}

async function resolveSnapshotCandidates(candidates) {
  const resolved = [];
  const seen = new Set();
  for (const candidate of candidates || []) {
    const aliasType = candidate.aliasType;
    const aliasValue = candidate.value;
    const key = `${aliasType}:${aliasValue}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const entity = await resolveSnapshotSubject(aliasType, aliasValue);
    if (entity) {
      resolved.push({ ...candidate, entity });
    }
  }
  return resolved;
}

function extractEvidenceRefsFromSnapshots(snapshots) {
  const refs = new Set();
  snapshots.forEach((snapshot) => {
    if (Array.isArray(snapshot?.evidence_refs)) {
      snapshot.evidence_refs.forEach((ref) => refs.add(ref));
    }
    const probeResults = snapshot?.probe_results || [];
    probeResults.forEach((probe) => {
      if (Array.isArray(probe?.evidence_refs)) {
        probe.evidence_refs.forEach((ref) => refs.add(ref));
      }
    });
  });
  return Array.from(refs);
}

function initRunMeta(service, action, params) {
  const meta = {
    service,
    action,
    label: action ? resolveActionLabel(service, action) : null,
    mode: ACTIONS_UI?.[service]?.[action]?.mode || "graph",
    params: sanitizeParams(params || {}),
    started_at: new Date().toISOString(),
  };
  lastRunMeta[service] = meta;
  return meta;
}

function updateRunMeta(service, updates) {
  const current = lastRunMeta[service] || { service };
  lastRunMeta[service] = { ...current, ...updates };
  return lastRunMeta[service];
}

function finalizeRunMeta(service, updates) {
  return updateRunMeta(service, { ...updates, ended_at: new Date().toISOString() });
}

function estimateItemCount(payload) {
  if (!payload) return null;
  if (Array.isArray(payload)) return payload.length;
  if (payload && typeof payload === "object") {
    if (Array.isArray(payload.items)) return payload.items.length;
    if (Array.isArray(payload.value)) return payload.value.length;
    if (Number.isFinite(payload["@odata.count"])) return payload["@odata.count"];
  }
  return null;
}

function resolveIncidentRows(payload) {
  if (!payload || typeof payload === "string") return null;
  const preferredKeys = ["items", "value", "results", "devices", "users", "members"];
  for (const key of preferredKeys) {
    const rows = selectExportArray(payload, { preferredKey: key, allowPrompt: false });
    if (rows) return rows;
  }
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === "object") return [payload];
  return null;
}

async function fetchIncidentAuditEntries(service, meta) {
  const since = meta?.started_at
    ? meta.started_at
    : new Date(Date.now() - 30 * 60 * 1000).toISOString();
  const params = new URLSearchParams();
  params.set("service", service);
  if (meta?.action) params.set("action", meta.action);
  params.set("since", since);
  if (meta?.ended_at) params.set("until", meta.ended_at);
  params.set("limit", "200");
  try {
    const res = await fetch(`/api/audit?${params.toString()}`);
    const data = await res.json();
    if (!data.ok) {
      return { ok: false, error: data.error || "Audit fetch failed", items: [] };
    }
    const items = data.data?.items || [];
    return { ok: true, items, total: data.data?.total || items.length };
  } catch (err) {
    return { ok: false, error: err.message || "Audit fetch failed", items: [] };
  }
}

function buildIncidentSummary({ service, meta, status, context, payload, audit, activity, rawOutput, generatedAt }) {
  const lines = [];
  const now = generatedAt || new Date().toISOString();
  const serviceLabel = formatServiceLabel(service) || service;
  const action = meta?.action;
  const actionLabel = action ? resolveActionLabel(service, action) : "Unknown action";
  const mode = meta?.mode ? modeLabel(meta.mode) : "Graph";
  const elapsed = meta?.elapsed_ms != null ? formatElapsed(meta.elapsed_ms) : null;
  const errorMeta = extractErrorMeta(payload);
  const itemCount = estimateItemCount(payload);

  lines.push("Incident bundle");
  lines.push(`Generated: ${now}`);
  lines.push(`Service: ${serviceLabel} (${service})`);
  lines.push(`Command: ${actionLabel}${action ? ` (${action})` : ""}`);
  lines.push(`Mode: ${mode}`);
  if (meta?.started_at) lines.push(`Started: ${meta.started_at}`);
  if (meta?.ended_at) lines.push(`Ended: ${meta.ended_at}`);
  if (elapsed) lines.push(`Elapsed: ${elapsed}`);
  if (status?.text) lines.push(`Status: ${status.text}`);
  if (status?.meta) lines.push(`Status meta: ${status.meta}`);
  if (meta?.http_status) lines.push(`HTTP status: ${meta.http_status}`);
  if (meta?.status_code) lines.push(`Graph status: ${meta.status_code}`);
  if (meta?.request_id) lines.push(`Request ID: ${meta.request_id}`);
  if (meta?.ok === true) lines.push("Result: OK");
  if (meta?.ok === false && meta?.cancelled) lines.push("Result: Cancelled");
  if (meta?.ok === false && !meta?.cancelled) lines.push("Result: Failed");
  if (errorMeta?.message) lines.push(`Error: ${errorMeta.message}`);
  if (errorMeta?.code) lines.push(`Error code: ${errorMeta.code}`);
  if (errorMeta?.hint) lines.push(`Hint: ${errorMeta.hint}`);
  if (meta?.rate_limit && typeof meta.rate_limit === "object") {
    const entries = Object.entries(meta.rate_limit)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => `${key}: ${value}`);
    if (entries.length) lines.push(`Rate-limit headers: ${entries.join(", ")}`);
  }
  if (meta?.suggested_wait_seconds) {
    lines.push(`Suggested wait: ${meta.suggested_wait_seconds}s`);
  }
  if (itemCount !== null) lines.push(`Result count: ${itemCount}`);
  if (audit?.items) lines.push(`Audit entries: ${audit.items.length}`);
  if (rawOutput && rawOutput.trim()) lines.push(`Raw output length: ${rawOutput.length} chars`);

  if (context?.highlights && Object.keys(context.highlights).length) {
    lines.push("");
    lines.push("Context highlights:");
    Object.entries(context.highlights)
      .slice(0, 12)
      .forEach(([key, value]) => {
        lines.push(`- ${key}: ${formatValue(value)}`);
      });
  }

  if (meta?.preflight) {
    lines.push("");
    lines.push(`Preflight: ${meta.preflight.ok ? "OK" : "Failed"}`);
    if (meta.preflight.warning) {
      const warnStatus = meta.preflight.warning?.status ? `HTTP ${meta.preflight.warning.status}` : "HTTP 5xx";
      lines.push(`Preflight warning: ${warnStatus}`);
    }
  }

  if (activity && activity.length) {
    lines.push("");
    lines.push("Recent activity:");
    activity.slice(0, 5).forEach((entry) => {
      lines.push(`- ${entry.time} ${entry.text}`);
    });
  }

  return lines.join("\n");
}

function buildIncidentTicketData({
  service,
  meta,
  status,
  context,
  payload,
  audit,
  activity,
  rawOutput,
  generatedAt,
  bundleName,
}) {
  const serviceLabel = formatServiceLabel(service) || service;
  const action = meta?.action || null;
  const actionLabel = action ? resolveActionLabel(service, action) : "Unknown action";
  const mode = meta?.mode ? modeLabel(meta.mode) : "Graph";
  const errorMeta = extractErrorMeta(payload) || extractErrorMeta(meta) || null;
  const itemCount = estimateItemCount(payload);
  const resultLabel = meta?.ok === true ? "OK" : meta?.cancelled ? "Cancelled" : "Failed";
  const statusText = status?.text || meta?.error || errorMeta?.message || null;
  const requestId = meta?.request_id || errorMeta?.requestId || null;

  return {
    generatedAt: generatedAt || new Date().toISOString(),
    service,
    serviceLabel,
    action,
    actionLabel,
    mode,
    resultLabel,
    statusText,
    itemCount,
    auditCount: audit?.items ? audit.items.length : 0,
    requestId,
    errorMeta,
    rawOutput,
    payload,
    context: context?.highlights || {},
    preflight: meta?.preflight || null,
    rateLimit: meta?.rate_limit || null,
    suggestedWaitSeconds: meta?.suggested_wait_seconds || null,
    startedAt: meta?.started_at || null,
    endedAt: meta?.ended_at || null,
    elapsedMs: meta?.elapsed_ms ?? null,
    statusMeta: status?.meta || null,
    activity: activity || [],
    bundleName: bundleName || null,
  };
}

function truncateLines(value, maxLines, maxChars) {
  if (!value) return { text: "", truncated: false };
  const lines = String(value).split(/\r?\n/);
  const limited = lines.slice(0, maxLines);
  let text = limited.join("\n");
  let truncated = lines.length > maxLines;
  if (text.length > maxChars) {
    text = text.slice(0, maxChars);
    truncated = true;
  }
  return { text, truncated };
}

function buildIncidentMarkdownSummary(data, attachments) {
  const lines = [];
  const title = `${data.serviceLabel}: ${data.actionLabel} (${data.resultLabel})`;

  lines.push("# Incident summary");
  lines.push("");
  lines.push(`**Title:** ${title}`);
  lines.push(`**Generated:** ${data.generatedAt}`);
  lines.push(`**Service:** ${data.serviceLabel}`);
  if (data.action) lines.push(`**Command:** ${data.actionLabel} (${data.action})`);
  lines.push(`**Mode:** ${data.mode}`);
  lines.push(`**Result:** ${data.resultLabel}`);
  if (data.statusText) lines.push(`**Status:** ${data.statusText}`);
  if (data.requestId) lines.push(`**Request ID:** ${data.requestId}`);
  if (data.itemCount !== null) lines.push(`**Result count:** ${data.itemCount}`);
  if (data.auditCount) lines.push(`**Audit entries:** ${data.auditCount}`);

  lines.push("");
  lines.push("## Timing");
  if (data.startedAt) lines.push(`- Started: ${data.startedAt}`);
  if (data.endedAt) lines.push(`- Ended: ${data.endedAt}`);
  if (data.elapsedMs != null) lines.push(`- Elapsed: ${formatElapsed(data.elapsedMs)}`);

  if (data.errorMeta?.message || data.errorMeta?.code || data.errorMeta?.hint) {
    lines.push("");
    lines.push("## Error");
    if (data.errorMeta.message) lines.push(`- Message: ${data.errorMeta.message}`);
    if (data.errorMeta.code) lines.push(`- Code: ${data.errorMeta.code}`);
    if (data.errorMeta.hint) lines.push(`- Hint: ${data.errorMeta.hint}`);
  }

  if (data.preflight) {
    lines.push("");
    lines.push("## Preflight");
    lines.push(`- Result: ${data.preflight.ok ? "OK" : "Failed"}`);
    if (data.preflight.warning?.status) {
      lines.push(`- Warning: HTTP ${data.preflight.warning.status}`);
    }
  }

  if (data.rateLimit && typeof data.rateLimit === "object") {
    const entries = Object.entries(data.rateLimit)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => `${key}: ${value}`);
    if (entries.length) {
      lines.push("");
      lines.push("## Rate limits");
      entries.forEach((entry) => lines.push(`- ${entry}`));
    }
  }
  if (data.suggestedWaitSeconds) {
    lines.push("");
    lines.push("## Suggested wait");
    lines.push(`- ${data.suggestedWaitSeconds}s`);
  }

  lines.push("");
  lines.push("## Context highlights");
  const contextEntries = Object.entries(data.context || {});
  if (!contextEntries.length) {
    lines.push("- None captured");
  } else {
    contextEntries.slice(0, 12).forEach(([key, value]) => {
      lines.push(`- ${key}: ${formatValue(value)}`);
    });
  }

  if (data.activity && data.activity.length) {
    lines.push("");
    lines.push("## Recent activity");
    data.activity.slice(0, 5).forEach((entry) => {
      lines.push(`- ${entry.time} ${entry.text}`);
    });
  }

  if (data.rawOutput && data.rawOutput.trim()) {
    const snippet = truncateLines(data.rawOutput, 20, 1200);
    lines.push("");
    lines.push("## Output snippet");
    lines.push("```text");
    lines.push(snippet.text);
    if (snippet.truncated) lines.push("... (truncated)");
    lines.push("```");
  }

  if (attachments && attachments.length) {
    lines.push("");
    lines.push("## Attachments");
    attachments.forEach((name) => lines.push(`- ${name}`));
    if (data.bundleName) lines.push(`- ${data.bundleName}`);
  }

  return lines.join("\n");
}

function buildTicketTemplates({ title, summaryText, summaryMarkdown, attachments, bundleName }) {
  const attachmentLines = (attachments || []).map((name) => `- ${name}`);
  if (bundleName) attachmentLines.push(`- ${bundleName}`);

  const serviceNowLines = [];
  serviceNowLines.push(`Short description: ${title}`);
  serviceNowLines.push("");
  serviceNowLines.push("Description:");
  serviceNowLines.push(summaryText);
  serviceNowLines.push("");
  serviceNowLines.push("Work notes:");
  if (bundleName) serviceNowLines.push(`- Evidence bundle: ${bundleName}`);
  if (attachmentLines.length) {
    serviceNowLines.push("");
    serviceNowLines.push("Attachments:");
    serviceNowLines.push(...attachmentLines);
  }

  const freshdeskLines = [];
  freshdeskLines.push(`Subject: ${title}`);
  freshdeskLines.push("");
  freshdeskLines.push("Description:");
  freshdeskLines.push(summaryText);
  if (attachmentLines.length) {
    freshdeskLines.push("");
    freshdeskLines.push("Attachments:");
    freshdeskLines.push(...attachmentLines);
  }

  const jiraLines = [];
  jiraLines.push(`## ${title}`);
  jiraLines.push("");
  jiraLines.push("### Summary");
  jiraLines.push("```text");
  jiraLines.push(summaryMarkdown || summaryText);
  jiraLines.push("```");
  if (attachmentLines.length) {
    jiraLines.push("");
    jiraLines.push("### Attachments");
    jiraLines.push(...attachmentLines.map((line) => line.replace("- ", "- ")));
  }

  return {
    servicenow: serviceNowLines.join("\n"),
    freshdesk: freshdeskLines.join("\n"),
    jira: jiraLines.join("\n"),
  };
}

function buildIncidentRequestPayload({ service, meta, status, context }) {
  return {
    generated_at: new Date().toISOString(),
    service,
    action: meta?.action || null,
    label: meta?.label || null,
    mode: meta?.mode || null,
    params: context?.params || sanitizeParams(meta?.params || {}),
    context: context?.highlights || {},
    status: {
      ok: meta?.ok ?? null,
      cancelled: Boolean(meta?.cancelled),
      http_status: meta?.http_status ?? null,
      graph_status: meta?.status_code ?? null,
      request_id: meta?.request_id ?? null,
      error: meta?.error ?? null,
      hint: meta?.hint ?? null,
      rate_limit: meta?.rate_limit ?? null,
      suggested_wait_seconds: meta?.suggested_wait_seconds ?? null,
      output_state: status?.state || null,
      output_text: status?.text || null,
      output_meta: status?.meta || null,
    },
    timing: {
      started_at: meta?.started_at || null,
      ended_at: meta?.ended_at || null,
      elapsed_ms: meta?.elapsed_ms ?? null,
    },
    preflight: meta?.preflight || null,
  };
}

function getCachedGlobalAdmin(key) {
  if (!key) return null;
  const entry = GLOBAL_ADMIN_CACHE.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expires) {
    GLOBAL_ADMIN_CACHE.delete(key);
    return null;
  }
  return entry.data;
}

function setCachedGlobalAdmin(key, data) {
  if (!key) return;
  GLOBAL_ADMIN_CACHE.set(key, { data, expires: Date.now() + GLOBAL_ADMIN_CACHE_TTL_MS });
}

function extractTargetUser(params) {
  if (!params || typeof params !== "object") return null;
  const candidates = [
    "user_principal_name",
    "user_upn",
    "upn",
    "user_id",
    "member_id",
    "member_upn",
    "sam_account_name",
  ];
  for (const key of candidates) {
    const value = params[key];
    if (value) return { key, value };
  }
  return null;
}

function extractUpnFromParams(params) {
  const target = extractTargetUser(params);
  if (!target) return null;
  const value = String(target.value || "");
  if (value.includes("@")) return value;
  return null;
}

function parseListCount(value) {
  if (!value) return 0;
  if (Array.isArray(value)) return value.length;
  if (typeof value === "string") {
    const parts = value.split(",").map((item) => item.trim()).filter(Boolean);
    return parts.length;
  }
  return 0;
}

function estimateImpactCount(params) {
  if (!params || typeof params !== "object") return null;
  const counts = [];
  const listKeys = [
    "items",
    "targets",
    "target_ids",
    "user_ids",
    "group_ids",
    "member_ids",
    "role_ids",
    "ids",
    "add_sku_ids",
    "remove_sku_ids",
    "roles",
  ];
  listKeys.forEach((key) => {
    const value = params[key];
    if (value) counts.push(parseListCount(value));
  });
  ["top", "limit", "count"].forEach((key) => {
    const value = params[key];
    if (value === undefined || value === null) return;
    const num = Number(value);
    if (Number.isFinite(num)) counts.push(num);
  });
  if (!counts.length) return null;
  return Math.max(...counts);
}

async function fetchGlobalAdminStatus(userValue) {
  if (!userValue) return null;
  const key = String(userValue || "").toLowerCase();
  const cached = getCachedGlobalAdmin(key);
  if (cached) return cached;
  try {
    const response = await runSystemTask("global_admin_check", { user_id: userValue });
    if (response.ok && response.data) {
      setCachedGlobalAdmin(key, response.data);
      const upn = response.data.user_principal_name;
      if (upn) setCachedGlobalAdmin(upn.toLowerCase(), response.data);
      const uid = response.data.user_id;
      if (uid) setCachedGlobalAdmin(uid.toLowerCase(), response.data);
      return response.data;
    }
  } catch (err) {
    return null;
  }
  return null;
}

async function applyGuardrails(service, action, params) {
  const risk = getActionRisk(service, action);
  const impact = estimateImpactCount(params);
  updateRunMeta(service, { guardrails: { risk, impact } });

  if (impact !== null && impact > IMPACT_WARN_THRESHOLD && risk !== "safe") {
    const confirmImpact = await confirmModal({
      title: "High impact action",
      message: `This action may affect about ${impact} objects. Continue?`,
      confirmLabel: "Continue",
      cancelLabel: "Cancel",
      danger: risk === "danger",
    });
    if (!confirmImpact) {
      return false;
    }
  }

  let globalAdminInfo = null;
  const target = extractTargetUser(params);
  if (target && GLOBAL_ADMIN_CHECK_SERVICES.has(service) && risk !== "safe") {
    globalAdminInfo = await fetchGlobalAdminStatus(target.value);
    if (globalAdminInfo?.user_principal_name) {
      updateRunMeta(service, { target_upn: globalAdminInfo.user_principal_name });
    }
    if (globalAdminInfo) {
      updateRunMeta(service, {
        global_admin_check: {
          is_global_admin: globalAdminInfo.is_global_admin,
          user_id: globalAdminInfo.user_id,
          user_principal_name: globalAdminInfo.user_principal_name,
        },
      });
    }
    if (globalAdminInfo?.is_global_admin) {
      const upnLabel = globalAdminInfo.user_principal_name || target.value;
      const confirmAdmin = await confirmModal({
        title: "Global administrator",
        message: `Warning: ${upnLabel} is a Global Administrator. Continue?`,
        confirmLabel: "Continue",
        cancelLabel: "Cancel",
        danger: true,
      });
      if (!confirmAdmin) {
        return false;
      }
    }
  }

  if (risk === "danger") {
    const upn = globalAdminInfo?.user_principal_name || extractUpnFromParams(params);
    const label = upn || target?.value || "the target user";
    const promptText = upn
      ? `Type the UPN to confirm this action:\n${upn}`
      : `Type the target identifier to confirm:\n${label}`;
    const typed = await promptModal({
      title: "Confirm dangerous action",
      subtitle: "Type the target identifier to confirm.",
      label: "Confirmation",
      placeholder: upn || label,
      confirmLabel: "Confirm",
      cancelLabel: "Cancel",
      required: true,
      hint: promptText,
    });
    if (!typed) return false;
    if (upn) {
      if (typed.trim().toLowerCase() !== upn.trim().toLowerCase()) {
        showToast("UPN did not match. Action cancelled.");
        return false;
      }
    } else if (typed.trim() !== String(label).trim()) {
      showToast("Confirmation did not match. Action cancelled.");
      return false;
    }
  }

  return true;
}

async function exportIncidentBundle(service) {
  const meta = lastRunMeta[service] || {};
  const status = lastOutputStatus[service] || {};
  const rawPanel = getOutputPanel(service);
  const rawOutput = rawPanel?.textContent || "";
  const payload = getExportPayload(service);
  if (!payload && !rawOutput.trim() && !meta.action) {
    showToast("No output to bundle yet");
    return;
  }
  showToast("Preparing incident bundle...");
  const generatedAt = new Date().toISOString();
  const context = buildIncidentContext(meta.params || {});
  const audit = await fetchIncidentAuditEntries(service, meta);
  const activity = loadActivity();
  const summaryPlain = buildIncidentSummary({
    service,
    meta,
    status,
    context,
    payload,
    audit,
    activity,
    rawOutput,
    generatedAt,
  });
  const entries = [];
  entries.push({ name: "summary.txt", data: summaryPlain });
  entries.push({
    name: "request.json",
    data: JSON.stringify(buildIncidentRequestPayload({ service, meta, status, context }), null, 2),
  });
  if (rawOutput.trim()) {
    entries.push({ name: "output.txt", data: rawOutput });
  }
  if (payload !== null && payload !== undefined) {
    entries.push({ name: "output.json", data: JSON.stringify(payload, null, 2) });
    const rows = resolveIncidentRows(payload);
    if (rows && rows.length) {
      entries.push({ name: "output.csv", data: toCsv(rows) });
    }
  }
  if (audit?.items && audit.items.length) {
    entries.push({ name: "audit-log.json", data: JSON.stringify(audit.items, null, 2) });
    entries.push({ name: "audit-log.csv", data: toCsv(audit.items) });
  } else if (audit?.error) {
    entries.push({ name: "audit-log.txt", data: `Audit fetch failed: ${audit.error}` });
  }
  if (activity && activity.length) {
    entries.push({ name: "activity.json", data: JSON.stringify(activity.slice(0, 25), null, 2) });
  }

  const snapshotCandidates = collectSnapshotCandidates(meta, context);
  const resolvedSubjects = await resolveSnapshotCandidates(snapshotCandidates);
  const canonicalIds = resolvedSubjects.map((entry) => entry.entity?.canonical_id).filter(Boolean);
  const snapshotSets = [];
  for (const entry of resolvedSubjects) {
    const canonicalId = entry.entity?.canonical_id;
    if (!canonicalId) continue;
    const snapshots = await fetchSnapshotHistory(canonicalId, 5);
    snapshotSets.push({
      canonical_id: canonicalId,
      kind: entry.entity?.kind,
      display_name: entry.entity?.display_name,
      snapshots,
    });
  }
  if (snapshotSets.length) {
    entries.push({ name: "snapshots.json", data: JSON.stringify(snapshotSets, null, 2) });
  }
  const diffs = [];
  for (const set of snapshotSets) {
    const snapshots = set.snapshots || [];
    if (snapshots.length < 2) continue;
    const diff = await fetchSnapshotEngineDiff(snapshots[0].snapshot_id, snapshots[1].snapshot_id);
    if (diff) {
      diffs.push({ canonical_id: set.canonical_id, diff });
    }
  }
  if (diffs.length) {
    entries.push({ name: "snapshot-diffs.json", data: JSON.stringify(diffs, null, 2) });
  }
  if (canonicalIds.length) {
    const events = await fetchSnapshotEvents(canonicalIds, 50);
    if (events.length) {
      entries.push({ name: "snapshot-events.json", data: JSON.stringify(events, null, 2) });
    }
  }
  const evidenceRefs = extractEvidenceRefsFromSnapshots(snapshotSets.flatMap((entry) => entry.snapshots || []));
  if (evidenceRefs.length) {
    entries.push({ name: "evidence-refs.json", data: JSON.stringify(evidenceRefs, null, 2) });
  }
  const stamp = generatedAt.replace(/[:.]/g, "-");
  const base = sanitizeFilename(`${service}-${meta?.action || "output"}-${stamp}`);
  const bundleName = `${base}.zip`;
  const ticketData = buildIncidentTicketData({
    service,
    meta,
    status,
    context,
    payload,
    audit,
    activity,
    rawOutput,
    generatedAt,
    bundleName,
  });
  const attachmentNames = entries.map((entry) => entry.name);
  const markdownSummary = buildIncidentMarkdownSummary(ticketData, attachmentNames);
  const templates = buildTicketTemplates({
    title: `${ticketData.serviceLabel}: ${ticketData.actionLabel} (${ticketData.resultLabel})`,
    summaryText: summaryPlain,
    summaryMarkdown: markdownSummary,
    attachments: attachmentNames,
    bundleName,
  });
  entries.push({ name: "summary.md", data: markdownSummary });
  entries.push({ name: "ticket-servicenow.txt", data: templates.servicenow });
  entries.push({ name: "ticket-freshdesk.txt", data: templates.freshdesk });
  entries.push({ name: "ticket-jira.md", data: templates.jira });
  downloadZip(bundleName, entries);
  showToast("Incident bundle exported");
}

function buildPackSummary(pack, results, status, runParams) {
  const lines = [];
  lines.push(`Action pack: ${pack.name || pack.id}`);
  lines.push(`Status: ${status}`);
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push("");
  lines.push("Steps:");
  results.forEach((result, index) => {
    const label = result.label || `${result.service}.${result.action}`;
    const outcome = result.ok ? "OK" : "FAILED";
    lines.push(`- ${index + 1}. ${label}: ${outcome}`);
  });
  if (runParams) {
    lines.push("");
    lines.push("Params:");
    try {
      lines.push(JSON.stringify(runParams, null, 2));
    } catch (err) {
      lines.push("Unable to serialize params.");
    }
  }
  return lines.join("\n");
}

function exportActionPackBundle(pack, results, runParams, status) {
  const generatedAt = new Date().toISOString();
  const stamp = generatedAt.replace(/[:.]/g, "-");
  const base = sanitizeFilename(`pack-${pack.id || "action-pack"}-${stamp}`);
  const bundleName = `${base}.zip`;
  const entries = [];
  const summary = buildPackSummary(pack, results, status, runParams);
  entries.push({ name: "summary.txt", data: summary });
  entries.push({
    name: "pack.json",
    data: JSON.stringify(
      {
        id: pack.id,
        name: pack.name,
        description: pack.description,
        status,
        generated_at: generatedAt,
        params: runParams,
      },
      null,
      2
    ),
  });
  entries.push({ name: "steps.json", data: JSON.stringify(results, null, 2) });

  const artifacts = [];
  results.forEach((result, index) => {
    const stepLabel = sanitizeFilename(`${index + 1}-${result.service}-${result.action}`);
    const payload = result.data ?? result.error ?? null;
    entries.push({
      name: `step-${stepLabel}.json`,
      data: JSON.stringify(
        {
          label: result.label,
          service: result.service,
          action: result.action,
          ok: result.ok,
          params: result.params || {},
          data: result.data ?? null,
          error: result.error ?? null,
        },
        null,
        2
      ),
    });
    const rows = resolveIncidentRows(payload);
    if (rows && rows.length) {
      entries.push({ name: `step-${stepLabel}.csv`, data: toCsv(rows) });
    }
    if (result?.artifact?.url) {
      artifacts.push({
        step: stepLabel,
        name: result.artifact.name,
        url: result.artifact.url,
      });
    }
  });

  if (artifacts.length) {
    entries.push({ name: "artifacts.json", data: JSON.stringify(artifacts, null, 2) });
  }

  downloadZip(bundleName, entries);
  showToast("Action pack incident bundle exported");
}

function hasPowerShellFallback(service) {
  const actions = ACTIONS_UI?.[service] || {};
  return Object.values(actions).some((meta) => meta?.mode === "powershell");
}

function classifyError(meta) {
  if (!meta) return null;
  const status = Number(meta.status || 0);
  const code = String(meta.code || "").toLowerCase();
  const message = String(meta.message || "").toLowerCase();
  const detailText = typeof meta.detail === "string" ? meta.detail.toLowerCase() : "";
  const errorText = extractErrorText(meta);
  const source = meta.failureSource || meta.failureOrigin || "";
  const outcome = meta.failureOutcome || "";
  const errorClass = String(meta.errorClass || "").toLowerCase();

  if (errorClass === "circuit_open" || outcome === "circuit_open") {
    return {
      type: "circuit_open",
      label: "Circuit breaker open",
      summary: "Graph returned repeated 5xx errors; the dashboard opened a circuit breaker to prevent amplification.",
    };
  }
  if (source === "dashboard_parse_error") {
    return {
      type: "dashboard_parse_error",
      label: "Dashboard parse error",
      summary: "Dashboard received a non-JSON response when JSON was expected.",
    };
  }
  if (source === "dashboard_http") {
    return {
      type: "dashboard_http",
      label: "Network/transport error",
      summary: "Dashboard failed before receiving a response from Graph.",
    };
  }

  if (
    status === 401 ||
    code.includes("invalidauthenticationtoken") ||
    message.includes("invalid authentication") ||
    message.includes("token expired")
  ) {
    return { type: "auth", label: "Token expired or invalid", summary: "Authentication token is missing or expired." };
  }
  if (status === 403 || code.includes("insufficientprivileges") || code.includes("authorization_requestdenied")) {
    return { type: "permission", label: "Missing permission", summary: "App lacks required Graph permissions." };
  }
  if (status === 429 || message.includes("throttle") || message.includes("too many")) {
    return { type: "throttle", label: "Throttled", summary: "Graph rate limits were hit." };
  }
  if (errorText.includes("module") && (errorText.includes("not found") || errorText.includes("could not be loaded"))) {
    return { type: "missing_module", label: "Missing module", summary: "Required PowerShell module is not installed." };
  }
  if (errorText.includes("access is denied") || errorText.includes("unauthorized")) {
    return { type: "access_denied", label: "Access denied", summary: "The account lacks required rights." };
  }
  if (errorText.includes("rpc server is unavailable")) {
    return { type: "rpc_unavailable", label: "RPC unavailable", summary: "RPC server is unavailable or blocked." };
  }
  if (
    errorText.includes("dns") &&
    (errorText.includes("failed") || errorText.includes("not found") || errorText.includes("nxdomain"))
  ) {
    return { type: "dns_failure", label: "DNS failure", summary: "Name resolution failed." };
  }
  if (errorText.includes("no such host")) {
    return { type: "dns_failure", label: "DNS failure", summary: "Host name could not be resolved." };
  }
  if (errorText.includes("connection refused") || errorText.includes("actively refused")) {
    return { type: "connection_refused", label: "Connection refused", summary: "Target refused the connection." };
  }
  if (status >= 500 || code.includes("serviceunavailable") || message.includes("service unavailable")) {
    return { type: "incident", label: "Service incident", summary: "Graph returned a 5xx transient error." };
  }
  if (
    code.includes("unsupported") ||
    message.includes("not supported") ||
    message.includes("unsupported") ||
    detailText.includes("not supported")
  ) {
    return { type: "unsupported", label: "Graph limitation", summary: "Graph does not support this operation." };
  }
  if (status === 404 || code.includes("request_resourcenotfound")) {
    return { type: "notfound", label: "Not found", summary: "Target resource could not be found." };
  }
  if (status === 400) {
    return { type: "badrequest", label: "Bad request", summary: "Inputs are invalid or incomplete." };
  }
  return { type: "unknown", label: "Unknown error", summary: "An unexpected error occurred." };
}

function summarizeGraphIssues(checks) {
  const buckets = {
    auth: [],
    permission: [],
    throttle: [],
    incident: [],
    latency: [],
    unknown: [],
  };
  Object.entries(checks || {}).forEach(([service, check]) => {
    if (!check) return;
    const status = Number(check.status || 0);
    const latencyMs = Number(check?.latency_ms ?? check?.latencyMs);
    const sla = getLatencySla(Number.isFinite(latencyMs) ? latencyMs : undefined, check?.ok);
    if (check.ok === false) {
      if (status === 401) buckets.auth.push(service);
      else if (status === 403) buckets.permission.push(service);
      else if (status === 429) buckets.throttle.push(service);
      else if (status >= 500) buckets.incident.push(service);
      else buckets.unknown.push(service);
    } else if (sla.state && sla.state !== "ok") {
      buckets.latency.push(service);
    }
  });
  return buckets;
}

function explainPrinterIssues(payload) {
  const list = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.printers)
      ? payload.printers
      : Array.isArray(payload?.value)
        ? payload.value
        : [];
  const conflicts = Array.isArray(payload?.conflicts) ? payload.conflicts : [];
  const issues = [];
  const offline = [];
  const error = [];
  const paused = [];
  list.forEach((printer) => {
    const status = String(printer?.PrinterStatus || printer?.Status || "").toLowerCase();
    const name = printer?.Name || printer?.ShareName || "Printer";
    if (!status) return;
    if (status.includes("offline")) offline.push(name);
    if (status.includes("error") || status.includes("failed")) error.push(name);
    if (status.includes("paused")) paused.push(name);
  });
  if (offline.length || error.length || paused.length || conflicts.length) {
    if (offline.length) issues.push(`Offline printers: ${offline.slice(0, 3).join(", ")}`);
    if (error.length) issues.push(`Error states: ${error.slice(0, 3).join(", ")}`);
    if (paused.length) issues.push(`Paused queues: ${paused.slice(0, 3).join(", ")}`);
    if (conflicts.length) issues.push(`${conflicts.length} GPO/printer mapping conflicts detected.`);
  }
  if (!issues.length) return null;
  return {
    title: "Printer queue errors detected",
    severity: "warn",
    summary: "Printer queues reported errors or deployment conflicts.",
    causes: [
      "Print spooler service may be stopped or unhealthy.",
      "Network connectivity or printer offline states.",
      "GPO deployment conflicts or missing print shares.",
    ],
    actions: [
      "Check printer online status and spooler service.",
      "Review GPO mappings for conflicts or missing shares.",
      "Verify driver availability on the print server.",
    ],
    details: issues,
  };
}

function explainGraphHealth(payload) {
  if (!payload?.graph?.checks) return null;
  const checks = payload.graph.checks;
  const buckets = summarizeGraphIssues(checks);
  const issues = []
    .concat(buckets.auth.length ? [`Auth failures: ${buckets.auth.map(formatServiceLabel).join(", ")}`] : [])
    .concat(
      buckets.permission.length
        ? [`Missing permissions: ${buckets.permission.map(formatServiceLabel).join(", ")}`]
        : []
    )
    .concat(
      buckets.throttle.length ? [`Throttling: ${buckets.throttle.map(formatServiceLabel).join(", ")}`] : []
    )
    .concat(
      buckets.incident.length ? [`Service incidents: ${buckets.incident.map(formatServiceLabel).join(", ")}`] : []
    )
    .concat(
      buckets.latency.length ? [`High latency: ${buckets.latency.map(formatServiceLabel).join(", ")}`] : []
    )
    .concat(buckets.unknown.length ? [`Other failures: ${buckets.unknown.map(formatServiceLabel).join(", ")}`] : []);
  if (!issues.length) {
    return {
      title: "Graph status healthy",
      severity: "ok",
      summary: "All Graph checks passed within SLA.",
      causes: [],
      actions: [],
    };
  }
  return {
    title: "Graph status degraded",
    severity: "warn",
    summary: "One or more Graph services reported degraded health.",
    causes: [
      "Missing permissions or invalid credentials.",
      "Rate limiting or transient service incidents.",
      "High latency impacting SLA thresholds.",
    ],
    actions: [
      "Verify app permissions and admin consent.",
      "Retry throttled calls after suggested wait.",
      "Check Microsoft 365 service health dashboard.",
    ],
    details: issues,
  };
}

function explainPowerShellHealth(payload) {
  if (!payload?.powershell?.modules) return null;
  const modules = payload.powershell.modules || {};
  const missing = Object.entries(modules)
    .filter(([, info]) => info?.installed === false)
    .map(([name]) => name);
  if (!missing.length) {
    return {
      title: "PowerShell modules ready",
      severity: "ok",
      summary: "Required PowerShell modules are installed.",
      causes: [],
      actions: [],
    };
  }
  return {
    title: "PowerShell modules missing",
    severity: "warn",
    summary: "Some required PowerShell modules are not installed.",
    causes: ["Required admin modules are missing from this host."],
    actions: [
      "Install the missing modules and restart the session.",
      "Confirm PowerShell 7 is available on this host.",
    ],
    details: [`Missing: ${missing.slice(0, 5).join(", ")}`],
  };
}

function explainSecurityPosture(payload) {
  if (!payload || typeof payload !== "object") return null;
  const explanations = [];
  const permissions = payload.permissions?.graph_app_permissions;
  if (permissions?.ok === false) {
    explanations.push({
      title: "Graph permissions inventory unavailable",
      severity: "warn",
      summary: permissions.error || "Unable to read Graph app role assignments.",
      causes: ["Missing Directory.Read.All or Application.Read.All permissions."],
      actions: ["Grant permissions and admin consent, then refresh the report."],
    });
  } else if (permissions) {
    const count = Number(permissions.assigned_count || 0);
    explanations.push({
      title: "Graph app permissions",
      severity: count > 0 ? "ok" : "warn",
      summary: count > 0 ? `${count} app permissions granted.` : "No Graph app permissions detected.",
      details: permissions.assigned?.length ? [permissions.assigned.slice(0, 6).join(", ")] : [],
      actions: count > 0 ? [] : ["Assign required app permissions and grant admin consent."],
    });
  }

  const secrets = payload.secrets || {};
  const storage = secrets.storage || "Unknown storage";
  if (!secrets.client_secret_set) {
    explanations.push({
      title: "Client secret missing",
      severity: "fail",
      summary: "Client secret is not configured, so app-only Graph cannot authenticate.",
      actions: ["Set the client secret in Settings and refresh the report."],
    });
  } else {
    const severity = secrets.use_keychain ? "ok" : secrets.keychain_available ? "warn" : "info";
    const actions = [];
    if (!secrets.use_keychain && secrets.keychain_available) {
      actions.push("Enable keychain storage to protect the client secret.");
    }
    if (!secrets.config_lock) {
      actions.push("Enable environment lock to prevent accidental edits.");
    }
    explanations.push({
      title: "Secret storage",
      severity,
      summary: `Secrets stored in ${storage}.`,
      actions,
    });
  }

  const boundaries = payload.boundaries || {};
  const boundaryItems = [];
  if (Array.isArray(boundaries.local_only) && boundaries.local_only.length) {
    boundaryItems.push(`Local-only: ${boundaries.local_only.map(formatServiceLabel).join(", ")}`);
  }
  if (Array.isArray(boundaries.cloud_services) && boundaries.cloud_services.length) {
    boundaryItems.push(`Cloud services: ${boundaries.cloud_services.map(formatServiceLabel).join(", ")}`);
  }
  if (Array.isArray(boundaries.cannot) && boundaries.cannot.length) {
    boundaryItems.push(`Cannot: ${boundaries.cannot.slice(0, 2).join(" · ")}`);
  }
  if (boundaryItems.length) {
    explanations.push({
      title: "Operational boundaries",
      severity: "info",
      summary: "Clarifies what runs locally vs in Microsoft 365 cloud.",
      causes: boundaryItems,
    });
  }

  return explanations;
}

function buildExplanations(service, payload) {
  const explanations = [];
  const meta = extractErrorMeta(payload);
  const context = lastActionContext[service] || {};
  const actionMeta = ACTIONS_UI?.[service]?.[context.action] || {};
  const actionLabel = actionMeta?.label || context.action || service;

  if (service === "health" && payload?.graph) {
    const graphExplain = explainGraphHealth(payload);
    if (graphExplain) explanations.push(graphExplain);
    const psExplain = explainPowerShellHealth(payload);
    if (psExplain) explanations.push(psExplain);
  }

  if (service === "printers") {
    const printerExplain = explainPrinterIssues(payload);
    if (printerExplain) explanations.push(printerExplain);
  }

  if (service === "security") {
    const securityExplain = explainSecurityPosture(payload) || [];
    securityExplain.forEach((item) => explanations.push(item));
  }

  if (meta && (payload?.ok === false || meta.status || meta.code || meta.message)) {
    const classification = classifyError(meta);
    const causes = [];
    const actions = [];
    if (classification?.type === "dashboard_parse_error") {
      causes.push("Dashboard expected JSON but received an unexpected response format.");
      actions.push("Check backend logs for an unhandled exception or proxy response.");
      actions.push("Retry after confirming the backend is running and reachable.");
    }
    if (classification?.type === "dashboard_http") {
      causes.push("Dashboard could not reach Graph or a network timeout occurred.");
      actions.push("Check network connectivity, proxy settings, and firewall rules.");
      actions.push("Retry after connectivity is restored.");
    }
    if (classification?.type === "circuit_open") {
      causes.push("Circuit breaker opened after repeated transient failures for this route group.");
      if (meta.suggestedWait) {
        actions.push(`Wait ${meta.suggestedWait} seconds, then retry.`);
      } else {
        actions.push("Wait briefly, then retry the action.");
      }
      actions.push("If the issue persists, export a support bundle and check Graph service health.");
    }
    if (classification?.type === "permission") {
      causes.push("App permission missing or admin consent not granted.");
      actions.push("Grant required permissions in Entra and grant admin consent.");
    }
    if (classification?.type === "auth") {
      causes.push("Token expired or invalid client credentials.");
      actions.push("Re-save client secret and retry.");
    }
    if (classification?.type === "throttle") {
      causes.push("Too many requests within a short window.");
      actions.push("Reduce request volume and retry after a delay.");
    }
    if (classification?.type === "missing_module") {
      causes.push("Required PowerShell module is not installed on this host.");
      actions.push("Install the missing module and restart the PowerShell session.");
    }
    if (classification?.type === "access_denied") {
      causes.push("Insufficient rights for the requested operation.");
      actions.push("Run as administrator or use an account with elevated rights.");
    }
    if (classification?.type === "rpc_unavailable") {
      causes.push("RPC service unavailable or blocked by firewall.");
      actions.push("Check RPC services and firewall rules between client and target.");
    }
    if (classification?.type === "dns_failure") {
      causes.push("DNS name resolution failed.");
      actions.push("Verify DNS records and resolve the hostname before retrying.");
    }
    if (classification?.type === "connection_refused") {
      causes.push("Target refused the connection.");
      actions.push("Verify the service is listening and firewall allows the port.");
    }
    if (classification?.type === "incident") {
      causes.push("Service incident or transient failure.");
      actions.push("Retry and monitor Microsoft 365 service health.");
    }
    if (classification?.type === "unsupported") {
      causes.push("Graph API does not support this operation.");
      if (hasPowerShellFallback(service)) {
        actions.push("Use the PowerShell fallback for this workflow.");
      }
    }
    if (service === "exchange" && classification?.type === "unsupported") {
      causes.push("Exchange mailbox permissions are not fully supported in Graph.");
      if (hasPowerShellFallback(service)) {
        actions.push("Use the Exchange PowerShell fallback for this mailbox task.");
      }
    }
    if (service === "exchange" && meta.status && classification?.type !== "permission") {
      causes.push("Mailbox settings can be restricted by tenant configuration.");
      actions.push("Verify Exchange settings and mailbox licensing.");
    }
    const triage = buildTriage(meta);
    if (triage?.recommendations?.length) {
      triage.recommendations.slice(0, 3).forEach((item) => actions.push(item));
    }
    explanations.push({
      title: `${actionLabel ? `${actionLabel} failed` : "Action failed"}`,
      severity: classification?.type === "incident" || classification?.type === "throttle" ? "warn" : "fail",
      summary: classification?.summary || "The action failed with an error.",
      causes: causes.length ? causes : ["Unexpected error; see details for context."],
      actions: actions.length ? actions : ["Review the error and retry."],
      details: meta.message ? [meta.message] : [],
    });

    const traceFacts = [];
    const traceActions = [];
    const requestTarget = meta.path || meta.url || null;
    const requestLine = [meta.method, requestTarget].filter(Boolean).join(" ");
    const sourceValue = meta.failureSource || meta.failureOrigin || null;
    const outcomeValue = meta.failureOutcome || null;
    if (sourceValue) {
      const sourceLabel = String(sourceValue).replace(/_/g, " ");
      traceFacts.push(`Source: ${sourceLabel}`);
    }
    if (outcomeValue) {
      const outcomeLabel = String(outcomeValue).replace(/_/g, " ");
      traceFacts.push(`Outcome: ${outcomeLabel}`);
    }
    if (meta.errorClass) {
      traceFacts.push(`error_class: ${meta.errorClass}`);
    }
    if (requestLine) traceFacts.push(`Request: ${requestLine}`);
    if (meta.requestId) traceFacts.push(`request-id: ${meta.requestId}`);
    if (meta.correlationId) traceFacts.push(`client-request-id: ${meta.correlationId}`);
    if (meta.uiRequestId) traceFacts.push(`ui_request_id: ${meta.uiRequestId}`);
    if (meta.tenantId) traceFacts.push(`tenant_id: ${meta.tenantId}`);
    if (meta.durationMs) traceFacts.push(`duration_ms: ${meta.durationMs}`);
    if (meta.queueWaitMs) traceFacts.push(`queue_wait_ms: ${meta.queueWaitMs}`);
    if (meta.routeGroup) traceFacts.push(`route_group: ${meta.routeGroup}`);
    if (meta.diagnostics?.date) traceFacts.push(`date: ${meta.diagnostics.date}`);
    if (meta.diagnostics?.ags) traceFacts.push(`x-ms-ags-diagnostic: ${trimText(String(meta.diagnostics.ags), 180)}`);

    const retryAttempts = meta.retry?.attempts;
    if (Array.isArray(retryAttempts) && retryAttempts.length) {
      traceFacts.push(
        `Attempts: ${retryAttempts.length}/${meta.retry?.total_attempts || retryAttempts.length}`
      );
      const timeline = retryAttempts
        .map((attempt) => {
          const status = attempt.status !== undefined && attempt.status !== null ? attempt.status : "ERR";
          const wait = attempt.wait_ms ? ` wait ${Math.round(attempt.wait_ms / 1000)}s` : "";
          return `${status}${wait}`;
        })
        .join(" · ");
      if (timeline) traceFacts.push(`Retry timeline: ${trimText(timeline, 220)}`);
    }

    if (meta.suggestedWait) {
      traceFacts.push(`suggested_wait_seconds: ${meta.suggestedWait}`);
    }
    if (meta.circuit && typeof meta.circuit === "object") {
      if (meta.circuit.route_group) {
        traceFacts.push(`circuit.route_group: ${meta.circuit.route_group}`);
      }
      if (meta.circuit.state) {
        traceFacts.push(`circuit.state: ${meta.circuit.state}`);
      }
      if (meta.circuit.remaining_seconds) {
        traceFacts.push(`circuit.remaining_seconds: ${meta.circuit.remaining_seconds}`);
      }
      if (meta.circuit.opened_reason) {
        traceFacts.push(`circuit.opened_reason: ${meta.circuit.opened_reason}`);
      }
      if (meta.circuit.last_upstream_status) {
        traceFacts.push(`circuit.last_upstream_status: ${meta.circuit.last_upstream_status}`);
      }
      if (meta.circuit.last_upstream_request_id) {
        traceFacts.push(`circuit.last_upstream_request_id: ${meta.circuit.last_upstream_request_id}`);
      }
      if (meta.circuit.last_upstream_timestamp) {
        traceFacts.push(`circuit.last_upstream_timestamp: ${meta.circuit.last_upstream_timestamp}`);
      }
    }
    if (sourceValue === "graph_upstream") {
      traceActions.push("Graph returned an error response. Use 'Export support bundle' to share request-id and headers for escalation.");
      if (outcomeValue === "retry_exhausted") {
        traceActions.push("Graph returned 5xx repeatedly; dashboard retries were exhausted.");
      }
    } else if (sourceValue === "dashboard_http") {
      traceActions.push("Request failed before reaching Graph; check backend connectivity/DNS/proxy and local network health.");
    } else if (sourceValue === "dashboard_parse_error") {
      traceActions.push("Dashboard could not parse the upstream response; inspect raw body/headers for HTML/proxy interstitials.");
    } else if (sourceValue === "dashboard_config_error") {
      traceActions.push("Configuration is incomplete; open Settings and verify tenant/client IDs and client secret.");
    } else if (
      (sourceValue === "dashboard_guardrail" || sourceValue === "dashboard_retry_policy") &&
      outcomeValue === "circuit_open"
    ) {
      traceActions.push("Graph returned repeated 5xx errors; the dashboard opened a circuit breaker to prevent amplification.");
      traceActions.push("Wait for cooldown, then retry. If errors persist, reduce request volume and check Microsoft 365 service health.");
    }
    if (traceFacts.length) {
      explanations.push({
        title: "Request context",
        severity: sourceValue && sourceValue !== "graph_upstream" ? "warn" : "info",
        summary: "Trace context and headers captured for root-cause analysis.",
        causes: traceFacts,
        actions: traceActions,
      });
    }
  }

  return explanations;
}

function renderWorkflowGuidance(service, payload, container) {
  if (service !== "remote_workflows") return false;
  if (!payload || typeof payload !== "object") return false;
  const guidance = payload.guidance || null;
  if (!guidance) return false;
  container.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.classList.add("workflow-guidance");

  const header = document.createElement("div");
  header.classList.add("guidance-header");
  const title = document.createElement("div");
  title.classList.add("guidance-title");
  title.textContent = payload.workflow?.name || "Remote workflow";
  const subtitle = document.createElement("div");
  subtitle.classList.add("guidance-subtitle");
  const purpose = payload.workflow?.purpose || "";
  const target = payload.meta?.target ? `Target: ${payload.meta.target}` : "";
  subtitle.textContent = [purpose, target].filter(Boolean).join(" · ");
  header.appendChild(title);
  header.appendChild(subtitle);
  wrapper.appendChild(header);

  const summarySection = document.createElement("div");
  summarySection.classList.add("guidance-section");
  const summaryTitle = document.createElement("div");
  summaryTitle.classList.add("guidance-section-title");
  summaryTitle.textContent = "Summary";
  const summaryRow = document.createElement("div");
  summaryRow.classList.add("guidance-summary");
  const statusPill = document.createElement("span");
  const status = payload.summary?.status || (guidance.observed?.length ? "warn" : "ok");
  statusPill.classList.add("status-pill", status);
  statusPill.textContent = status.toUpperCase();
  const summaryText = document.createElement("div");
  summaryText.textContent = payload.summary?.headline || guidance.summary || "Summary unavailable.";
  summaryRow.appendChild(statusPill);
  summaryRow.appendChild(summaryText);
  summarySection.appendChild(summaryTitle);
  summarySection.appendChild(summaryRow);
  wrapper.appendChild(summarySection);

  const guidanceSection = document.createElement("div");
  guidanceSection.classList.add("guidance-section");
  const guidanceTitle = document.createElement("div");
  guidanceTitle.classList.add("guidance-section-title");
  guidanceTitle.textContent = "Guidance";
  guidanceSection.appendChild(guidanceTitle);

  if (guidance.observed?.length) {
    const observedTitle = document.createElement("div");
    observedTitle.classList.add("guidance-subtitle");
    observedTitle.textContent = "What we observed";
    const observedList = document.createElement("ul");
    observedList.classList.add("guidance-list");
    guidance.observed.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item.text || "";
      if (Array.isArray(item.evidence_keys)) {
        item.evidence_keys.slice(0, 2).forEach((key) => {
          const tag = document.createElement("span");
          tag.classList.add("evidence-tag");
          tag.textContent = key;
          li.appendChild(tag);
        });
      }
      observedList.appendChild(li);
    });
    guidanceSection.appendChild(observedTitle);
    guidanceSection.appendChild(observedList);
  }

  if (guidance.why) {
    const whyTitle = document.createElement("div");
    whyTitle.classList.add("guidance-subtitle");
    whyTitle.textContent = "Why this matters";
    const whyText = document.createElement("div");
    whyText.textContent = guidance.why;
    guidanceSection.appendChild(whyTitle);
    guidanceSection.appendChild(whyText);
  }

  if (guidance.likely_cause?.text) {
    const likelyTitle = document.createElement("div");
    likelyTitle.classList.add("guidance-subtitle");
    likelyTitle.textContent = "Likely cause";
    const likelyText = document.createElement("div");
    likelyText.textContent = guidance.likely_cause.text;
    const confidence = document.createElement("span");
    confidence.classList.add("confidence-pill");
    confidence.textContent = `${(guidance.likely_cause.confidence || "low").toUpperCase()} confidence`;
    likelyText.appendChild(confidence);
    guidanceSection.appendChild(likelyTitle);
    guidanceSection.appendChild(likelyText);
  }

  if (guidance.next_checks?.length) {
    const nextTitle = document.createElement("div");
    nextTitle.classList.add("guidance-subtitle");
    nextTitle.textContent = "Suggested next checks";
    const nextList = document.createElement("ul");
    nextList.classList.add("guidance-list");
    guidance.next_checks.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      nextList.appendChild(li);
    });
    guidanceSection.appendChild(nextTitle);
    guidanceSection.appendChild(nextList);
  }

  if (guidance.limitations?.length) {
    const limitTitle = document.createElement("div");
    limitTitle.classList.add("guidance-subtitle");
    limitTitle.textContent = "Coverage limitations";
    const limitList = document.createElement("ul");
    limitList.classList.add("guidance-list");
    guidance.limitations.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      limitList.appendChild(li);
    });
    guidanceSection.appendChild(limitTitle);
    guidanceSection.appendChild(limitList);
  }

  wrapper.appendChild(guidanceSection);

  const evidence = payload.summary?.evidence || [];
  if (evidence.length) {
    const evidenceSection = document.createElement("div");
    evidenceSection.classList.add("guidance-section");
    const evidenceTitle = document.createElement("div");
    evidenceTitle.classList.add("guidance-section-title");
    evidenceTitle.textContent = "Evidence highlights";
    const grid = document.createElement("div");
    grid.classList.add("guidance-evidence-grid");
    evidence.forEach((item) => {
      const card = document.createElement("div");
      card.classList.add("guidance-evidence-item");
      const label = document.createElement("div");
      label.classList.add("guidance-evidence-label");
      label.textContent = item.label || "Evidence";
      const value = document.createElement("div");
      value.classList.add("guidance-evidence-value");
      value.textContent = item.value !== undefined && item.value !== null ? String(item.value) : "—";
      card.appendChild(label);
      card.appendChild(value);
      grid.appendChild(card);
    });
    evidenceSection.appendChild(evidenceTitle);
    evidenceSection.appendChild(grid);
    wrapper.appendChild(evidenceSection);
  }

  container.appendChild(wrapper);
  return true;
}

function renderExplanation(service, payload) {
  const container = getExplainPanel(service);
  if (!container) return;
  container.innerHTML = "";
  if (renderWorkflowGuidance(service, payload, container)) {
    return;
  }
  const explanations = buildExplanations(service, payload) || [];
  if (!explanations.length) {
    const empty = document.createElement("div");
    empty.classList.add("explain-empty");
    empty.textContent = "No issues detected. Outputs look healthy.";
    container.appendChild(empty);
    return;
  }
  explanations.forEach((exp) => {
    const card = document.createElement("div");
    card.classList.add("explain-card", exp.severity || "info");
    const title = document.createElement("div");
    title.classList.add("explain-title");
    title.textContent = exp.title || "Explanation";
    const summary = document.createElement("div");
    summary.classList.add("explain-summary");
    summary.textContent = exp.summary || "";
    card.appendChild(title);
    card.appendChild(summary);

    if (exp.details?.length) {
      const detail = document.createElement("div");
      detail.classList.add("explain-detail");
      detail.textContent = exp.details[0];
      card.appendChild(detail);
    }

    if (exp.causes?.length) {
      const list = document.createElement("ul");
      list.classList.add("explain-list");
      exp.causes.forEach((cause) => {
        const li = document.createElement("li");
        li.textContent = cause;
        list.appendChild(li);
      });
      card.appendChild(list);
    }

    if (exp.actions?.length) {
      const list = document.createElement("ul");
      list.classList.add("explain-list", "actions");
      exp.actions.forEach((action) => {
        const li = document.createElement("li");
        li.textContent = action;
        list.appendChild(li);
      });
      card.appendChild(list);
    }

    container.appendChild(card);
  });
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

function isPrimitive(value) {
  return value === null || value === undefined || typeof value !== "object";
}

function isEditableValue(value) {
  if (isPrimitive(value)) return true;
  if (Array.isArray(value)) {
    return value.every(isPrimitive);
  }
  return false;
}

function coerceValue(inputValue, originalValue) {
  if (originalValue === null || originalValue === undefined) {
    return inputValue === "" ? null : inputValue;
  }
  if (Array.isArray(originalValue)) {
    if (inputValue === "") return [];
    return inputValue
      .split(",")
      .map((entry) => entry.trim())
      .filter(Boolean);
  }
  if (typeof originalValue === "number") {
    if (inputValue === "") return null;
    const num = Number(inputValue);
    return Number.isNaN(num) ? originalValue : num;
  }
  if (typeof originalValue === "boolean") {
    return inputValue === "true";
  }
  return inputValue === "" ? null : inputValue;
}

function valuesEqual(a, b) {
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((value, idx) => String(value) === String(b[idx]));
  }
  return a === b;
}

function getUpdateCapability(service) {
  const context = lastActionContext[service];
  if (!context) return null;
  const mapping = UPDATE_CONTEXT_MAP?.[service] || {};
  const config = mapping[context.action];
  if (!config) return null;
  return { ...config, context };
}

function shouldStoreContext(service, action) {
  return Boolean(UPDATE_CONTEXT_MAP?.[service]?.[action]);
}

function buildUpdateParams(updateConfig, itemId, updates) {
  const params = {};
  const context = updateConfig.context?.params || {};
  updateConfig.contextKeys?.forEach((key) => {
    if (context[key] !== undefined) {
      params[key] = context[key];
    }
  });
  params[updateConfig.idParam || "id"] = itemId;
  params[updateConfig.payloadKey || "updates"] = updates;
  return params;
}

function applyUpdatePayload(current, updates, updateConfig) {
  const next = cloneRecord(current || {});
  if (updateConfig?.payloadKey === "fields") {
    if (!next.fields || typeof next.fields !== "object") {
      next.fields = {};
    }
    Object.entries(updates || {}).forEach(([key, value]) => {
      next.fields[key] = value;
    });
  } else {
    Object.assign(next, updates || {});
  }
  return next;
}

function normalizeFieldKey(key) {
  return String(key || "").toLowerCase();
}

function isFieldAllowed(updateConfig, fieldKey) {
  if (!updateConfig) return false;
  const key = normalizeFieldKey(fieldKey);
  if (updateConfig.payloadKey === "fields") {
    if (READ_ONLY_SHAREPOINT_FIELDS.has(key)) {
      return false;
    }
  }
  const allow = updateConfig.allowedFields;
  if (Array.isArray(allow) && allow.length) {
    return allow.map(normalizeFieldKey).includes(key);
  }
  return true;
}

function getFieldValidator(updateConfig, fieldKey) {
  const validators = updateConfig?.validators || {};
  const key = normalizeFieldKey(fieldKey);
  const direct = validators[fieldKey] || validators[key];
  if (direct) return direct;
  if (updateConfig?.autoValidators) {
    if (key.includes("email") || key.includes("mail")) return "email";
    if (key.endsWith("guid") || key.includes("guid")) return "guid";
    if (key.endsWith("date") || key.endsWith("datetime") || key.includes("date")) return "date";
  }
  return null;
}

function validateValue(kind, value) {
  if (value === null || value === undefined || value === "") return true;
  const raw = String(value).trim();
  if (!raw) return true;
  if (kind === "email") {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw);
  }
  if (kind === "guid") {
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(raw);
  }
  if (kind === "date") {
    const iso = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})?)?$/;
    if (!iso.test(raw)) return false;
    return !Number.isNaN(Date.parse(raw));
  }
  return true;
}

function validateUpdates(updateConfig, updates) {
  const errors = [];
  Object.entries(updates || {}).forEach(([key, value]) => {
    if (!isFieldAllowed(updateConfig, key)) {
      errors.push({ field: key, reason: "Read-only or not allowed" });
      return;
    }
    const validator = getFieldValidator(updateConfig, key);
    if (validator && !validateValue(validator, value)) {
      errors.push({ field: key, reason: `Invalid ${validator}` });
    }
  });
  return errors;
}

function buildDiffEntries(updateConfig, current, updates) {
  const diffs = [];
  Object.entries(updates || {}).forEach(([key, value]) => {
    let before;
    if (updateConfig?.payloadKey === "fields") {
      before = current?.fields?.[key];
    } else {
      before = current?.[key];
    }
    diffs.push({ field: key, from: before, to: value });
  });
  return diffs;
}

function buildDiffPreviewItem(updateConfig, current, updates) {
  const before = cloneRecord(current || {});
  const after = applyUpdatePayload(current, updates, updateConfig);
  const id = current?.[updateConfig?.idField || "id"];
  return {
    id,
    label: getPrimaryLabel(current || {}),
    changes: buildDiffEntries(updateConfig, current || {}, updates || {}),
    before,
    after,
  };
}

function buildDiffExportPayload(items, title) {
  return {
    generated_at: new Date().toISOString(),
    title: title || "Diff preview",
    items: items || [],
  };
}

function ensureDiffModal() {
  let modal = document.getElementById("diff-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "diff-modal";
  modal.classList.add("modal");
  modal.innerHTML = `
    <div class="modal-card diff-modal-card">
      <div class="modal-header">
        <div class="modal-title" id="diff-modal-title">Confirm changes</div>
        <div class="modal-actions">
          <button class="ghost small" id="diff-export">Export diff</button>
          <button class="ghost small" id="diff-cancel">Cancel</button>
          <button class="primary small" id="diff-confirm">Apply</button>
        </div>
      </div>
      <div class="modal-body">
        <div class="diff-toolbar">
          <label class="diff-toggle">
            <input type="checkbox" id="diff-dry-run" />
            <span>Dry run only (do not apply changes)</span>
          </label>
        </div>
        <div class="diff-list" id="diff-list"></div>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("open");
    }
  });
  return modal;
}

function showDiffPreview(items, title) {
  const modal = ensureDiffModal();
  const titleEl = modal.querySelector("#diff-modal-title");
  const listEl = modal.querySelector("#diff-list");
  const cancelBtn = modal.querySelector("#diff-cancel");
  const confirmBtn = modal.querySelector("#diff-confirm");
  const exportBtn = modal.querySelector("#diff-export");
  const dryRunToggle = modal.querySelector("#diff-dry-run");
  if (titleEl) titleEl.textContent = title || "Confirm changes";
  if (listEl) listEl.innerHTML = "";
  if (dryRunToggle) dryRunToggle.checked = false;

  (items || []).forEach((item) => {
    const card = document.createElement("div");
    card.classList.add("diff-item");
    const header = document.createElement("div");
    header.classList.add("diff-item-title");
    header.textContent = `${item.label || "Item"}${item.id ? ` · ${item.id}` : ""}`;
    card.appendChild(header);
    const changes = item.changes || [];
    changes.forEach((change) => {
      const row = document.createElement("div");
      row.classList.add("diff-row");
      const field = document.createElement("span");
      field.classList.add("diff-field");
      field.textContent = change.field;
      const from = document.createElement("span");
      from.classList.add("diff-from");
      from.textContent = formatValue(change.from);
      const arrow = document.createElement("span");
      arrow.classList.add("diff-arrow");
      arrow.textContent = "→";
      const to = document.createElement("span");
      to.classList.add("diff-to");
      to.textContent = formatValue(change.to);
      row.appendChild(field);
      row.appendChild(from);
      row.appendChild(arrow);
      row.appendChild(to);
      card.appendChild(row);
    });
    if (item.before || item.after) {
      const details = document.createElement("details");
      details.classList.add("diff-details");
      const summary = document.createElement("summary");
      summary.textContent = "Current vs Proposed";
      details.appendChild(summary);
      const beforeWrap = document.createElement("div");
      beforeWrap.classList.add("diff-section");
      const beforeTitle = document.createElement("div");
      beforeTitle.classList.add("diff-section-title");
      beforeTitle.textContent = "Current state";
      beforeWrap.appendChild(beforeTitle);
      beforeWrap.appendChild(renderValueTree(item.before));
      const afterWrap = document.createElement("div");
      afterWrap.classList.add("diff-section");
      const afterTitle = document.createElement("div");
      afterTitle.classList.add("diff-section-title");
      afterTitle.textContent = "Proposed state";
      afterWrap.appendChild(afterTitle);
      afterWrap.appendChild(renderValueTree(item.after));
      details.appendChild(beforeWrap);
      details.appendChild(afterWrap);
      card.appendChild(details);
    }
    listEl?.appendChild(card);
  });

  modal.classList.add("open");
  return new Promise((resolve) => {
    const cleanup = () => {
      modal.classList.remove("open");
      confirmBtn.onclick = null;
      cancelBtn.onclick = null;
      if (exportBtn) exportBtn.onclick = null;
    };
    if (exportBtn) {
      exportBtn.onclick = () => {
        const payload = buildDiffExportPayload(items, title);
        downloadJson(payload, `diff-${sanitizeFilename(title || "preview")}.json`);
      };
    }
    if (confirmBtn) {
      confirmBtn.onclick = () => {
        cleanup();
        resolve({ confirmed: true, dryRun: Boolean(dryRunToggle?.checked) });
      };
    }
    if (cancelBtn) {
      cancelBtn.onclick = () => {
        cleanup();
        resolve({ confirmed: false, dryRun: false });
      };
    }
  });
}

function getOutputCard(service) {
  const panel = getOutputPanel(service);
  if (!panel) return null;
  return panel.closest(".output-card");
}

function getBulkConcurrency(service) {
  const raw = localStorage.getItem(`${BULK_CONCURRENCY_KEY}:${service}`);
  const parsed = Number.parseInt(raw, 10);
  if (Number.isFinite(parsed) && parsed > 0) return parsed;
  return BULK_CONCURRENCY_DEFAULT;
}

function setBulkConcurrency(service, value) {
  const parsed = Math.max(1, Math.min(10, Number.parseInt(value, 10) || BULK_CONCURRENCY_DEFAULT));
  localStorage.setItem(`${BULK_CONCURRENCY_KEY}:${service}`, String(parsed));
  return parsed;
}

function registerBulkRetryButton(service, button) {
  if (!button) return;
  if (!bulkRetryButtons[service]) bulkRetryButtons[service] = [];
  bulkRetryButtons[service].push(button);
  updateBulkRetryButtons(service);
}

function updateBulkRetryButtons(service) {
  let buttons = bulkRetryButtons[service] || [];
  buttons = buttons.filter((button) => document.body.contains(button));
  bulkRetryButtons[service] = buttons;
  const failed = bulkFailureCache[service]?.items || [];
  const count = failed.length;
  buttons.forEach((button) => {
    button.disabled = count === 0;
    button.textContent = count ? `Retry failed (${count})` : "Retry failed";
  });
}

function setBulkFailures(service, data) {
  if (!data || !Array.isArray(data.items)) {
    delete bulkFailureCache[service];
  } else {
    bulkFailureCache[service] = data;
  }
  updateBulkRetryButtons(service);
}

function findRowById(service, id, mode) {
  if (!id) return null;
  const container = mode === "pretty" ? getPrettyPanel(service) : getTablePanel(service);
  if (!container) return null;
  const safe = CSS?.escape ? CSS.escape(String(id)) : String(id).replace(/"/g, '\\"');
  return container.querySelector(`[data-row-id="${safe}"]`);
}

function ensureBulkProgress(service) {
  const card = getOutputCard(service);
  if (!card) return null;
  let container = card.querySelector(`.bulk-progress[data-service="${service}"]`);
  if (container) return container;
  container = document.createElement("div");
  container.classList.add("bulk-progress");
  container.dataset.service = service;
  const title = document.createElement("div");
  title.classList.add("bulk-progress-title");
  title.textContent = "Bulk update progress";
  const list = document.createElement("div");
  list.classList.add("bulk-progress-list");
  container.appendChild(title);
  container.appendChild(list);
  card.insertBefore(container, card.querySelector(".output-status"));
  return container;
}

function updateBulkProgress(service, entries, summaryText) {
  const container = ensureBulkProgress(service);
  if (!container) return;
  const title = container.querySelector(".bulk-progress-title");
  if (title) {
    title.textContent = summaryText || "Bulk update progress";
  }
  const list = container.querySelector(".bulk-progress-list");
  if (!list) return;
  list.innerHTML = "";
  (entries || []).forEach((entry) => {
    const row = document.createElement("div");
    row.classList.add("bulk-progress-item", entry.status || "pending");
    const label = document.createElement("span");
    label.textContent = entry.label || entry.id || "Item";
    const status = document.createElement("span");
    status.textContent = entry.message || entry.status || "";
    row.appendChild(label);
    row.appendChild(status);
    list.appendChild(row);
  });
}

function clearBulkProgress(service) {
  const card = getOutputCard(service);
  if (!card) return;
  const container = card.querySelector(`.bulk-progress[data-service="${service}"]`);
  if (container) {
    container.remove();
  }
}

async function executeUpdate(service, updateConfig, itemId, updates) {
  const params = buildUpdateParams(updateConfig, itemId, updates);
  params._ui_request_id = generateUiRequestId();
  try {
    const res = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service, action: updateConfig.updateAction, params }),
    });
    const data = await res.json();
    if (!data.ok) {
      return {
        ok: false,
        error: data.error || "Update failed",
        status_code: data.status_code,
        data,
      };
    }
    return { ok: true, data: unwrapEnvelopeData(data.data) };
  } catch (err) {
    return { ok: false, error: err.message || "Update failed" };
  }
}

async function executeBulkUpdate(service, updateConfig, items) {
  const context = updateConfig.context?.params || {};
  try {
    const res = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        service,
        action: "bulk_update",
        params: {
          update_action: updateConfig.updateAction,
          items,
          context,
          _ui_request_id: generateUiRequestId(),
        },
      }),
    });
    const data = await res.json();
    if (!data.ok) {
      return { ok: false, error: data.error || "Bulk update failed", data };
    }
    return { ok: true, data: unwrapEnvelopeData(data.data) };
  } catch (err) {
    return { ok: false, error: err.message || "Bulk update failed" };
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTransientStatus(status) {
  const code = Number(status || 0);
  if (!code) return false;
  return code === 429 || code >= 500;
}

async function executeUpdateWithRetry(service, updateConfig, itemId, updates, options = {}) {
  const maxAttempts = options.maxAttempts || 3;
  const baseDelay = options.baseDelay || 600;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const result = await executeUpdate(service, updateConfig, itemId, updates);
    if (result.ok) return result;
    const status = result.status_code || result.data?.status_code;
    if (!isTransientStatus(status) || attempt === maxAttempts) {
      return result;
    }
    const suggested = result.data?.suggested_wait_seconds;
    const waitMs = suggested ? suggested * 1000 : Math.min(baseDelay * 2 ** (attempt - 1), 8000);
    const jitter = Math.floor(Math.random() * 250);
    if (options.onRetry) {
      options.onRetry({ attempt, waitMs: waitMs + jitter, status });
    }
    await sleep(waitMs + jitter);
  }
  return { ok: false, error: "Update failed" };
}

async function runBulkUpdateTasks(service, updateConfig, tasks, options = {}) {
  if (!tasks.length) {
    return { summary: { service, action: updateConfig.updateAction, total: 0, success: 0, failed: 0, results: [] }, failed: [] };
  }
  const concurrency = Math.min(
    Math.max(1, Number(options.concurrency || getBulkConcurrency(service)) || BULK_CONCURRENCY_DEFAULT),
    tasks.length
  );
  const progressEntries = tasks.map((task) => ({
    id: task.id,
    label: task.label || task.id || "Item",
    status: "pending",
    message: "Queued",
  }));
  updateBulkProgress(service, progressEntries, "Bulk update in progress");

  const summary = {
    service,
    action: updateConfig.updateAction,
    total: tasks.length,
    success: 0,
    failed: 0,
    results: [],
  };
  let completed = 0;
  let cursor = 0;
  const failedItems = [];

  const worker = async () => {
    while (cursor < tasks.length) {
      const index = cursor;
      cursor += 1;
      const task = tasks[index];
      const progress = progressEntries[index];
      progress.status = "running";
      progress.message = "Updating...";
      updateBulkProgress(service, progressEntries, `Updating ${completed + 1} of ${tasks.length}`);

      const response = await executeUpdateWithRetry(service, updateConfig, task.id, task.updates, {
        onRetry: ({ attempt, waitMs }) => {
          progress.message = `Retry ${attempt} in ${(waitMs / 1000).toFixed(1)}s`;
          updateBulkProgress(service, progressEntries, `Retrying ${completed + 1} of ${tasks.length}`);
        },
      });

      if (response.ok) {
        progress.status = "ok";
        progress.message = "Updated";
        summary.success += 1;
        summary.results.push({ id: task.id, ok: true });
        if (task.onSuccess) task.onSuccess();
      } else {
        progress.status = "fail";
        progress.message = response.error || "Failed";
        summary.failed += 1;
        summary.results.push({ id: task.id, ok: false, error: response.error });
        failedItems.push({ id: task.id, updates: task.updates, label: task.label });
        if (task.onFailure) task.onFailure();
      }
      completed += 1;
      updateBulkProgress(service, progressEntries, `Processed ${completed} of ${tasks.length}`);
    }
  };

  const workers = Array.from({ length: concurrency }, worker);
  await Promise.all(workers);
  return { summary, failed: failedItems };
}

function finalizeBulkSummary(service, summary, label) {
  const bulkSummary = { ...summary, __bulk_summary__: true };
  setOutput(service, bulkSummary);
  setOutputStatus(service, {
    state: summary.failed ? "warn" : "ok",
    text: label || "Bulk update complete",
    meta: `${summary.success} ok · ${summary.failed} failed`,
    running: false,
  });
}

function reportDryRun(service, diffs, updateConfig) {
  const payload = {
    ok: true,
    dry_run: true,
    action: updateConfig?.updateAction,
    count: diffs.length,
    context: updateConfig?.context?.params || {},
    items: diffs,
  };
  setOutput(service, payload);
  setOutputStatus(service, {
    state: "ok",
    text: "Dry run complete",
    meta: `${diffs.length} change${diffs.length === 1 ? "" : "s"} (not applied)`,
    running: false,
  });
  showToast("Dry run complete");
}

async function retryFailedBulkUpdates(service, mode, columns) {
  const cache = bulkFailureCache[service];
  if (!cache || !cache.items?.length) {
    showToast("No failed updates to retry");
    return;
  }
  const updateConfig = cache.updateConfig;
  if (!updateConfig) {
    showToast("Missing update configuration");
    return;
  }
  const tasks = cache.items.map((item) => {
    const row = findRowById(service, item.id, mode);
    let original = null;
    if (row) {
      const current = mode === "pretty" ? prettyRowCurrent.get(row) || {} : tableRowCurrent.get(row) || {};
      original = cloneRecord(current);
      const optimistic = applyUpdatePayload(current, item.updates, updateConfig);
      if (mode === "pretty") {
        applyPrettyRowUpdates(row, optimistic);
      } else if (columns) {
        applyRowUpdates(row, columns, optimistic);
      }
    }
    return {
      id: item.id,
      updates: item.updates,
      label: item.label || item.id,
      onSuccess: () => {
        if (row) {
          if (mode === "pretty") {
            prettyRowOriginal.set(row, cloneRecord(prettyRowCurrent.get(row)));
          } else {
            tableRowOriginal.set(row, cloneRecord(tableRowCurrent.get(row)));
          }
        }
      },
      onFailure: () => {
        if (row && original) {
          if (mode === "pretty") {
            applyPrettyRowUpdates(row, original);
          } else if (columns) {
            applyRowUpdates(row, columns, original);
          }
        }
      },
    };
  });

  const { summary, failed } = await runBulkUpdateTasks(service, updateConfig, tasks, {
    concurrency: getBulkConcurrency(service),
  });
  setBulkFailures(service, {
    updateConfig,
    context: cache.context || {},
    items: failed,
    source: mode,
    columns,
  });
  finalizeBulkSummary(service, summary, "Retry complete");
  showToast("Retry completed");
}

function renderValueTree(value) {
  const container = document.createElement("div");
  container.classList.add("pretty-tree");

  if (isPrimitive(value)) {
    const leaf = document.createElement("div");
    leaf.classList.add("pretty-leaf");
    leaf.textContent = formatValue(value);
    container.appendChild(leaf);
    return container;
  }

  if (Array.isArray(value)) {
    if (!value.length) {
      const empty = document.createElement("div");
      empty.classList.add("pretty-empty");
      empty.textContent = "[]";
      container.appendChild(empty);
      return container;
    }
    value.forEach((item, index) => {
      const row = document.createElement("div");
      row.classList.add("pretty-node");
      const key = document.createElement("div");
      key.classList.add("pretty-key");
      key.textContent = `[${index}]`;
      const val = document.createElement("div");
      val.classList.add("pretty-value");
      if (isPrimitive(item)) {
        val.textContent = formatValue(item);
      } else {
        const details = document.createElement("details");
        details.classList.add("pretty-details");
        details.open = true;
        const summary = document.createElement("summary");
        summary.textContent = Array.isArray(item) ? `Array(${item.length})` : "Object";
        details.appendChild(summary);
        details.appendChild(renderValueTree(item));
        val.appendChild(details);
      }
      row.appendChild(key);
      row.appendChild(val);
      container.appendChild(row);
    });
    return container;
  }

  const entries = Object.entries(value || {});
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.classList.add("pretty-empty");
    empty.textContent = "{}";
    container.appendChild(empty);
    return container;
  }
  entries.forEach(([keyName, valRaw]) => {
    const row = document.createElement("div");
    row.classList.add("pretty-node");
    const key = document.createElement("div");
    key.classList.add("pretty-key");
    key.textContent = keyName;
    const val = document.createElement("div");
    val.classList.add("pretty-value");
    if (isPrimitive(valRaw)) {
      val.textContent = formatValue(valRaw);
    } else {
      const details = document.createElement("details");
      details.classList.add("pretty-details");
      details.open = false;
      const summary = document.createElement("summary");
      if (Array.isArray(valRaw)) {
        summary.textContent = `Array(${valRaw.length})`;
      } else {
        summary.textContent = "Object";
      }
      details.appendChild(summary);
      details.appendChild(renderValueTree(valRaw));
      val.appendChild(details);
    }
    row.appendChild(key);
    row.appendChild(val);
    container.appendChild(row);
  });
  return container;
}

function jsonPointer(parts) {
  if (!parts || !parts.length) return "/";
  return (
    "/" +
    parts
      .map((part) => String(part).replace(/~/g, "~0").replace(/\//g, "~1"))
      .join("/")
  );
}

function createInspectorState(rootValue) {
  return {
    rootValue,
    valueMap: new Map(),
    selectedPointer: null,
    searchQuery: "",
    matches: [],
    matchIndex: -1,
  };
}

function selectInspectorNode(modal, element, pointer) {
  if (!modal || !element) return;
  const prev = modal.querySelector(".json-selected");
  if (prev) prev.classList.remove("json-selected");
  element.classList.add("json-selected");
  modal._inspectorState.selectedPointer = pointer;
}

function renderJsonInspector(value, options = {}) {
  const state = options.state || createInspectorState(value);
  const container = document.createElement("div");
  container.classList.add("json-inspector");
  if (options.wrap) {
    container.classList.add("wrap");
  }
  const maxItems = options.maxItems || 200;
  const step = options.step || 200;

  const renderNode = (val, path, depth, label, isRoot = false) => {
    if (isPrimitive(val)) {
      const row = document.createElement("div");
      row.classList.add("json-row");
      row.style.setProperty("--depth", depth);
      const key = document.createElement("span");
      key.classList.add("json-key");
      key.textContent = label ?? "";
      const sep = document.createElement("span");
      sep.classList.add("json-sep");
      sep.textContent = label != null ? ":" : "";
      const valueEl = document.createElement("span");
      valueEl.classList.add("json-value");
      valueEl.textContent = formatValue(val);
      row.appendChild(key);
      row.appendChild(sep);
      row.appendChild(valueEl);
      const pointer = jsonPointer(path);
      row.dataset.pointer = pointer;
      row.dataset.search = `${label ?? ""} ${formatValue(val)}`.toLowerCase();
      state.valueMap.set(pointer, val);
      row.addEventListener("click", (event) => {
        event.stopPropagation();
        selectInspectorNode(options.modal, row, pointer);
      });
      return row;
    }

    const details = document.createElement("details");
    details.classList.add("json-node");
    details.open = isRoot;
    details.style.setProperty("--depth", depth);
    const summary = document.createElement("summary");
    summary.classList.add("json-summary");
    const key = document.createElement("span");
    key.classList.add("json-key");
    key.textContent = label ?? (isRoot ? "root" : "");
    const sep = document.createElement("span");
    sep.classList.add("json-sep");
    sep.textContent = label != null || isRoot ? ":" : "";
    const type = document.createElement("span");
    type.classList.add("json-type");
    const isArray = Array.isArray(val);
    const count = isArray ? val.length : Object.keys(val || {}).length;
    type.textContent = isArray ? `Array(${count})` : `Object(${count})`;
    summary.appendChild(key);
    summary.appendChild(sep);
    summary.appendChild(type);
    details.appendChild(summary);

    const pointer = jsonPointer(path);
    details.dataset.pointer = pointer;
    details.dataset.search = `${label ?? ""} ${type.textContent}`.toLowerCase();
    state.valueMap.set(pointer, val);

    summary.addEventListener("click", (event) => {
      event.stopPropagation();
      selectInspectorNode(options.modal, details, pointer);
    });

    const children = document.createElement("div");
    children.classList.add("json-children");
    details.appendChild(children);

    if (isArray) {
      let limit = maxItems;
      const renderArray = () => {
        children.innerHTML = "";
        const sliced = val.slice(0, limit);
        sliced.forEach((item, idx) => {
          children.appendChild(renderNode(item, [...path, idx], depth + 1, `[${idx}]`));
        });
        if (limit < val.length) {
          const more = document.createElement("div");
          more.classList.add("json-more");
          more.textContent = `Showing first ${limit} of ${val.length} items. `;
          const btn = document.createElement("button");
          btn.type = "button";
          btn.classList.add("ghost", "small");
          btn.textContent = `Load ${Math.min(step, val.length - limit)} more`;
          btn.addEventListener("click", (event) => {
            event.stopPropagation();
            limit = Math.min(val.length, limit + step);
            renderArray();
            if (options.modal) {
              runModalSearch(options.modal, options.modal._inspectorState.searchQuery || "");
            }
          });
          more.appendChild(btn);
          children.appendChild(more);
        }
      };
      renderArray();
    } else {
      Object.entries(val || {}).forEach(([childKey, childVal]) => {
        children.appendChild(renderNode(childVal, [...path, childKey], depth + 1, childKey));
      });
    }
    return details;
  };

  container.appendChild(renderNode(value, [], 0, null, true));
  return { container, state };
}

function runModalSearch(modal, queryOverride) {
  if (!modal) return;
  const state = modal._inspectorState;
  if (!state) return;
  const input = modal.querySelector("#modal-search");
  const meta = modal.querySelector("#modal-search-meta");
  const query = (queryOverride !== undefined ? queryOverride : input?.value || "").toLowerCase().trim();
  state.searchQuery = query;
  const matches = [];
  modal.querySelectorAll("[data-search]").forEach((node) => {
    node.classList.remove("match", "match-active");
    if (!query) return;
    if ((node.dataset.search || "").includes(query)) {
      node.classList.add("match");
      matches.push(node);
    }
  });
  state.matches = matches;
  state.matchIndex = matches.length ? 0 : -1;
  if (matches.length) {
    matches[0].classList.add("match-active");
    if (matches[0].scrollIntoView) {
      matches[0].scrollIntoView({ behavior: "smooth", block: "center" });
    }
    if (meta) meta.textContent = `1 / ${matches.length} matches`;
  } else {
    if (meta) meta.textContent = query ? "0 matches" : "";
  }
}

function jumpModalSearch(modal, direction) {
  if (!modal) return;
  const state = modal._inspectorState;
  if (!state || !state.matches.length) return;
  state.matches[state.matchIndex]?.classList.remove("match-active");
  const nextIndex = (state.matchIndex + direction + state.matches.length) % state.matches.length;
  state.matchIndex = nextIndex;
  const node = state.matches[nextIndex];
  node.classList.add("match-active");
  if (node.scrollIntoView) {
    node.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  const meta = modal.querySelector("#modal-search-meta");
  if (meta) meta.textContent = `${nextIndex + 1} / ${state.matches.length} matches`;
}

async function copyModalSelection(modal, mode) {
  if (!modal) return;
  const state = modal._inspectorState;
  if (!state) return;
  const pointer = state.selectedPointer;
  const value = pointer ? state.valueMap.get(pointer) : null;
  let payload = null;
  if (mode === "all") {
    payload = JSON.stringify(state.rootValue, null, 2);
  } else if (!pointer) {
    showToast("Select a node to copy");
    return;
  } else if (mode === "path") {
    payload = pointer;
  } else if (mode === "value") {
    payload = isPrimitive(value) ? String(value ?? "") : JSON.stringify(value, null, 2);
  } else {
    payload = JSON.stringify(value, null, 2);
  }
  try {
    await navigator.clipboard.writeText(payload);
    showToast("Copied");
  } catch (err) {
    showToast("Copy failed");
  }
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

function getStructuredList(service, parsed) {
  if (!parsed) return null;
  if (parsed?.__bulk_summary__ && lastStructuredLists[service]) {
    return lastStructuredLists[service];
  }
  if (Array.isArray(parsed)) return parsed;
  if (Array.isArray(parsed?.value)) return parsed.value;
  return null;
}

function getTableRows(service, parsed) {
  const list = getStructuredList(service, parsed);
  if (list) return list;
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
          <button class="ghost small" id="modal-expand">Expand all</button>
          <button class="ghost small" id="modal-collapse">Collapse all</button>
          <button class="ghost small" id="modal-copy-all">Copy JSON</button>
          <button class="ghost small" id="modal-top">Back to top</button>
          <button class="ghost small" id="modal-edit">Edit</button>
          <button class="primary small" id="modal-save">Save</button>
          <button class="ghost small" id="modal-close">Close</button>
        </div>
      </div>
      <div class="modal-toolbar">
        <div class="modal-search">
          <input id="modal-search" type="search" placeholder="Search keys/values" />
          <button class="ghost small" id="modal-search-prev">Prev</button>
          <button class="ghost small" id="modal-search-next">Next</button>
          <span class="modal-search-meta" id="modal-search-meta"></span>
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

  const expandButton = modal.querySelector("#modal-expand");
  const collapseButton = modal.querySelector("#modal-collapse");
  const topButton = modal.querySelector("#modal-top");
  const toggleModalDetails = (open) => {
    const body = modal.querySelector("#modal-body");
    if (!body) return;
    body.querySelectorAll("details.json-node").forEach((detail) => {
      detail.open = open;
    });
  };
  if (expandButton) {
    expandButton.addEventListener("click", () => toggleModalDetails(true));
  }
  if (collapseButton) {
    collapseButton.addEventListener("click", () => toggleModalDetails(false));
  }
  if (topButton) {
    topButton.addEventListener("click", () => {
      const card = modal.querySelector(".modal-card");
      if (card) {
        card.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }

  modal.dataset.wrap = "true";

  const searchInput = modal.querySelector("#modal-search");
  const searchPrev = modal.querySelector("#modal-search-prev");
  const searchNext = modal.querySelector("#modal-search-next");
  if (searchInput) {
    searchInput.addEventListener("input", () => runModalSearch(modal));
  }
  if (searchPrev) {
    searchPrev.addEventListener("click", () => jumpModalSearch(modal, -1));
  }
  if (searchNext) {
    searchNext.addEventListener("click", () => jumpModalSearch(modal, 1));
  }

  const copyAll = modal.querySelector("#modal-copy-all");
  if (copyAll) {
    copyAll.addEventListener("click", () => copyModalSelection(modal, "all"));
  }

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
  const expandButton = modal.querySelector("#modal-expand");
  const collapseButton = modal.querySelector("#modal-collapse");
  const topButton = modal.querySelector("#modal-top");
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

  const inspector = renderJsonInspector(data, { modal, wrap: modal.dataset.wrap === "true", maxItems: 200, step: 200 });
  modal._inspectorState = inspector.state;
  bodyEl.appendChild(inspector.container);
  if (topButton) {
    topButton.onclick = () => {
      bodyEl.scrollTo({ top: 0, behavior: "smooth" });
    };
  }
  runModalSearch(modal, "");

  if (expandButton && collapseButton) {
    const hasNested = Boolean(bodyEl.querySelector("details.json-node"));
    expandButton.style.display = hasNested ? "inline-flex" : "none";
    collapseButton.style.display = hasNested ? "inline-flex" : "none";
  }

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
        input.addEventListener("change", () => {
          input.dataset.touched = "true";
        });
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
        const wasTouched = input.dataset.touched === "true";
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
          if (field.key === "accountEnabled" && !wasTouched) {
            return;
          }
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
          const existing = bodyEl.querySelector(".json-inspector");
          if (existing) existing.remove();
          const refreshed = renderJsonInspector(data, { modal, wrap: modal.dataset.wrap === "true", maxItems: 200, step: 200 });
          modal._inspectorState = refreshed.state;
          const editPanel = bodyEl.querySelector(".edit-panel");
          if (editPanel) {
            bodyEl.insertBefore(refreshed.container, editPanel);
          } else {
            bodyEl.appendChild(refreshed.container);
          }
          runModalSearch(modal, modal._inspectorState.searchQuery || "");
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
  const updateConfig = getUpdateCapability(service);
  const canEdit = Boolean(updateConfig);
  if (!parsed) {
    const empty = document.createElement("div");
    empty.classList.add("pretty-empty");
    empty.textContent = "No structured data to display.";
    container.appendChild(empty);
    return;
  }

  const list = getStructuredList(service, parsed);
  if (list) {
    lastStructuredLists[service] = list;
  }
  if (list) {
    const listEl = document.createElement("div");
    listEl.classList.add("pretty-list");
    if (canEdit) {
      const toolbar = document.createElement("div");
      toolbar.classList.add("pretty-toolbar");
      const selectAll = document.createElement("input");
      selectAll.type = "checkbox";
      selectAll.classList.add("pretty-select-all");
      const selectLabel = document.createElement("span");
      selectLabel.textContent = "Select all";
      const editSelected = document.createElement("button");
      editSelected.type = "button";
      editSelected.classList.add("ghost", "small");
      editSelected.textContent = "Edit selected";
      const saveSelected = document.createElement("button");
      saveSelected.type = "button";
      saveSelected.classList.add("primary", "small");
      saveSelected.textContent = "Save selected";
      const cancelSelected = document.createElement("button");
      cancelSelected.type = "button";
      cancelSelected.classList.add("ghost", "small");
      cancelSelected.textContent = "Cancel";
      const retryFailed = document.createElement("button");
      retryFailed.type = "button";
      retryFailed.classList.add("ghost", "small");
      retryFailed.textContent = "Retry failed";
      registerBulkRetryButton(service, retryFailed);
      const concurrencyWrap = document.createElement("label");
      concurrencyWrap.classList.add("bulk-concurrency");
      const concurrencyLabel = document.createElement("span");
      concurrencyLabel.textContent = "Concurrency";
      const concurrencyInput = document.createElement("input");
      concurrencyInput.type = "number";
      concurrencyInput.min = "1";
      concurrencyInput.max = "10";
      concurrencyInput.value = String(getBulkConcurrency(service));
      concurrencyInput.addEventListener("change", () => {
        const next = setBulkConcurrency(service, concurrencyInput.value);
        concurrencyInput.value = String(next);
      });
      concurrencyWrap.appendChild(concurrencyLabel);
      concurrencyWrap.appendChild(concurrencyInput);
      toolbar.appendChild(selectAll);
      toolbar.appendChild(selectLabel);
      toolbar.appendChild(editSelected);
      toolbar.appendChild(saveSelected);
      toolbar.appendChild(cancelSelected);
      toolbar.appendChild(retryFailed);
      toolbar.appendChild(concurrencyWrap);
      listEl.appendChild(toolbar);

      selectAll.addEventListener("change", () => {
        const checked = selectAll.checked;
        listEl.querySelectorAll(".pretty-row .row-select").forEach((input) => {
          input.checked = checked;
        });
      });

      editSelected.addEventListener("click", () => {
        listEl.querySelectorAll(".pretty-row").forEach((row) => {
          const checkbox = row.querySelector(".row-select");
          if (checkbox?.checked) {
            enterPrettyEdit(row);
          }
        });
      });

      cancelSelected.addEventListener("click", () => {
        listEl.querySelectorAll(".pretty-row").forEach((row) => {
          const checkbox = row.querySelector(".row-select");
          if (checkbox?.checked) {
            exitPrettyEdit(row, true);
          }
        });
      });

      saveSelected.addEventListener("click", async () => {
        const selected = Array.from(listEl.querySelectorAll(".pretty-row")).filter((row) =>
          row.querySelector(".row-select")?.checked
        );
        if (!selected.length) {
          showToast("No rows selected");
          return;
        }
        if (selected.length > IMPACT_WARN_THRESHOLD) {
          const proceed = await confirmModal({
            title: "Bulk update confirmation",
            message: `This bulk update will affect ${selected.length} items. Continue?`,
            confirmLabel: "Continue",
            cancelLabel: "Cancel",
            danger: true,
          });
          if (!proceed) {
            showToast("Bulk update cancelled");
            return;
          }
        }
        const payloads = [];
        const optimistic = [];
        const diffs = [];
        const validationFailures = [];
        selected.forEach((row) => {
          const result = collectPrettyRowUpdates(row);
          if (!result) return;
          const { updates, original, current } = result;
          if (!Object.keys(updates).length) return;
          const errors = validateUpdates(updateConfig, updates);
          if (errors.length) {
            validationFailures.push({
              label: getPrimaryLabel(current),
              errors,
            });
            return;
          }
          optimistic.push({ row, original, current });
          payloads.push({
            id: current?.[updateConfig.idField || "id"],
            updates,
          });
          diffs.push(buildDiffPreviewItem(updateConfig, current, updates));
        });
        if (validationFailures.length) {
          const fields = validationFailures
            .map((entry) => `${entry.label}: ${entry.errors.map((err) => err.field).join(", ")}`)
            .slice(0, 3)
            .join(" | ");
          showToast(`Validation failed: ${fields}`);
          return;
        }
        if (!payloads.length) {
          showToast("No changes to save");
          return;
        }
        const preview = await showDiffPreview(diffs, "Confirm bulk updates");
        if (!preview.confirmed) {
          showToast("Bulk update cancelled");
          return;
        }
        if (preview.dryRun) {
          reportDryRun(service, diffs, updateConfig);
          return;
        }
        optimistic.forEach(({ row, current }) => {
          const updates = payloads.find((entry) => entry.id === current?.[updateConfig.idField || "id"])?.updates;
          const nextData = applyUpdatePayload(current, updates || {}, updateConfig);
          applyPrettyRowUpdates(row, nextData);
        });
        const tasks = optimistic.map((item, index) => ({
          id: item.current?.[updateConfig.idField || "id"],
          updates: payloads[index].updates,
          label: getPrimaryLabel(item.current),
          onSuccess: () => {
            prettyRowOriginal.set(item.row, cloneRecord(prettyRowCurrent.get(item.row)));
          },
          onFailure: () => {
            applyPrettyRowUpdates(item.row, item.original);
          },
        }));
        const { summary, failed } = await runBulkUpdateTasks(service, updateConfig, tasks, {
          concurrency: getBulkConcurrency(service),
        });
        setBulkFailures(service, {
          updateConfig,
          context: updateConfig.context?.params || {},
          items: failed,
          source: "pretty",
        });
        finalizeBulkSummary(service, summary, "Bulk update complete");
        showToast("Bulk update completed");
      });

      retryFailed.addEventListener("click", async () => {
        await retryFailedBulkUpdates(service, "pretty");
      });
    }
    list.forEach((item) => {
      const row = document.createElement("div");
      row.classList.add("pretty-row");
      row.dataset.search = buildSearchIndex(item);
      if (updateConfig?.idField && item?.[updateConfig.idField]) {
        row.dataset.rowId = item[updateConfig.idField];
      }
      prettyRowCurrent.set(row, cloneRecord(item));
      prettyRowOriginal.set(row, cloneRecord(item));

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
      if (canEdit) {
        const select = document.createElement("input");
        select.type = "checkbox";
        select.classList.add("row-select");
        actions.appendChild(select);
      }
      const viewBtn = document.createElement("button");
      viewBtn.type = "button";
      viewBtn.classList.add("ghost", "small");
      viewBtn.textContent = "View";
      viewBtn.addEventListener("click", () =>
        showModal(getPrimaryLabel(item), prettyRowCurrent.get(row), service)
      );
      const expandBtn = document.createElement("button");
      expandBtn.type = "button";
      expandBtn.classList.add("ghost", "small");
      expandBtn.textContent = "Expand";
      actions.appendChild(viewBtn);
      actions.appendChild(expandBtn);
      if (canEdit) {
        const editBtn = document.createElement("button");
        editBtn.type = "button";
        editBtn.classList.add("ghost", "small");
        editBtn.textContent = "Edit";
        const saveBtn = document.createElement("button");
        saveBtn.type = "button";
        saveBtn.classList.add("primary", "small");
        saveBtn.textContent = "Save";
        saveBtn.style.display = "none";
        const cancelBtn = document.createElement("button");
        cancelBtn.type = "button";
        cancelBtn.classList.add("ghost", "small");
        cancelBtn.textContent = "Cancel";
        cancelBtn.style.display = "none";
        editBtn.addEventListener("click", () => {
          enterPrettyEdit(row);
          editBtn.style.display = "none";
          saveBtn.style.display = "inline-flex";
          cancelBtn.style.display = "inline-flex";
        });
        cancelBtn.addEventListener("click", () => {
          exitPrettyEdit(row, true);
          editBtn.style.display = "inline-flex";
          saveBtn.style.display = "none";
          cancelBtn.style.display = "none";
        });
        saveBtn.addEventListener("click", async () => {
          const result = collectPrettyRowUpdates(row);
          if (!result) return;
          const { updates, original, current } = result;
          if (!Object.keys(updates).length) {
            showToast("No changes to save");
            exitPrettyEdit(row, false);
            editBtn.style.display = "inline-flex";
            saveBtn.style.display = "none";
            cancelBtn.style.display = "none";
            return;
          }
          const errors = validateUpdates(updateConfig, updates);
          if (errors.length) {
            showToast(`Validation failed: ${errors.map((err) => err.field).join(", ")}`);
            return;
          }
        const diffItem = buildDiffPreviewItem(updateConfig, current, updates);
        const preview = await showDiffPreview([diffItem], "Confirm update");
        if (!preview.confirmed) {
          showToast("Update cancelled");
          return;
        }
        if (preview.dryRun) {
          reportDryRun(service, [diffItem], updateConfig);
          return;
        }
          const optimisticData = applyUpdatePayload(current, updates, updateConfig);
          applyPrettyRowUpdates(row, optimisticData);
          const response = await executeUpdateWithRetry(
            service,
            updateConfig,
            current?.[updateConfig.idField],
            updates
          );
          if (!response.ok) {
            applyPrettyRowUpdates(row, original);
            showToast(response.error || "Update failed");
          } else {
            prettyRowOriginal.set(row, cloneRecord(prettyRowCurrent.get(row)));
            showToast("Row updated");
          }
          exitPrettyEdit(row, false);
          editBtn.style.display = "inline-flex";
          saveBtn.style.display = "none";
          cancelBtn.style.display = "none";
        });
        actions.appendChild(editBtn);
        actions.appendChild(saveBtn);
        actions.appendChild(cancelBtn);
      }

      row.appendChild(title);
      row.appendChild(meta);
      row.appendChild(actions);
      const detail = document.createElement("details");
      detail.classList.add("pretty-expand");
      detail.open = false;
      const summaryRow = document.createElement("summary");
      summaryRow.textContent = "Full details";
      detail.appendChild(summaryRow);
      detail.appendChild(renderValueTree(item));
      row.appendChild(detail);
      expandBtn.addEventListener("click", () => {
        detail.open = !detail.open;
        expandBtn.textContent = detail.open ? "Collapse" : "Expand";
      });
      expandBtn.textContent = "Expand";
      if (canEdit) {
        const editPanel = document.createElement("div");
        editPanel.classList.add("pretty-edit");
        editPanel.style.display = "none";
        const editFields = document.createElement("div");
        editFields.classList.add("pretty-edit-fields");
        let editableKeys = Object.keys(item || {}).filter(
          (key) => isEditableValue(item[key]) && isFieldAllowed(updateConfig, key)
        );
        if (updateConfig?.payloadKey === "fields" && item?.fields && typeof item.fields === "object") {
          editableKeys = Object.keys(item.fields)
            .filter((key) => isFieldAllowed(updateConfig, key))
            .map((key) => `fields.${key}`);
        }
        editableKeys.forEach((key) => {
          const field = document.createElement("label");
          field.classList.add("pretty-edit-field");
          field.textContent = key;
          const value = key.startsWith("fields.") ? item.fields?.[key.slice(7)] : item[key];
          const editor = buildCellEditor(value);
          editor.dataset.key = key;
          field.appendChild(editor);
          editFields.appendChild(field);
        });
        editPanel.appendChild(editFields);
        row.appendChild(editPanel);
      }
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
  card.appendChild(renderValueTree(parsed));
  container.appendChild(card);
  applyOutputSearch(service);
}

function buildCellEditor(value) {
  if (typeof value === "boolean") {
    const select = document.createElement("select");
    const optTrue = document.createElement("option");
    optTrue.value = "true";
    optTrue.textContent = "true";
    const optFalse = document.createElement("option");
    optFalse.value = "false";
    optFalse.textContent = "false";
    select.appendChild(optTrue);
    select.appendChild(optFalse);
    select.value = value ? "true" : "false";
    return select;
  }
  if (Array.isArray(value)) {
    const input = document.createElement("input");
    input.type = "text";
    input.value = value.map((entry) => String(entry)).join(", ");
    return input;
  }
  const input = document.createElement("input");
  input.type = typeof value === "number" ? "number" : "text";
  input.value = value === null || value === undefined ? "" : String(value);
  return input;
}

function enterTableEdit(tr, columns, updateConfig) {
  if (tr.dataset.editing === "true") return;
  const current = tableRowCurrent.get(tr) || {};
  columns.forEach((col) => {
    const td = tr.querySelector(`td[data-key="${col}"]`);
    if (!td) return;
    if (updateConfig?.payloadKey === "fields" && !col.startsWith("fields.")) {
      return;
    }
    const value = getColumnValue(current, col);
    const fieldName = col.startsWith("fields.") ? col.slice(7) : col;
    if (!isFieldAllowed(updateConfig, fieldName)) return;
    if (!isEditableValue(value)) return;
    td.innerHTML = "";
    const editor = buildCellEditor(value);
    editor.dataset.original = value;
    td.appendChild(editor);
  });
  tr.dataset.editing = "true";
}

function exitTableEdit(tr, columns, revert) {
  const current = tableRowCurrent.get(tr) || {};
  if (revert) {
    applyRowUpdates(tr, columns, current);
  } else {
    applyRowUpdates(tr, columns, current);
  }
  tr.dataset.editing = "false";
}

function collectTableRowUpdates(tr, columns, updateConfig) {
  const current = tableRowCurrent.get(tr) || {};
  const original = cloneRecord(current);
  const updates = {};
  columns.forEach((col) => {
    if (updateConfig?.payloadKey === "fields" && !col.startsWith("fields.")) {
      return;
    }
    const fieldName = col.startsWith("fields.") ? col.slice(7) : col;
    if (!isFieldAllowed(updateConfig, fieldName)) {
      return;
    }
    const td = tr.querySelector(`td[data-key="${col}"]`);
    if (!td) return;
    const input = td.querySelector("input, select");
    if (!input) return;
    const originalValue = getColumnValue(current, col);
    if (!isEditableValue(originalValue)) return;
    const nextValue = coerceValue(input.value, originalValue);
    if (!valuesEqual(nextValue, originalValue)) {
      if (col.startsWith("fields.")) {
        updates[col.slice(7)] = nextValue;
      } else {
        updates[col] = nextValue;
      }
    }
  });
  return { updates, original, current };
}

function applyRowUpdates(tr, columns, data) {
  tableRowCurrent.set(tr, cloneRecord(data));
  tr.dataset.search = buildSearchIndex(data);
  columns.forEach((col) => {
    const td = tr.querySelector(`td[data-key="${col}"]`);
    if (!td) return;
    const value = getColumnValue(data, col);
    const formatted = formatCellValue(value);
    const shortValue = trimText(formatted, 140);
    td.textContent = shortValue;
    if (formatted && formatted !== shortValue) {
      td.title = formatted.slice(0, 600);
    } else {
      td.removeAttribute("title");
    }
  });
  tr.dataset.editing = "false";
}

function getColumnValue(data, col) {
  if (col.startsWith("fields.")) {
    const key = col.slice(7);
    return data?.fields?.[key];
  }
  return data?.[col];
}

function setColumnValue(data, col, value) {
  if (col.startsWith("fields.")) {
    const key = col.slice(7);
    if (!data.fields || typeof data.fields !== "object") {
      data.fields = {};
    }
    data.fields[key] = value;
    return;
  }
  data[col] = value;
}

function updatePrettyRowDisplay(row, data) {
  prettyRowCurrent.set(row, cloneRecord(data));
  row.dataset.search = buildSearchIndex(data);
  const title = row.querySelector(".pretty-title");
  if (title) title.textContent = getPrimaryLabel(data);
  const meta = row.querySelector(".pretty-meta");
  if (meta) {
    meta.innerHTML = "";
    const summary = getSummaryFields(data);
    summary.forEach((field) => {
      const chip = document.createElement("span");
      chip.classList.add("meta-chip");
      chip.textContent = `${field.key}: ${field.value}`;
      meta.appendChild(chip);
    });
  }
  const detail = row.querySelector(".pretty-expand");
  if (detail) {
    detail.querySelectorAll(".pretty-tree").forEach((node) => node.remove());
    detail.appendChild(renderValueTree(data));
  }
  const editPanel = row.querySelector(".pretty-edit");
  if (editPanel) {
    editPanel.querySelectorAll("input, select").forEach((input) => {
      const key = input.dataset.key;
      if (!key) return;
      const value = data?.[key];
      if (input.tagName === "SELECT") {
        input.value = value ? "true" : "false";
      } else {
        input.value = value === null || value === undefined ? "" : String(value);
      }
    });
  }
}

function enterPrettyEdit(row) {
  if (row.dataset.editing === "true") return;
  const panel = row.querySelector(".pretty-edit");
  if (panel) {
    panel.style.display = "grid";
  }
  row.dataset.editing = "true";
}

function exitPrettyEdit(row, revert) {
  if (revert) {
    const current = prettyRowCurrent.get(row) || {};
    updatePrettyRowDisplay(row, current);
  }
  const panel = row.querySelector(".pretty-edit");
  if (panel) {
    panel.style.display = "none";
  }
  row.dataset.editing = "false";
}

function collectPrettyRowUpdates(row) {
  const current = prettyRowCurrent.get(row) || {};
  const original = cloneRecord(current);
  const updates = {};
  const panel = row.querySelector(".pretty-edit");
  if (!panel) return { updates, original, current };
  panel.querySelectorAll("input, select").forEach((input) => {
    const key = input.dataset.key;
    if (!key) return;
    const originalValue = key.startsWith("fields.") ? current?.fields?.[key.slice(7)] : current?.[key];
    if (!isEditableValue(originalValue)) return;
    const nextValue = coerceValue(input.value, originalValue);
    if (!valuesEqual(nextValue, originalValue)) {
      if (key.startsWith("fields.")) {
        updates[key.slice(7)] = nextValue;
      } else {
        updates[key] = nextValue;
      }
    }
  });
  return { updates, original, current };
}

function applyPrettyRowUpdates(row, data) {
  updatePrettyRowDisplay(row, data);
  row.dataset.editing = "false";
}

function renderTable(service, parsed) {
  const container = getTablePanel(service);
  if (!container) return;
  container.innerHTML = "";
  const rows = getTableRows(service, parsed);
  if (rows) {
    lastStructuredLists[service] = rows;
  }
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
  let columns = computeTableColumns(normalized);
  const updateConfig = getUpdateCapability(service);
  const canEdit = Boolean(updateConfig);
  if (updateConfig?.payloadKey === "fields") {
    const fieldColumns = new Set();
    normalized.forEach((row) => {
      const fields = row?.fields;
      if (fields && typeof fields === "object") {
        Object.keys(fields).forEach((key) => fieldColumns.add(`fields.${key}`));
      }
    });
    columns = columns.filter((col) => col !== "fields");
    columns = columns.concat(Array.from(fieldColumns));
  }

  const wrap = document.createElement("div");
  wrap.classList.add("table-wrap");
  if (canEdit) {
    const toolbar = document.createElement("div");
    toolbar.classList.add("table-toolbar");
    const selectAll = document.createElement("input");
    selectAll.type = "checkbox";
    selectAll.classList.add("table-select-all");
    const selectLabel = document.createElement("span");
    selectLabel.textContent = "Select all";
    const editSelected = document.createElement("button");
    editSelected.type = "button";
    editSelected.classList.add("ghost", "small");
    editSelected.textContent = "Edit selected";
    const saveSelected = document.createElement("button");
    saveSelected.type = "button";
    saveSelected.classList.add("primary", "small");
    saveSelected.textContent = "Save selected";
    const cancelSelected = document.createElement("button");
    cancelSelected.type = "button";
    cancelSelected.classList.add("ghost", "small");
    cancelSelected.textContent = "Cancel";
    const retryFailed = document.createElement("button");
    retryFailed.type = "button";
    retryFailed.classList.add("ghost", "small");
    retryFailed.textContent = "Retry failed";
    registerBulkRetryButton(service, retryFailed);
    const concurrencyWrap = document.createElement("label");
    concurrencyWrap.classList.add("bulk-concurrency");
    const concurrencyLabel = document.createElement("span");
    concurrencyLabel.textContent = "Concurrency";
    const concurrencyInput = document.createElement("input");
    concurrencyInput.type = "number";
    concurrencyInput.min = "1";
    concurrencyInput.max = "10";
    concurrencyInput.value = String(getBulkConcurrency(service));
    concurrencyInput.addEventListener("change", () => {
      const next = setBulkConcurrency(service, concurrencyInput.value);
      concurrencyInput.value = String(next);
    });
    concurrencyWrap.appendChild(concurrencyLabel);
    concurrencyWrap.appendChild(concurrencyInput);
    toolbar.appendChild(selectAll);
    toolbar.appendChild(selectLabel);
    toolbar.appendChild(editSelected);
    toolbar.appendChild(saveSelected);
    toolbar.appendChild(cancelSelected);
    toolbar.appendChild(retryFailed);
    toolbar.appendChild(concurrencyWrap);
    wrap.appendChild(toolbar);

    selectAll.addEventListener("change", () => {
      const checked = selectAll.checked;
      wrap.querySelectorAll("tbody .row-select").forEach((input) => {
        input.checked = checked;
      });
    });

    editSelected.addEventListener("click", () => {
      wrap.querySelectorAll("tbody tr").forEach((tr) => {
        const checkbox = tr.querySelector(".row-select");
        if (checkbox?.checked) {
          enterTableEdit(tr, columns, updateConfig);
        }
      });
    });

    cancelSelected.addEventListener("click", () => {
      wrap.querySelectorAll("tbody tr").forEach((tr) => {
        const checkbox = tr.querySelector(".row-select");
        if (checkbox?.checked) {
          exitTableEdit(tr, columns, true);
        }
      });
    });

      saveSelected.addEventListener("click", async () => {
        const selected = Array.from(wrap.querySelectorAll("tbody tr")).filter((tr) =>
          tr.querySelector(".row-select")?.checked
        );
        if (!selected.length) {
          showToast("No rows selected");
          return;
        }
        const validationFailures = [];
        const payloads = [];
        const optimistic = [];
        const diffs = [];
        selected.forEach((tr) => {
          const result = collectTableRowUpdates(tr, columns, updateConfig);
          if (!result) return;
          const { updates, original, current } = result;
          if (!Object.keys(updates).length) return;
          const errors = validateUpdates(updateConfig, updates);
          if (errors.length) {
            validationFailures.push({
              label: getPrimaryLabel(current),
              errors,
            });
            return;
          }
          const nextData = applyUpdatePayload(current, updates, updateConfig);
          optimistic.push({ tr, original, current, nextData });
          payloads.push({
            id: current?.[updateConfig.idField || "id"],
            updates,
          });
          diffs.push(buildDiffPreviewItem(updateConfig, current, updates));
        });
        if (validationFailures.length) {
          const fields = validationFailures
            .map((entry) => `${entry.label}: ${entry.errors.map((err) => err.field).join(", ")}`)
            .slice(0, 3)
            .join(" | ");
          showToast(`Validation failed: ${fields}`);
          return;
        }
        if (!payloads.length) {
          showToast("No changes to save");
          return;
        }
        const preview = await showDiffPreview(diffs, "Confirm bulk updates");
        if (!preview.confirmed) {
          showToast("Bulk update cancelled");
          return;
        }
        if (preview.dryRun) {
          reportDryRun(service, diffs, updateConfig);
          return;
        }
        optimistic.forEach(({ tr, nextData }) => applyRowUpdates(tr, columns, nextData));
        const tasks = optimistic.map((item, index) => ({
          id: item.current?.[updateConfig.idField || "id"],
          updates: payloads[index].updates,
          label: getPrimaryLabel(item.current),
          onSuccess: () => {
            tableRowOriginal.set(item.tr, cloneRecord(tableRowCurrent.get(item.tr)));
          },
          onFailure: () => {
            applyRowUpdates(item.tr, columns, item.original);
          },
        }));
        const { summary, failed } = await runBulkUpdateTasks(service, updateConfig, tasks, {
          concurrency: getBulkConcurrency(service),
        });
        setBulkFailures(service, {
          updateConfig,
          context: updateConfig.context?.params || {},
          items: failed,
          source: "table",
          columns,
        });
        finalizeBulkSummary(service, summary, "Bulk update complete");
        showToast("Bulk update completed");
      });

    retryFailed.addEventListener("click", async () => {
      await retryFailedBulkUpdates(service, "table", columns);
    });
    }

  const table = document.createElement("table");
  table.classList.add("data-table");
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  if (canEdit) {
    const thSelect = document.createElement("th");
    thSelect.textContent = "";
    headerRow.appendChild(thSelect);
  }
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
    if (updateConfig?.idField && row?.[updateConfig.idField]) {
      tr.dataset.rowId = row[updateConfig.idField];
    }
    tableRowCurrent.set(tr, cloneRecord(row));
    tableRowOriginal.set(tr, cloneRecord(row));
    if (canEdit) {
      const tdSelect = document.createElement("td");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.classList.add("row-select");
      tdSelect.appendChild(checkbox);
      tr.appendChild(tdSelect);
    }
    columns.forEach((col) => {
      const td = document.createElement("td");
      td.dataset.key = col;
      const rawValue = getColumnValue(row, col);
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
    viewBtn.addEventListener("click", () => showModal(getPrimaryLabel(row), tableRowCurrent.get(tr), service));
    actionTd.appendChild(viewBtn);
    if (canEdit) {
      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.classList.add("ghost", "small");
      editBtn.textContent = "Edit";
      const saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.classList.add("primary", "small");
      saveBtn.textContent = "Save";
      saveBtn.style.display = "none";
      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.classList.add("ghost", "small");
      cancelBtn.textContent = "Cancel";
      cancelBtn.style.display = "none";
      editBtn.addEventListener("click", () => {
        enterTableEdit(tr, columns, updateConfig);
        editBtn.style.display = "none";
        saveBtn.style.display = "inline-flex";
        cancelBtn.style.display = "inline-flex";
      });
      cancelBtn.addEventListener("click", () => {
        exitTableEdit(tr, columns, true);
        editBtn.style.display = "inline-flex";
        saveBtn.style.display = "none";
        cancelBtn.style.display = "none";
      });
      saveBtn.addEventListener("click", async () => {
        const result = collectTableRowUpdates(tr, columns, updateConfig);
        if (!result) return;
        const { updates, original, current } = result;
        if (!Object.keys(updates).length) {
          showToast("No changes to save");
          exitTableEdit(tr, columns, false);
          editBtn.style.display = "inline-flex";
          saveBtn.style.display = "none";
          cancelBtn.style.display = "none";
          return;
        }
        const errors = validateUpdates(updateConfig, updates);
        if (errors.length) {
          showToast(`Validation failed: ${errors.map((err) => err.field).join(", ")}`);
          return;
        }
        const diffItem = buildDiffPreviewItem(updateConfig, current, updates);
        const preview = await showDiffPreview([diffItem], "Confirm update");
        if (!preview.confirmed) {
          showToast("Update cancelled");
          return;
        }
        if (preview.dryRun) {
          reportDryRun(service, [diffItem], updateConfig);
          return;
        }
        const optimisticData = applyUpdatePayload(current, updates, updateConfig);
        applyRowUpdates(tr, columns, optimisticData);
          const response = await executeUpdateWithRetry(
            service,
            updateConfig,
            current?.[updateConfig.idField],
            updates
          );
        if (!response.ok) {
          applyRowUpdates(tr, columns, original);
          showToast(response.error || "Update failed");
        } else {
          tableRowOriginal.set(tr, cloneRecord(tableRowCurrent.get(tr)));
          showToast("Row updated");
        }
        exitTableEdit(tr, columns, false);
        editBtn.style.display = "inline-flex";
        saveBtn.style.display = "none";
        cancelBtn.style.display = "none";
      });
      actionTd.appendChild(editBtn);
      actionTd.appendChild(saveBtn);
      actionTd.appendChild(cancelBtn);
    }
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
  const isBulkSummary = typeof content === "object" && content?.__bulk_summary__;
  const isPowerShellEnvelope =
    typeof content === "object" &&
    content !== null &&
    Object.prototype.hasOwnProperty.call(content, "ok") &&
    Object.prototype.hasOwnProperty.call(content, "data") &&
    Object.prototype.hasOwnProperty.call(content, "error") &&
    Object.prototype.hasOwnProperty.call(content, "meta");

  if (typeof content === "string") {
    rawText = content;
    parsed = tryParseJson(content);
  } else {
    parsed = isPowerShellEnvelope ? content.data : content;
    rawText = JSON.stringify(content, null, 2) || "OK";
  }

  if (target) {
    target.textContent = rawText;
  }
  if (dashboard && service !== "dashboard") {
    dashboard.textContent = rawText;
  }
  lastOutputs[service] = parsed ?? rawText;
  updateArtifactButton(service, extractArtifact(content));
  updateSupportBundleButton(service, content);
  if (!isBulkSummary) {
    setBulkFailures(service, null);
  }
  renderPretty(service, parsed);
  renderTable(service, parsed);
  renderExplanation(service, parsed);
  renderGraph(service, parsed);
  if (service === "reports") {
    updateReportExportOptions(parsed);
  }
}

function extractArtifact(content) {
  if (!content || typeof content !== "object") return null;
  const meta = content.meta || content?.data?.meta;
  if (meta?.artifact) return meta.artifact;
  if (meta?.artifact_url) {
    return {
      url: meta.artifact_url,
      name: meta.artifact_name || meta.artifact_url,
    };
  }
  if (content.artifact) return content.artifact;
  return null;
}

function updateArtifactButton(service, artifact) {
  const card = document.querySelector(`.output-card[data-panel="${service}"]`);
  if (!card) return;
  let actions = card.querySelector(".output-actions");
  if (!actions) {
    const clearButton = card.querySelector(`.clear-output[data-output-target="${service}"]`);
    actions = document.createElement("div");
    actions.classList.add("output-actions");
    if (clearButton && clearButton.parentElement === card) {
      card.insertBefore(actions, clearButton);
    } else {
      card.appendChild(actions);
    }
  }
  let button = actions.querySelector(".artifact-download");
  if (!artifact) {
    if (button) button.remove();
    return;
  }
  if (!button) {
    button = document.createElement("button");
    button.type = "button";
    button.classList.add("ghost", "small", "artifact-download");
    actions.appendChild(button);
  }
  button.textContent = "Download report";
  button.dataset.url = artifact.url || "";
  button.onclick = () => {
    const url = button.dataset.url;
    if (!url) return;
    window.open(url, "_blank");
  };
}

function normalizeHeaderMap(headers) {
  const map = new Map();
  if (!headers || typeof headers !== "object") return map;
  Object.entries(headers).forEach(([key, value]) => {
    map.set(String(key).toLowerCase(), value);
  });
  return map;
}

function buildGraphSupportBundle(errorPayload) {
  if (!errorPayload || typeof errorPayload !== "object") return null;
  const rawGraph = errorPayload.raw_graph || errorPayload.rawGraph || {};
  const headersMap = normalizeHeaderMap(rawGraph.headers || {});
  const diagnostics = errorPayload.diagnostics || {};
  const rate = errorPayload.rate_limit || errorPayload.rateLimit || {};
  const rateMap = normalizeHeaderMap(rate || {});
  const pick = (key) => headersMap.get(key) ?? rateMap.get(key) ?? null;

  const selectedHeaders = {};
  [
    "retry-after",
    "x-ms-ags-diagnostic",
    "request-id",
    "client-request-id",
    "date",
    "x-ms-retry-after-ms",
  ].forEach((key) => {
    const val = pick(key);
    if (val !== null && val !== undefined && val !== "") {
      selectedHeaders[key] = val;
    }
  });
  if (!selectedHeaders.date && diagnostics?.date) {
    selectedHeaders.date = diagnostics.date;
  }

  return {
    service: errorPayload.service || null,
    action: errorPayload.action || null,
    method: errorPayload.method || null,
    path: errorPayload.path || null,
    url: errorPayload.url || null,
    timestamp: errorPayload.timestamp || null,
    status_code: errorPayload.status_code || errorPayload.status || null,
    request_id: errorPayload.request_id || null,
    correlation_id: errorPayload.correlation_id || null,
    ui_request_id: errorPayload.ui_request_id || null,
    failure_origin: errorPayload.failure_origin || null,
    duration_ms: errorPayload.duration_ms || null,
    headers: selectedHeaders,
    raw_body: rawGraph.body ?? null,
    attempts: errorPayload.retry?.attempts || null,
  };
}

function updateSupportBundleButton(service, content) {
  const card = document.querySelector(`.output-card[data-panel="${service}"]`);
  if (!card) return;
  let actions = card.querySelector(".output-actions");
  if (!actions) {
    const clearButton = card.querySelector(`.clear-output[data-output-target="${service}"]`);
    actions = document.createElement("div");
    actions.classList.add("output-actions");
    if (clearButton && clearButton.parentElement === card) {
      card.insertBefore(actions, clearButton);
    } else {
      card.appendChild(actions);
    }
  }
  let button = actions.querySelector(".support-bundle-download");

  const errorPayload =
    content && typeof content === "object" && content.ok === false ? content : null;
  const hasRawGraph = Boolean(errorPayload?.raw_graph || errorPayload?.rawGraph);
  if (!errorPayload || !hasRawGraph) {
    if (button) button.remove();
    return;
  }

  if (!button) {
    button = document.createElement("button");
    button.type = "button";
    button.classList.add("ghost", "small", "support-bundle-download");
    actions.appendChild(button);
  }
  button.textContent = "Export support bundle";
  button.onclick = () => {
    const bundle = buildGraphSupportBundle(errorPayload);
    if (!bundle) return;
    const context = lastActionContext[service] || {};
    const safeAction = sanitizeFilename(context.action || errorPayload.action || service);
    const id = sanitizeFilename(errorPayload.request_id || errorPayload.ui_request_id || "graph-error");
    downloadJson(bundle, `support-bundle-${service}-${safeAction}-${id}.json`);
    showToast("Support bundle exported");
  };
}

function unwrapEnvelopeData(payload) {
  if (
    payload &&
    typeof payload === "object" &&
    Object.prototype.hasOwnProperty.call(payload, "ok") &&
    Object.prototype.hasOwnProperty.call(payload, "data") &&
    Object.prototype.hasOwnProperty.call(payload, "error") &&
    Object.prototype.hasOwnProperty.call(payload, "meta")
  ) {
    return payload.data;
  }
  return payload;
}

async function confirmAction(service, action, params = {}) {
  const meta = ACTIONS_UI?.[service]?.[action];
  if (!meta?.confirm) return true;
  const label = meta.label || `${service}.${action}`;
  const risk = formatRiskLabel(getActionRisk(service, action));
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
  const detailBlock = details.length ? `\n\n${details.join("\n")}` : "";
  const message = `Risk: ${risk}\nConfirm ${label}?${detailBlock}`;
  const confirmed = await confirmModal({
    title: "Confirm action",
    message,
    confirmLabel: "Confirm",
    cancelLabel: "Cancel",
    danger: risk === "Dangerous",
  });
  return confirmed;
}

async function runAction(service, action, params = {}, options = {}) {
  initRunMeta(service, action, params);
  const executionTarget = options.target || resolveTargetSelection(service, action);
  const allowedTargets = getActionAllowedTargets(service, action);
  if (executionTarget.type === "ssh" && !allowedTargets.includes("ssh")) {
    showToast("This action is not permitted on remote targets.");
    return { ok: false, error: "Target not allowed" };
  }
  const preflight = await preflightAction(service, action, executionTarget);
  updateRunMeta(service, { preflight: sanitizeParams(preflight || {}) });
  if (!preflight.ok) {
    finalizeRunMeta(service, {
      ok: false,
      stage: "preflight_failed",
      error: "Preflight failed",
      details: preflight.data || preflight.error,
    });
    handlePreflightFailure(service, action, preflight.data || preflight.error);
    return { ok: false, preflight };
  }
  if (preflight.warning) {
    updateRunMeta(service, { preflight_warning: sanitizeParams(preflight.warning) });
    handlePreflightWarning(service, action, preflight.warning);
  }
  const track = options.track !== false;
  if (track && activeRequests.has(service)) {
    finalizeRunMeta(service, { ok: false, busy: true, error: "Action already running" });
    showToast("Action already running");
    return { ok: false, busy: true };
  }
  const guardrailsOk = await applyGuardrails(service, action, params);
  if (!guardrailsOk) {
    finalizeRunMeta(service, { ok: false, cancelled: true, stage: "guardrails" });
    showToast("Action cancelled by guardrails");
    addActivity(`Guardrails cancelled: ${activityLabel(service, action)}`);
    setOutput(service, "Cancelled.");
    setOutputStatus(service, {
      state: "warn",
      text: `${activityLabel(service, action)} cancelled`,
      meta: "Guardrails stopped the action",
      running: false,
    });
    return { ok: false, cancelled: true };
  }
  const controller = options.controller || new AbortController();
  if (track) {
    activeRequests.set(service, controller);
    setRunnerRunning(service, true);
  }
  if (!(await confirmAction(service, action, params))) {
    finalizeRunMeta(service, { ok: false, cancelled: true, stage: "cancelled" });
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
  updateRunMeta(service, {
    label,
    mode,
    params: sanitizeParams(params || {}),
    execution_target: executionTarget,
  });
  if (shouldStoreContext(service, action)) {
    lastActionContext[service] = { action, params };
  }
  showToast("Dispatching action...");
  updateRunMeta(service, { dispatched_at: new Date().toISOString() });
  setOutput(service, "Running...");
  const targetLabel = formatSshTargetLabel(executionTarget);
  setOutputStatus(service, {
    state: "running",
    text: `${label} running`,
    meta: `${modeText} · ${targetLabel} · Elapsed 0.0s`,
    running: true,
  });
  startOutputTimer(service, `${modeText} · ${targetLabel}`);
  const stats = getStats();
  stats.total += 1;
  saveStats(stats);
  updateMetrics();

  try {
    const startedAt = performance.now();
    updateRunMeta(service, { request_started_at: new Date().toISOString() });
    const finalParams = { ...(params || {}) };
    if (shouldDisableSnapshots(service, action)) {
      finalParams._snapshot = false;
    }
    const uiRequestId = generateUiRequestId();
    finalParams._ui_request_id = uiRequestId;
    updateRunMeta(service, { ui_request_id: uiRequestId });
    const res = await fetch("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service, action, params: finalParams, target: executionTarget }),
      signal: controller.signal,
    });
    const data = await res.json();
    const elapsedMs = performance.now() - startedAt;
    if (!data.ok) {
      const errorMeta = extractErrorMeta(data) || {};
      finalizeRunMeta(service, {
        ok: false,
        http_status: res.status,
        status_code: errorMeta.status || data.status_code || data.status || null,
        request_id: errorMeta.requestId || data.request_id || null,
        correlation_id: errorMeta.correlationId || data.correlation_id || null,
        failure_source: errorMeta.failureSource || data.failure_source || data.failure_origin || null,
        failure_outcome: errorMeta.failureOutcome || data.failure_outcome || null,
        failure_origin: errorMeta.failureOrigin || data.failure_origin || null,
        error: errorMeta.message || data.error || null,
        hint: errorMeta.hint || data.hint || null,
        rate_limit: errorMeta.rateLimit || data.rate_limit || null,
        suggested_wait_seconds: errorMeta.suggestedWait || data.suggested_wait_seconds || null,
        elapsed_ms: elapsedMs,
      });
      setOutput(service, data);
      const source = errorMeta.failureSource || data.failure_source || data.failure_origin || null;
      const outcome = errorMeta.failureOutcome || data.failure_outcome || null;
      const sourceLabel = source ? String(source).replace(/_/g, " ") : "";
      const outcomeLabel = outcome ? String(outcome).replace(/_/g, " ") : "";
      const statusLabel = `HTTP ${res.status}`;
      setOutputStatus(service, {
        state: "fail",
        text: `${label} failed`,
        meta: [statusLabel, sourceLabel, outcomeLabel, formatElapsed(elapsedMs)].filter(Boolean).join(" · "),
        running: false,
      });
      addActivity(`Failed: ${activityLabel(service, action)}`);
      updateMetrics();
      return { ok: false, data };
    }
    const payload = unwrapEnvelopeData(data.data);
    if (shouldStoreContext(service, action)) {
      lastActionContext[service] = { action, params };
    }
    setOutput(service, data.data);
    if (service === "reports") {
      refreshReportHistory();
    }
    if (service === "onedrive" && action === "get_user_drive_id") {
      const pending = payload?.status === "pending";
      const cached = Boolean(payload?.cached);
      const fallback = Boolean(payload?.cache_fallback);
      const source = payload?.source || null;
      const pendingRow = payload?.pending && typeof payload.pending === "object" ? payload.pending : null;
      const verified = payload?.last_verified_at ? formatRelativeTime(payload.last_verified_at) : null;
      const circuitRemaining = payload?.circuit?.remaining_seconds ? Number(payload.circuit.remaining_seconds) : null;
      const nextRetrySeconds = Number.isFinite(Number(payload?.next_retry_seconds))
        ? Number(payload.next_retry_seconds)
        : null;
      const attempts = Number.isFinite(Number(pendingRow?.attempts)) ? Number(pendingRow.attempts) : null;
      const maxAttempts = Number.isFinite(Number(pendingRow?.max_attempts)) ? Number(pendingRow.max_attempts) : 10;
      const nextRunAt = pendingRow?.next_run_at ? String(pendingRow.next_run_at) : "";
      let nextRunAtLabel = null;
      if (nextRunAt) {
        const parsed = new Date(nextRunAt);
        if (!Number.isNaN(parsed.getTime())) {
          nextRunAtLabel = parsed.toLocaleString();
        }
      }
      const bannerMetaParts = []
        .concat(verified ? [`Last verified: ${verified}`] : [])
        .concat(Number.isFinite(circuitRemaining) ? [`Cooldown: ${circuitRemaining}s`] : [])
        .concat(Number.isFinite(nextRetrySeconds) ? [`Next retry: ${nextRetrySeconds}s`] : [])
        .concat(Number.isFinite(attempts) ? [`Attempts: ${attempts}/${maxAttempts}`] : [])
        .concat(nextRunAtLabel ? [`Retry at: ${nextRunAtLabel}`] : []);
      if (pending) {
        const identifier = (pendingRow?.user_upn || "").trim();
        const actions = identifier
          ? [
              {
                label: "Requeue",
                title: "Reset attempts and retry soon",
                onClick: () => {
                  runAction("onedrive", "requeue_drive_resolution", { user_upn: identifier }).catch(() => {});
                },
              },
              {
                label: "Force live",
                title: "Attempt live resolution now",
                onClick: () => {
                  runAction("onedrive", "force_live_resolve", { user_upn: identifier }).catch(() => {});
                },
              },
              {
                label: "Seed cache",
                title: "Manually seed the drive cache (escape hatch)",
                onClick: async () => {
                  const values = await openFormModal({
                    title: "Seed OneDrive drive cache",
                    subtitle: "Manual override (use when Graph is degraded)",
                    fields: [
                      { key: "user_upn", label: "User UPN", value: identifier, required: true },
                      { key: "drive_id", label: "Drive ID", required: true },
                      { key: "web_url", label: "Web URL (optional)" },
                      { key: "drive_type", label: "Drive type (optional)" },
                      { key: "user_object_id", label: "User object ID (optional)" },
                    ],
                    confirmLabel: "Seed cache",
                    cancelLabel: "Cancel",
                    size: "medium",
                  });
                  if (!values) return;
                  runAction("onedrive", "seed_drive_cache", values).catch(() => {});
                },
              },
            ]
          : null;
        showGraphStatusBanner(
          payload?.warning || "Drive ID queued for background resolution.",
          bannerMetaParts.filter(Boolean).join(" · "),
          actions
        );
      } else if (fallback) {
        const message = payload?.warning || "Using cached drive ID (Graph degraded)";
        showGraphStatusBanner(message, bannerMetaParts.filter(Boolean).join(" · "));
      } else if (source === "fallback") {
        showGraphStatusBanner(
          "Fallback resolver used (personal site path).",
          bannerMetaParts.filter(Boolean).join(" · ")
        );
      } else if (graphStatusMessage && graphStatusMessage.textContent.includes("Using cached drive ID")) {
        hideGraphStatusBanner();
      }
      if (cached) {
        updateRunMeta(service, {
          cache: { cached, fallback, last_verified_at: payload?.last_verified_at, source },
        });
      }
    }
    if (service === "onedrive" && action !== "get_user_drive_id") {
      const pending = payload && typeof payload === "object" && payload.status === "pending";
      if (pending) {
        const drive = payload?.drive || {};
        const verified = drive?.last_verified_at ? formatRelativeTime(drive.last_verified_at) : null;
        const circuitRemaining = drive?.circuit?.remaining_seconds ? Number(drive.circuit.remaining_seconds) : null;
        const nextRetrySeconds = Number.isFinite(Number(drive?.next_retry_seconds))
          ? Number(drive.next_retry_seconds)
          : Number.isFinite(Number(payload?.next_retry_seconds))
            ? Number(payload.next_retry_seconds)
            : null;
        const bannerMetaParts = []
          .concat(verified ? [`Last verified: ${verified}`] : [])
          .concat(Number.isFinite(circuitRemaining) ? [`Cooldown: ${circuitRemaining}s`] : [])
          .concat(Number.isFinite(nextRetrySeconds) ? [`Next retry: ${nextRetrySeconds}s`] : []);
        showGraphStatusBanner(
          payload?.warning || "Drive action queued; drive ID resolution pending.",
          bannerMetaParts.filter(Boolean).join(" · ")
        );
      }
    }
    if (service === "sharepoint" && action === "list_sites") {
      const fallback = Boolean(payload?.cache_fallback);
      const verified = payload?.last_verified_at ? formatRelativeTime(payload.last_verified_at) : null;
      const circuitRemaining = payload?.circuit?.remaining_seconds ? Number(payload.circuit.remaining_seconds) : null;
      const bannerMetaParts = []
        .concat(verified ? [`Last verified: ${verified}`] : [])
        .concat(Number.isFinite(circuitRemaining) ? [`Cooldown: ${circuitRemaining}s`] : []);
      if (fallback) {
        const message = payload?.warning || "Using cached sites (Graph degraded)";
        showGraphStatusBanner(message, bannerMetaParts.filter(Boolean).join(" · "));
      }
    }
    const pendingStatus = payload && typeof payload === "object" && payload.status === "pending";
    const onedrivePending = service === "onedrive" && pendingStatus;
    setOutputStatus(service, {
      state: onedrivePending ? "warn" : "ok",
      text: onedrivePending ? `${label} queued` : `${label} complete`,
      meta: (() => {
        if (service === "onedrive" && action === "get_user_drive_id" && payload && typeof payload === "object") {
          return [
            payload.status === "pending"
              ? Number.isFinite(Number(payload.next_retry_seconds))
                ? `Next retry: ${payload.next_retry_seconds}s`
                : "Queued"
              : null,
            payload.cache_fallback ? "Cache fallback" : payload.cached ? "Cached" : null,
            payload.source === "fallback" ? "Fallback resolver" : payload.source === "primary" ? "Primary resolver" : null,
            modeText,
            formatElapsed(elapsedMs),
          ]
            .filter(Boolean)
            .join(" · ");
        }
        if (onedrivePending) {
          const drive = payload?.drive || {};
          const nextRetrySeconds = Number.isFinite(Number(drive?.next_retry_seconds))
            ? Number(drive.next_retry_seconds)
            : Number.isFinite(Number(payload?.next_retry_seconds))
              ? Number(payload.next_retry_seconds)
              : null;
          return [
            Number.isFinite(nextRetrySeconds) ? `Next retry: ${nextRetrySeconds}s` : "Queued",
            modeText,
            formatElapsed(elapsedMs),
          ]
            .filter(Boolean)
            .join(" · ");
        }
        return `${modeText} · ${formatElapsed(elapsedMs)}`;
      })(),
      running: false,
    });
    finalizeRunMeta(service, {
      ok: true,
      http_status: res.status,
      request_id: data.request_id || data.data?.request_id || data.data?.requestId || null,
      elapsed_ms: elapsedMs,
    });
    if (service === "topology") {
      if (action === "collect_topology") {
        topologyData = payload;
        topologyPing = null;
        const snapshot = storeTopologySnapshot(payload);
        syncTopologyHistory(snapshot);
      } else if (action === "ping_targets") {
        topologyPing = payload;
      }
    }
    addActivity(`Ran: ${activityLabel(service, action)}`);
    if (service === "reports") {
      addReportHistory({
        id: `report-${Date.now()}-${Math.random().toString(16).slice(2)}`,
        action,
        label: activityLabel(service, action),
        timestamp: Date.now(),
        params,
        data: payload,
      });
    }
    if (!(service === "onedrive" && payload?.status === "pending")) {
      stats.success += 1;
      saveStats(stats);
      updateMetrics();
      showToast("Action completed");
    } else {
      saveStats(stats);
      updateMetrics();
      showToast(action === "get_user_drive_id" ? "Drive ID queued for warmup" : "Action queued");
    }
    return { ok: true, data: payload };
  } catch (err) {
    if (err.name === "AbortError") {
      finalizeRunMeta(service, { ok: false, cancelled: true, error: "Aborted" });
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
    finalizeRunMeta(service, { ok: false, error: err.message || "Error" });
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
    updateRunnerDraftButton(service);
  }
}

async function buildParams(service, action) {
  const prompts = ACTIONS_UI?.[service]?.[action]?.fields || [];
  const params = {};
  let cancelled = false;
  for (const prompt of prompts) {
    const value = await promptModal({
      title: prompt.label,
      label: prompt.label,
      confirmLabel: "Add",
      cancelLabel: "Cancel",
    });
    if (value === null) {
      cancelled = true;
      break;
    }
    params[prompt.key] = value;
  }
  if (cancelled) return null;
  return params;
}

function openRunnerForAction(service, action, params = {}) {
  if (!service || !action) return;
  setSection(service);
  const form = document.querySelector(`.runner[data-service="${service}"]`);
  if (!form) return;
  const select = form.querySelector(".action-select");
  if (select) {
    select.value = action;
    select.dispatchEvent(new Event("change"));
  }
  const fieldNodes = form.querySelectorAll(".runner-fields .field");
  fieldNodes.forEach((field) => {
    const key = field.dataset.field;
    if (!key || !(key in params)) return;
    const input = field.querySelector("input, select, textarea");
    if (!input) return;
    if (input.type === "checkbox") {
      input.checked = Boolean(params[key]);
      return;
    }
    input.value = params[key];
  });
  if (select) {
    select.scrollIntoView({ behavior: "smooth", block: "center" });
  }
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

  presetSave.addEventListener("click", async () => {
    const action = getActionSelection(service);
    const params = collectParams(service);
    if (!params) return;
    const name = await promptModal({
      title: "Save preset",
      label: "Preset name",
      confirmLabel: "Save",
      cancelLabel: "Cancel",
      required: true,
    });
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

  templateSave.addEventListener("click", async () => {
    const action = getActionSelection(service);
    const params = collectParams(service);
    if (!params) return;
    const defaultName = `${activityLabel(service, action)}`;
    const name = await promptModal({
      title: "Save template",
      label: "Template name",
      defaultValue: defaultName,
      confirmLabel: "Save",
      cancelLabel: "Cancel",
      required: true,
    });
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
  if (mode === "local") return "Local";
  return "Graph";
}

function formatRiskLabel(risk) {
  if (risk === "danger") return "Dangerous";
  if (risk === "caution") return "Caution";
  return "Safe";
}

function getActionAllowedTargets(service, action) {
  const meta = ACTIONS_UI?.[service]?.[action];
  if (!meta) return ["local"];
  if (Array.isArray(meta.allowed_targets)) return meta.allowed_targets;
  if (meta.mode === "graph") return ["local", "graph"];
  return ["local"];
}

function resolveTargetSelection(service, action) {
  const allowed = getActionAllowedTargets(service, action);
  const selection = runnerTargetSelections[service] || "local";
  if (selection.startsWith("ssh:") && allowed.includes("ssh")) {
    const id = selection.replace("ssh:", "");
    const target = sshTargets.find((item) => item.id === id);
    if (target) return { type: "ssh", ...target };
  }
  return { type: "local" };
}

function refreshRunnerTargets() {
  document.querySelectorAll(".runner-target-select").forEach((select) => {
    const service = select.dataset.service;
    const action = select.dataset.action;
    const allowed = getActionAllowedTargets(service, action);
    const current = runnerTargetSelections[service] || "local";
    select.innerHTML = "";
    const allowLocal = allowed.includes("local") || allowed.includes("graph");
    if (allowLocal) {
      const localOption = document.createElement("option");
      localOption.value = "local";
      localOption.textContent = "Local machine";
      select.appendChild(localOption);
    }
    if (allowed.includes("ssh")) {
      sshTargets.forEach((target) => {
        const option = document.createElement("option");
        option.value = `ssh:${target.id}`;
        option.textContent = target.name || formatSshTargetLabel({ type: "ssh", ...target });
        select.appendChild(option);
      });
    }
    select.disabled = !allowed.includes("ssh") && allowLocal && allowed.length === 1;
    if (allowed.includes("ssh") && current.startsWith("ssh:")) {
      select.value = current;
    } else if (allowLocal) {
      select.value = "local";
    } else if (allowed.includes("ssh") && sshTargets.length) {
      select.value = `ssh:${sshTargets[0].id}`;
      runnerTargetSelections[service] = select.value;
    }
  });
}

function getActionRisk(service, action) {
  const meta = ACTIONS_UI?.[service]?.[action] || {};
  if (meta.risk) return meta.risk;
  const name = String(action || "").toLowerCase();
  if (
    name.includes("delete") ||
    name.includes("remove") ||
    name.includes("disable") ||
    name.includes("unlink") ||
    name.includes("reset") ||
    name.includes("restore") ||
    name.includes("set_user_license") ||
    name.includes("set_static_ip") ||
    name.includes("set_dns_servers") ||
    name.includes("set_interface_metric") ||
    name.includes("set_mtu")
  ) {
    return "danger";
  }
  if (
    name.startsWith("set") ||
    name.includes("set_") ||
    name.includes("update") ||
    name.includes("assign") ||
    name.includes("grant") ||
    name.includes("create") ||
    name.includes("enable") ||
    name.includes("link") ||
    name.includes("move") ||
    name.includes("rename")
  ) {
    return "caution";
  }
  if (meta.confirm) return "caution";
  return "safe";
}

function addRiskBadge(container, risk) {
  const badge = document.createElement("span");
  badge.classList.add("badge", "risk", `risk-${risk}`);
  badge.textContent = formatRiskLabel(risk);
  container.appendChild(badge);
}

function addChipBadge(chip, mode) {
  const badge = document.createElement("span");
  badge.classList.add("badge");
  badge.classList.add(mode === "powershell" ? "ps" : "graph");
  badge.textContent = modeLabel(mode);
  chip.appendChild(badge);
}

const SNAPSHOT_TOGGLE_EXCLUDE = new Set(["dashboard", "health", "security", "ssh"]);

function ensureSnapshotToggle(actions, service) {
  return;
}

function decorateChips() {
  document.querySelectorAll(".chip[data-action]").forEach((chip) => {
    const { service, action } = chip.dataset;
    const meta = ACTIONS_UI?.[service]?.[action];
    if (!meta) return;
    const mode = meta.mode || "graph";
    chip.dataset.mode = mode;
    if (!chip.querySelector(".badge.ps, .badge.graph")) {
      addChipBadge(chip, mode);
    }
    if (!chip.querySelector(".badge.risk")) {
      const risk = getActionRisk(service, action);
      addRiskBadge(chip, risk);
    }
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

    const clearButton = card.querySelector(`.clear-output[data-output-target="${service}"]`);
    if (clearButton) {
      const terminalControls = clearButton.closest(".terminal-controls");
      if (terminalControls) {
        if (!terminalControls.querySelector(".incident-bundle")) {
          const bundleButton = document.createElement("button");
          bundleButton.type = "button";
          bundleButton.classList.add("ghost", "small", "incident-bundle");
          bundleButton.dataset.outputTarget = service;
          bundleButton.textContent = "Export incident bundle";
          bundleButton.addEventListener("click", () => exportIncidentBundle(service));
          terminalControls.appendChild(bundleButton);
        }
      } else {
        let actions = card.querySelector(".output-actions");
        if (!actions) {
          actions = document.createElement("div");
          actions.classList.add("output-actions");
          if (clearButton.parentElement === card) {
            card.insertBefore(actions, clearButton);
          } else {
            card.appendChild(actions);
          }
        }
        if (!actions.contains(clearButton)) {
          actions.appendChild(clearButton);
        }
        if (!actions.querySelector(".incident-bundle")) {
          const bundleButton = document.createElement("button");
          bundleButton.type = "button";
          bundleButton.classList.add("ghost", "small", "incident-bundle");
          bundleButton.dataset.outputTarget = service;
          bundleButton.textContent = "Export incident bundle";
          bundleButton.addEventListener("click", () => exportIncidentBundle(service));
          actions.appendChild(bundleButton);
        }
      }
    }

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
    const explainButton = document.createElement("button");
    explainButton.type = "button";
    explainButton.classList.add("tab");
    explainButton.dataset.view = "explain";
    explainButton.textContent = "Explain";
    const wantsGraph = service === "topology-report" || service === "incident";
    const includeTable = service !== "topology-report";
    let tableButton = null;
    if (includeTable) {
      tableButton = document.createElement("button");
      tableButton.type = "button";
      tableButton.classList.add("tab");
      tableButton.dataset.view = "table";
      tableButton.textContent = "Table";
    }
    let graphButton = null;
    if (wantsGraph) {
      graphButton = document.createElement("button");
      graphButton.type = "button";
      graphButton.classList.add("tab");
      graphButton.dataset.view = "graph";
      graphButton.textContent = "Graph";
    }
    tabs.appendChild(rawButton);
    tabs.appendChild(prettyButton);
    tabs.appendChild(explainButton);
    if (tableButton) tabs.appendChild(tableButton);
    if (graphButton) tabs.appendChild(graphButton);

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
    const explain = document.createElement("div");
    explain.classList.add("output-explain");
    explain.dataset.output = pre.dataset.output;
    const table = document.createElement("div");
    table.classList.add("output-table");
    table.dataset.output = pre.dataset.output;
    const graph = document.createElement("div");
    graph.classList.add("output-graph");
    graph.dataset.output = pre.dataset.output;

    pre.classList.add("output-raw");
    card.insertBefore(searchWrap, anchor);
    card.insertBefore(tabs, anchor);
    card.insertBefore(wrapper, anchor);
    wrapper.appendChild(pre);
    wrapper.appendChild(pretty);
    wrapper.appendChild(explain);
    if (includeTable) {
      wrapper.appendChild(table);
    }
    if (wantsGraph) {
      wrapper.appendChild(graph);
    }

    const switchView = (view) => {
      rawButton.classList.toggle("active", view === "raw");
      prettyButton.classList.toggle("active", view === "pretty");
      explainButton.classList.toggle("active", view === "explain");
      if (tableButton) tableButton.classList.toggle("active", view === "table");
      if (graphButton) graphButton.classList.toggle("active", view === "graph");
      pre.style.display = view === "raw" ? "block" : "none";
      pretty.style.display = view === "pretty" ? "block" : "none";
      explain.style.display = view === "explain" ? "block" : "none";
      if (includeTable) {
        table.style.display = view === "table" ? "block" : "none";
      }
      if (wantsGraph) {
        graph.style.display = view === "graph" ? "block" : "none";
        if (view === "graph") {
          renderGraph(service, lastOutputs[service]);
        }
      }
      if (view === "explain") {
        renderExplanation(service, lastOutputs[service]);
      }
    };

    rawButton.addEventListener("click", () => switchView("raw"));
    prettyButton.addEventListener("click", () => switchView("pretty"));
    explainButton.addEventListener("click", () => switchView("explain"));
    if (tableButton) {
      tableButton.addEventListener("click", () => switchView("table"));
    }
    if (graphButton) {
      graphButton.addEventListener("click", () => switchView("graph"));
    }
    switchView(wantsGraph ? "graph" : "raw");
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
  if (actionsRow) actionsRow.classList.add("execution-bar");
  let cancelButton = form.querySelector(".runner-cancel");
  let draftButton = form.querySelector(".runner-draft");
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
  if (!draftButton && actionsRow) {
    draftButton = document.createElement("button");
    draftButton.type = "button";
    draftButton.classList.add("ghost", "small", "runner-draft");
    draftButton.dataset.service = service;
    draftButton.textContent = "Add result to draft";
    actionsRow.appendChild(draftButton);
  }
  if (draftButton && !draftButton.dataset.bound) {
    draftButton.dataset.bound = "true";
    draftButton.addEventListener("click", () => addLatestResultToDraft(service));
  }
  if (draftButton) updateRunnerDraftButton(service);

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
    const risk = formatRiskLabel(getActionRisk(service, action));
    option.textContent = `${meta.label} · ${modeLabel(meta.mode)} · ${risk}`;
    select.appendChild(option);
  });

  function renderFields(action) {
    container.innerHTML = "";
    const meta = actions[action];
    const fields = meta?.fields || [];
    const risk = getActionRisk(service, action);

    const riskLine = document.createElement("div");
    riskLine.classList.add("runner-risk", `risk-${risk}`);
    const riskLabel = document.createElement("span");
    riskLabel.classList.add("risk-label");
    riskLabel.textContent = "Risk";
    const riskValue = document.createElement("span");
    riskValue.classList.add("risk-value", `risk-${risk}`);
    riskValue.textContent = formatRiskLabel(risk);
    riskLine.appendChild(riskLabel);
    riskLine.appendChild(riskValue);
    container.appendChild(riskLine);

    const modeLine = document.createElement("div");
    modeLine.classList.add("runner-mode");
    modeLine.textContent = `Mode: ${modeLabel(meta?.mode)}`;
    container.appendChild(modeLine);

    const allowedTargets = getActionAllowedTargets(service, action);
    const targetRow = document.createElement("div");
    targetRow.classList.add("runner-target-row");
    const targetLabel = document.createElement("span");
    targetLabel.classList.add("runner-target-label");
    targetLabel.textContent = "Execution target";
    const targetSelect = document.createElement("select");
    targetSelect.classList.add("runner-target-select");
    targetSelect.dataset.service = service;
    targetSelect.dataset.action = action;
    const allowLocal = allowedTargets.includes("local") || allowedTargets.includes("graph");
    if (allowLocal) {
      const localOption = document.createElement("option");
      localOption.value = "local";
      localOption.textContent = "Local machine";
      targetSelect.appendChild(localOption);
    }
    if (allowedTargets.includes("ssh")) {
      sshTargets.forEach((target) => {
        const option = document.createElement("option");
        option.value = `ssh:${target.id}`;
        option.textContent = target.name || formatSshTargetLabel({ type: "ssh", ...target });
        targetSelect.appendChild(option);
      });
    }
    const currentTarget = runnerTargetSelections[service] || "local";
    if (allowedTargets.includes("ssh") && currentTarget.startsWith("ssh:")) {
      targetSelect.value = currentTarget;
    } else if (allowLocal) {
      targetSelect.value = "local";
      runnerTargetSelections[service] = "local";
    } else if (allowedTargets.includes("ssh") && sshTargets.length) {
      targetSelect.value = `ssh:${sshTargets[0].id}`;
      runnerTargetSelections[service] = targetSelect.value;
    }
    targetSelect.disabled = !allowedTargets.includes("ssh") && allowLocal && allowedTargets.length === 1;
    const targetActions = document.createElement("div");
    targetActions.classList.add("runner-target-actions");
    const manageButton = document.createElement("button");
    manageButton.type = "button";
    manageButton.classList.add("ghost", "small");
    manageButton.textContent = "Manage targets";
    manageButton.addEventListener("click", () => {
      setSection("settings", { scrollTarget: "ssh-targets-panel" });
    });
    const testButton = document.createElement("button");
    testButton.type = "button";
    testButton.classList.add("ghost", "small");
    testButton.textContent = "Test connection";
    testButton.disabled = !targetSelect.value.startsWith("ssh:");
    testButton.addEventListener("click", () => {
      const target = resolveTargetSelection(service, action);
      if (target.type !== "ssh") {
        showToast("Select an SSH target first");
        return;
      }
      testSshTarget(target);
    });
    targetSelect.addEventListener("change", () => {
      runnerTargetSelections[service] = targetSelect.value;
      testButton.disabled = !targetSelect.value.startsWith("ssh:");
    });
    if (allowedTargets.includes("ssh")) {
      targetActions.appendChild(manageButton);
      targetActions.appendChild(testButton);
    }
    targetRow.appendChild(targetLabel);
    targetRow.appendChild(targetSelect);
    if (allowedTargets.includes("ssh")) {
      targetRow.appendChild(targetActions);
    }
    container.appendChild(targetRow);

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

const SNAPSHOT_KIND_BY_SERVICE = {
  exchange: "user",
  onedrive: "user",
  sharepoint: "user",
  teams: "user",
  entra: "user",
  azure: "user",
  defender: "user",
  powerplatform: "user",
  purview: "user",
  localad: "user",
  endpoint: "device",
  domaincontroller: "dc",
  printers: "print_server",
  network: "device",
  ssh: "device",
  remote_workflows: "device",
  fileserver: "file_server",
  topology: "admin_host",
  time: "admin_host",
  certificates: "admin_host",
  processes: "admin_host",
  baselines: "admin_host",
  eventlogs: "admin_host",
  registry: "admin_host",
};

const SNAPSHOT_USER_KEYS = [
  "user_id",
  "user_principal_name",
  "userprincipalname",
  "shared_mailbox",
  "mailbox",
  "user",
  "upn",
  "user_dn",
  "userdn",
];

const SNAPSHOT_HOST_KEYS = [
  "host",
  "hostname",
  "host_name",
  "computer",
  "computer_name",
  "device",
  "device_id",
  "deviceid",
  "server",
  "server_name",
  "fqdn",
  "ip",
  "ip_address",
  "address",
  "dc",
  "domain",
];

function isGuidValue(value) {
  if (!value) return false;
  return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(
    String(value)
  );
}

function normalizeIdentifierValue(value) {
  if (!value) return null;
  if (Array.isArray(value)) return value[0];
  const raw = String(value).trim();
  if (!raw) return null;
  if (raw.includes(",")) {
    return raw.split(",")[0].trim();
  }
  return raw;
}

function pickParamValue(params, keys) {
  for (const key of keys) {
    if (params[key]) return { key, value: normalizeIdentifierValue(params[key]) };
  }
  return null;
}

function aliasTypeFor(kind, key, value) {
  const lowerKey = String(key || "").toLowerCase();
  if (kind === "user") {
    if (lowerKey.includes("dn")) return "user_dn";
    if (value && value.includes("@")) return "upn";
    if (isGuidValue(value)) return "objectId";
    return "user_id";
  }
  if (lowerKey.includes("domain")) return "domain";
  return isIpAddress(value) ? "ip" : "hostname";
}

function inferSnapshotSubjectFromPanel(service) {
  const params = readRunnerParams(service);
  const defaultKind = SNAPSHOT_KIND_BY_SERVICE[service] || "admin_host";
  let kind = defaultKind;
  let identifier = null;
  let key = null;

  if (kind === "user") {
    const picked = pickParamValue(params, SNAPSHOT_USER_KEYS);
    if (picked) {
      identifier = picked.value;
      key = picked.key;
    }
  } else if (kind === "dc") {
    const picked = pickParamValue(params, ["dc", "domain", ...SNAPSHOT_HOST_KEYS]);
    if (picked) {
      identifier = picked.value;
      key = picked.key;
    }
  } else if (kind === "file_server" || kind === "print_server") {
    const picked = pickParamValue(params, ["server", "host", ...SNAPSHOT_HOST_KEYS]);
    if (picked) {
      identifier = picked.value;
      key = picked.key;
    }
  } else if (kind === "device") {
    const picked = pickParamValue(params, SNAPSHOT_HOST_KEYS);
    if (picked) {
      identifier = picked.value;
      key = picked.key;
    }
  }

  if (!identifier && defaultKind !== "admin_host") {
    const fallback = pickParamValue(params, SNAPSHOT_HOST_KEYS);
    if (fallback) {
      identifier = fallback.value;
      key = fallback.key;
      kind = "device";
    }
  }

  if (!identifier && kind !== "admin_host") {
    return null;
  }

  const identifiers = {};
  if (identifier) {
    identifiers[aliasTypeFor(kind, key, identifier)] = identifier;
  }
  return { kind, identifiers };
}

navLinks.forEach((link) => {
  link.addEventListener("click", () =>
    setSection(link.dataset.section, { scrollTarget: link.dataset.scroll })
  );
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

if (navList) {
  navList.addEventListener("scroll", () => {
    updateNavShadows();
  });
  window.addEventListener("resize", () => {
    updateNavShadows();
  });
  updateNavShadows();
}

initDiffTabs("snapshot");
initDiffTabs("report");
bindDiffCopy(snapshotDiffCopy, snapshotDiffTriage);
bindDiffCopy(reportDiffCopy, reportDiffTriage);

const connectPsButton = document.getElementById("connect-ps");
if (connectPsButton) {
  connectPsButton.addEventListener("click", () => {
    showToast("PowerShell connection queued");
  });
}

const openTaskRunnerButton = document.getElementById("open-task-runner");
if (openTaskRunnerButton) {
  openTaskRunnerButton.addEventListener("click", () => {
    setSection("exchange");
    showToast("Opened Task Runner");
  });
}

const viewActivityButton = document.getElementById("view-activity");
if (viewActivityButton) {
  viewActivityButton.addEventListener("click", () => {
    const list = document.getElementById("activity-list");
    if (list) {
      list.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

if (statusViewDetails) {
  statusViewDetails.addEventListener("click", () => {
    setSection("healthcheck", { scrollTarget: "health-card" });
  });
}

if (snapshotsViewHistory) {
  snapshotsViewHistory.addEventListener("click", () => {
    setSection("reports", { scrollTarget: "snapshot-history" });
  });
}

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
  profileDeleteButton.addEventListener("click", async () => {
    const name = profileSelect?.value || profileNameInput?.value.trim();
    if (!name) {
      showToast("Select a profile");
      return;
    }
    const confirmDelete = await confirmModal({
      title: "Delete profile",
      message: `Delete profile "${name}"?`,
      confirmLabel: "Delete",
      cancelLabel: "Cancel",
      danger: true,
    });
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

  profileImportFile.addEventListener("change", async () => {
    const file = profileImportFile.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async () => {
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
      for (const profile of imported) {
        const name = profile?.name?.trim();
        if (!name || !profile?.config) continue;
        const exists = existing.find((item) => item.name === name);
        if (exists) {
          const overwrite = await confirmModal({
            title: "Overwrite profile",
            message: `Profile "${name}" exists. Overwrite?`,
            confirmLabel: "Overwrite",
            cancelLabel: "Cancel",
          });
          if (!overwrite) continue;
          existing.splice(existing.indexOf(exists), 1);
        }
        existing.push({ name, config: normalizeProfileConfig(profile.config) });
      }
      saveProfiles(existing);
      renderProfileSelect();
      showToast("Profiles imported");
    };
    reader.readAsText(file);
  });
}

if (auditRefreshButton) {
  auditRefreshButton.addEventListener("click", () => {
    fetchAuditLogs();
  });
}

if (auditServiceSelect) {
  auditServiceSelect.addEventListener("change", () => fetchAuditLogs());
}
if (auditStatusSelect) {
  auditStatusSelect.addEventListener("change", () => fetchAuditLogs());
}
if (auditLimitSelect) {
  auditLimitSelect.addEventListener("change", () => fetchAuditLogs());
}
const auditInputHandlers = [auditActionInput, auditUserInput, auditQueryInput, auditSinceInput, auditUntilInput];
auditInputHandlers.forEach((input) => {
  if (!input) return;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      fetchAuditLogs();
    }
  });
});

if (auditExportJsonButton) {
  auditExportJsonButton.addEventListener("click", () => {
    exportAuditJson();
  });
}

if (auditExportCsvButton) {
  auditExportCsvButton.addEventListener("click", () => {
    exportAuditCsv();
  });
}

if (configExportButton) {
  configExportButton.addEventListener("click", () => {
    exportEncryptedConfig();
  });
}

if (configImportButton && configImportFile) {
  configImportButton.addEventListener("click", () => {
    configImportFile.value = "";
    configImportFile.click();
  });

  configImportFile.addEventListener("change", () => {
    const file = configImportFile.files?.[0];
    if (!file) return;
    importEncryptedConfigFile(file);
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

if (cfgAllowRemoteDangerous) {
  cfgAllowRemoteDangerous.addEventListener("change", async () => {
    if (configLocked) {
      cfgAllowRemoteDangerous.checked = !cfgAllowRemoteDangerous.checked;
      showToast("Config is locked");
      return;
    }
    const desired = cfgAllowRemoteDangerous.checked;
    const ok = await updateConfigPartial(
      { allow_remote_dangerous: desired },
      desired ? "Remote dangerous actions enabled" : "Remote dangerous actions blocked"
    );
    if (!ok) {
      cfgAllowRemoteDangerous.checked = !desired;
    }
  });
}

if (sshTargetSaveButton) {
  sshTargetSaveButton.addEventListener("click", async () => {
    const target = readSshTargetForm();
    if (!target.host) {
      showToast("Host is required");
      return;
    }
    if (!target.id) {
      target.id = generateTargetId();
    }
    const idx = sshTargets.findIndex((item) => item.id === target.id);
    if (idx >= 0) {
      sshTargets[idx] = target;
    } else {
      sshTargets.push(target);
    }
    renderSshTargets();
    refreshRunnerTargets();
    clearSshTargetForm();
    await persistSshTargets();
  });
}

if (sshTargetClearButton) {
  sshTargetClearButton.addEventListener("click", () => {
    clearSshTargetForm();
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

if (smokeTestButton) {
  smokeTestButton.addEventListener("click", (event) => {
    event.preventDefault();
    runSmokeTest();
  });
}

if (securityRefreshButton) {
  securityRefreshButton.addEventListener("click", (event) => {
    event.preventDefault();
    runSecurityPosture();
  });
}

if (warningDismiss) {
  warningDismiss.addEventListener("click", () => {
    hideWarningBanner();
  });
}

if (helpLinkButton) {
  helpLinkButton.addEventListener("click", () => {
    setSection("help");
  });
}

window.addEventListener("popstate", () => {
  const section = resolveSectionFromPath();
  if (section) {
    setSection(section);
  }
});

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

if (issueAddButton) {
  issueAddButton.addEventListener("click", () => {
    addIssue();
  });
}

if (issueClearButton) {
  issueClearButton.addEventListener("click", async () => {
    const confirmClear = await confirmModal({
      title: "Clear issues",
      message: "Clear all issues?",
      confirmLabel: "Clear",
      cancelLabel: "Cancel",
      danger: true,
    });
    if (!confirmClear) return;
    saveIssues([]);
    renderIssues();
  });
}

if (topologyCollectButton) {
  topologyCollectButton.addEventListener("click", async () => {
    const params = collectParams("topology");
    const result = await runAction("topology", "collect_topology", params || {});
    if (result?.ok) {
      topologyData = result.data;
      topologyPing = null;
    }
  });
}

if (topologyPingButton) {
  topologyPingButton.addEventListener("click", async () => {
    if (!topologyData) {
      showToast("Collect topology first");
      return;
    }
    const targets = extractTopologyTargets(topologyData);
    if (!targets.length) {
      showToast("No targets found");
      return;
    }
    const result = await runAction("topology", "ping_targets", { targets, count: 1, timeout_seconds: 2 });
    if (result?.ok) {
      topologyPing = result.data;
    }
  });
}

if (topologyReportButton) {
  topologyReportButton.addEventListener("click", () => {
    generateIssueReport();
  });
}

function runTopologyDiffBySelection() {
  const history = loadTopologyHistory();
  if (history.length < 2) {
    showToast("Need at least two snapshots");
    return;
  }
  const snapA = findSnapshotById(history, topologyDiffSelectA?.value);
  const snapB = findSnapshotById(history, topologyDiffSelectB?.value);
  if (!snapA || !snapB) {
    showToast("Select two snapshots to compare");
    return;
  }
  const report = buildTopologyDiffReport(snapA, snapB);
  setOutput("topology-changes", report);
  setOutputStatus("topology-changes", { state: "ok", text: "Diff ready", meta: "" });
  setOutputView("topology-changes", "pretty");
  showToast("Topology diff generated");
}

function runTopologyDiff24h() {
  const history = loadTopologyHistory();
  if (history.length < 2) {
    showToast("Need at least two snapshots");
    return;
  }
  const latest = history[0];
  const older = findSnapshotBefore(history, 24);
  if (!older || older === latest) {
    showToast("No snapshot older than 24h found");
    return;
  }
  const report = buildTopologyDiffReport(older, latest, 24);
  setOutput("topology-changes", report);
  setOutputStatus("topology-changes", { state: "ok", text: "Last 24h changes", meta: "" });
  setOutputView("topology-changes", "pretty");
  showToast("24h change report generated");
}

if (topologyHistoryDepthSelect) {
  topologyHistoryDepthSelect.value = String(getTopologyHistoryLimit());
  topologyHistoryDepthSelect.addEventListener("change", async () => {
    const next = Number.parseInt(topologyHistoryDepthSelect.value, 10);
    if (!Number.isFinite(next)) return;
    setTopologyHistoryLimit(next);
    const current = trimHistoryToLimit(loadTopologyHistory(), next);
    saveTopologyHistory(current);
    await fetchTopologyHistory();
    showToast(`History depth set to ${next}`);
  });
}

if (topologyDiffRunButton) {
  topologyDiffRunButton.addEventListener("click", () => {
    runTopologyDiffBySelection();
  });
}

if (topologyDiff24hButton) {
  topologyDiff24hButton.addEventListener("click", () => {
    runTopologyDiff24h();
  });
}

if (topologyExportJsonButton) {
  topologyExportJsonButton.addEventListener("click", () => {
    exportTopologyReportJson();
  });
}

if (topologyExportCsvButton) {
  topologyExportCsvButton.addEventListener("click", () => {
    exportTopologyReportCsv();
  });
}

if (actionPackPrevButton) {
  actionPackPrevButton.addEventListener("click", () => {
    const packs = getAllActionPacks({ includeDeleted: getActionPackFilter() === "deleted" });
    const { pageIndex } = getActionPackPaging(packs);
    if (pageIndex > 0) {
      setActionPackPageIndex(pageIndex - 1);
      renderActionPacks();
    }
  });
}

if (actionPackNextButton) {
  actionPackNextButton.addEventListener("click", () => {
    const packs = getAllActionPacks({ includeDeleted: getActionPackFilter() === "deleted" });
    const { pageIndex, totalPages } = getActionPackPaging(packs);
    if (pageIndex < totalPages - 1) {
      setActionPackPageIndex(pageIndex + 1);
      renderActionPacks();
    }
  });
}

if (actionPackFilterSelect) {
  const currentFilter = getActionPackFilter();
  if (!actionPackFilterSelect.querySelector(`option[value="${currentFilter}"]`)) {
    setActionPackFilter("current");
    actionPackFilterSelect.value = "current";
  } else {
    actionPackFilterSelect.value = currentFilter;
  }
  actionPackFilterSelect.addEventListener("change", () => {
    setActionPackFilter(actionPackFilterSelect.value);
    setActionPackPageIndex(0);
    renderActionPacks();
    renderDeletedActionPacks();
  });
}

if (actionPackRunButton) {
  actionPackRunButton.addEventListener("click", () => {
    runSelectedActionPack();
  });
}

if (actionPackRunnerSteps) {
  const updatePackPreview = () => {
    if (!selectedPackId) return;
    const pack = getActionPackById(selectedPackId);
    if (!pack) return;
    const params = collectActionPackRunnerParams(pack);
    renderActionPackHowItRuns(pack, actionPackHowPanel, params);
  };
  actionPackRunnerSteps.addEventListener("input", updatePackPreview);
  actionPackRunnerSteps.addEventListener("change", updatePackPreview);
}

if (actionPackPreviewButton) {
  actionPackPreviewButton.addEventListener("click", () => {
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
    renderActionPackPlan(pack, params, actionPackPlanPanel, { mode: "preview" });
  });
}

if (actionPackValidateButton) {
  actionPackValidateButton.addEventListener("click", () => {
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
    renderActionPackPlan(pack, params, actionPackPlanPanel, { mode: "validate" });
  });
}

if (actionPackDryRunToggle) {
  actionPackDryRunToggle.addEventListener("change", () => {
    if (!selectedPackId) return;
    const params = getPackParams(selectedPackId);
    params.dryRun = actionPackDryRunToggle.checked;
    setPackParams(selectedPackId, params);
    const pack = getActionPackById(selectedPackId);
    if (pack) {
      renderActionPackHowItRuns(pack, actionPackHowPanel, params);
    }
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
  actionPackHistoryClear.addEventListener("click", async () => {
    const confirmDelete = await confirmModal({
      title: "Clear action pack history",
      message: "Clear action pack history?",
      confirmLabel: "Clear",
      cancelLabel: "Cancel",
      danger: true,
    });
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
  reportHistoryClear.addEventListener("click", async () => {
    const confirmDelete = await confirmModal({
      title: "Clear report history",
      message: "Clear report history?",
      confirmLabel: "Clear",
      cancelLabel: "Cancel",
      danger: true,
    });
    if (!confirmDelete) return;
    saveReportHistory([]);
    renderReportHistory();
    showToast("Local report history cleared");
    refreshReportHistory();
  });
}

if (incidentRunButton) {
  incidentRunButton.addEventListener("click", () => {
    runIncidentWorkspace();
  });
}

if (incidentRunFixButton) {
  incidentRunFixButton.addEventListener("click", () => {
    if (!incidentFixPackId) {
      showToast("No fix pack available");
      return;
    }
    const pack = getActionPackById(incidentFixPackId);
    if (!pack) {
      showToast("Fix pack not found");
      return;
    }
    const params = buildIncidentPackParams(pack, lastIncidentContext || {});
    if (params) {
      setPackParams(pack.id, params);
    }
    selectActionPack(pack, { scroll: true });
    runActionPack(pack, params || getPackParams(pack.id));
  });
}

if (incidentReportLoadButton) {
  incidentReportLoadButton.addEventListener("click", () => {
    const id = incidentReportSelect?.value || activeIncidentId;
    if (!id) {
      showToast("Select an incident first");
      return;
    }
    activeIncidentId = id;
    loadIncidentReportFor(id);
  });
}

if (incidentReportSelect) {
  incidentReportSelect.addEventListener("change", () => {
    const id = incidentReportSelect.value;
    if (id) {
      activeIncidentId = id;
    }
  });
}

if (incidentReportTimelineAdd) {
  incidentReportTimelineAdd.addEventListener("click", async () => {
    if (!incidentReport) {
      showToast("Load an incident report first");
      return;
    }
    const skipPrompt = localStorage.getItem("gas.timeline_prompt_skip") === "1";
    let label = "";
    if (skipPrompt) {
      label = "Manual timeline entry";
    } else {
      const values = await openFormModal({
        title: "Add timeline entry",
        fields: [
          {
            key: "label",
            label: "Timeline entry label",
            required: true,
            placeholder: "Describe the step",
          },
          {
            key: "skip",
            label: "Don't ask again",
            type: "checkbox",
            value: false,
          },
        ],
        confirmLabel: "Add entry",
        cancelLabel: "Cancel",
      });
      if (!values) return;
      label = values.label;
      if (values.skip) {
        localStorage.setItem("gas.timeline_prompt_skip", "1");
      }
    }
    const entry = {
      timestamp: new Date().toISOString(),
      label,
      type: "manual",
    };
    incidentReport.timeline = [...(incidentReport.timeline || []), entry];
    renderIncidentReportTimeline(incidentReport);
  });
}

if (incidentReportTimelineAuto) {
  incidentReportTimelineAuto.addEventListener("click", async () => {
    if (!incidentReport?.incident_id) {
      showToast("Load an incident first");
      return;
    }
    const timelineData = await fetchIncidentTimeline(incidentReport.incident_id);
    const entries = [];
    (timelineData?.timeline || []).forEach((entry) => {
      entries.push({
        timestamp: entry.time || entry.timestamp,
        label: entry.kind || "Event",
        summary: entry.kind || "",
        type: entry.kind || "event",
      });
    });
    draftSnapshots.forEach((draft) => {
      (draft.entries || []).forEach((item) => {
        entries.push({
          timestamp: item.timestamp,
          label: item.action_label || item.service,
          summary: item.result_status,
          type: "draft_entry",
        });
      });
    });
    incidentReport.timeline = entries.sort((a, b) => {
      return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
    });
    renderIncidentReportTimeline(incidentReport);
  });
}

if (incidentReportEvidenceRefresh) {
  incidentReportEvidenceRefresh.addEventListener("click", () => {
    if (!incidentReport) {
      showToast("Load an incident report first");
      return;
    }
    refreshIncidentReportEvidence(incidentReport);
  });
}

if (incidentReportPreview) {
  incidentReportPreview.addEventListener("click", () => {
    previewIncidentReport("markdown");
  });
}

if (incidentReportExportMd) {
  incidentReportExportMd.addEventListener("click", () => {
    previewIncidentReport("markdown");
  });
}

if (incidentReportExportText) {
  incidentReportExportText.addEventListener("click", () => {
    previewIncidentReport("text");
  });
}

if (incidentReportExportPdf) {
  incidentReportExportPdf.addEventListener("click", () => {
    previewIncidentReport("pdf");
  });
}

if (incidentReportSave) {
  incidentReportSave.addEventListener("click", async () => {
    if (!incidentReport?.incident_id) {
      showToast("Select an incident first");
      return;
    }
    const payload = collectIncidentReportForm();
    payload.timeline = incidentReport.timeline || [];
    payload.evidence_refs = incidentReport.evidence_refs || [];
    const saved = await saveIncidentReport(incidentReport.incident_id, payload);
    if (saved) {
      incidentReport = saved;
      showToast("Incident report saved");
    }
  });
}

if (incidentReportReset) {
  incidentReportReset.addEventListener("click", () => {
    if (!incidentReport) return;
    applyIncidentReportToForm(incidentReport);
    renderIncidentReportTimeline(incidentReport);
    refreshIncidentReportEvidence(incidentReport);
  });
}

if (reportCollapsibleButtons.length) {
  reportCollapsibleButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
    });
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
if (draftNewButton) {
  draftNewButton.addEventListener("click", () => {
    createDraftSnapshot({ title: "New draft" });
    renderDraftSnapshots();
    showToast("Draft created");
  });
}

if (draftArchiveButton) {
  draftArchiveButton.addEventListener("click", () => {
    const draft = getActiveDraft();
    if (!draft) {
      showToast("No draft selected");
      return;
    }
    archiveDraftSnapshot(draft.id);
    renderDraftSnapshots();
    showToast("Draft archived");
  });
}

if (draftSelect) {
  draftSelect.addEventListener("change", () => {
    const id = draftSelect.value;
    if (!id) return;
    setActiveDraftId(id);
    renderDraftSnapshots();
  });
}

if (draftTitleInput) {
  draftTitleInput.addEventListener("input", () => updateDraftFromInputs());
}
if (draftNotesInput) {
  draftNotesInput.addEventListener("input", () => updateDraftFromInputs());
}
if (draftSubjectKind) {
  draftSubjectKind.addEventListener("change", () => updateDraftFromInputs());
}
if (draftSubjectValue) {
  draftSubjectValue.addEventListener("input", () => updateDraftFromInputs());
}
if (draftSubjectName) {
  draftSubjectName.addEventListener("input", () => updateDraftFromInputs());
}
if (draftProfileSelect) {
  draftProfileSelect.addEventListener("change", () => updateDraftFromInputs());
}
if (draftFinalizeButton) {
  draftFinalizeButton.addEventListener("click", () => {
    finalizeDraftSnapshot();
  });
}
if (draftClearButton) {
  draftClearButton.addEventListener("click", async () => {
    const draft = getActiveDraft();
    if (!draft) return;
    const confirmClear = await confirmModal({
      title: "Clear draft entries",
      message: "Clear all entries from this draft?",
      confirmLabel: "Clear entries",
      cancelLabel: "Cancel",
      danger: true,
    });
    if (!confirmClear) return;
    clearDraftEntries(draft.id);
    renderDraftSnapshots();
    showToast("Draft entries cleared");
  });
}
if (snapshotHistoryRefresh) {
  snapshotHistoryRefresh.addEventListener("click", () => {
    refreshSnapshotEntities();
    refreshSnapshotHistory();
  });
}
if (snapshotSubjectSelect) {
  snapshotSubjectSelect.addEventListener("change", () => {
    refreshSnapshotHistory();
  });
}
if (snapshotDiffRunButton) {
  snapshotDiffRunButton.addEventListener("click", () => {
    runSnapshotDiff();
  });
}
if (snapshotDiffSelectA) {
  snapshotDiffSelectA.addEventListener("change", () => {
    runSnapshotDiff();
  });
}
if (snapshotDiffSelectB) {
  snapshotDiffSelectB.addEventListener("change", () => {
    runSnapshotDiff();
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

if (packSaveCopyButton) {
  packSaveCopyButton.addEventListener("click", () => {
    savePackFromBuilder({ asCopy: true });
  });
}

if (packNewButton) {
  packNewButton.addEventListener("click", () => {
    resetPackBuilder();
  });
}

if (packDeleteButton) {
  packDeleteButton.addEventListener("click", async () => {
    await deletePackFromBuilder();
  });
}

const packBuilderInputs = [packNameInput, packDescriptionInput, packDefaultsInput, packScopeSelect];
packBuilderInputs.forEach((input) => {
  if (!input) return;
  input.addEventListener("input", () => renderPackBuilderHowItRuns());
  input.addEventListener("change", () => renderPackBuilderHowItRuns());
});

if (packVersionRestoreButton) {
  packVersionRestoreButton.addEventListener("click", () => {
    if (!packVersionSelect) return;
    const selected = packVersionSelect.value;
    if (!selected) {
      showToast("Select a version first");
      return;
    }
    const version = currentPackVersions.find((entry) => entry.version_id === selected);
    if (!version) {
      showToast("Version not found");
      return;
    }
    currentPackSteps = version.steps.map((step) => ({ ...step }));
    if (packNameInput) packNameInput.value = version.name;
    if (packDescriptionInput) packDescriptionInput.value = version.description || "";
    if (packDefaultsInput) {
      packDefaultsInput.value = version.defaults ? JSON.stringify(version.defaults, null, 2) : "";
    }
    renderPackSteps();
    showToast("Version restored. Save to apply.");
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
  presetDeleteButton.addEventListener("click", async () => {
    await deletePresetFromBuilder();
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
      showToast("Exit edit mode to open actions");
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
      openRunnerForAction(template.service, template.action, template.params || {});
      return;
    }
    const { service, action } = chip.dataset;
    openRunnerForAction(service, action);
  });
}

if (quickLinks) {
  quickLinks.addEventListener("click", (event) => {
    const button = event.target.closest("[data-quick-link]");
    if (!button) return;
    const link = button.dataset.quickLink;
    if (link === "health") {
      setSection("healthcheck", { scrollTarget: "health-card" });
      return;
    }
    if (link === "task-runner") {
      setSection("exchange");
      return;
    }
    if (link === "action-packs") {
      setSection("actionpacks", { scrollTarget: "action-pack-panel" });
      return;
    }
    if (link === "help") {
      setSection("help");
    }
  });
}

if (workspaceSelect) {
  workspaceSelect.addEventListener("change", () => {
    setActiveWorkspaceId(workspaceSelect.value);
    renderWorkspaces();
  });
}

if (workspaceNewButton) {
  workspaceNewButton.addEventListener("click", async () => {
    const name = await promptModal({
      title: "New workspace",
      label: "Workspace name",
      defaultValue: "New workspace",
      confirmLabel: "Create",
      cancelLabel: "Cancel",
      required: true,
    });
    if (!name) return;
    const workspace = createWorkspace(name);
    upsertWorkspace(workspace);
    setActiveWorkspaceId(workspace.id);
    renderWorkspaces();
    showToast("Workspace created");
  });
}

if (workspaceRenameButton) {
  workspaceRenameButton.addEventListener("click", async () => {
    const activeId = getActiveWorkspaceId();
    if (!activeId) return;
    const workspace = getWorkspaceById(activeId);
    if (!workspace) return;
    const name = await promptModal({
      title: "Rename workspace",
      label: "Workspace name",
      defaultValue: workspace.name || "Workspace",
      confirmLabel: "Rename",
      cancelLabel: "Cancel",
      required: true,
    });
    if (!name) return;
    workspace.name = name;
    upsertWorkspace(workspace);
    renderWorkspaces();
    showToast("Workspace renamed");
  });
}

if (workspaceDuplicateButton) {
  workspaceDuplicateButton.addEventListener("click", () => {
    const activeId = getActiveWorkspaceId();
    if (!activeId) return;
    const workspace = getWorkspaceById(activeId);
    if (!workspace) return;
    const copy = {
      ...workspace,
      id: generateWorkspaceId(),
      name: `${workspace.name || "Workspace"} (copy)`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    upsertWorkspace(copy);
    setActiveWorkspaceId(copy.id);
    renderWorkspaces();
    showToast("Workspace duplicated");
  });
}

if (workspaceDeleteButton) {
  workspaceDeleteButton.addEventListener("click", async () => {
    const activeId = getActiveWorkspaceId();
    if (!activeId) return;
    const workspace = getWorkspaceById(activeId);
    if (!workspace) return;
    const confirmDelete = await confirmModal({
      title: "Delete workspace",
      message: `Delete workspace "${workspace.name || "Workspace"}"?`,
      confirmLabel: "Delete",
      cancelLabel: "Cancel",
      danger: true,
    });
    if (!confirmDelete) return;
    deleteWorkspace(activeId);
    setActiveWorkspaceId("");
    renderWorkspaces();
    showToast("Workspace deleted");
  });
}

if (workspaceAddTileButton) {
  workspaceAddTileButton.addEventListener("click", () => {
    openWorkspacePalette();
  });
}

if (workspaceSaveButton) {
  workspaceSaveButton.addEventListener("click", () => {
    persistWorkspaceLayout();
    showToast("Workspace layout saved");
  });
}

if (workspaceExportButton) {
  workspaceExportButton.addEventListener("click", () => {
    const activeId = getActiveWorkspaceId();
    if (!activeId) return;
    const workspace = getWorkspaceById(activeId);
    if (!workspace) return;
    downloadJson(workspace, `workspace-${sanitizeFilename(workspace.name || "workspace")}.json`);
  });
}

if (workspaceImportButton && workspaceImportFile) {
  workspaceImportButton.addEventListener("click", () => workspaceImportFile.click());
  workspaceImportFile.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      if (!data || typeof data !== "object") throw new Error("Invalid file");
      const workspace = {
        ...data,
        id: data.id || generateWorkspaceId(),
        name: data.name || "Imported workspace",
        created_at: data.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
        layout: data.layout || { order: [], spans: {} },
        tiles: Array.isArray(data.tiles) ? data.tiles : [],
      };
      upsertWorkspace(workspace);
      setActiveWorkspaceId(workspace.id);
      renderWorkspaces();
      showToast("Workspace imported");
    } catch (err) {
      showToast("Workspace import failed");
    } finally {
      workspaceImportFile.value = "";
    }
  });
}

// Service toolkit chips (outside Quick Actions) should be clickable.
// Default behavior: open the matching runner with the action selected.
// Some chips opt into immediate execution via data-run-now="true" (safe read-only utilities).
document.querySelectorAll('.chip[data-service][data-action]').forEach((chip) => {
  if (chip.dataset.bound === "true") return;
  if (chip.closest("#quick-actions")) return; // handled by Quick Actions grid delegation
  chip.dataset.bound = "true";
  chip.addEventListener("click", () => {
    const { service, action } = chip.dataset;
    if (!service || !action) return;
    if (chip.dataset.runNow === "true") {
      runAction(service, action, {});
      return;
    }
    openRunnerForAction(service, action);
  });
});

document.querySelectorAll(".runner-run").forEach((button) => {
  button.addEventListener("click", async () => {
    const service = button.dataset.service;
    const form = document.querySelector(`.runner[data-service="${service}"]`);
    if (!form) return;
    const action = form.querySelector(".action-select").value;
    const params = collectParams(service);
    if (!params) return;
    if (service === "topology") {
      const result = await runAction(service, action, params);
      if (result?.ok) {
        if (action === "collect_topology") {
          topologyData = result.data;
          topologyPing = null;
        } else if (action === "ping_targets") {
          topologyPing = result.data;
        }
      }
      return;
    }
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
    updateArtifactButton(target, null);
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
  button.addEventListener("click", async () => {
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
      rows = await selectExportArrayWithModal(payload);
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

window.addEventListener("resize", () => {
  if (lastOutputs["topology-report"]) {
    renderGraph("topology-report", lastOutputs["topology-report"]);
  }
});

const initialSection = resolveSectionFromPath();
if (initialSection && initialSection !== "dashboard") {
  setSection(initialSection);
} else {
  setSection("dashboard");
}
fetchStatus();
fetchSystemStatusSummary();
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
draftSnapshots = loadDraftSnapshots();
activeDraftId = getActiveDraftId();
renderDraftSnapshots();
initTileLayout();
renderWorkspaces();
setupWorkspacePinButtons();
renderActionPacks();
renderDeletedActionPacks();
renderReportPresets();
updateReportExportOptions(getExportPayload("reports"));
renderActionPackHistory();
renderReportHistory();
refreshReportHistory();
renderReportQueue();
renderActivity(loadActivity());
updateMetrics();
renderAuditServiceOptions();
fetchAuditLogs();
refreshSymptomTemplates();
refreshSnapshotEntities().then(() => refreshSnapshotHistory());
initHelpCenter();
if (sshTerminalOutput) {
  setSshConnectionStatus("fail", "Disconnected");
}
renderIssues();
renderIncidents();
renderIncidentReportSelect();
fetchTopologyHistory();
refreshTopologyChangeViews();
