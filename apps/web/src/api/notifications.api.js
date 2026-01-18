import { apiFetch } from "./client.js";

export function listNotifications(token) {
  return apiFetch("/notifications/", { method: "GET", token });
}

export function markRead(token, notificationId) {
  return apiFetch(`/notifications/${notificationId}/read`, { method: "PATCH", token });
}
