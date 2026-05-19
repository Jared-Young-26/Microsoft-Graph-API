const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const schema = require("./portal_schema.js");
const serviceShells = require("./service_shells.js");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const dom = new JSDOM(html);
const { document } = dom.window;

const EXPECTED_SCRIPT_ORDER = [
  "triage.js",
  "investigation_summary.js",
  "next_steps.js",
  "portal_schema.js",
  "service_shells.js",
  "persistence_security.js",
  "app.js",
];

const REQUIRED_TEMPLATE_IDS = [
  "service-shell-template",
  "service-shell-chip-template",
  "service-shell-note-template",
  "service-shell-info-item-template",
];

const REQUIRED_SERVICE_SHELL_TEMPLATE_SELECTORS = [
  '[data-shell-text="toolkit-title"]',
  '[data-shell-text="toolkit-subtitle"]',
  '[data-shell-text="runner-title"]',
  '[data-shell-text="runner-subtitle"]',
  '[data-shell-text="output-title"]',
  '[data-shell-text="output-subtitle"]',
  '[data-shell-slot="toolkit-body"]',
  "[data-shell-runner]",
  "[data-shell-action-select]",
  "[data-shell-runner-fields]",
  "[data-shell-runner-reset]",
  "[data-shell-runner-run]",
  "[data-shell-info]",
  "[data-shell-info-summary]",
  "[data-shell-info-list]",
  "[data-shell-output]",
  "[data-shell-clear]",
];

const scriptSources = Array.from(document.querySelectorAll("script[src]")).map((node) => node.getAttribute("src"));
assert.deepEqual(scriptSources, EXPECTED_SCRIPT_ORDER, "index.html script order drifted");

REQUIRED_TEMPLATE_IDS.forEach((id) => {
  const template = document.getElementById(id);
  assert.ok(template, `Missing boot template #${id}`);
  assert.equal(template.tagName, "TEMPLATE", `#${id} must stay a template element`);
});

const serviceShellTemplate = document.getElementById("service-shell-template");
REQUIRED_SERVICE_SHELL_TEMPLATE_SELECTORS.forEach((selector) => {
  assert.ok(
    serviceShellTemplate.content.querySelector(selector),
    `service-shell-template is missing required selector ${selector}`
  );
});

const domServices = Array.from(document.querySelectorAll("[data-service-shell]")).map((node) =>
  node.getAttribute("data-service-shell")
);
assert.deepEqual(
  [...new Set(domServices)].sort(),
  [...serviceShells.TARGET_SERVICES].sort(),
  "data-service-shell mounts drifted from GraphAdminServiceShells.TARGET_SERVICES"
);
assert.equal(domServices.length, serviceShells.TARGET_SERVICES.length, "duplicate data-service-shell mounts detected");
assert.equal(document.querySelector('[data-service-shell="remote_workflows"]'), null);
serviceShells.renderServiceShells(document);
assert.deepEqual(
  serviceShells.validateRenderedServiceShells(document, serviceShells.SERVICE_SHELLS),
  [],
  "Rendered service shells drifted from the index.html boot contract"
);

const panelRoots = new Set(Object.values(schema.sections).map((meta) => meta.panel));
const navSections = Array.from(document.querySelectorAll(".nav-link[data-section]")).map((node) =>
  node.getAttribute("data-section")
);

navSections.forEach((sectionKey) => {
  assert.ok(schema.sections[sectionKey], `Nav link ${sectionKey} is missing from portal_schema.js`);
});

Object.entries(schema.sections).forEach(([sectionKey, meta]) => {
  const navLink = document.querySelector(`.nav-link[data-section="${sectionKey}"]`);
  const isSharedPanelRoot = sectionKey === meta.panel && panelRoots.has(sectionKey) && !navLink;
  if (!isSharedPanelRoot) {
    assert.ok(navLink, `Missing nav link for ${sectionKey}`);
  }
  assert.ok(document.querySelector(`[data-panel="${meta.panel}"]`), `Missing DOM panel for ${sectionKey} -> ${meta.panel}`);
  if (meta.scrollTarget) {
    assert.ok(document.getElementById(meta.scrollTarget), `Missing scroll target #${meta.scrollTarget} for ${sectionKey}`);
  }
});

serviceShells.TARGET_SERVICES.forEach((service) => {
  const section = schema.sections[service];
  assert.ok(section, `Missing schema section for service shell ${service}`);
  assert.equal(section.panel, service, `Service shell ${service} must keep a same-name panel`);
  assert.ok(document.querySelector(`.nav-link[data-section="${service}"]`), `Missing nav link for service ${service}`);
});

console.log("boot contract tests passed");
