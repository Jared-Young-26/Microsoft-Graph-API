const assert = require("assert");
const triage = require("./triage");

function makeDiff(sections, quality) {
  return { sections, quality };
}

// metadata-only diff
(() => {
  const diff = makeDiff(
    {
      change: {
        added: [],
        removed: [],
        changed: [{ path: "change.previous_snapshot_id", before: "a", after: "b" }],
      },
    },
    { a: { completeness: 1 }, b: { completeness: 1 } }
  );
  const result = triage.buildTriage(diff, {});
  assert.strictEqual(result.counts.security, 0);
  assert.strictEqual(result.counts.config, 0);
  assert.strictEqual(result.counts.metadata, 1);
  assert.ok(result.summaryText.includes("No security-relevant"));
  assert.ok(result.confidenceByBucket.security);
})();

// authz change diff
(() => {
  const diff = makeDiff(
    {
      authz: {
        groups: { added: [], removed: [], changed: [{ key: "group-1", before: {}, after: {} }] },
        licenses: { added: [], removed: [], changed: [] },
        signins: { added: [], removed: [], changed: [] },
      },
    },
    { a: { completeness: 1 }, b: { completeness: 1 } }
  );
  const result = triage.buildTriage(diff, {});
  assert.strictEqual(result.counts.security, 1);
})();

// config drift diff
(() => {
  const diff = makeDiff(
    {
      config: {
        firewall: { added: [], removed: [], changed: [{ path: "config.firewall.enabled", before: true, after: false }] },
      },
    },
    { a: { completeness: 1 }, b: { completeness: 1 } }
  );
  const result = triage.buildTriage(diff, {});
  assert.strictEqual(result.counts.config, 1);
})();

// warnings-only coverage limitations
(() => {
  const diff = makeDiff(
    {},
    {
      a: {
        completeness: 0.75,
        warnings: [{ probe: "authz.user_groups_core", message: "Graph request handler not configured" }],
      },
      b: { completeness: 0.8 },
    }
  );
  const limitations = triage.buildCoverageLimitations(diff.quality);
  assert.ok(limitations.some((item) => item.includes("Group membership not evaluated")));
  assert.ok(limitations.some((item) => item.includes("Graph handler not configured")));
})();

console.log("triage tests passed");
