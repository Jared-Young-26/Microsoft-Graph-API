const assert = require("assert");
const summary = require("./investigation_summary");

function makeRun({ time, ok, http_status, failure_source, failure_outcome, error_class, service, action }) {
  return {
    time,
    kind: "action_run",
    summary: `${ok ? "Ran" : "Failed"}: ${service}.${action}`,
    data: {
      captured_at: time,
      service,
      action,
      action_id: `${service}.${action}`,
      ok,
      http_status,
      failure_source,
      failure_outcome,
      normalized: {
        ok,
        status_code: http_status,
        error_class,
        failure_source,
        failure_outcome,
      },
    },
  };
}

// Empty timeline produces a readable scaffold.
(() => {
  const text = summary.buildSummary([], {}, { title: "Test Investigation" });
  assert.ok(text.includes("# Test Investigation"));
  assert.ok(text.includes("## Key events"));
  assert.ok(text.includes("No timeline events"));
})();

// Upstream 503 storms are classified as upstream 5xx with actionable next steps.
(() => {
  const events = [
    makeRun({
      time: "2026-01-30T06:47:43Z",
      ok: false,
      http_status: 503,
      failure_source: "graph_upstream",
      failure_outcome: "retry_exhausted",
      error_class: "transient_upstream_persistent",
      service: "onedrive",
      action: "get_user_drive_id",
    }),
    makeRun({
      time: "2026-01-30T06:48:10Z",
      ok: false,
      http_status: 503,
      failure_source: "graph_upstream",
      failure_outcome: "retry_exhausted",
      error_class: "transient_upstream_persistent",
      service: "onedrive",
      action: "get_user_drive_id",
    }),
  ];
  const text = summary.buildSummary(events, { user_upn: "user@contoso.com" }, { title: "503 storm" });
  assert.ok(text.includes("Scope"));
  assert.ok(text.toLowerCase().includes("transient 5xx"));
  assert.ok(text.includes("## Next steps"));
})();

// Permissions failures are classified as missing permissions.
(() => {
  const events = [
    makeRun({
      time: "2026-01-30T07:10:00Z",
      ok: false,
      http_status: 403,
      failure_source: "graph_upstream",
      failure_outcome: "failed",
      error_class: "missing_permission",
      service: "entra",
      action: "list_users",
    }),
  ];
  const text = summary.buildSummary(events, {}, { title: "403 test" });
  assert.ok(text.toLowerCase().includes("missing"));
  assert.ok(text.toLowerCase().includes("permission"));
})();

console.log("investigation summary tests passed");

