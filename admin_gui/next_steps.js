(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminNextSteps = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  function coerceNumber(value) {
    if (value === null || value === undefined) return 0;
    const num = Number(value);
    return Number.isFinite(num) ? num : 0;
  }

  function addUnique(list, item, seen) {
    if (!item || typeof item !== "object") return;
    const key = `${item.service || ""}.${item.action || ""}`;
    if (!key || key === ".") return;
    if (seen.has(key)) return;
    seen.add(key);
    list.push(item);
  }

  function suggestFromSnapshot(snapshot) {
    const suggestions = [];
    const seen = new Set();
    const lens = snapshot && typeof snapshot === "object" ? snapshot.lens || {} : {};
    const authz = lens.authz || {};
    const signins = authz.signins || {};
    const summary = signins.summary || {};
    const failures = coerceNumber(summary.failure || summary.failures);
    const caFailures = coerceNumber(summary.conditional_access_failures);
    const caBlocks = (authz.policy || {}).ca_blocks || [];
    const hasCaBlocks = Array.isArray(caBlocks) && caBlocks.length > 0;

    if (failures > 0) {
      addUnique(
        suggestions,
        {
          service: "reports",
          action: "sign_in_summary",
          reason: "Sign-in failures were detected. Run the sign-in summary report for expanded details and filtering.",
        },
        seen
      );
      if (caFailures > 0 || hasCaBlocks) {
        addUnique(
          suggestions,
          {
            service: "reports",
            action: "conditional_access_summary",
            reason: "Conditional Access failures were detected. Review CA policy configuration and targeting.",
          },
          seen
        );
        addUnique(
          suggestions,
          {
            service: "reports",
            action: "device_compliance",
            reason: "Conditional Access often depends on device compliance. Check device compliance state for the affected user.",
          },
          seen
        );
      }
    }
    return suggestions;
  }

  function suggestFromSignInReport(report) {
    const suggestions = [];
    const seen = new Set();
    const summary = report && typeof report === "object" ? report.summary || {} : {};
    const failures = coerceNumber(summary.failure);
    const ca = summary.conditional_access || {};
    const caFailures = coerceNumber(ca.failure || ca.Failure);
    if (failures > 0) {
      if (caFailures > 0) {
        addUnique(
          suggestions,
          {
            service: "reports",
            action: "conditional_access_summary",
            reason: "Conditional Access failures were observed in sign-ins. Review CA policy state and recent changes.",
          },
          seen
        );
        addUnique(
          suggestions,
          {
            service: "reports",
            action: "device_compliance",
            reason: "Device compliance often drives CA outcomes. Review managed device compliance for the affected user.",
          },
          seen
        );
      }
    }
    return suggestions;
  }

  function isSnapshot(payload) {
    if (!payload || typeof payload !== "object") return false;
    if (payload.lens && payload.snapshot_id) return true;
    const schema = payload.schema || payload.schema_id || "";
    return typeof schema === "string" && schema.startsWith("gas.snapshot.");
  }

  function isSignInReport(payload) {
    if (!payload || typeof payload !== "object") return false;
    if (!payload.summary || typeof payload.summary !== "object") return false;
    return Array.isArray(payload.signIns);
  }

  function suggest(payload) {
    if (!payload || typeof payload !== "object") return { suggestions: [] };
    // Timeline event wrapper: recurse into stored output when present.
    if (payload.kind === "action_run" && payload.data && payload.data.output) {
      return suggest(payload.data.output);
    }
    if (isSnapshot(payload)) {
      return { suggestions: suggestFromSnapshot(payload) };
    }
    if (isSignInReport(payload)) {
      return { suggestions: suggestFromSignInReport(payload) };
    }
    return { suggestions: [] };
  }

  return {
    suggest,
    _internal: {
      suggestFromSnapshot,
      suggestFromSignInReport,
    },
  };
});

