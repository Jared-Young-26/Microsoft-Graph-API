(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminInvestigationSummary = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  function safeString(value) {
    if (value === null || value === undefined) return "";
    return String(value);
  }

  function isoToShort(iso) {
    const raw = safeString(iso).trim();
    if (!raw) return "";
    // Prefer a compact, human-readable time without locale dependencies.
    // Example: 2026-01-30T06:47:43Z -> 2026-01-30 06:47Z
    return raw.replace("T", " ").replace(/:\d\d(\.\d+)?(Z|[+-]\d\d:\d\d)?$/, "$1").trim();
  }

  function normalizeContext(context) {
    if (!context || typeof context !== "object" || Array.isArray(context)) return {};
    return context;
  }

  function normalizeEvents(events) {
    if (!Array.isArray(events)) return [];
    return events
      .filter((ev) => ev && typeof ev === "object")
      .map((ev) => {
        const data = ev.data && typeof ev.data === "object" && !Array.isArray(ev.data) ? ev.data : {};
        return {
          time: ev.time || data.captured_at || data.timestamp || null,
          kind: safeString(ev.kind || data.kind || "event") || "event",
          summary: safeString(ev.summary || ev.label || "").trim(),
          data,
        };
      })
      .filter((ev) => ev.time || ev.summary || ev.kind);
  }

  function summarizeScope(context) {
    const ctx = normalizeContext(context);
    const parts = [];
    const user = safeString(ctx.user_upn || ctx.user_id).trim();
    const device = safeString(ctx.device_name || ctx.managed_device_id).trim();
    const mailbox = safeString(ctx.mailbox_smtp).trim();
    const site = safeString(ctx.site_id).trim();
    const drive = safeString(ctx.drive_id).trim();
    if (user) parts.push(`user=${user}`);
    if (device) parts.push(`device=${device}`);
    if (mailbox) parts.push(`mailbox=${mailbox}`);
    if (site) parts.push(`site=${site}`);
    if (drive) parts.push(`drive=${drive}`);
    return parts.join(" · ");
  }

  function extractRunMeta(ev) {
    const data = ev.data || {};
    const normalized = data.normalized && typeof data.normalized === "object" ? data.normalized : {};
    const httpStatus = Number.isFinite(data.http_status) ? data.http_status : normalized.status_code;
    const errorClass = safeString(normalized.error_class || data.error_class || "").trim() || null;
    return {
      ok: data.ok === true,
      failed: data.ok === false,
      cancelled: data.cancelled === true,
      service: safeString(data.service || "").trim() || null,
      action: safeString(data.action || "").trim() || null,
      actionId: safeString(data.action_id || "").trim() || null,
      httpStatus: Number.isFinite(httpStatus) ? httpStatus : null,
      failureSource: safeString(data.failure_source || normalized.failure_source || "").trim() || null,
      failureOutcome: safeString(data.failure_outcome || normalized.failure_outcome || "").trim() || null,
      errorClass,
      error: safeString(data.error || normalized.error || "").trim() || null,
      hint: safeString(data.hint || normalized.hint || "").trim() || null,
    };
  }

  function bucketFailure(run) {
    const status = run.httpStatus;
    const cls = safeString(run.errorClass || "").toLowerCase();
    if (cls.includes("missing_permission") || status === 403) return { id: "missing_permission", label: "Missing permissions" };
    if (cls === "auth" || status === 401) return { id: "auth", label: "Authentication/config issue" };
    if (cls.includes("throttl") || status === 429) return { id: "throttling", label: "Rate limiting (429)" };
    if ([502, 503, 504].includes(status) || cls.includes("transient_upstream")) {
      return { id: "upstream_5xx", label: "Upstream transient 5xx (Graph/SPO/OD)" };
    }
    if (cls.includes("circuit") || run.failureOutcome === "circuit_open") return { id: "circuit_open", label: "Circuit breaker open" };
    if (cls.includes("db_schema")) return { id: "db_schema", label: "Local DB schema issue" };
    return { id: "unknown", label: "Unknown failure" };
  }

  function inferSuspectedCause(failedRuns) {
    const failures = Array.isArray(failedRuns) ? failedRuns : [];
    if (!failures.length) {
      return {
        cause: "No failures were captured in the investigation timeline.",
        confidence: "High",
        bucket: { id: "none", label: "No failures" },
      };
    }

    const buckets = {};
    failures.forEach((run) => {
      const bucket = bucketFailure(run);
      buckets[bucket.id] = buckets[bucket.id] || { bucket, count: 0, examples: [] };
      buckets[bucket.id].count += 1;
      if (buckets[bucket.id].examples.length < 2) buckets[bucket.id].examples.push(run);
    });

    const priority = ["missing_permission", "auth", "throttling", "upstream_5xx", "circuit_open", "db_schema", "unknown"];
    let top = null;
    for (const id of priority) {
      if (buckets[id]) {
        top = buckets[id];
        break;
      }
    }
    if (!top) top = { bucket: { id: "unknown", label: "Unknown" }, count: failures.length, examples: failures.slice(0, 2) };

    const confidence = top.count >= 3 ? "High" : top.count === 2 ? "Moderate" : "Low";
    const bucket = top.bucket;

    // Deterministic templates (no inference beyond observed patterns).
    let cause = bucket.label;
    if (bucket.id === "missing_permission") {
      cause = "One or more actions failed with HTTP 403 / missing permission. This is consistent with missing or unconsented app permissions.";
    } else if (bucket.id === "auth") {
      cause = "One or more actions failed with HTTP 401 / auth errors. This is consistent with invalid credentials, tenant/app configuration, or expired secrets.";
    } else if (bucket.id === "throttling") {
      cause = "Graph returned HTTP 429 (throttling) during investigation runs.";
    } else if (bucket.id === "upstream_5xx") {
      cause = "Graph returned transient 5xx (502/503/504) repeatedly. This is consistent with an upstream Microsoft service degradation (often SPO/OneDrive surfaces).";
    } else if (bucket.id === "circuit_open") {
      cause = "The dashboard circuit breaker opened to prevent retry amplification after repeated upstream failures.";
    } else if (bucket.id === "db_schema") {
      cause = "A local database schema error occurred (cache/migration mismatch).";
    } else if (bucket.id === "unknown") {
      cause = "Failures were captured, but they did not match a known classification pattern.";
    }

    return { cause, confidence, bucket };
  }

  function nextStepsForCause(bucketId) {
    if (bucketId === "missing_permission") {
      return [
        "Review Entra app permissions for the failing API surface and grant admin consent.",
        "Re-run the failed action and confirm the error clears.",
      ];
    }
    if (bucketId === "auth") {
      return [
        "Verify Tenant ID / Client ID / client secret or certificate configuration in Settings.",
        "Re-authenticate and re-run the failed action.",
      ];
    }
    if (bucketId === "throttling") {
      return [
        "Wait for the suggested retry window (Retry-After/backoff) and re-run.",
        "Reduce concurrency/fan-out and prefer cached inventory where available.",
      ];
    }
    if (bucketId === "upstream_5xx") {
      return [
        "Re-run after a short delay; transient 503 storms often clear.",
        "Use cached results where available (drive/site caches) to avoid amplification.",
        "If persistent, capture a support bundle (request-id + headers) for escalation.",
      ];
    }
    if (bucketId === "circuit_open") {
      return [
        "Wait for the circuit breaker cooldown, then retry the action.",
        "If a cache exists, use cached/stale results to proceed while upstream is degraded.",
      ];
    }
    if (bucketId === "db_schema") {
      return ["Restart the portal to run migrations, then re-run the affected action.", "Verify the cache status endpoints return counts > 0 after warmup."];
    }
    return ["Add more evidence: capture a snapshot and attach the last output to the timeline.", "Run a control diagnostic to separate upstream failures from dashboard issues."];
  }

  function describeEvent(ev) {
    const stamp = isoToShort(ev.time);
    if (ev.kind === "action_run") {
      const run = extractRunMeta(ev);
      const label = safeString(ev.summary || run.actionId || "Action run").trim();
      const status = run.cancelled ? "cancelled" : run.failed ? "failed" : run.ok ? "ok" : "unknown";
      const bits = [];
      if (run.httpStatus) bits.push(`HTTP ${run.httpStatus}`);
      if (run.errorClass) bits.push(run.errorClass);
      if (run.failureOutcome && !bits.includes(run.failureOutcome)) bits.push(run.failureOutcome);
      const suffix = bits.length ? ` (${bits.join(", ")})` : "";
      return `- ${stamp} · ${status.toUpperCase()} · ${label}${suffix}`;
    }
    if (ev.kind === "snapshot") {
      const snap = ev.data || {};
      const kind = safeString(snap.subject_kind || "").trim();
      const profile = safeString(snap.profile || "").trim();
      const id = safeString(snap.snapshot_id || "").trim();
      const extra = [kind, profile].filter(Boolean).join(" · ");
      return `- ${stamp} · SNAPSHOT · ${extra}${id ? ` (id=${id})` : ""}`;
    }
    if (ev.kind === "evidence") {
      const items = Array.isArray(ev.data?.evidence) ? ev.data.evidence.length : null;
      return `- ${stamp} · EVIDENCE · ${ev.summary || "Evidence stored"}${items !== null ? ` (${items})` : ""}`;
    }
    if (ev.kind === "note") {
      const note = safeString(ev.data?.note || "").trim();
      const preview = note ? (note.length > 80 ? note.slice(0, 77) + "..." : note) : "";
      return `- ${stamp} · NOTE · ${preview || ev.summary || "Note"}`;
    }
    return `- ${stamp} · ${safeString(ev.kind).toUpperCase()} · ${safeString(ev.summary || "").trim()}`;
  }

  function buildKeyEvents(events) {
    const timeline = normalizeEvents(events);
    if (!timeline.length) return [];
    const runs = timeline.filter((ev) => ev.kind === "action_run");
    const failedRuns = runs.filter((ev) => extractRunMeta(ev).failed);
    const snapshots = timeline.filter((ev) => ev.kind === "snapshot");
    const evidence = timeline.filter((ev) => ev.kind === "evidence");
    const notes = timeline.filter((ev) => ev.kind === "note");

    const selected = new Set();
    function pick(list, limit) {
      for (const ev of list) {
        if (selected.size >= 8) break;
        if (selected.has(ev)) continue;
        selected.add(ev);
        if (selected.size >= limit) break;
      }
    }

    // Prioritize failed runs, then snapshots/evidence, then notes/success.
    pick(failedRuns.slice(0, 4), 4);
    pick(snapshots.slice(0, 2), 6);
    pick(evidence.slice(0, 1), 7);
    pick(notes.slice(0, 1), 8);

    // Ensure we show at least something: first and last events.
    if (!selected.size) {
      selected.add(timeline[0]);
      if (timeline.length > 1) selected.add(timeline[timeline.length - 1]);
    }

    const out = Array.from(selected);
    out.sort((a, b) => safeString(a.time).localeCompare(safeString(b.time)));
    return out.map(describeEvent);
  }

  function buildActionsTaken(events) {
    const timeline = normalizeEvents(events);
    const runs = timeline.filter((ev) => ev.kind === "action_run");
    const okRuns = runs.filter((ev) => extractRunMeta(ev).ok);
    const failedRuns = runs.filter((ev) => extractRunMeta(ev).failed);
    const snapshots = timeline.filter((ev) => ev.kind === "snapshot");
    const evidence = timeline.filter((ev) => ev.kind === "evidence");
    const uniqueActions = new Set(okRuns.map((ev) => extractRunMeta(ev).actionId || ev.summary).filter(Boolean));

    const lines = [];
    if (uniqueActions.size) {
      lines.push(`- Successful runs: ${uniqueActions.size}`);
    } else if (okRuns.length) {
      lines.push(`- Successful runs: ${okRuns.length}`);
    } else {
      lines.push(`- Successful runs: 0`);
    }
    lines.push(`- Failed runs: ${failedRuns.length}`);
    lines.push(`- Snapshots captured: ${snapshots.length}`);
    lines.push(`- Evidence artifacts stored: ${evidence.length}`);
    return lines;
  }

  function buildSummary(events, context, options) {
    const timeline = normalizeEvents(events);
    const ctx = normalizeContext(context);
    const opts = options && typeof options === "object" ? options : {};
    const title = safeString(opts.title || "").trim() || "Investigation summary";
    const scope = summarizeScope(ctx);
    const start = timeline[0]?.time || null;
    const end = timeline.length ? timeline[timeline.length - 1].time : null;
    const timeframe = start && end ? `${isoToShort(start)} → ${isoToShort(end)}` : start ? isoToShort(start) : "";

    const runs = timeline.filter((ev) => ev.kind === "action_run");
    const failedRuns = runs.map(extractRunMeta).filter((run) => run.failed);
    const suspected = inferSuspectedCause(failedRuns);
    const nextSteps = nextStepsForCause(suspected.bucket.id);
    const keyEvents = buildKeyEvents(timeline);
    const actionsTaken = buildActionsTaken(timeline);

    const lines = [];
    lines.push(`# ${title}`);
    if (scope) lines.push(`\n**Scope:** ${scope}`);
    if (timeframe) lines.push(`\n**Timeframe:** ${timeframe}`);
    lines.push(`\n## Key events`);
    if (keyEvents.length) lines.push(keyEvents.join("\n"));
    else lines.push("- No timeline events captured yet.");
    lines.push(`\n## Suspected cause`);
    lines.push(`- ${suspected.cause}`);
    lines.push(`- Confidence: ${suspected.confidence}`);
    lines.push(`\n## Actions taken`);
    lines.push(actionsTaken.join("\n"));
    lines.push(`\n## Next steps`);
    nextSteps.forEach((step) => lines.push(`- ${step}`));
    lines.push(""); // trailing newline
    return lines.join("\n");
  }

  return {
    buildSummary,
  };
});

