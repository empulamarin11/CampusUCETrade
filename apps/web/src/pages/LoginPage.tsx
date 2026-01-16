import { useState } from "react";
import { login } from "../lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    try {
      const token = await login(email, password);
      localStorage.setItem("access_token", token.access_token);
      setMsg("Login OK. Token saved in localStorage.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div>
      <h3>Login</h3>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: "100%", padding: 8 }} />
        </label>

        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: 8 }} />
        </label>

        <button type="submit" style={{ padding: 10 }}>Sign in</button>
      </form>

      {msg && <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{msg}</pre>}
    </div>
  );
}
