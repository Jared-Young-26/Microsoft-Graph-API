let jsdom = null;
try {
  jsdom = require("jsdom");
} catch (err) {
  console.log("jsdom not installed; skipping json inspector tests.");
  process.exit(0);
}

const { JSDOM } = jsdom;
const fs = require("fs");
const path = require("path");

const html = `<html><body></body></html>`;
const dom = new JSDOM(html, { runScripts: "dangerously" });
global.window = dom.window;
global.document = dom.window.document;

const appJs = fs.readFileSync(path.join(__dirname, "json_inspector.js"), "utf8");
dom.window.eval(appJs);

const { renderJsonInspector, runModalSearch } = dom.window.GraphAdminJsonInspector;

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || "Assertion failed");
  }
}

// Deep object rendering
(() => {
  const data = { a: { b: { c: { d: { e: 1 } } } } };
  const inspector = renderJsonInspector(data, { modal: document.body });
  assert(inspector.container.querySelectorAll(".json-node").length > 0, "Missing json nodes");
})();

// Large array virtualization (load more)
(() => {
  const data = { items: Array.from({ length: 250 }).map((_, idx) => ({ id: idx })) };
  const inspector = renderJsonInspector(data, { modal: document.body, maxItems: 100, step: 50 });
  const more = inspector.container.querySelector(".json-more");
  assert(more, "Missing load more row for large array");
})();

// Search highlighting
(() => {
  const data = { servicePlans: [{ servicePlanName: "SPO" }] };
  const inspector = renderJsonInspector(data, { modal: document.body });
  document.body.appendChild(inspector.container);
  const modal = document.createElement("div");
  modal._inspectorState = inspector.state;
  modal.appendChild(inspector.container);
  runModalSearch(modal, "serviceplanname");
  const matches = modal.querySelectorAll(".match");
  assert(matches.length > 0, "Search did not highlight matches");
})();

console.log("json inspector tests passed");
