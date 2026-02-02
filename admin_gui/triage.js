(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminTriage = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  const DEFAULT_RULES = {
    metadata: [
      /^change\.previous_snapshot_id$/,
      /^change\.previousSnapshotId$/,
      /^change\.snapshot_id$/,
      /^change\.captured_at$/,
      /^change\.timestamp$/,
      /^change\.profile$/,
      /^change\.snapshot/,
      /^snapshots\./,
    ],
    security: [/^authz\./, /^identity\./],
    config: [/^config\./, /^connectivity\./, /^health\./, /^dependencies\./],
  };

  const DESCRIPTION_PREFIXES = [
    { prefix: "authz.groups", label: "Group membership" },
    { prefix: "authz.licenses", label: "License assignment" },
    { prefix: "authz.signins", label: "Sign-in summary" },
    { prefix: "authz", label: "Authorization state" },
    { prefix: "identity", label: "Identity profile" },
    { prefix: "config.firewall", label: "Firewall configuration" },
    { prefix: "config.printers", label: "Printer configuration" },
    { prefix: "config.dns", label: "DNS configuration" },
    { prefix: "config.dhcp", label: "DHCP configuration" },
    { prefix: "config.registry_watchlist", label: "Registry watchlist" },
    { prefix: "config", label: "Configuration" },
    { prefix: "connectivity.interfaces", label: "Network interfaces" },
    { prefix: "connectivity.routes", label: "Routing table" },
    { prefix: "connectivity.probes", label: "Connectivity probes" },
    { prefix: "connectivity", label: "Connectivity" },
    { prefix: "health.replication", label: "Replication health" },
    { prefix: "health.time", label: "Time sync" },
    { prefix: "health.eventlog_summary", label: "Event log summary" },
    { prefix: "health.services", label: "Service state" },
    { prefix: "health", label: "Health status" },
    { prefix: "dependencies", label: "Dependencies" },
    { prefix: "change", label: "Snapshot metadata" },
  ];

  const LIMITATION_MAP = {
    "identity.user_core": "Identity data unavailable",
    "authz.user_groups_core": "Group membership not evaluated",
    "authz.user_licenses_core": "License state not evaluated",
    "authz.signin_summary_24h": "Sign-in summary not evaluated",
    "authz.ca_block_summary_24h": "Conditional access not evaluated",
    "identity.device_directory_record": "Device directory record unavailable",
    "health.replication_summary": "Replication summary not evaluated",
    "health.dcdiag_quick": "DC health checks not evaluated",
    "connectivity.dns_resolve_external": "External DNS probes not evaluated",
    "connectivity.port_probe_external": "External port probes not evaluated",
    "health.eventlog.summary": "Event log summary not evaluated",
    "config.registry.watchlist_snapshot": "Registry watchlist not evaluated",
  };

  function applyOverrides(path, overrides) {
    if (!overrides || typeof overrides !== "object") return null;
    const entries = Object.entries(overrides);
    for (const [rule, bucket] of entries) {
      if (!bucket) continue;
      if (rule.startsWith("re:")) {
        const re = new RegExp(rule.slice(3));
        if (re.test(path)) return bucket;
      } else if (rule.endsWith("*")) {
        const prefix = rule.slice(0, -1);
        if (path.startsWith(prefix)) return bucket;
      } else if (rule === path) {
        return bucket;
      }
    }
    return null;
  }

  function classifyChangePath(path, overrides) {
    const override = applyOverrides(path, overrides);
    if (override) return override;
    for (const rule of DEFAULT_RULES.metadata) {
      if (rule.test(path)) return "metadata";
    }
    for (const rule of DEFAULT_RULES.security) {
      if (rule.test(path)) return "security";
    }
    for (const rule of DEFAULT_RULES.config) {
      if (rule.test(path)) return "config";
    }
    return "metadata";
  }

  function addObjectDiff(items, diff, basePath) {
    if (!diff) return;
    ["added", "removed", "changed"].forEach((type) => {
      const list = diff[type] || [];
      list.forEach((entry) => {
        items.push({
          path: entry.path || basePath,
          type,
          before: entry.before,
          after: entry.after,
          value: entry.value,
          key: entry.key,
          base: basePath,
        });
      });
    });
  }

  function addListDiff(items, diff, basePath) {
    if (!diff) return;
    (diff.added || []).forEach((entry) => {
      items.push({
        path: basePath,
        type: "added",
        key: entry.key,
        value: entry.item || entry.value,
        base: basePath,
      });
    });
    (diff.removed || []).forEach((entry) => {
      items.push({
        path: basePath,
        type: "removed",
        key: entry.key,
        value: entry.item || entry.value,
        base: basePath,
      });
    });
    (diff.changed || []).forEach((entry) => {
      items.push({
        path: basePath,
        type: "changed",
        key: entry.key,
        before: entry.before,
        after: entry.after,
        base: basePath,
      });
    });
  }

  function flattenDiffChanges(diff) {
    const items = [];
    if (!diff || typeof diff !== "object") return items;
    const sections = diff.sections || {};
    addObjectDiff(items, sections.identity, "identity");
    if (sections.connectivity) {
      addListDiff(items, sections.connectivity.interfaces, "connectivity.interfaces");
      addListDiff(items, sections.connectivity.probes, "connectivity.probes");
      addObjectDiff(items, sections.connectivity.routes, "connectivity.routes");
    }
    if (sections.authz) {
      addListDiff(items, sections.authz.groups, "authz.groups");
      addListDiff(items, sections.authz.licenses, "authz.licenses");
      addObjectDiff(items, sections.authz.signins, "authz.signins");
    }
    if (sections.config) {
      addListDiff(items, sections.config.printers, "config.printers");
      addObjectDiff(items, sections.config.firewall, "config.firewall");
      addObjectDiff(items, sections.config.dns, "config.dns");
      addObjectDiff(items, sections.config.dhcp, "config.dhcp");
      addListDiff(items, sections.config.registry_watchlist, "config.registry_watchlist");
    }
    if (sections.health) {
      addListDiff(items, sections.health.services, "health.services");
      addObjectDiff(items, sections.health.replication, "health.replication");
      addObjectDiff(items, sections.health.time, "health.time");
      addObjectDiff(items, sections.health.eventlog_summary, "health.eventlog_summary");
    }
    addObjectDiff(items, sections.dependencies, "dependencies");
    addObjectDiff(items, sections.change, "change");

    if (!items.length && diff.details) {
      addObjectDiff(items, diff.details, "report");
    }
    return items;
  }

  function labelFromPath(path) {
    const entry = DESCRIPTION_PREFIXES.find((rule) => path.startsWith(rule.prefix));
    return entry ? entry.label : path.replace(/\./g, " ");
  }

  function describeChange(item) {
    const label = labelFromPath(item.path || item.base || "");
    const action =
      item.type === "added" ? "added" : item.type === "removed" ? "removed" : "updated";
    const key = item.key ? ` (${item.key})` : "";
    return `${label} ${action}${key}.`;
  }

  function extractQuality(diff) {
    const quality = diff?.quality || {};
    const a = quality.a || quality.snapshot_a || {};
    const b = quality.b || quality.snapshot_b || {};
    return { a, b };
  }

  function completenessFromQuality(quality) {
    if (!quality || typeof quality !== "object") return null;
    return quality.completeness ?? quality.overall ?? null;
  }

  function computeCoverage(quality) {
    const values = [completenessFromQuality(quality.a), completenessFromQuality(quality.b)].filter(
      (value) => typeof value === "number"
    );
    if (!values.length) return { percent: null, label: "Unknown" };
    const score = Math.min(...values);
    const percent = Math.round(score * 100);
    let label = "Low";
    if (score >= 0.9) label = "High";
    else if (score >= 0.7) label = "Moderate";
    return { percent, label };
  }

  function buildCoverageLimitations(quality) {
    const warnings = []
      .concat(quality?.a?.warnings || [], quality?.a?.gaps || [])
      .concat(quality?.b?.warnings || [], quality?.b?.gaps || []);
    const seen = new Set();
    const limitations = [];
    warnings.forEach((entry) => {
      const probe = entry?.probe || "unknown";
      let label = LIMITATION_MAP[probe] || probe.replace(/_/g, " ");
      const message = entry?.message || entry?.details || "";
      let reason = "";
      if (typeof message === "string" && message.trim()) {
        reason = message
          .replace(/Graph request handler not configured/gi, "Graph handler not configured")
          .replace(/PowerShell \(pwsh\) not found/gi, "PowerShell not available");
        if (reason && !reason.trim().endsWith(".")) {
          reason = `${reason.trim()}.`;
        }
      }
      const finalLabel = reason ? `${label} (${reason})` : label;
      if (!seen.has(finalLabel)) {
        seen.add(finalLabel);
        limitations.push(finalLabel);
      }
    });
    return limitations;
  }

  function computeConfidenceByBucket(groups, limitations, coverage) {
    const values = {};
    const limitationText = (limitations || []).join(" ").toLowerCase();
    const hasAuthzGap =
      limitationText.includes("identity") ||
      limitationText.includes("group") ||
      limitationText.includes("license") ||
      limitationText.includes("sign-in") ||
      limitationText.includes("conditional access");
    const hasConfigGap =
      limitationText.includes("dns") ||
      limitationText.includes("firewall") ||
      limitationText.includes("registry") ||
      limitationText.includes("replication") ||
      limitationText.includes("event log");
    const totals = {
      security: groups.security.length,
      config: groups.config.length,
      metadata: groups.metadata.length,
    };
    const classify = (score) => {
      if (score >= 0.8) return { score, label: "High", key: "high" };
      if (score >= 0.5) return { score, label: "Moderate", key: "moderate" };
      return { score, label: "Low", key: "low" };
    };
    const coverageScore =
      coverage && typeof coverage.percent === "number" ? coverage.percent / 100 : 1;
    const securityBase = hasAuthzGap ? 0.5 : 0.9;
    const configBase = hasConfigGap ? 0.55 : 0.9;
    values.security = classify(securityBase * coverageScore);
    values.config = classify(configBase * coverageScore);
    values.metadata = classify(0.95);
    values.totals = totals;
    return values;
  }

  function buildSummaryText(counts, coverage, limitations) {
    const meaningful = counts.security + counts.config;
    const lines = [];
    if (meaningful === 0) {
      lines.push(
        "No security-relevant or configuration changes were detected between snapshots."
      );
      if (counts.metadata) {
        lines.push(
          `${counts.metadata} administrative metadata change${
            counts.metadata === 1 ? "" : "s"
          } detected.`
        );
      }
    } else {
      const securityPart = `${counts.security} security-impacting change${
        counts.security === 1 ? "" : "s"
      }`;
      const configPart = `${counts.config} configuration drift change${
        counts.config === 1 ? "" : "s"
      }`;
      lines.push(`Detected ${securityPart} and ${configPart}.`);
      if (counts.metadata) {
        lines.push(
          `${counts.metadata} administrative metadata change${
            counts.metadata === 1 ? "" : "s"
          } recorded.`
        );
      }
    }
    if (coverage?.percent !== null && coverage?.percent !== undefined) {
      if (coverage.percent < 100) {
        const limitationText = limitations.length
          ? ` Some checks could not be evaluated: ${limitations.slice(0, 4).join(", ")}.`
          : "";
        lines.push(`Coverage is incomplete (${coverage.percent}%).${limitationText}`);
      }
    } else if (limitations.length) {
      lines.push(`Coverage limitations detected: ${limitations.slice(0, 4).join(", ")}.`);
    }
    return lines.join(" ");
  }

  function buildTriage(diff, overrides) {
    const changes = flattenDiffChanges(diff);
    const groups = { security: [], config: [], metadata: [] };
    changes.forEach((item) => {
      const bucket = classifyChangePath(item.path || item.base || "", overrides);
      item.bucket = bucket;
      item.summary = describeChange(item);
      groups[bucket] = groups[bucket] || [];
      groups[bucket].push(item);
    });
    const counts = {
      security: groups.security.length,
      config: groups.config.length,
      metadata: groups.metadata.length,
    };
    const quality = extractQuality(diff);
    const coverage = computeCoverage(quality);
    const limitations = buildCoverageLimitations(quality);
    const confidenceByBucket = computeConfidenceByBucket(groups, limitations, coverage);
    const summaryText = buildSummaryText(counts, coverage, limitations);
    return {
      headline: "Snapshot Comparison Summary",
      counts,
      groups,
      coverage,
      limitations,
      confidenceByBucket,
      summaryText,
    };
  }

  return {
    classifyChangePath,
    flattenDiffChanges,
    buildCoverageLimitations,
    computeConfidenceByBucket,
    buildSummaryText,
    buildTriage,
  };
});
