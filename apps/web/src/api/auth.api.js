import { apiFetch } from "./client.js";

export function login(email, password) {
  // If your endpoint is /auth/token, change this path
  return apiFetch("/login", {
    method: "POST",
    body: { email, password },
  });
}