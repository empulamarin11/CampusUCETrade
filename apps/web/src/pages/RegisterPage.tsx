import { useState } from "react";
import { registerUser } from "../lib/users";
import { useNavigate } from "react-router-dom";


export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const navigate = useNavigate();


  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    try {
      await registerUser(email, password, fullName || undefined);
      setMsg("Register OK. Now go to Login.");
      setTimeout(() => navigate("/login"), 500);

    } catch (err) {
      setMsg(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div>
      <h3>Register</h3>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <label>
          Full name (optional)
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} style={{ width: "100%", padding: 8 }} />
        </label>

        <label>
          UCE Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: "100%", padding: 8 }} />
        </label>

        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: 8 }} />
        </label>

        <button type="submit" style={{ padding: 10 }}>Create account</button>
      </form>

      {msg && <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{msg}</pre>}
    </div>
  );
}
