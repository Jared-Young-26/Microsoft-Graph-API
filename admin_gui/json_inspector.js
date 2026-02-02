(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminJsonInspector = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  const defaultHelpers = {
    isPrimitive(value) {
      return value === null || value === undefined || typeof value !== "object";
    },
    formatValue(value) {
      if (value === null) return "null";
      if (value === undefined) return "undefined";
      if (typeof value === "string") return value;
      if (typeof value === "boolean") return value ? "true" : "false";
      return String(value);
    },
    showToast() {},
  };

  function jsonPointer(parts) {
    if (!parts || !parts.length) return "/";
    return (
      "/" +
      parts
        .map((part) => String(part).replace(/~/g, "~0").replace(/\//g, "~1"))
        .join("/")
    );
  }

  function createInspectorState(rootValue) {
    return {
      rootValue,
      valueMap: new Map(),
      selectedPointer: null,
      searchQuery: "",
      matches: [],
      matchIndex: -1,
    };
  }

  function selectInspectorNode(modal, element, pointer) {
    if (!modal || !element) return;
    const prev = modal.querySelector(".json-selected");
    if (prev) prev.classList.remove("json-selected");
    element.classList.add("json-selected");
    if (modal._inspectorState) {
      modal._inspectorState.selectedPointer = pointer;
    }
  }

  function renderJsonInspector(value, options = {}) {
    const helpers = options.helpers || defaultHelpers;
    const state = options.state || createInspectorState(value);
    const container = document.createElement("div");
    container.classList.add("json-inspector");
    if (options.wrap) {
      container.classList.add("wrap");
    }
    const maxItems = options.maxItems || 200;
    const step = options.step || 200;

    const renderNode = (val, path, depth, label, isRoot = false) => {
      if (helpers.isPrimitive(val)) {
        const row = document.createElement("div");
        row.classList.add("json-row");
        row.style.setProperty("--depth", depth);
        const key = document.createElement("span");
        key.classList.add("json-key");
        key.textContent = label ?? "";
        const sep = document.createElement("span");
        sep.classList.add("json-sep");
        sep.textContent = label != null ? ":" : "";
        const valueEl = document.createElement("span");
        valueEl.classList.add("json-value");
        valueEl.textContent = helpers.formatValue(val);
        row.appendChild(key);
        row.appendChild(sep);
        row.appendChild(valueEl);
        const pointer = jsonPointer(path);
        row.dataset.pointer = pointer;
        row.dataset.search = `${label ?? ""} ${helpers.formatValue(val)}`.toLowerCase();
        state.valueMap.set(pointer, val);
        row.addEventListener("click", (event) => {
          event.stopPropagation();
          if (options.modal) {
            selectInspectorNode(options.modal, row, pointer);
          }
        });
        return row;
      }

      const details = document.createElement("details");
      details.classList.add("json-node");
      details.open = isRoot;
      details.style.setProperty("--depth", depth);
      const summary = document.createElement("summary");
      summary.classList.add("json-summary");
      const key = document.createElement("span");
      key.classList.add("json-key");
      key.textContent = label ?? (isRoot ? "root" : "");
      const sep = document.createElement("span");
      sep.classList.add("json-sep");
      sep.textContent = label != null || isRoot ? ":" : "";
      const type = document.createElement("span");
      type.classList.add("json-type");
      const isArray = Array.isArray(val);
      const count = isArray ? val.length : Object.keys(val || {}).length;
      type.textContent = isArray ? `Array(${count})` : `Object(${count})`;
      summary.appendChild(key);
      summary.appendChild(sep);
      summary.appendChild(type);
      details.appendChild(summary);

      const pointer = jsonPointer(path);
      details.dataset.pointer = pointer;
      details.dataset.search = `${label ?? ""} ${type.textContent}`.toLowerCase();
      state.valueMap.set(pointer, val);

      summary.addEventListener("click", (event) => {
        event.stopPropagation();
        if (options.modal) {
          selectInspectorNode(options.modal, details, pointer);
        }
      });

      const children = document.createElement("div");
      children.classList.add("json-children");
      details.appendChild(children);

      if (isArray) {
        let limit = maxItems;
        const renderArray = () => {
          children.innerHTML = "";
          const sliced = val.slice(0, limit);
          sliced.forEach((item, idx) => {
            children.appendChild(renderNode(item, [...path, idx], depth + 1, `[${idx}]`));
          });
          if (limit < val.length) {
            const more = document.createElement("div");
            more.classList.add("json-more");
            more.textContent = `Showing first ${limit} of ${val.length} items. `;
            const btn = document.createElement("button");
            btn.type = "button";
            btn.classList.add("ghost", "small");
            btn.textContent = `Load ${Math.min(step, val.length - limit)} more`;
            btn.addEventListener("click", (event) => {
              event.stopPropagation();
              limit = Math.min(val.length, limit + step);
              renderArray();
            });
            more.appendChild(btn);
            children.appendChild(more);
          }
        };
        renderArray();
      } else {
        Object.entries(val || {}).forEach(([childKey, childVal]) => {
          children.appendChild(renderNode(childVal, [...path, childKey], depth + 1, childKey));
        });
      }
      return details;
    };

    container.appendChild(renderNode(value, [], 0, null, true));
    return { container, state };
  }

  function runModalSearch(modal, queryOverride) {
    if (!modal) return;
    const state = modal._inspectorState;
    if (!state) return;
    const input = modal.querySelector("#modal-search");
    const meta = modal.querySelector("#modal-search-meta");
    const query = (queryOverride !== undefined ? queryOverride : input?.value || "").toLowerCase().trim();
    state.searchQuery = query;
    const matches = [];
    modal.querySelectorAll("[data-search]").forEach((node) => {
      node.classList.remove("match", "match-active");
      if (!query) return;
      if ((node.dataset.search || "").includes(query)) {
        node.classList.add("match");
        matches.push(node);
      }
    });
    state.matches = matches;
    state.matchIndex = matches.length ? 0 : -1;
    if (matches.length) {
      matches[0].classList.add("match-active");
      matches[0].scrollIntoView({ behavior: "smooth", block: "center" });
      if (meta) meta.textContent = `1 / ${matches.length} matches`;
    } else {
      if (meta) meta.textContent = query ? "0 matches" : "";
    }
  }

  function jumpModalSearch(modal, direction) {
    if (!modal) return;
    const state = modal._inspectorState;
    if (!state || !state.matches.length) return;
    state.matches[state.matchIndex]?.classList.remove("match-active");
    const nextIndex = (state.matchIndex + direction + state.matches.length) % state.matches.length;
    state.matchIndex = nextIndex;
    const node = state.matches[nextIndex];
    node.classList.add("match-active");
    node.scrollIntoView({ behavior: "smooth", block: "center" });
    const meta = modal.querySelector("#modal-search-meta");
    if (meta) meta.textContent = `${nextIndex + 1} / ${state.matches.length} matches`;
  }

  async function copyModalSelection(modal, mode, helpers = defaultHelpers) {
    if (!modal) return;
    const state = modal._inspectorState;
    if (!state) return;
    const pointer = state.selectedPointer;
    const value = pointer ? state.valueMap.get(pointer) : null;
    let payload = null;
    if (mode === "all") {
      payload = JSON.stringify(state.rootValue, null, 2);
    } else if (!pointer) {
      helpers.showToast("Select a node to copy");
      return;
    } else if (mode === "path") {
      payload = pointer;
    } else if (mode === "value") {
      payload = helpers.isPrimitive(value) ? String(value ?? "") : JSON.stringify(value, null, 2);
    } else {
      payload = JSON.stringify(value, null, 2);
    }
    try {
      await navigator.clipboard.writeText(payload);
      helpers.showToast("Copied");
    } catch (err) {
      helpers.showToast("Copy failed");
    }
  }

  return {
    jsonPointer,
    createInspectorState,
    renderJsonInspector,
    runModalSearch,
    jumpModalSearch,
    copyModalSelection,
  };
});
