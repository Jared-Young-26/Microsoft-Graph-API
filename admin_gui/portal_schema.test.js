const assert = require("assert");
const schema = require("./portal_schema");

const errors = schema.validatePortalSchema(schema);
assert.deepStrictEqual(errors, [], `Schema validation failed: ${errors.join("; ")}`);

assert.ok(schema.sections.dashboard, "dashboard section missing");
assert.strictEqual(schema.sections.dashboard.panel, "dashboard");
assert.strictEqual(schema.sections.dashboard.mode, "observe");

assert.ok(schema.sections.incidents, "incidents section missing");
assert.strictEqual(schema.sections.incidents.panel, "reports");
assert.strictEqual(schema.sections.incidents.mode, "observe");
assert.strictEqual(schema.sections.incidents.sharedPanelLabel, "Reports");
assert.ok(
  schema.sections.incidents.sharedPanelCopy.includes("focuses the incident workspace"),
  "incidents shared context should explain the focused reports view"
);

assert.ok(schema.sections.quickactions, "quickactions section missing");
assert.strictEqual(schema.sections.quickactions.panel, "dashboard");
assert.strictEqual(schema.sections.quickactions.mode, "act");
assert.strictEqual(schema.sections.quickactions.scrollTarget, "quick-actions-card");

assert.ok(schema.sections.auditlog, "auditlog section missing");
assert.strictEqual(schema.sections.auditlog.panel, "settings");
assert.strictEqual(schema.sections.auditlog.mode, "observe");

assert.ok(schema.sections.healthcheck, "healthcheck section missing");
assert.strictEqual(schema.sections.healthcheck.panel, "settings");
assert.strictEqual(schema.sections.healthcheck.mode, "configure");
assert.strictEqual(schema.sections.healthcheck.scrollTarget, "health-card");

assert.ok(schema.sections.baselines, "baselines section missing");
assert.strictEqual(schema.sections.baselines.mode, "analyze");
assert.strictEqual(schema.sections.baselines.subtitle, "Golden baselines and drift comparison");

assert.ok(schema.getSectionMeta("tools"), "getSectionMeta should resolve tools");
assert.strictEqual(schema.getSectionMeta("tools").panel, "controlplane");
assert.strictEqual(schema.getModeMeta("learn").label, "Learn");

const toolsContext = schema.getSharedPanelContext("tools");
assert.deepStrictEqual(toolsContext, {
  label: "Control Plane",
  copy: "This section focuses the tool catalog inside the shared Control Plane surface.",
});

console.log("portal schema tests passed");
