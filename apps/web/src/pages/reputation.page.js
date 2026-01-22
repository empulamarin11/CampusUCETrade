import { getReputation, rateUser } from "../api/reputation.api.js";

export function renderReputation(container, goBack, goToLogin) {
  const token = localStorage.getItem("token");
  if (!token) { goToLogin(); return; }

  const myEmail = getJwtEmail() || "";
  const lastLookup = localStorage.getItem("rep_last_lookup") || myEmail;

  container.innerHTML = `
    <div class="topbar">
      <div>
        <h1 class="h1" style="margin:0">Reputation</h1>
        <p class="small" style="margin-top:6px">Check reputation and rate users.</p>
      </div>
      <div class="topActions">
        <button class="btn" id="backBtn" type="button">Back</button>
        <button class="btn" id="logoutBtn" type="button">Sign out</button>
      </div>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>

    <div class="section" style="border-top:none; padding-top:0">
      <h2 class="h2" style="margin-top:0">My reputation</h2>
      <div class="row">
        <div class="field" style="flex:1; min-width:260px">
          <label>My email (from token)</label>
          <input id="myEmail" value="${escapeHtml(myEmail)}" readonly />
        </div>
        <div style="display:flex; align-items:flex-end; gap:10px">
          <button class="btn primary" id="myBtn" type="button">Load</button>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="h2" style="margin-top:0">Lookup by email</h2>
      <div class="row">
        <div class="field" style="flex:1; min-width:260px">
          <label>User email</label>
          <input id="lookupEmail" value="${escapeHtml(lastLookup)}" placeholder="user@uce.edu.ec" />
        </div>
        <div style="display:flex; align-items:flex-end; gap:10px">
          <button class="btn" id="lookupBtn" type="button">Lookup</button>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="h2" style="margin-top:0">Rate user</h2>

      <form id="rateForm" class="form">
        <div class="row">
          <div class="field" style="flex:1; min-width:260px">
            <label>User email</label>
            <input name="user_email" placeholder="user@uce.edu.ec" required />
          </div>

          <div class="field" style="width:160px; min-width:160px">
            <label>Points (1-5)</label>
            <input name="points" type="number" min="1" max="5" value="5" required />
          </div>
        </div>

        <div class="row">
          <div class="field" style="flex:1">
            <label>Feedback</label>
            <input name="feedback" placeholder="Fast delivery, great communication..." />
          </div>
        </div>

        <div class="row" style="justify-content:flex-end">
          <button class="btn primary" type="submit">Submit rating</button>
        </div>
      </form>
    </div>

    <div class="section">
      <h2 class="h2" style="margin-top:0">Response</h2>
      <pre id="out" class="codeBox">{}</pre>
    </div>
  `;

  const msg = container.querySelector("#msg");
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

  container.querySelector("#myBtn").onclick = async () => {
    if (!myEmail) { setMsg("Token has no email (sub).", false); return; }
    await doLookup(myEmail);
  };

  container.querySelector("#lookupBtn").onclick = async () => {
    const email = container.querySelector("#lookupEmail").value.trim().toLowerCase();
    if (!email) { setMsg("Enter an email.", false); return; }
    localStorage.setItem("rep_last_lookup", email);
    await doLookup(email);
  };

  container.querySelector("#rateForm").onsubmit = async (ev) => {
    ev.preventDefault();
    out.textContent = "{}";
    setMsg("Submitting rating...", true);

    const fd = new FormData(ev.target);
    const payload = {
      user_email: String(fd.get("user_email") || "").trim().toLowerCase(),
      points: Number(fd.get("points") || 0),
      feedback: String(fd.get("feedback") || "").trim(),
    };

    try {
      const data = await rateUser(token, payload);
      setMsg("Rating submitted ✅", true);
      out.textContent = JSON.stringify(data, null, 2);

      // Auto lookup after rating
      if (payload.user_email) {
        localStorage.setItem("rep_last_lookup", payload.user_email);
        container.querySelector("#lookupEmail").value = payload.user_email;
      }
    } catch (e) {
      setMsg(`Rate failed: ${e.message}`, false);
    }
  };

  async function doLookup(email) {
    out.textContent = "{}";
    setMsg("Loading reputation...", true);
    try {
      const data = await getReputation(token, email);
      setMsg("Loaded ✅", true);
      out.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      setMsg(`Lookup failed: ${e.message}`, false);
    }
  }
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

function escapeHtml(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
