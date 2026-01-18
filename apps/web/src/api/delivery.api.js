import { apiFetch } from "./client.js";

export function createDelivery(token, payload) {
  return apiFetch("/delivery/deliveries", { method: "POST", token, body: payload });
}

export function getDelivery(token, deliveryId) {
  return apiFetch(`/delivery/deliveries/${encodeURIComponent(deliveryId)}`, {
    method: "GET",
    token,
  });
}

/**
 * Confirm endpoint sometimes returns text/plain (a string), not JSON.
 * So we parse safely.
 */
export async function confirmDelivery(token, deliveryId) {
  const res = await fetch(`/delivery/deliveries/${encodeURIComponent(deliveryId)}/confirm`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const ct = res.headers.get("content-type") || "";
  const body = ct.includes("application/json") ? await res.json() : await res.text();

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${typeof body === "string" ? body : JSON.stringify(body)}`);
  }

  return body;
}
