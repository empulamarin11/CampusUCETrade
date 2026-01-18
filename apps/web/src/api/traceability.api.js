import { apiFetch } from "./client.js";

export function listAudit(token) {
  return apiFetch("/traceability/audit", { method: "GET", token });
}

export function seedAudit(token) {
  return apiFetch("/traceability/audit/seed", { method: "POST", token });
}
