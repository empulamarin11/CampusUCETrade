import { apiFetch } from "./client.js";

export function createReservation(token, payload) {
  return apiFetch("/reservations/", { method: "POST", token, body: payload });
}

export function listReservations(token) {
  return apiFetch("/reservations/", { method: "GET", token });
}
