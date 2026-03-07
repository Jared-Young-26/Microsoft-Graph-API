(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.GraphAdminServiceShells = api;
    if (root.document && typeof root.document.querySelectorAll === "function") {
      api.renderServiceShells(root.document);
    }
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const TARGET_SERVICES = [
    "exchange",
    "onedrive",
    "sharepoint",
    "teams",
    "entra",
    "azure",
    "defender",
    "powerplatform",
    "purview",
    "localad",
    "endpoint",
    "domaincontroller",
    "printers",
    "network",
    "fileserver",
    "time",
    "certificates",
    "processes",
    "baselines",
    "eventlogs",
    "registry",
  ];

  const SHELL_SECTIONS = ["toolkit", "runner", "output"];

  const SHELL_TEXT_BINDINGS = [
    ["toolkit-title", (shell) => shell.toolkit.title],
    ["toolkit-subtitle", (shell) => shell.toolkit.subtitle],
    ["runner-title", (shell) => shell.runner.title],
    ["runner-subtitle", (shell) => shell.runner.subtitle],
    ["output-title", (shell) => shell.output.title],
    ["output-subtitle", (shell) => shell.output.subtitle],
  ];

  const SINGLE_NODE_DATA_BINDINGS = [
    {
      selector: "[data-shell-runner]",
      datasetKey: "service",
      removeAttributes: ["data-shell-runner"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-action-select]",
      datasetKey: "service",
      removeAttributes: ["data-shell-action-select"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-runner-fields]",
      datasetKey: "service",
      removeAttributes: ["data-shell-runner-fields"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-runner-reset]",
      datasetKey: "service",
      removeAttributes: ["data-shell-runner-reset"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-runner-run]",
      datasetKey: "service",
      removeAttributes: ["data-shell-runner-run"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-output]",
      datasetKey: "output",
      removeAttributes: ["data-shell-output"],
      getValue: (service) => service,
    },
    {
      selector: "[data-shell-clear]",
      datasetKey: "outputTarget",
      removeAttributes: ["data-shell-clear"],
      getValue: (service) => service,
    },
  ];

  function normalizeWorkspaceKey(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
  }

  function isNonEmptyString(value) {
    return typeof value === "string" && value.trim();
  }

  function defineShell(service, definition) {
    return {
      service,
      toolkit: definition.toolkit,
      runner: definition.runner,
      output: definition.output,
      workspaceBlocks: {
        toolkit: `${service}.toolkit`,
        runner: `${service}.runner`,
        output: `${service}.output`,
      },
    };
  }

  const SERVICE_SHELLS = {
    exchange: defineShell("exchange", {
      toolkit: {
        title: "Exchange toolkit",
        subtitle: "Mail, calendars, shared mailbox admin",
        chips: [
          { action: "list_mail_folders", label: "List mail folders" },
          { action: "list_messages", label: "Search messages" },
          { action: "list_events", label: "Calendar view" },
          { action: "enable_shared_sent_items", label: "Enable shared sent items (PS)" },
        ],
      },
      runner: {
        title: "Exchange task runner",
        subtitle: "Fine-grained controls",
        actionsClassNames: ["execution-bar"],
        info: {
          summary: "Where to find Exchange IDs",
          items: [
            "<strong>Shared mailbox UPN</strong>: Exchange admin center &rarr; Recipients &rarr; Shared &rarr; select mailbox &rarr; Primary SMTP address.",
            "<strong>User ID / UPN</strong>: Entra admin center &rarr; Users &rarr; select user &rarr; copy UPN or Object ID.",
          ],
        },
      },
      output: {
        title: "Exchange output",
        subtitle: "Latest response",
      },
    }),
    onedrive: defineShell("onedrive", {
      toolkit: {
        title: "OneDrive toolkit",
        subtitle: "Drive operations and sync",
        chips: [
          { action: "list_drive_items", label: "List root items" },
          { action: "create_upload_session", label: "Create upload session" },
          { action: "list_personal_sites", label: "List personal sites (PS)" },
          { action: "drive_cache_status", label: "Drive cache status", runNow: true },
          { action: "warm_drive_cache", label: "Warm drive cache now", runNow: true },
        ],
      },
      runner: {
        title: "OneDrive task runner",
        subtitle: "Targeted file operations",
        info: {
          summary: "Where to find OneDrive IDs",
          items: [
            "<strong>OneDrive drive ID</strong>: Graph Explorer &rarr; <code>GET /users/{userId}/drive</code> &rarr; copy <code>id</code>.",
            "<strong>User ID / UPN</strong>: Entra admin center &rarr; Users &rarr; select user &rarr; copy UPN or Object ID.",
          ],
        },
      },
      output: {
        title: "OneDrive output",
        subtitle: "Latest response",
      },
    }),
    sharepoint: defineShell("sharepoint", {
      toolkit: {
        title: "SharePoint toolkit",
        subtitle: "Sites, lists, and pages",
        chips: [
          { action: "list_sites", label: "List sites" },
          { action: "create_list", label: "Create list" },
          { action: "list_list_items", label: "List list items" },
          { action: "list_sites_admin", label: "SPO admin (PS)" },
        ],
      },
      runner: {
        title: "SharePoint task runner",
        subtitle: "List and site management",
        info: {
          summary: "Where to find SharePoint IDs",
          items: [
            "<strong>Site ID</strong>: Graph Explorer &rarr; <code>GET /sites?search=*</code> &rarr; copy <code>id</code>.",
            "<strong>List ID</strong>: Graph Explorer &rarr; <code>GET /sites/{siteId}/lists</code> &rarr; copy list <code>id</code>.",
            "<strong>Admin URL</strong>: <code>https://&lt;tenant&gt;-admin.sharepoint.com</code>.",
          ],
        },
      },
      output: {
        title: "SharePoint output",
        subtitle: "Latest response",
      },
    }),
    teams: defineShell("teams", {
      toolkit: {
        title: "Teams toolkit",
        subtitle: "Teams, channels, chats",
        chips: [
          { action: "list_teams", label: "List teams" },
          { action: "list_team_members", label: "List team members" },
          { action: "create_channel", label: "Create channel" },
          { action: "list_chat_messages", label: "List chat messages" },
          { action: "ps_list_policies", label: "Policies (PS)" },
        ],
      },
      runner: {
        title: "Teams task runner",
        subtitle: "Channel and chat tools",
        info: {
          summary: "Where to find Teams IDs",
          items: [
            "<strong>Team ID</strong>: Teams admin center &rarr; Teams &rarr; Manage teams &rarr; select team &rarr; Group ID.",
            "<strong>Chat ID</strong>: Graph Explorer &rarr; <code>GET /chats</code> (delegated) &rarr; copy <code>id</code>.",
          ],
        },
      },
      output: {
        title: "Teams output",
        subtitle: "Latest response",
      },
    }),
    entra: defineShell("entra", {
      toolkit: {
        title: "Entra toolkit",
        subtitle: "Users, groups, apps",
        chips: [
          { action: "list_users", label: "List users" },
          { action: "get_user", label: "Get user" },
          { action: "create_user", label: "Create user" },
          { action: "update_user", label: "Update user" },
          { action: "delete_user", label: "Delete user" },
          { action: "add_group_member", label: "Add group member" },
          { action: "list_service_principals", label: "List service principals" },
          { action: "set_user_license", label: "Set user license (PS)" },
        ],
      },
      runner: {
        title: "Entra task runner",
        subtitle: "Directory operations",
        info: {
          summary: "Where to find Entra IDs",
          items: [
            "<strong>User ID</strong>: Entra admin center &rarr; Users &rarr; select user &rarr; Object ID.",
            "<strong>Group ID</strong>: Entra admin center &rarr; Groups &rarr; select group &rarr; Object ID.",
            "<strong>App/Service principal ID</strong>: Entra admin center &rarr; App registrations / Enterprise apps &rarr; select app &rarr; Object ID.",
          ],
        },
      },
      output: {
        title: "Entra output",
        subtitle: "Latest response",
      },
    }),
    azure: defineShell("azure", {
      toolkit: {
        title: "Azure toolkit",
        subtitle: "Subscriptions and inventory",
        chips: [
          { action: "list_subscriptions", label: "List subscriptions" },
          { action: "list_resource_groups", label: "List resource groups" },
          { action: "list_virtual_machines", label: "List VMs" },
          { action: "list_key_vaults", label: "List Key Vaults" },
        ],
      },
      runner: {
        title: "Azure task runner",
        subtitle: "Inventory and metadata",
        info: {
          summary: "Where to find Azure IDs",
          items: [
            "<strong>Subscription ID</strong>: Azure portal &rarr; Subscriptions &rarr; copy Subscription ID.",
            "<strong>Resource group</strong>: Azure portal &rarr; Resource groups &rarr; copy name.",
            "<strong>Key Vault name</strong>: Azure portal &rarr; Key vaults &rarr; copy name.",
          ],
        },
      },
      output: {
        title: "Azure output",
        subtitle: "Latest response",
      },
    }),
    defender: defineShell("defender", {
      toolkit: {
        title: "Defender for Cloud",
        subtitle: "Security posture and cloud workload protection",
        chips: [
          { action: "secure_score_summary", label: "Secure score summary" },
          { action: "recommendations_list", label: "Recommendations list" },
        ],
      },
      runner: {
        title: "Defender task runner",
        subtitle: "Add actions as they are implemented",
      },
      output: {
        title: "Defender output",
        subtitle: "Latest response",
      },
    }),
    powerplatform: defineShell("powerplatform", {
      toolkit: {
        title: "Power Platform",
        subtitle: "Admin operations for Power Apps & Power Automate",
        chips: [
          { action: "list_environments", label: "List environments" },
          { action: "list_flows", label: "List flows (environment)" },
        ],
      },
      runner: {
        title: "Power Platform task runner",
        subtitle: "Add actions as they are implemented",
      },
      output: {
        title: "Power Platform output",
        subtitle: "Latest response",
      },
    }),
    purview: defineShell("purview", {
      toolkit: {
        title: "Purview toolkit",
        subtitle: "Compliance and eDiscovery",
        chips: [
          { action: "list_retention_policies", label: "List retention policies" },
          { action: "create_compliance_search", label: "Create compliance search" },
          { action: "list_dlp_policies", label: "List DLP policies" },
          { action: "list_compliance_actions", label: "Compliance actions" },
        ],
      },
      runner: {
        title: "Purview task runner",
        subtitle: "Compliance tasks",
        info: {
          summary: "Where to find Purview items",
          items: [
            "<strong>Retention/DLP policy names</strong>: Microsoft Purview compliance portal &rarr; Data lifecycle / DLP.",
            "<strong>Compliance searches</strong>: Purview portal &rarr; eDiscovery &rarr; Content search.",
          ],
        },
      },
      output: {
        title: "Purview output",
        subtitle: "Latest response",
      },
    }),
    localad: defineShell("localad", {
      toolkit: {
        title: "Local Active Directory",
        subtitle: "On-prem AD users, groups, OUs, GPOs",
        chips: [
          { action: "list_gpos", label: "List GPOs" },
          { action: "gpo_inheritance", label: "GPO inheritance" },
          { action: "gpo_links", label: "GPO links" },
          { action: "gpo_report", label: "GPO report" },
          { action: "gppref_registry", label: "GPP registry values" },
          { action: "gpresult_report", label: "GPResult report" },
        ],
        notes: ["Requires PowerShell on a domain-joined host with RSAT / ActiveDirectory + GroupPolicy modules."],
      },
      runner: {
        title: "Local AD task runner",
        subtitle: "Local-only PowerShell actions",
      },
      output: {
        title: "Local AD output",
        subtitle: "Latest response",
      },
    }),
    endpoint: defineShell("endpoint", {
      toolkit: {
        title: "Endpoint toolkit",
        subtitle: "Workstation inventory, logs, patching, and GPO context",
        chips: [
          { action: "computer_info", label: "Computer info" },
          { action: "cim_summary", label: "CIM summary" },
          { action: "systeminfo", label: "Systeminfo baseline" },
          { action: "list_processes", label: "Top processes" },
          { action: "list_services", label: "List services" },
          { action: "query_event_logs", label: "Query event logs" },
          { action: "list_hotfixes", label: "Hotfix inventory" },
          { action: "whoami_all", label: "Whoami /all" },
          { action: "gpresult_report", label: "GPResult report" },
        ],
        notes: ["Best run on the target workstation (or a remote session) with GroupPolicy module available for RSoP."],
      },
      runner: {
        title: "Endpoint task runner",
        subtitle: "System identity, event logs, updates, and policy reports",
        info: {
          summary: "What these checks tell you",
          items: [
            "<strong>System identity</strong>: hardware, OS build, uptime, domain join status.",
            "<strong>Logs &amp; services</strong>: rapid fault isolation and service health.",
            "<strong>Updates &amp; policy</strong>: patch status plus applied GPO context.",
          ],
        },
      },
      output: {
        title: "Endpoint output",
        subtitle: "Latest response",
      },
    }),
    domaincontroller: defineShell("domaincontroller", {
      toolkit: {
        title: "Domain controller toolkit",
        subtitle: "Replication, topology, and forest/domain health",
        chips: [
          { action: "list_domain_controllers", label: "List domain controllers" },
          { action: "replication_health_summary", label: "Replication summary" },
          { action: "show_replication_partners", label: "Show replication partners" },
          { action: "dc_diagnostics", label: "Run dcdiag" },
          { action: "list_fsmo_roles", label: "List FSMO roles" },
          { action: "time_sync_status", label: "Time sync status" },
        ],
        notes: ["Best run on a domain-joined admin workstation with RSAT + ActiveDirectory module."],
      },
      runner: {
        title: "Domain controller task runner",
        subtitle: "repadmin, dcdiag, nltest, AD replication cmdlets, and time health",
        info: {
          summary: "Why these checks help",
          items: [
            "<strong>Replication summary/partners</strong>: finds stale DC links and failure hotspots quickly.",
            "<strong>dcdiag</strong>: surfaces DNS/service/advertising issues that break auth and policy flow.",
            "<strong>FSMO/time checks</strong>: catches role holder and time skew problems that impact Kerberos.",
          ],
        },
      },
      output: {
        title: "Domain controller output",
        subtitle: "Latest response",
      },
    }),
    printers: defineShell("printers", {
      toolkit: {
        title: "Printers",
        subtitle: "Print server inventory and GPO cross-checks",
        chips: [
          { action: "list_printers", label: "List printers" },
          { action: "list_gpo_printer_mappings", label: "List GPO printer mappings" },
          { action: "cross_reference_printers_gpo", label: "Cross-reference printers vs GPOs" },
        ],
        notes: ["Requires PrintManagement + GroupPolicy modules on a domain-joined host."],
      },
      runner: {
        title: "Printer task runner",
        subtitle: "PowerShell-only printer controls",
        info: {
          summary: "Where to find printer details",
          items: [
            "<strong>Printer names/shares</strong>: Print Management &rarr; Printers &rarr; Name / Share name.",
            "<strong>GPO printer deployments</strong>: Group Policy Management &rarr; GPO &rarr; User/Computer Configuration &rarr; Printers.",
          ],
        },
      },
      output: {
        title: "Printers output",
        subtitle: "Latest response",
      },
    }),
    network: defineShell("network", {
      toolkit: {
        title: "Network adapters",
        subtitle: "On-prem interface inventory and configuration",
        chips: [
          { action: "list_adapters", label: "List adapters" },
          { action: "get_adapter_config", label: "Get adapter config" },
          { action: "set_dhcp", label: "Enable/disable DHCP" },
          { action: "set_dns_servers", label: "Set DNS servers" },
          { action: "ping_host", label: "Ping host" },
          { action: "resolve_dns_name", label: "Resolve hostname" },
          { action: "test_port", label: "Test port" },
          { action: "trace_route", label: "Trace route" },
          { action: "list_routes", label: "Route table" },
          { action: "firewall_profiles", label: "Firewall profiles" },
          { action: "smb_connections", label: "SMB connections" },
        ],
        notes: [
          "Requires admin rights for most changes. Uses NetAdapter/NetTCPIP plus optional NetSecurity, DnsServer, SmbShare modules.",
        ],
      },
      runner: {
        title: "Network task runner",
        subtitle: "PowerShell-only network actions",
        info: {
          summary: "Where to find adapter details",
          items: [
            "<strong>Adapter name</strong>: Get-NetAdapter &rarr; Name column.",
            "<strong>IPv4 settings</strong>: Get-NetIPConfiguration &rarr; IPv4Address / IPv4DefaultGateway.",
          ],
        },
      },
      output: {
        title: "Network output",
        subtitle: "Latest response",
      },
    }),
    fileserver: defineShell("fileserver", {
      toolkit: {
        title: "File server",
        subtitle: "Enumerate files on UNC shares",
        chips: [{ action: "list_files", label: "List files in share" }],
        notes: ["Uses PowerShell on the local host. Provide a UNC path (\\\\\\\\server\\\\share)."],
      },
      runner: {
        title: "File server task runner",
        subtitle: "Share enumeration with optional credentials",
        info: {
          summary: "UNC path format",
          items: [
            "<strong>UNC</strong>: \\\\\\\\server\\\\share (e.g., \\\\\\\\files01\\\\Accounting).",
            "<strong>Credentials</strong>: domain\\\\user or user@domain.com.",
          ],
        },
      },
      output: {
        title: "File server output",
        subtitle: "Latest response",
      },
    }),
    time: defineShell("time", {
      toolkit: {
        title: "Time & drift toolkit",
        subtitle: "NTP, DC offsets, and drift checks",
        chips: [
          { action: "time_chain", label: "Run time chain" },
          { action: "time_drift_history", label: "View drift history" },
        ],
      },
      runner: {
        title: "Time & drift runner",
        subtitle: "Fine-grained time probes",
      },
      output: {
        title: "Time output",
        subtitle: "Latest response",
      },
    }),
    certificates: defineShell("certificates", {
      toolkit: {
        title: "Certificates toolkit",
        subtitle: "Machine store inventory and TLS trust",
        chips: [
          { action: "list_machine_certificates", label: "List certificates" },
          { action: "tls_probe", label: "TLS trust probe" },
        ],
      },
      runner: {
        title: "Certificates runner",
        subtitle: "Targeted certificate checks",
      },
      output: {
        title: "Certificates output",
        subtitle: "Latest response",
      },
    }),
    processes: defineShell("processes", {
      toolkit: {
        title: "Processes toolkit",
        subtitle: "Process inventory and service mapping",
        chips: [
          { action: "process_inventory", label: "Process inventory" },
          { action: "service_process_map", label: "Service → process map" },
        ],
      },
      runner: {
        title: "Processes runner",
        subtitle: "Binary and service reality checks",
      },
      output: {
        title: "Processes output",
        subtitle: "Latest response",
      },
    }),
    baselines: defineShell("baselines", {
      toolkit: {
        title: "Baselines toolkit",
        subtitle: "Golden snapshots and comparisons",
        chips: [
          { action: "list_golden", label: "List golden baselines" },
          { action: "compare_golden", label: "Compare to golden" },
        ],
      },
      runner: {
        title: "Baselines runner",
        subtitle: "Set and compare golden baselines",
      },
      output: {
        title: "Baselines output",
        subtitle: "Latest response",
      },
    }),
    eventlogs: defineShell("eventlogs", {
      toolkit: {
        title: "Event Logs toolkit",
        subtitle: "Summaries, exports, and incident attachments",
        chips: [
          { action: "eventlog_summary", label: "Last 24h summary" },
          { action: "eventlog_gpo_failures", label: "GPO failures summary" },
          { action: "eventlog_print_failures", label: "Print failures summary" },
          { action: "eventlog_rdp_failures", label: "RDP/logon failures summary" },
          { action: "eventlog_windows_update_failures", label: "Windows Update failures" },
        ],
      },
      runner: {
        title: "Event Logs runner",
        subtitle: "Query and export event data",
      },
      output: {
        title: "Event Logs output",
        subtitle: "Latest response",
      },
    }),
    registry: defineShell("registry", {
      toolkit: {
        title: "Registry toolkit",
        subtitle: "Watchlists, snapshots, and exports",
        chips: [
          { action: "list_watchlists", label: "List watchlists" },
          { action: "capture_watchlist", label: "Capture watchlist snapshot" },
          { action: "diff_watchlist", label: "Diff watchlist snapshots" },
        ],
      },
      runner: {
        title: "Registry runner",
        subtitle: "Watchlists and exports",
      },
      output: {
        title: "Registry output",
        subtitle: "Latest response",
      },
    }),
  };

  function getServiceShell(service) {
    return SERVICE_SHELLS[service] || null;
  }

  function getWorkspaceBlockIds(service) {
    return getServiceShell(service)?.workspaceBlocks || null;
  }

  function buildLegacyWorkspaceBlocks(registry) {
    const aliases = {};
    Object.entries(registry).forEach(([service, shell]) => {
      SHELL_SECTIONS.forEach((section) => {
        aliases[`${service}.${normalizeWorkspaceKey(shell[section].title) || "tile"}`] = shell.workspaceBlocks[section];
      });
    });
    return aliases;
  }

  const legacyWorkspaceBlocks = buildLegacyWorkspaceBlocks(SERVICE_SHELLS);

  function validateShellSection(errors, service, section, meta) {
    if (!meta || typeof meta !== "object") {
      errors.push(`Service shell ${service} is missing ${section}.`);
      return;
    }
    if (!isNonEmptyString(meta.title)) {
      errors.push(`Service shell ${service} is missing ${section} title.`);
    }
    if (typeof meta.subtitle !== "string") {
      errors.push(`Service shell ${service} is missing ${section} subtitle.`);
    }
  }

  function validateToolkitChip(errors, service, chip, index) {
    if (!chip || typeof chip !== "object") {
      errors.push(`Service shell ${service} chip ${index} must be an object.`);
      return;
    }
    if (!isNonEmptyString(chip.action)) {
      errors.push(`Service shell ${service} chip ${index} is missing action.`);
    }
    if (!isNonEmptyString(chip.label)) {
      errors.push(`Service shell ${service} chip ${index} is missing label.`);
    }
  }

  function validateRunnerInfo(errors, service, info) {
    if (!info) return;
    if (!isNonEmptyString(info.summary)) {
      errors.push(`Service shell ${service} runner info is missing summary.`);
    }
    if (!Array.isArray(info.items) || !info.items.length) {
      errors.push(`Service shell ${service} runner info is missing items.`);
    }
  }

  function validateWorkspaceBlocks(errors, service, blocks) {
    if (blocks.toolkit !== `${service}.toolkit`) {
      errors.push(`Service shell ${service} has invalid toolkit workspace block.`);
    }
    if (blocks.runner !== `${service}.runner`) {
      errors.push(`Service shell ${service} has invalid runner workspace block.`);
    }
    if (blocks.output !== `${service}.output`) {
      errors.push(`Service shell ${service} has invalid output workspace block.`);
    }
  }

  function validateServiceShellRegistry(registry) {
    const errors = [];
    if (!registry || typeof registry !== "object") {
      return ["Service shell registry must be an object."];
    }

    Object.entries(registry).forEach(([service, shell]) => {
      if (!shell || typeof shell !== "object") {
        errors.push(`Service shell ${service} must be an object.`);
        return;
      }
      if (shell.service !== service) {
        errors.push(`Service shell ${service} has mismatched service key.`);
      }
      SHELL_SECTIONS.forEach((section) => validateShellSection(errors, service, section, shell[section]));
      if (!Array.isArray(shell.toolkit?.chips) || !shell.toolkit.chips.length) {
        errors.push(`Service shell ${service} is missing toolkit chips.`);
      }
      (shell.toolkit?.chips || []).forEach((chip, index) => validateToolkitChip(errors, service, chip, index));
      validateRunnerInfo(errors, service, shell.runner?.info);
      validateWorkspaceBlocks(errors, service, shell.workspaceBlocks || {});
    });

    return errors;
  }

  const RENDER_VALIDATIONS = [
    {
      expectedCount: 0,
      selector: (service) => `[data-service-shell="${service}"]`,
      error: (service) => `Service shell ${service} mount was not replaced.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.runner[data-service="${service}"]`,
      error: (service) => `Service shell ${service} must render one runner.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.action-select[data-service="${service}"]`,
      error: (service) => `Service shell ${service} must render one action select.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.runner-fields[data-service="${service}"]`,
      error: (service) => `Service shell ${service} must render one runner field container.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.output[data-output="${service}"]`,
      error: (service) => `Service shell ${service} must render one output panel.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.output-card[data-panel="${service}"]`,
      error: (service) => `Service shell ${service} must render one output card.`,
    },
    {
      expectedCount: 1,
      selector: (service, shell) =>
        `.card[data-panel="${service}"][data-workspace-block="${shell?.workspaceBlocks?.toolkit || `${service}.toolkit`}"]`,
      error: (service) => `Service shell ${service} is missing toolkit workspace block.`,
    },
    {
      expectedCount: 1,
      selector: (service, shell) =>
        `.card[data-panel="${service}"][data-workspace-block="${shell?.workspaceBlocks?.runner || `${service}.runner`}"]`,
      error: (service) => `Service shell ${service} is missing runner workspace block.`,
    },
    {
      expectedCount: 1,
      selector: (service, shell) =>
        `.output-card[data-panel="${service}"][data-workspace-block="${shell?.workspaceBlocks?.output || `${service}.output`}"]`,
      error: (service) => `Service shell ${service} is missing output workspace block.`,
    },
    {
      expectedCount: 1,
      selector: (service) => `.output-card[data-panel="${service}"] .clear-output[data-output-target="${service}"]`,
      error: (service) => `Service shell ${service} is missing the clear-output target.`,
    },
  ];

  function validateRenderedServiceShell(host, service, shell, errors) {
    RENDER_VALIDATIONS.forEach((rule) => {
      if (host.querySelectorAll(rule.selector(service, shell)).length !== rule.expectedCount) {
        errors.push(rule.error(service));
      }
    });
  }

  function validateRenderedServiceShells(root, registry) {
    const host = root && typeof root.querySelectorAll === "function" ? root : null;
    if (!host) {
      return ["Rendered service shell root must support querySelectorAll."];
    }

    const shells = registry || SERVICE_SHELLS;
    const errors = [];
    Object.entries(shells).forEach(([service, shell]) => validateRenderedServiceShell(host, service, shell, errors));
    return errors;
  }

  function queryById(root, id) {
    if (!root) return null;
    if (typeof root.getElementById === "function") return root.getElementById(id);
    if (typeof root.querySelector === "function") return root.querySelector(`#${id}`);
    return null;
  }

  function cloneTemplate(root, id) {
    const template = queryById(root, id);
    if (!template || !template.content) {
      throw new Error(`Missing template: ${id}`);
    }
    return template.content.cloneNode(true);
  }

  function setText(root, selector, value) {
    const node = root.querySelector(selector);
    if (node) node.textContent = value;
  }

  function bindSingleDataAttribute(fragment, service, binding) {
    const element = fragment.querySelector(binding.selector);
    if (!element) return;
    element.dataset[binding.datasetKey] = binding.getValue(service);
    binding.removeAttributes.forEach((attribute) => element.removeAttribute(attribute));
  }

  function bindDataAttributes(fragment, service, shell) {
    fragment.querySelectorAll("[data-shell-card]").forEach((card) => {
      const role = card.getAttribute("data-shell-card");
      card.dataset.panel = service;
      card.dataset.workspaceBlock = shell.workspaceBlocks[role];
      card.removeAttribute("data-shell-card");
      card.removeAttribute("data-shell-panel");
    });

    SINGLE_NODE_DATA_BINDINGS.forEach((binding) => bindSingleDataAttribute(fragment, service, binding));
  }

  function appendClonedNode(root, templateId, selector, target, populate) {
    const node = cloneTemplate(root, templateId).querySelector(selector);
    populate(node);
    target.appendChild(node);
  }

  function renderToolkitBody(root, shellRoot, shell) {
    const stack = shellRoot.querySelector("[data-shell-slot='toolkit-body']");
    if (!stack) return;
    shell.toolkit.chips.forEach((chipMeta) => {
      appendClonedNode(root, "service-shell-chip-template", ".chip", stack, (chip) => {
        chip.textContent = chipMeta.label;
        chip.dataset.service = shell.service;
        chip.dataset.action = chipMeta.action;
        if (chipMeta.runNow) {
          chip.dataset.runNow = "true";
        }
      });
    });
    (shell.toolkit.notes || []).forEach((noteText) => {
      appendClonedNode(root, "service-shell-note-template", ".note", stack, (note) => {
        note.textContent = noteText;
      });
    });
  }

  function renderRunnerInfo(root, shellRoot, shell) {
    const infoMeta = shell.runner.info;
    const info = shellRoot.querySelector("[data-shell-info]");
    if (!infoMeta) {
      if (info) info.remove();
      return;
    }
    setText(shellRoot, "[data-shell-info-summary]", infoMeta.summary);
    const list = shellRoot.querySelector("[data-shell-info-list]");
    if (!list) return;
    infoMeta.items.forEach((item) => {
      appendClonedNode(root, "service-shell-info-item-template", "li", list, (itemNode) => {
        itemNode.innerHTML = item;
      });
    });
  }

  function applyShellText(fragment, shell) {
    SHELL_TEXT_BINDINGS.forEach(([key, getValue]) => {
      setText(fragment, `[data-shell-text='${key}']`, getValue(shell));
    });
  }

  function renderServiceShell(root, mount, shell) {
    const fragment = cloneTemplate(root, "service-shell-template");
    bindDataAttributes(fragment, shell.service, shell);

    applyShellText(fragment, shell);

    const actionsRow = fragment.querySelector("[data-shell-runner-actions]");
    if (actionsRow) {
      actionsRow.removeAttribute("data-shell-runner-actions");
      (shell.runner.actionsClassNames || []).forEach((className) => actionsRow.classList.add(className));
    }

    renderToolkitBody(root, fragment, shell);
    renderRunnerInfo(root, fragment, shell);

    mount.before(fragment);
    mount.remove();
  }

  function renderServiceShells(root) {
    const host = root && typeof root.querySelectorAll === "function" ? root : null;
    if (!host) return [];
    const errors = validateServiceShellRegistry(SERVICE_SHELLS);
    if (errors.length) {
      throw new Error(`Invalid service shell registry: ${errors.join("; ")}`);
    }
    const mounts = Array.from(host.querySelectorAll("[data-service-shell]"));
    const rendered = [];
    mounts.forEach((mount) => {
      const service = mount.getAttribute("data-service-shell");
      const shell = getServiceShell(service);
      if (!shell) {
        throw new Error(`Unknown service shell mount: ${service}`);
      }
      renderServiceShell(host, mount, shell);
      rendered.push(service);
    });
    const renderErrors = validateRenderedServiceShells(host, SERVICE_SHELLS);
    if (renderErrors.length) {
      throw new Error(`Invalid rendered service shells: ${renderErrors.join("; ")}`);
    }
    return rendered;
  }

  return {
    TARGET_SERVICES,
    SERVICE_SHELLS,
    legacyWorkspaceBlocks,
    getServiceShell,
    getWorkspaceBlockIds,
    validateServiceShellRegistry,
    validateRenderedServiceShells,
    renderServiceShells,
  };
});
