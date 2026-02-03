(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminHelpParser = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function slugifyHeading(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)+/g, "");
  }

  function parseMarkdown(md) {
    const lines = String(md || "").replace(/\r\n/g, "\n").split("\n");
    const html = [];
    const headings = [];
    const idCounts = new Map();
    let inCode = false;
    let codeLang = "";
    let codeLines = [];
    let listType = null;
    let listBuffer = [];
    let tableBuffer = null;
    let callout = null;

    const flushList = () => {
      if (!listType || !listBuffer.length) return;
      const items = listBuffer.map((item) => `<li>${item}</li>`).join("");
      html.push(`<${listType}>${items}</${listType}>`);
      listType = null;
      listBuffer = [];
    };

    const flushTable = () => {
      if (!tableBuffer || tableBuffer.length < 2) {
        tableBuffer = null;
        return;
      }
      const header = tableBuffer[0];
      const rows = tableBuffer.slice(2);
      const headerCells = header.map((cell) => `<th>${cell}</th>`).join("");
      const bodyRows = rows
        .map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`)
        .join("");
      html.push(`<table><thead><tr>${headerCells}</tr></thead><tbody>${bodyRows}</tbody></table>`);
      tableBuffer = null;
    };

    const flushCallout = () => {
      if (!callout) return;
      html.push(
        `<div class="doc-callout ${callout.type}"><div class="doc-callout-title">${callout.title}</div>${callout.body}</div>`
      );
      callout = null;
    };

    const formatInline = (text) => {
      let value = escapeHtml(text);
      value = value.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      value = value.replace(/\*(.+?)\*/g, "<em>$1</em>");
      value = value.replace(/`([^`]+)`/g, "<code>$1</code>");
      value = value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
      value = value.replace(/\[\[BADGE:([a-z]+)\]\]/gi, (_, kind) => {
        const key = kind.toLowerCase();
        const label = key === "powershell" ? "PowerShell" : key === "ssh" ? "SSH" : key === "local" ? "Local" : "Graph";
        return `<span class="doc-badge ${key}">${label}</span>`;
      });
      value = value.replace(/\[\[RISK:([a-z]+)\]\]/gi, (_, level) => {
        const label = level === "dangerous" ? "Dangerous" : level === "caution" ? "Caution" : "Safe";
        return `<span class="doc-badge risk ${level.toLowerCase()}">${label}</span>`;
      });
      return value;
    };

    const placeholder = (text) => {
      return text
        .replace(/<Badge\s+kind="([^"]+)"\s*\/>/gi, (_, kind) => `[[BADGE:${kind}]]`)
        .replace(/<RiskBadge\s+level="([^"]+)"\s*\/>/gi, (_, level) => `[[RISK:${level}]]`);
    };

    lines.forEach((rawLine, idx) => {
      const line = placeholder(rawLine);
      if (line.startsWith("```")) {
        if (inCode) {
          html.push(
            `<pre><code class="language-${codeLang}">${escapeHtml(codeLines.join("\n"))}</code></pre>`
          );
          inCode = false;
          codeLang = "";
          codeLines = [];
        } else {
          flushList();
          flushTable();
          flushCallout();
          inCode = true;
          codeLang = line.replace(/```/, "").trim();
        }
        return;
      }
      if (inCode) {
        codeLines.push(line);
        return;
      }

      if (tableBuffer && line.match(/^\s*\|?\s*[-:| ]+\|?\s*$/)) {
        return;
      }

      if (line.startsWith("> [!")) {
        flushList();
        flushTable();
        const match = line.match(/> \[!([A-Z]+)\]\s*(.*)/);
        const type = match ? match[1].toLowerCase() : "note";
        const title = type === "warning" ? "Warning" : type === "danger" ? "Danger" : "Note";
        callout = {
          type,
          title,
          body: match && match[2] ? `<p>${formatInline(match[2])}</p>` : "",
        };
        return;
      }
      if (line.startsWith("> ") && callout) {
        callout.body += `<p>${formatInline(line.replace(/^> /, ""))}</p>`;
        return;
      } else if (callout) {
        flushCallout();
      }

      if (!line.trim()) {
        flushList();
        flushTable();
        return;
      }

      if (line.match(/^\s*[-*]\s+/)) {
        const item = formatInline(line.replace(/^\s*[-*]\s+/, ""));
        if (listType !== "ul") {
          flushList();
          listType = "ul";
        }
        listBuffer.push(item);
        return;
      }
      if (line.match(/^\s*\d+\.\s+/)) {
        const item = formatInline(line.replace(/^\s*\d+\.\s+/, ""));
        if (listType !== "ol") {
          flushList();
          listType = "ol";
        }
        listBuffer.push(item);
        return;
      }
      flushList();

      if (line.includes("|") && lines[idx + 1] && lines[idx + 1].match(/^\s*\|?\s*[-:| ]+\|?\s*$/)) {
        const splitRow = (row) =>
          row
            .trim()
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((cell) => formatInline(cell.trim()));
        tableBuffer = [splitRow(line), splitRow(lines[idx + 1])];
        return;
      }
      if (tableBuffer) {
        if (line.includes("|")) {
          const row = line
            .trim()
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((cell) => formatInline(cell.trim()));
          tableBuffer.push(row);
          return;
        }
        flushTable();
      }

      const headingMatch = line.match(/^(#{1,3})\s+(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2].trim();
        const base = slugifyHeading(text);
        const count = (idCounts.get(base) || 0) + 1;
        idCounts.set(base, count);
        const id = count > 1 ? `${base}-${count}` : base;
        headings.push({ id, text, level });
        html.push(
          `<h${level} id="${id}">${formatInline(text)}<a class="help-anchor" href="#${id}" data-anchor="${id}">#</a></h${level}>`
        );
        return;
      }

      html.push(`<p>${formatInline(line)}</p>`);
    });

    flushList();
    flushTable();
    flushCallout();

    return { html: html.join("\n"), headings };
  }

  return {
    escapeHtml,
    slugifyHeading,
    parseMarkdown,
  };
});
