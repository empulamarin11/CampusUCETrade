import { apiFetch } from "./client.js";

export function getReputation(token, userEmail) {
  return apiFetch(`/reputation/reputation/${encodeURIComponent(userEmail)}`, {
    method: "GET",
    token,
  });
}

export function rateUser(token, payload) {
  return apiFetch("/reputation/reputation/rate", {
    method: "POST",
    token,
    body: payload,
  });
}
