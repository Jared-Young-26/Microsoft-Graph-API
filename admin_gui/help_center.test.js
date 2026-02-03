const fs = require("fs");
const path = require("path");
const { parseMarkdown } = require("./help_parser");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || "Assertion failed");
  }
}

const manifestPath = path.join(__dirname, "docs", "help", "help_manifest.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

assert(Array.isArray(manifest.pages) && manifest.pages.length > 0, "Help manifest is empty");

let searchHits = 0;

manifest.pages.forEach((page) => {
  const pagePath = path.join(__dirname, page.path);
  assert(fs.existsSync(pagePath), `Missing help doc: ${page.path}`);
  const md = fs.readFileSync(pagePath, "utf8");
  const parsed = parseMarkdown(md);
  assert(parsed.html.includes("<h"), `Doc missing heading: ${page.path}`);
  assert(Array.isArray(parsed.headings), `Doc headings not parsed: ${page.path}`);
  if (md.toLowerCase().includes("graph")) searchHits += 1;
});

assert(searchHits > 0, "Search should find 'graph' in help docs");

console.log("help center tests passed");
