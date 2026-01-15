type TokenOut = { access_token: string; token_type: string };

export async function login(email: string, password: string): Promise<TokenOut> {
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Login failed (${res.status}): ${text}`);
  }

  return (await res.json()) as TokenOut;
}
