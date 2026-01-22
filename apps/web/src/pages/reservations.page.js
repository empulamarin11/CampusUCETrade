import { listReservations } from "../api/reservations.api.js";

export function renderReservations(container, goToItems, goToLogin) {
  const token = localStorage.getItem("token");
  if (!token) { goToLogin(); return; }

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Reservations</h1>
        <p class="small" style="margin-top:6px">Your reservations.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back to items</button>
        <button class="btn" id="logoutBtn" type="button">Sign out</button>
      </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section">
      <div class="row" style="justify-content:space-between; align-items:center">
        <h2 class="h2" style="margin:0">List</h2>
        <button class="btn" id="refreshBtn" type="button">Refresh</button>
      </div>
      <div id="list" class="small" style="margin-top:12px">Loading...</div>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const list = container.querySelector("#list");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#backBtn").onclick = goToItems;
  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };

  async function refresh() {
    msg.className = "msg";
    msg.textContent = "Loading reservations...";
    list.textContent = "Loading...";

    try {
      const data = await listReservations(token);
      const rows = Array.isArray(data) ? data : (data?.reservations ?? data?.items ?? []);
      setMsg(`Loaded ✅ (${rows.length})`, true);

      if (!rows.length) {
        list.textContent = "No reservations found.";
        return;
      }

      list.innerHTML = `
        <div class="grid">
          ${rows.map((r) => `
            <div class="itemCard">
              <div class="itemTitle">Reservation</div>
              <div class="small">ID: ${escapeHtml(r.id ?? r.reservation_id ?? "")}</div>
              <div class="small">Item: ${escapeHtml(r.item_id ?? "")}</div>
              <div class="small">Status: <b>${escapeHtml(r.status ?? "N/A")}</b></div>
              <div class="small" style="opacity:.85">Created: ${escapeHtml(r.created_at ?? "")}</div>
            </div>
          `).join("")}
        </div>
      `;
    } catch (e) {
      setMsg(`Load failed: ${e.message}`, false);
      list.textContent = "Failed to load reservations.";
    }
  }

  container.querySelector("#refreshBtn").onclick = refresh;

  refresh();
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
