import { login } from "../api/auth.api.js";

export function renderLogin(container, goToRegister, goToItems) {
  container.innerHTML = `
    <h1 class="h1">Sign in</h1>
    <p class="small">Use your institutional email (@uce.edu.ec).</p>

    <form id="loginForm" class="form">
      <div class="field">
        <label>Email</label>
        <input name="email" type="email" placeholder="name@uce.edu.ec" required />
      </div>

      <div class="field">
        <label>Password</label>
        <input name="password" type="password" placeholder="••••••••" required />
      </div>

      <button class="btn primary" type="submit">Sign in</button>

      <div class="small linkRow">
        <span>Don't have an account?</span>
        <button class="linkBtn" type="button" id="goRegister">Sign up</button>
      </div>

      <div id="msg" class="msg" aria-live="polite"></div>
    </form>
  `;

  const form = container.querySelector("#loginForm");
  const msg = container.querySelector("#msg");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#goRegister").onclick = goToRegister;

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    msg.className = "msg";
    msg.textContent = "Signing in...";

    const fd = new FormData(form);
    const email = fd.get("email");
    const password = fd.get("password");

    try {
      const r = await login(email, password);

      if (r?.access_token) localStorage.setItem("token", r.access_token);

      setMsg("Signed in successfully ✅", true);

      // IMPORTANT: go to Items
      if (goToItems) goToItems();
    } catch (e) {
      setMsg(`Sign in failed: ${e.message}`, false);
    }
  };
}
