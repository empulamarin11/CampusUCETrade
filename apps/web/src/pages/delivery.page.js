import { apiFetch } from "../api/client.js";
import { createDelivery, confirmDelivery, getDelivery } from "../api/delivery.api.js";

export function renderDelivery(container, goBack, goToLogin) {
  const token = localStorage.getItem("token");
  if (!token) { goToLogin(); return; }

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Delivery</h1>
        <p class="small" style="margin-top:6px">Select a reservation, create delivery, then confirm as buyer/seller.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back</button>
        <button class="btn" id="logoutBtn" type="button">Sign out</button>
      </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section" style="border-top:none; padding-top:0">
      <div class="row">
        <div class="field" style="flex:1; min-width:220px">
          <label>Status filter</label>
          <select id="statusSelect">
            <option value="confirmed" selected>confirmed</option>
            <option value="pending">pending</option>
            <option value="cancelled">cancelled</option>
            <option value="">all</option>
          </select>
          <p class="small muted" style="margin-top:8px">
            Tip: only confirmed reservations are usually deliverable.
          </p>
        </div>
        <div style="display:flex; align-items:flex-end; gap:10px">
          <button class="btn" id="refreshBtn" type="button">Refresh</button>
        </div>
      </div>

      <div id="grid" class="cardsGrid"></div>
    </div>

    <div class="section">
      <h2 class="h2" style="margin-top:0">Result</h2>
      <pre id="out" class="codeBox">{}</pre>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const out = container.querySelector("#out");
  const grid = container.querySelector("#grid");
  const statusSelect = container.querySelector("#statusSelect");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#backBtn").onclick = goBack;
  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };

  // Cache item details
  const itemCache = new Map();

  async function fetchItem(itemId) {
    if (itemCache.has(itemId)) return itemCache.get(itemId);
    const item = await apiFetch(`/items/${encodeURIComponent(itemId)}`, { method: "GET" });
    itemCache.set(itemId, item);
    return item;
  }

  function getJwtEmail() {
    try {
      const t = localStorage.getItem("token");
      if (!t) return "";
      const payload = t.split(".")[1];
      const json = JSON.parse(atob(payload.replaceAll("-", "+").replaceAll("_", "/")));
      return (json.sub || "").toLowerCase();
    } catch {
      return "";
    }
  }

  function deliveryKey(resId) {
    return `delivery_for_${resId}`;
  }

  async function loadReservations() {
    grid.innerHTML = `<div class="small muted">Loading reservations...</div>`;
    out.textContent = "{}";
    setMsg("Loading reservations...", true);

    const status = statusSelect.value;
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";

    try {
      // GET /reservations/
      const reservations = await apiFetch(`/reservations/${qs}`, { method: "GET", token });

      if (!Array.isArray(reservations) || reservations.length === 0) {
        grid.innerHTML = `<div class="small muted">No reservations found.</div>`;
        setMsg("No reservations found.", true);
        return;
      }

      const viewerEmail = getJwtEmail();

      const enriched = await Promise.all(
        reservations.map(async (r) => {
          let item = null;
          try { item = await fetchItem(r.item_id); } catch { item = null; }
          return { r, item };
        })
      );

      grid.innerHTML = enriched.map(({ r, item }) => {
        const title = item?.title || "Item";
        const sellerEmail = (item?.owner_email || "").toLowerCase();
        const buyerEmail = (r.requester_email || "").toLowerCase();
        const did = localStorage.getItem(deliveryKey(r.id)) || "";

        const amBuyer = viewerEmail && buyerEmail && viewerEmail === buyerEmail;
        const amSeller = viewerEmail && sellerEmail && viewerEmail === sellerEmail;

        return `
          <div class="cardBox">
            <div class="cardHead">
              <div class="cardTitle">${escapeHtml(title)}</div>
              <div class="badge">${escapeHtml(r.status)}</div>
            </div>

            <div class="cardMeta">
              <div><span class="muted">Buyer</span> ${escapeHtml(buyerEmail || "-")}</div>
              <div><span class="muted">Seller</span> ${escapeHtml(sellerEmail || "-")}</div>
              <div><span class="muted">You</span> ${escapeHtml(viewerEmail || "-")}</div>
            </div>

            <div class="cardActions">
              <button class="btn primary" data-action="create" data-res="${escapeHtml(r.id)}" ${did ? "disabled" : ""}>
                ${did ? "Delivery created" : "Create delivery"}
              </button>

              <button class="btn" data-action="confirmBuyer" data-res="${escapeHtml(r.id)}" ${did && amBuyer ? "" : "disabled"}>
                Confirm as buyer
              </button>

              <button class="btn" data-action="confirmSeller" data-res="${escapeHtml(r.id)}" ${did && amSeller ? "" : "disabled"}>
                Confirm as seller
              </button>

              <button class="btn" data-action="view" data-res="${escapeHtml(r.id)}" ${did ? "" : "disabled"}>
                View
              </button>
            </div>

            <details style="margin-top:10px">
              <summary class="small muted">Technical details</summary>
              <pre class="codeBox" style="margin-top:10px; min-height:auto">${escapeHtml(JSON.stringify({
                reservation_id: r.id,
                item_id: r.item_id,
                buyer_email: buyerEmail,
                seller_email: sellerEmail,
                delivery_id: did || null,
              }, null, 2))}</pre>
            </details>

            <div class="small muted" style="margin-top:10px">
              ${did ? `Delivery ID stored ✅` : `Create a delivery to enable confirm.`}
            </div>
          </div>
        `;
      }).join("");

      setMsg(`Loaded ✅ (${reservations.length})`, true);

      grid.querySelectorAll("[data-action]").forEach((btn) => {
        btn.addEventListener("click", () => onAction(btn.dataset.action, btn.dataset.res));
      });

    } catch (e) {
      grid.innerHTML = `<div class="small" style="color:#ff8b8b">Failed to load reservations.</div>`;
      setMsg(`Load failed: ${e.message}`, false);
    }
  }

  async function onAction(action, reservationId) {
    out.textContent = "{}";
    try {
      const status = statusSelect.value;
      const qs = status ? `?status=${encodeURIComponent(status)}` : "";
      const reservations = await apiFetch(`/reservations/${qs}`, { method: "GET", token });
      const r = (reservations || []).find((x) => String(x.id) === String(reservationId));
      if (!r) { setMsg("Reservation not found. Refresh.", false); return; }

      const item = await fetchItem(r.item_id);
      const buyerEmail = (r.requester_email || "").toLowerCase();
      const sellerEmail = (item?.owner_email || "").toLowerCase();

      const mapKey = deliveryKey(r.id);
      let deliveryId = localStorage.getItem(mapKey) || "";

      if (action === "create") {
        if (!buyerEmail || !sellerEmail) {
          setMsg("Missing buyer/seller email. Check reservation/item data.", false);
          return;
        }

        setMsg("Creating delivery...", true);

        const data = await createDelivery(token, {
          reservation_id: r.id,
          item_id: r.item_id,
          buyer_email: buyerEmail,
          seller_email: sellerEmail,
        });

        deliveryId = data?.id || data?.delivery_id || "";
        if (!deliveryId) {
          setMsg("Created, but response has no delivery id.", false);
          out.textContent = JSON.stringify(data, null, 2);
          return;
        }

        localStorage.setItem(mapKey, deliveryId);
        localStorage.setItem("last_delivery_id", deliveryId);

        setMsg("Delivery created ✅", true);
        out.textContent = JSON.stringify(data, null, 2);
        await loadReservations();
        return;
      }

      if (!deliveryId) {
        setMsg("No delivery id stored for this reservation. Create first.", false);
        return;
      }

      if (action === "confirmBuyer" || action === "confirmSeller") {
        setMsg("Confirming...", true);

        // Same endpoint for both; backend decides who is confirming based on token.
        const data = await confirmDelivery(token, deliveryId);

        // Show response (string or JSON)
        out.textContent = typeof data === "string" ? JSON.stringify({ result: data }, null, 2) : JSON.stringify(data, null, 2);

        // Verify by GET (best UX)
        try {
          const after = await getDelivery(token, deliveryId);
          out.textContent = JSON.stringify(after, null, 2);

          // Heuristic: find flags if they exist
          const hint = buildConfirmHint(after);
          setMsg(hint || "Confirmed ✅", true);
        } catch {
          setMsg("Confirmed ✅ (could not auto-verify)", true);
        }

        return;
      }

      if (action === "view") {
        setMsg("Loading delivery...", true);
        const data = await getDelivery(token, deliveryId);
        out.textContent = JSON.stringify(data, null, 2);
        setMsg("Loaded ✅", true);
        return;
      }

    } catch (e) {
      setMsg(`${action} failed: ${e.message}`, false);
    }
  }

  function buildConfirmHint(deliveryObj) {
    if (!deliveryObj || typeof deliveryObj !== "object") return "";
    const keys = Object.keys(deliveryObj);

    const buyerKey = keys.find((k) => k.toLowerCase().includes("buyer") && k.toLowerCase().includes("confirm"));
    const sellerKey = keys.find((k) => k.toLowerCase().includes("seller") && k.toLowerCase().includes("confirm"));
    const statusKey = keys.find((k) => k.toLowerCase() === "status");

    const parts = [];
    if (buyerKey) parts.push(`buyer: ${String(deliveryObj[buyerKey])}`);
    if (sellerKey) parts.push(`seller: ${String(deliveryObj[sellerKey])}`);
    if (statusKey) parts.push(`status: ${String(deliveryObj[statusKey])}`);

    return parts.length ? `Confirmed ✅ (${parts.join(" | ")})` : "";
  }

  injectCardCssOnce();

  container.querySelector("#refreshBtn").onclick = loadReservations;
  statusSelect.onchange = loadReservations;

  loadReservations();
}

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function injectCardCssOnce() {
  if (document.getElementById("deliveryCardsCss")) return;
  const style = document.createElement("style");
  style.id = "deliveryCardsCss";
  style.textContent = `
    .cardsGrid{
      display:grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap:14px;
      margin-top:14px;
    }
    .cardBox{
      border:1px solid var(--stroke);
      border-radius:14px;
      padding:14px;
      background: rgba(0,0,0,.14);
    }
    .cardHead{
      display:flex;
      justify-content:space-between;
      gap:10px;
      align-items:flex-start;
    }
    .cardTitle{ font-weight:900; font-size:16px; }
    .badge{
      font-size:12px;
      padding:4px 10px;
      border:1px solid var(--stroke);
      border-radius:999px;
      opacity:.9;
    }
    .cardMeta{
      margin-top:10px;
      display:grid;
      gap:6px;
      font-size:13px;
    }
    .muted{ opacity:.78; }
    .cardActions{
      margin-top:12px;
      display:flex;
      flex-wrap:wrap;
      gap:10px;
    }
  `;
  document.head.appendChild(style);
  document.head.appendChild(style);
}
