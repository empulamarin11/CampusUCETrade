import { searchItems } from "../api/search.api.js";

export function renderSearch(container, goToItems) {
  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Search</h1>
        <p class="small" style="margin-top:6px">Find items by keyword.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back to items</button>
      </div>
    </div>

    <div class="section" style="border-top:none; padding-top:0">
      <form id="searchForm" class="form">
        <div class="row">
          <div class="field" style="flex:1; min-width:240px">
            <label>Keyword</label>
            <input name="q" type="text" placeholder="e.g. book, laptop, calculator" />
          </div>
          <div style="display:flex; align-items:flex-end">
            <button class="btn primary" type="submit">Search</button>
          </div>
        </div>
      </form>

      <div id="msg" class="msg" aria-live="polite"></div>
      <div id="results" class="small" style="margin-top:12px">Type a keyword and search.</div>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const results = container.querySelector("#results");
  container.querySelector("#backBtn").onclick = goToItems;

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#searchForm").onsubmit = async (ev) => {
    ev.preventDefault();
    msg.className = "msg";
    msg.textContent = "Searching...";
    results.textContent = "Loading...";

    const fd = new FormData(ev.target);
    const q = String(fd.get("q") || "").trim();

    try {
      const data = await searchItems(q);

      // Try common shapes: array or {items:[]}
      const items = Array.isArray(data) ? data : (data?.items ?? data?.results ?? []);

      setMsg(`Done ✅ (${items.length} results)`, true);

      if (!items.length) {
        results.textContent = "No results.";
        return;
      }

      results.innerHTML = `
        <div class="grid">
          ${items.map((i) => `
            <div class="itemCard">
              <div class="itemTitle">${escapeHtml(i.title ?? i.name ?? "Untitled")}</div>
              <div class="small">${escapeHtml(i.description ?? "")}</div>
              ${i.price != null ? `<div class="small" style="margin-top:6px">Price: <b>${escapeHtml(String(i.price))} ${escapeHtml(i.currency ?? "")}</b></div>` : ""}
              <div class="small" style="opacity:.8; margin-top:6px">ID: ${escapeHtml(i.id ?? i.item_id ?? "")}</div>
            </div>
          `).join("")}
        </div>
      `;
    } catch (e) {
      setMsg(`Search failed: ${e.message}`, false);
      results.textContent = "Failed to search.";
    }
  };
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
