import { register } from "../api/user.api.js";

export function renderRegister(container, goToLogin) {
  container.innerHTML = `
    <h1 class="h1">Sign up</h1>
    <p class="small">Create your account with @uce.edu.ec.</p>

    <form id="regForm" class="form">
      <div class="field">
        <label>Full name</label>
        <input name="full_name" type="text" placeholder="Your name" required />
      </div>

      <div class="field">
        <label>Email</label>
        <input name="email" type="email" placeholder="name@uce.edu.ec" required />
      </div>

      <div class="field">
        <label>Password</label>
        <input name="password" type="password" placeholder="Min 6 characters" minlength="6" required />
      </div>

      <button class="btn primary" type="submit">Create account</button>

      <div class="small linkRow">
        <span>Already have an account?</span>
        <button class="linkBtn" type="button" id="goLogin">Back to sign in</button>
      </div>

      <div id="msg" class="msg" aria-live="polite"></div>
    </form>
  `;

  const form = container.querySelector("#regForm");
  const msg = container.querySelector("#msg");

  const setMsg = (text, ok) => {
    msg.className = `msg ${ok ? "ok" : "bad"}`;
    msg.textContent = text;
  };

  container.querySelector("#goLogin").onclick = goToLogin;

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    msg.className = "msg";
    msg.textContent = "Creating account...";

    const fd = new FormData(form);
    const full_name = fd.get("full_name");
    const email = fd.get("email");
    const password = fd.get("password");

    try {
      await register(email, password, full_name);
      setMsg("Account created ✅ Redirecting to sign in...", true);

      setTimeout(() => goToLogin(), 700);
    } catch (e) {
      setMsg(`Sign up failed: ${e.message}`, false);
    }
  };
}