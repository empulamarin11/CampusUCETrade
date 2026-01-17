import { apiFetch } from "./client.js";

export function searchItems(q) {
  // Trailing slash avoids FastAPI redirect
  const qs = new URLSearchParams({ q: q ?? "" }).toString();
  return apiFetch(`/search/?${qs}`, { method: "GET" });
}
