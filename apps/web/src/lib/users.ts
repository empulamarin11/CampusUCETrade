type RegisterOut = { email: string; full_name: string | null; role: string; is_active: boolean };

export async function registerUser(email: string, password: string, full_name?: string): Promise<RegisterOut> {
  const res = await fetch("/users/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: full_name ?? null }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Register failed (${res.status}): ${text}`);
  }

  return (await res.json()) as RegisterOut;
}
