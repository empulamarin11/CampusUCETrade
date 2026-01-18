export function renderProtected(container, goToLogin) {
  const token = localStorage.getItem("token");

  if (!token) {
    goToLogin();
    return;
  }

  container.innerHTML = `
    <h1 class="h1">Protected</h1>
    <p class="small">You are logged in. Token is stored in localStorage.</p>

    <div class="field" style="margin-top:14px">
      <label>Access token</label>
      <input value="${escapeHtml(token)}" readonly />
    </div>

    <div class="row">
      <button class="btn" id="copyBtn" type="button">Copy token</button>
      <button class="btn" id="logoutBtn" type="button">Sign out</button>
    </div>

    <div id="msg" class="msg" aria-live="polite"></div>
  `;

  const msg = container.querySelector("#msg");
  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#copyBtn").onclick = async () => {
    try {
      await navigator.clipboard.writeText(token);
      setMsg("Copied ✅", true);
    } catch {
      setMsg("Copy failed", false);
    }
  };

  container.querySelector("#logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    goToLogin();
  };
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}