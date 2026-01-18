import { apiFetch } from "./client.js";

export function listItems() {
  // Important: trailing slash avoids FastAPI redirect (CORS issue)
  return apiFetch("/items/", { method: "GET" });
}

export function createItem(token, payload) {
  return apiFetch("/items/", { method: "POST", token, body: payload });
}

export function presignItemMedia(token, itemId, contentType) {
  return apiFetch(`/items/${itemId}/media/presign?content_type=${encodeURIComponent(contentType)}`, {
    method: "POST",
    token,
  });
}