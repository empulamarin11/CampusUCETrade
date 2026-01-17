import "./styles/base.css";
import "./styles/theme.css";
import "./styles/components.css";

import { renderLogin } from "./pages/login.page.js";
import { renderRegister } from "./pages/register.page.js";
import { renderItems } from "./pages/items.page.js";
import { renderSearch } from "./pages/search.page.js";

const root = document.querySelector("#app");

function setRoute(route) {
  const view = document.querySelector("#view");

  if (route === "register") {
    renderRegister(view, () => setRoute("login"));
    return;
  }

  if (route === "items") {
    renderItems(view, () => setRoute("login"), () => setRoute("search"));
    return;
  }

  if (route === "search") {
    renderSearch(view, () => setRoute("items"));
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
