const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const shells = require("./service_shells.js");

const EXPECTED_SERVICES = [
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

assert.deepEqual(shells.TARGET_SERVICES, EXPECTED_SERVICES);
assert.ok(!shells.TARGET_SERVICES.includes("remote_workflows"));

const validationErrors = shells.validateServiceShellRegistry(shells.SERVICE_SHELLS);
assert.deepEqual(validationErrors, []);

const validRoot = {
  querySelectorAll(selector) {
    if (selector.startsWith("[data-service-shell=")) return [];

    let match = selector.match(/\.runner\[data-service="([^"]+)"\]/);
    if (match) return EXPECTED_SERVICES.includes(match[1]) ? [{}] : [];

    match = selector.match(/\.action-select\[data-service="([^"]+)"\]/);
    if (match) return EXPECTED_SERVICES.includes(match[1]) ? [{}] : [];

    match = selector.match(/\.runner-fields\[data-service="([^"]+)"\]/);
    if (match) return EXPECTED_SERVICES.includes(match[1]) ? [{}] : [];

    match = selector.match(/\.output\[data-output="([^"]+)"\]/);
    if (match) return EXPECTED_SERVICES.includes(match[1]) ? [{}] : [];

    match = selector.match(/\.output-card\[data-panel="([^"]+)"\]\[data-workspace-block="([^"]+)"\]/);
    if (match) {
      const [service, blockId] = match.slice(1);
      return blockId === `${service}.output` && EXPECTED_SERVICES.includes(service) ? [{}] : [];
    }

    match = selector.match(/\.card\[data-panel="([^"]+)"\]\[data-workspace-block="([^"]+)"\]/);
    if (match) {
      const [service, blockId] = match.slice(1);
      const validBlocks = new Set([`${service}.toolkit`, `${service}.runner`, `${service}.output`]);
      return validBlocks.has(blockId) && EXPECTED_SERVICES.includes(service) ? [{}] : [];
    }

    match = selector.match(/\.output-card\[data-panel="([^"]+)"\] \.clear-output\[data-output-target="([^"]+)"\]/);
    if (match) {
      const [panel, target] = match.slice(1);
      return panel === target && EXPECTED_SERVICES.includes(panel) ? [{}] : [];
    }

    match = selector.match(/\.output-card\[data-panel="([^"]+)"\](?!\[)/);
    if (match) return EXPECTED_SERVICES.includes(match[1]) ? [{}] : [];

    return [];
  },
};

assert.deepEqual(shells.validateRenderedServiceShells(validRoot, shells.SERVICE_SHELLS), []);

const invalidRoot = {
  querySelectorAll() {
    return [];
  },
};

const renderedErrors = shells.validateRenderedServiceShells(invalidRoot, shells.SERVICE_SHELLS);
assert.ok(renderedErrors.some((entry) => entry.includes("exchange must render one runner")));

const missingWorkspaceRoot = {
  querySelectorAll(selector) {
    if (selector === '.output-card[data-panel="baselines"][data-workspace-block="baselines.output"]') return [];
    return validRoot.querySelectorAll(selector);
  },
};

const workspaceErrors = shells.validateRenderedServiceShells(missingWorkspaceRoot, shells.SERVICE_SHELLS);
assert.ok(workspaceErrors.includes("Service shell baselines is missing output workspace block."));

EXPECTED_SERVICES.forEach((service) => {
  const shell = shells.getServiceShell(service);
  assert.ok(shell, `${service} shell should exist`);
  assert.equal(shell.service, service);
  assert.ok(Array.isArray(shell.toolkit.chips));
  assert.ok(shell.toolkit.chips.length > 0);
  assert.deepEqual(shells.getWorkspaceBlockIds(service), {
    toolkit: `${service}.toolkit`,
    runner: `${service}.runner`,
    output: `${service}.output`,
  });
});

assert.equal(shells.getServiceShell("remote_workflows"), null);
assert.equal(shells.legacyWorkspaceBlocks["exchange.exchange-toolkit"], "exchange.toolkit");
assert.equal(shells.legacyWorkspaceBlocks["defender.defender-for-cloud"], "defender.toolkit");
assert.equal(shells.legacyWorkspaceBlocks["powerplatform.power-platform"], "powerplatform.toolkit");
assert.equal(shells.legacyWorkspaceBlocks["purview.purview-output"], "purview.output");
assert.equal(shells.legacyWorkspaceBlocks["localad.local-active-directory"], "localad.toolkit");
assert.equal(shells.legacyWorkspaceBlocks["fileserver.file-server-output"], "fileserver.output");
assert.equal(shells.legacyWorkspaceBlocks["baselines.baselines-toolkit"], "baselines.toolkit");
assert.equal(shells.legacyWorkspaceBlocks["eventlogs.event-logs-output"], "eventlogs.output");
assert.equal(shells.legacyWorkspaceBlocks["registry.registry-runner"], "registry.runner");

assert.equal(shells.getServiceShell("baselines").toolkit.subtitle, "Golden snapshots and comparisons");
assert.equal(shells.getServiceShell("baselines").runner.subtitle, "Set and compare golden baselines");

assert.deepEqual(
  shells.parseRunnerInfoItemMarkup("<strong>Logs &amp; services</strong>: use <code>GET /users/{id}</code> &rarr; confirm."),
  [
    { type: "strong", value: "Logs & services" },
    { type: "text", value: ": use " },
    { type: "code", value: "GET /users/{id}" },
    { type: "text", value: " → confirm." },
  ],
);

assert.deepEqual(shells.parseRunnerInfoItemMarkup("<img src=x onerror=1><strong>Safe</strong>"), [
  { type: "text", value: "<img src=x onerror=1>" },
  { type: "strong", value: "Safe" },
]);

const serviceShellSource = fs.readFileSync(path.join(__dirname, "service_shells.js"), "utf8");
assert.equal(serviceShellSource.includes("innerHTML"), false);

console.log("service shell tests passed");
