import { apiFetch } from "./client.js";

export function register(email, password, full_name) {
  return apiFetch("/users/register", {
    method: "POST",
    body: { email, password, full_name },
  });
}