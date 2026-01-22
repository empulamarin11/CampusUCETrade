import { apiFetch } from "./client.js";

export function listRooms() {
  return apiFetch("/chat/rooms", { method: "GET" });
}

export function listMessages(room = "general", limit = 50) {
  const qs = new URLSearchParams({ room, limit: String(limit) }).toString();
  return apiFetch(`/chat/messages?${qs}`, { method: "GET" });
}
