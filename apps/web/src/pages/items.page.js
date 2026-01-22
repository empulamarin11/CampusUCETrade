import { listItems, createItem } from "../api/items.api.js";
import { createReservation } from "../api/reservations.api.js";

export function renderItems(container, goToLogin, goToSearch, goToReservations, goToNotifications, goToChat, goToDelivery, goToReputation, goToTraceability) {
  const token = localStorage.getItem("token");
  if (!token) {
    goToLogin();
    return;
  }

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Items</h1>
        <p class="small" style="margin-top:6px">Browse all items.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="searchBtn" type="button">Search</button>
        <button class="btn" id="reservationsBtn" type="button">Reservations</button>
        <button class="btn" id="deliveryBtn">Delivery</button>
        <button class="btn primary" id="openCreateBtn" type="button">Create item</button>
        <button class="btn" id="chatBtn">Chat</button>
        <button class="btn" id="notificationsBtn" type="button">Notifications</button>
        <button class="btn" id="reputationBtn" type="button">Reputation</button>
        <button class="btn" id="traceBtn" type="button">Traceability</button>
        <button class="btn" id="logoutBtn" type="button">Sign out</button>
        
        </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section">
      <div class="row" style="justify-content:space-between; align-items:center">
        <h2 class="h2" style="margin:0">All items</h2>
        <button class="btn" id="refreshBtn" type="button">Refresh</button>
      </div>
      <div id="list" class="small" style="margin-top:12px">Loading...</div>
    </div>

    <!-- Create modal -->
    <div class="modal" id="createModal" aria-hidden="true">
      <div class="modalBackdrop" id="closeModalBackdrop"></div>
      <div class="modalCard" role="dialog" aria-modal="true" aria-labelledby="createTitle">
        <div class="modalHeader">
          <div>
            <div id="createTitle" style="font-weight:800; color:var(--text)">Create item</div>
            <div class="small">Title, description, price, currency</div>
          </div>
          <button class="btn" id="closeModalBtn" type="button">Close</button>
        </div>

        <form id="createForm" class="form" style="margin-top:10px">
          <div class="field">
            <label>Title</label>
            <input name="title" type="text" placeholder="e.g. Calculus book" required />
          </div>

          <div class="field">
            <label>Description</label>
            <input name="description" type="text" placeholder="Short description" />
          </div>

          <div class="row">
            <div class="field" style="flex:1; min-width:180px">
              <label>Price</label>
              <input name="price" type="number" step="0.01" min="0" placeholder="0.00" required />
            </div>

            <div class="field" style="flex:1; min-width:180px">
              <label>Currency</label>
              <input name="currency" type="text" value="USD" maxlength="3" required />
            </div>
          </div>

          <div class="row" style="justify-content:flex-end">
            <button class="btn primary" type="submit">Create</button>
          </div>
        </form>

        <div id="modalMsg" class="msg" aria-live="polite"></div>
      </div>
    </div>
  `;

  const msg = container.querySelector("#msg");
  const list = container.querySelector("#list");
  const modal = container.querySelector("#createModal");
  const modalMsg = container.querySelector("#modalMsg");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  const setModalMsg = (text, ok) => {
    modalMsg.className = `msg ${ok ? "ok" : "bad"}`;
    modalMsg.textContent = text;
  };

  function openModal() {
    modal.setAttribute("aria-hidden", "false");
    modal.classList.add("open");
    setModalMsg("", true);
  }

  function closeModal() {
    modal.setAttribute("aria-hidden", "true");
    modal.classList.remove("open");
  }

  // Topbar actions
  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };

  container.querySelector("#searchBtn").onclick = () => {
    if (goToSearch) goToSearch();
  };

  container.querySelector("#reservationsBtn").onclick = () => {
    if (goToReservations) goToReservations();
  };

  container.querySelector("#notificationsBtn").onclick = () => {
    if (goToNotifications) goToNotifications();
  };

  container.querySelector("#chatBtn").onclick = () => {
    if (goToChat) goToChat();
  };

  container.querySelector("#deliveryBtn").onclick = () => {
    if (goToDelivery) goToDelivery();
  };

  container.querySelector("#reputationBtn").onclick = () => {
    if (goToReputation) goToReputation();
  };

  container.querySelector("#traceBtn").onclick = () => goToTraceability && goToTraceability();



  // Modal actions
  container.querySelector("#openCreateBtn").onclick = openModal;
  container.querySelector("#closeModalBtn").onclick = closeModal;
  container.querySelector("#closeModalBackdrop").onclick = closeModal;

  async function refresh() {
    msg.className = "msg";
    msg.textContent = "Loading items...";
    list.textContent = "Loading...";

    try {
      const data = await listItems();
      const items = Array.isArray(data) ? data : (data?.items ?? []);
      setMsg("Items loaded ✅", true);

      if (!items.length) {
        list.textContent = "No items found.";
        return;
      }

      list.innerHTML = `
        <div class="grid">
          ${items.map((i) => `
            <div class="itemCard">
              <div class="itemTitle">${escapeHtml(i.title ?? "Untitled")}</div>
              <div class="small">${escapeHtml(i.description ?? "")}</div>
              <div class="small" style="margin-top:6px">
                Price: <b>${escapeHtml(String(i.price ?? ""))} ${escapeHtml(i.currency ?? "")}</b>
              </div>

              <div class="row" style="margin-top:10px">
                <button class="btn" type="button" data-reserve="${escapeHtml(i.id ?? "")}">Reserve</button>
              </div>

              <div class="small" style="opacity:.8; margin-top:6px">ID: ${escapeHtml(i.id ?? "")}</div>
            </div>
          `).join("")}
        </div>
      `;

      // Reserve buttons
      list.querySelectorAll("[data-reserve]").forEach((btn) => {
        btn.onclick = async () => {
          const itemId = btn.getAttribute("data-reserve");
          msg.className = "msg";
          msg.textContent = "Creating reservation...";

          try {
            // Most common payload: { item_id: "..." }
            const notes = prompt("Notes (optional):", "Reserved from UI") || "";
            await createReservation(token, { item_id: itemId, notes });
            setMsg("Reservation created ✅", true);
            if (goToReservations) goToReservations();
          } catch (e) {
            setMsg(`Reservation failed: ${e.message}`, false);
          }
        };
      });
    } catch (e) {
      setMsg(`Load failed: ${e.message}`, false);
      list.textContent = "Failed to load items.";
    }
  }

  container.querySelector("#refreshBtn").onclick = refresh;

  // Create item (modal)
  container.querySelector("#createForm").onsubmit = async (ev) => {
    ev.preventDefault();
    setModalMsg("Creating item...", true);

    const fd = new FormData(ev.target);
    const payload = {
      title: fd.get("title"),
      description: fd.get("description") || null,
      price: Number(fd.get("price")),
      currency: String(fd.get("currency") || "USD").toUpperCase().trim(),
    };

    try {
      await createItem(token, payload);
      setModalMsg("Item created ✅", true);
      ev.target.reset();
      closeModal();
      await refresh();
    } catch (e) {
      setModalMsg(`Create failed: ${e.message}`, false);
    }
  };

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
