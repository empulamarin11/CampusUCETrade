import { listAudit, seedAudit } from "../api/traceability.api.js";

export function renderTraceability(container, goBack, goToLogin) {
  const token = localStorage.getItem("token");
  if (!token) { goToLogin(); return; }

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Traceability</h1>
        <p class="small" style="margin-top:6px">Audit log (seed + list).</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back</button>
        <button class="btn" id="logoutBtn" type="button">Sign out</button>
      </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section" style="border-top:none; padding-top:0">
      <div class="row" style="gap:10px; align-items:flex-end">
        <button class="btn" id="refreshBtn" type="button">Refresh</button>
        <button class="btn primary" id="seedBtn" type="button">Seed demo audit</button>
      </div>
      <p class="small muted" style="margin-top:10px">
        Seed inserts demo audit events (useful to show the feature).
      </p>
    </div>

    <div class="section">
      <h2 class="h2" style="margin-top:0">Audit events</h2>
      <div id="list" class="auditList"></div>
      <details style="margin-top:12px">
        <summary class="small muted">Raw JSON</summary>
        <pre id="out" class="codeBox" style="margin-top:10px">{}</pre>
      </details>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const list = container.querySelector("#list");
  const out = container.querySelector("#out");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#backBtn").onclick = goBack;
  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };

  container.querySelector("#refreshBtn").onclick = load;
  container.querySelector("#seedBtn").onclick = async () => {
    setMsg("Seeding demo audit...", true);
    try {
      const data = await seedAudit(token);
      out.textContent = JSON.stringify(data, null, 2);
      setMsg("Seeded ✅ Now refresh.", true);
    } catch (e) {
      setMsg(`Seed failed: ${e.message}`, false);
    }
  };

  async function load() {
    list.innerHTML = `<div class="small muted">Loading...</div>`;
    out.textContent = "{}";
    setMsg("Loading audit...", true);

    try {
      const data = await listAudit(token);
      out.textContent = JSON.stringify(data, null, 2);

      const items = Array.isArray(data) ? data : (data.items || data.events || []);
      if (!Array.isArray(items) || items.length === 0) {
        list.innerHTML = `<div class="small muted">No audit events found.</div>`;
        setMsg("Loaded ✅ (empty)", true);
        return;
      }

      list.innerHTML = items.map((ev) => {
        const ts = ev.ts || ev.created_at || ev.time || "";
        const type = ev.type || ev.event_type || ev.action || "event";
        const msg = ev.message || ev.detail || "";
        const user = ev.user || ev.user_email || ev.actor || "";
        return `
          <div class="auditRow">
            <div class="auditTop">
              <div class="auditType">${escapeHtml(type)}</div>
              <div class="auditTs">${escapeHtml(ts)}</div>
            </div>
            <div class="auditMeta">
              ${user ? `<div><span class="muted">User</span> ${escapeHtml(user)}</div>` : ""}
              ${msg ? `<div><span class="muted">Info</span> ${escapeHtml(msg)}</div>` : ""}
            </div>
            <details style="margin-top:8px">
              <summary class="small muted">Details</summary>
              <pre class="codeBox" style="margin-top:8px; min-height:auto">${escapeHtml(JSON.stringify(ev, null, 2))}</pre>
            </details>
          </div>
        `;
      }).join("");

      setMsg(`Loaded ✅ (${items.length})`, true);
    } catch (e) {
      list.innerHTML = `<div class="small" style="color:#ff8b8b">Failed to load audit.</div>`;
      setMsg(`Load failed: ${e.message}`, false);
    }
  }

  injectCssOnce();
  load();
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function injectCssOnce() {
  if (document.getElementById("traceCss")) return;
  const style = document.createElement("style");
  style.id = "traceCss";
  style.textContent = `
    .auditList{ display:grid; gap:12px; margin-top:12px; }
    .auditRow{
      border:1px solid var(--stroke);
      border-radius:14px;
      padding:14px;
      background: rgba(0,0,0,.14);
    }
    .auditTop{
      display:flex;
      justify-content:space-between;
      gap:10px;
      align-items:center;
    }
    .auditType{ font-weight:900; }
    .auditTs{ font-size:12px; opacity:.8; }
    .auditMeta{ margin-top:10px; display:grid; gap:6px; font-size:13px; }
    .muted{ opacity:.78; }
  `;
  document.head.appendChild(style);
}
