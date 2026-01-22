import { listNotifications, markRead } from "../api/notifications.api.js";

export function renderNotifications(container, goBack, goToLogin) {
  const token = localStorage.getItem("token");
  if (!token) { goToLogin(); return; }

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Notifications</h1>
        <p class="small" style="margin-top:6px">Your latest notifications.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back</button>
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

  container.querySelector("#backBtn").onclick = goBack;
  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };

  async function refresh() {
    msg.className = "msg";
    msg.textContent = "Loading notifications...";
    list.textContent = "Loading...";

    try {
      const data = await listNotifications(token);
      const rows = Array.isArray(data) ? data : (data?.notifications ?? data?.items ?? []);
      setMsg(`Loaded ✅ (${rows.length})`, true);

      if (!rows.length) {
        list.textContent = "No notifications.";
        return;
      }

      list.innerHTML = `
        <div class="grid">
          ${rows.map((n) => `
            <div class="itemCard">
              <div class="itemTitle">${escapeHtml(n.title ?? "Notification")}</div>
              <div class="small">${escapeHtml(n.message ?? n.body ?? "")}</div>
              <div class="small" style="margin-top:6px">
                Status: <b>${escapeHtml(n.read ? "read" : "unread")}</b>
              </div>
              <div class="row" style="margin-top:10px">
                <button class="btn" type="button" data-read="${escapeHtml(n.id ?? n.notification_id ?? "")}">
                  Mark read
                </button>
              </div>
              <div class="small" style="opacity:.8; margin-top:6px">ID: ${escapeHtml(n.id ?? "")}</div>
            </div>
          `).join("")}
        </div>
      `;

      list.querySelectorAll("[data-read]").forEach((btn) => {
        btn.onclick = async () => {
          const id = btn.getAttribute("data-read");
          msg.className = "msg";
          msg.textContent = "Marking as read...";

          try {
            await markRead(token, id);
            setMsg("Updated ✅", true);
            await refresh();
          } catch (e) {
            setMsg(`Failed: ${e.message}`, false);
          }
        };
      });
    } catch (e) {
      setMsg(`Load failed: ${e.message}`, false);
      list.textContent = "Failed to load notifications.";
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
