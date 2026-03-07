(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminPortalSchema = factory();
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  function defineSection(panel, mode, label, subtitle, extras) {
    const options = extras || {};
    return {
      panel,
      mode,
      label,
      subtitle,
      scrollTarget: options.scrollTarget ?? null,
      sharedPanelLabel: options.sharedPanelLabel ?? null,
      sharedPanelCopy: options.sharedPanelCopy ?? null,
    };
  }

  function isRecord(value) {
    return !!value && typeof value === "object";
  }

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function validateRequiredString(errors, value, message) {
    if (typeof value !== "string" || !value) {
      errors.push(message);
    }
  }

  function validateOptionalString(errors, value, message) {
    if (value !== null && value !== undefined && typeof value !== "string") {
      errors.push(message);
    }
  }

  const modes = {
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

  const sections = {
    dashboard: defineSection("dashboard", "observe", "Dashboard", "Graph-first operations with PowerShell fallback"),
    reports: defineSection("reports", "analyze", "Reports", "Audit-ready reports and summaries"),
    settings: defineSection("settings", "configure", "Settings", "Local session and credentials"),
    controlplane: defineSection("controlplane", "observe", "Control Plane", "Agent fleet status and job queue"),
    actionpacks: defineSection("actionpacks", "act", "Action Packs", "Run multi-step workflows", {
      scrollTarget: "action-pack-panel",
    }),
    investigations: defineSection(
      "investigations",
      "observe",
      "Investigations",
      "Focused timeline + context workspace",
      { scrollTarget: "investigation-workspace" }
    ),
    workspaces: defineSection("workspaces", "observe", "Workspaces", "Saved multi-block dashboards"),
    help: defineSection("help", "learn", "Help", "In-app documentation and how-to guidance"),

    incidents: defineSection("reports", "observe", "Incidents", "Incident workspace, timeline, and evidence", {
      scrollTarget: "incident-workspace",
      sharedPanelLabel: "Reports",
      sharedPanelCopy: "This section focuses the incident workspace inside the shared Reports surface.",
    }),
    snapshots: defineSection("reports", "observe", "Snapshots", "Snapshot history, diffs, and coverage", {
      scrollTarget: "snapshot-history",
      sharedPanelLabel: "Reports",
      sharedPanelCopy: "This section focuses snapshot history inside the shared Reports surface.",
    }),
    auditlog: defineSection("settings", "observe", "Audit Log", "Audit trail and system events", {
      scrollTarget: "audit-card",
      sharedPanelLabel: "Settings",
      sharedPanelCopy: "This section focuses the audit trail inside the shared Settings surface.",
    }),
    healthcheck: defineSection("settings", "configure", "Health Check", "System health, readiness, and diagnostics", {
      scrollTarget: "health-card",
      sharedPanelLabel: "Settings",
      sharedPanelCopy: "This section focuses health and readiness checks inside the shared Settings surface.",
    }),
    quickactions: defineSection("dashboard", "act", "Quick Actions", "Dashboard shortcuts and pinned tasks", {
      scrollTarget: "quick-actions-card",
      sharedPanelLabel: "Dashboard",
      sharedPanelCopy: "This section focuses quick actions inside the shared Dashboard surface.",
    }),
    vision: defineSection("controlplane", "observe", "Vision", "Latest Vision-U-Eye snapshots, labels, and narration", {
      scrollTarget: "vision-card",
      sharedPanelLabel: "Control Plane",
      sharedPanelCopy: "This section focuses the Vision workspace inside the shared Control Plane surface.",
    }),
    tools: defineSection(
      "controlplane",
      "observe",
      "Tools Catalog",
      "All actions across agents, grouped by tool and filtered by capability/risk",
      {
        scrollTarget: "tools-catalog-card",
        sharedPanelLabel: "Control Plane",
        sharedPanelCopy: "This section focuses the tool catalog inside the shared Control Plane surface.",
      }
    ),
    actionrequests: defineSection(
      "controlplane",
      "observe",
      "Action Requests",
      "Promoted break-glass terminal commands (backlog only)",
      {
        scrollTarget: "action-requests-card",
        sharedPanelLabel: "Control Plane",
        sharedPanelCopy: "This section focuses the action request backlog inside the shared Control Plane surface.",
      }
    ),
    agents: defineSection("controlplane", "observe", "Agents", "Agent fleet status, capabilities, and labels", {
      scrollTarget: "agents-card",
      sharedPanelLabel: "Control Plane",
      sharedPanelCopy: "This section focuses the agent fleet view inside the shared Control Plane surface.",
    }),
    jobs: defineSection("controlplane", "observe", "Jobs", "Job queue, leases, and results across agents", {
      scrollTarget: "jobs-card",
      sharedPanelLabel: "Control Plane",
      sharedPanelCopy: "This section focuses the job queue inside the shared Control Plane surface.",
    }),
    catalog: defineSection(
      "controlplane",
      "observe",
      "Action Catalog",
      "Known actions and required capabilities (by agent)",
      {
        scrollTarget: "catalog-card",
        sharedPanelLabel: "Control Plane",
        sharedPanelCopy: "This section focuses the action catalog inside the shared Control Plane surface.",
      }
    ),
    bootstrap: defineSection(
      "controlplane",
      "observe",
      "Runner Bootstrap",
      "Pair runners, quick install, and connectivity verification",
      {
        scrollTarget: "runner-bootstrap-card",
        sharedPanelLabel: "Control Plane",
        sharedPanelCopy: "This section focuses runner bootstrap inside the shared Control Plane surface.",
      }
    ),

    exchange: defineSection("exchange", "act", "Exchange", "Mail, calendars, and shared mailbox controls"),
    onedrive: defineSection("onedrive", "act", "OneDrive", "Drive operations, permissions, and sync"),
    sharepoint: defineSection("sharepoint", "act", "SharePoint", "Sites, lists, and pages management"),
    teams: defineSection("teams", "act", "Teams", "Teams, channels, and messaging"),
    entra: defineSection("entra", "act", "Entra", "Directory, groups, and app inventory"),
    azure: defineSection("azure", "act", "Azure", "Subscription and infrastructure inventory"),
    defender: defineSection("defender", "act", "Defender for Cloud", "Defender for Cloud"),
    powerplatform: defineSection("powerplatform", "act", "Power Platform", "Power Platform admin"),
    purview: defineSection("purview", "act", "Purview", "Compliance and data governance"),
    localad: defineSection("localad", "act", "Local AD", "Local Active Directory (on-prem)"),
    endpoint: defineSection("endpoint", "act", "Endpoints", "Endpoint inventory and diagnostics"),
    domaincontroller: defineSection(
      "domaincontroller",
      "act",
      "Domain Controller",
      "Domain controller replication and health"
    ),
    printers: defineSection("printers", "act", "Printers", "On-prem print servers and GPO checks"),
    network: defineSection("network", "act", "Network", "On-prem network adapters and IP settings"),
    remote_workflows: defineSection(
      "remote_workflows",
      "act",
      "Remote Workflows",
      "Remote-only workflows with explainable guidance"
    ),
    ssh: defineSection("ssh", "act", "SSH", "Remote workstation sessions over SSH"),
    fileserver: defineSection("fileserver", "act", "File Server", "On-prem file share enumeration"),
    topology: defineSection("topology", "observe", "Network Topology", "Live on-prem device and service topology"),
    time: defineSection("time", "observe", "Time & Drift", "Time sync and drift intelligence"),
    certificates: defineSection("certificates", "observe", "Certificates", "Certificate inventory and TLS trust"),
    processes: defineSection("processes", "observe", "Processes", "Process, service, and binary reality checks"),
    baselines: defineSection("baselines", "analyze", "Baselines", "Golden baselines and drift comparison"),
    eventlogs: defineSection("eventlogs", "observe", "Event Logs", "Event log summaries and EVTX evidence"),
    registry: defineSection("registry", "observe", "Registry", "Registry watchlists and exports"),
  };

  function validatePortalSchema(schema) {
    const errors = [];
    if (!isRecord(schema)) {
      return ["Schema must be an object."];
    }
    if (!isRecord(schema.modes)) {
      errors.push("Schema is missing a modes object.");
    }
    if (!isRecord(schema.sections)) {
      errors.push("Schema is missing a sections object.");
    }
    if (errors.length) return errors;

    const modeNames = Object.keys(schema.modes);
    if (!modeNames.length) {
      errors.push("Schema must declare at least one mode.");
    }
    modeNames.forEach((modeName) => {
      const meta = schema.modes[modeName];
      if (!isRecord(meta)) {
        errors.push(`Mode ${modeName} must be an object.`);
        return;
      }
      validateRequiredString(errors, meta.label, `Mode ${modeName} is missing label.`);
      if (!hasOwn(meta, "subtitle") || typeof meta.subtitle !== "string") {
        errors.push(`Mode ${modeName} is missing subtitle.`);
      }
    });

    const sectionNames = Object.keys(schema.sections);
    if (!sectionNames.length) {
      errors.push("Schema must declare at least one section.");
    }
    sectionNames.forEach((sectionName) => {
      const meta = schema.sections[sectionName];
      if (!isRecord(meta)) {
        errors.push(`Section ${sectionName} must be an object.`);
        return;
      }
      if (typeof meta.panel !== "string" || !meta.panel) {
        errors.push(`Section ${sectionName} is missing panel.`);
      } else if (!schema.sections[meta.panel]) {
        errors.push(`Section ${sectionName} references unknown panel ${meta.panel}.`);
      }
      if (typeof meta.mode !== "string" || !meta.mode) {
        errors.push(`Section ${sectionName} is missing mode.`);
      } else if (!schema.modes[meta.mode]) {
        errors.push(`Section ${sectionName} references unknown mode ${meta.mode}.`);
      }
      validateRequiredString(errors, meta.label, `Section ${sectionName} is missing label.`);
      if (!hasOwn(meta, "subtitle") || typeof meta.subtitle !== "string") {
        errors.push(`Section ${sectionName} is missing subtitle.`);
      }
      if (!hasOwn(meta, "scrollTarget")) {
        errors.push(`Section ${sectionName} is missing scrollTarget.`);
      } else if (meta.scrollTarget !== null && typeof meta.scrollTarget !== "string") {
        errors.push(`Section ${sectionName} has invalid scrollTarget.`);
      }
      validateOptionalString(errors, meta.sharedPanelLabel, `Section ${sectionName} has invalid sharedPanelLabel.`);
      validateOptionalString(errors, meta.sharedPanelCopy, `Section ${sectionName} has invalid sharedPanelCopy.`);
    });

    return errors;
  }

  function getNamedMeta(registry, key) {
    const normalizedKey = String(key || "").trim();
    if (!normalizedKey) return null;
    return registry[normalizedKey] || null;
  }

  function getSectionMeta(section) {
    return getNamedMeta(sections, section);
  }

  function getModeMeta(mode) {
    return getNamedMeta(modes, mode);
  }

  function getSharedPanelContext(section) {
    const meta = getSectionMeta(section);
    if (!meta) return null;
    const panelMeta = getSectionMeta(meta.panel);
    const label = meta.sharedPanelLabel || (meta.panel !== section ? panelMeta?.label || null : null);
    const copy = meta.sharedPanelCopy || null;
    if (!label && !copy) return null;
    return { label, copy };
  }

  const schema = {
    modes,
    sections,
    validatePortalSchema,
    getSectionMeta,
    getModeMeta,
    getSharedPanelContext,
  };

  const errors = validatePortalSchema(schema);
  if (errors.length) {
    throw new Error(`Invalid GraphAdminPortalSchema: ${errors.join("; ")}`);
  }

  return schema;
});
