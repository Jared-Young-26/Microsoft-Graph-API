const assert = require("assert");

const { suggest } = require("./next_steps.js");

function hasSuggestion(list, service, action) {
  return (list || []).some((item) => item && item.service === service && item.action === action);
}

(() => {
  const snapshot = {
    snapshot_id: "snap1",
    lens: {
      authz: {
        signins: { summary: { total: 10, success: 6, failure: 4, conditional_access_failures: 3 } },
        policy: { ca_blocks: [{ id: "policy1" }] },
      },
    },
  };
  const out = suggest(snapshot);
  assert.ok(hasSuggestion(out.suggestions, "reports", "sign_in_summary"));
  assert.ok(hasSuggestion(out.suggestions, "reports", "conditional_access_summary"));
  assert.ok(hasSuggestion(out.suggestions, "reports", "device_compliance"));
})();

(() => {
  const report = {
    generated_at: "2026-02-01T00:00:00Z",
    count: 5,
    summary: {
      total: 5,
      success: 0,
      failure: 5,
      conditional_access: { failure: 5 },
    },
    signIns: [],
  };
  const out = suggest(report);
  assert.ok(hasSuggestion(out.suggestions, "reports", "conditional_access_summary"));
  assert.ok(hasSuggestion(out.suggestions, "reports", "device_compliance"));
})();

(() => {
  const actionRun = {
    kind: "action_run",
    data: {
      output: {
        generated_at: "2026-02-01T00:00:00Z",
        count: 1,
        summary: { failure: 1, conditional_access: { failure: 1 } },
        signIns: [],
      },
    },
  };
  const out = suggest(actionRun);
  assert.ok(hasSuggestion(out.suggestions, "reports", "conditional_access_summary"));
})();

console.log("next steps tests passed");

