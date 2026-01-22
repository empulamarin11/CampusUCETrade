import "./styles/base.css";
import "./styles/theme.css";
import "./styles/components.css";

import { renderLogin } from "./pages/login.page.js";
import { renderRegister } from "./pages/register.page.js";
import { renderItems } from "./pages/items.page.js";
import { renderSearch } from "./pages/search.page.js";
import { renderReservations } from "./pages/reservations.page.js";
import { renderNotifications } from "./pages/notifications.page.js";
import { renderChat } from "./pages/chat.page.js";
import { renderDelivery } from "./pages/delivery.page.js";
import { renderReputation } from "./pages/reputation.page.js";
import { renderTraceability } from "./pages/traceability.page.js";


const root = document.querySelector("#app");

function setRoute(route) {
  const view = document.querySelector("#view");

  if (route === "register") {
    renderRegister(view, () => setRoute("login"));
    return;
  }

  if (route === "items") {
    renderItems(
      view,
      () => setRoute("login"),
      () => setRoute("search"),
      () => setRoute("reservations"),
      () => setRoute("notifications"),
      () => setRoute("chat"),
      () => setRoute("delivery"),
      () => setRoute("reputation"),
      () => setRoute("traceability")
    );
    return;
  }

  if (route === "search") {
    renderSearch(view, () => setRoute("items"));
    return;
  }

  if (route === "reservations") {
    renderReservations(view, () => setRoute("items"), () => setRoute("login"));
    return;
  }

  if (route === "notifications") {
    renderNotifications(view, () => setRoute("items"), () => setRoute("login"));
    return;
  }

  if (route === "chat") {
    renderChat(view, () => setRoute("items"));
    return;
  }
  
  if (route === "delivery") {
    renderDelivery(view, () => setRoute("items"), () => setRoute("login"));
    return;
  }

  if (route === "reputation") {
    renderReputation(view, () => setRoute("items"), () => setRoute("login"));
    return;
  }

  if (route === "traceability") {
    renderTraceability(view, () => setRoute("items"), () => setRoute("login"));
    return;
  }

  // login
  renderLogin(view, () => setRoute("register"), () => setRoute("items"));
}

function layout() {
  root.innerHTML = `
    <div class="bg"></div>
    <div class="shell">
      <div class="card">
        <div class="header">
          <div class="brand">
            <div class="logo">CU</div>
            <div class="title">CampusUCETrade</div>
          </div>
        </div>
        <div class="content" id="view"></div>
      </div>
    </div>
  `;

  if (localStorage.getItem("token")) setRoute("items");
  else setRoute("login");
}

layout();
