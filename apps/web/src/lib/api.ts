async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function healthAuth(): Promise<{ status: string }> {
  const res = await fetch(`/auth/health`);
  return json(res);
}

export async function healthUser(): Promise<{ status: string }> {
  const res = await fetch(`/users/health`);
  return json(res);
}
