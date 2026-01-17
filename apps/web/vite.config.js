import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      "/login": "http://localhost:8001",
      "/users": "http://localhost:8002",
      "/items": "http://localhost:8003",
      "/reservations": "http://localhost:8004",
      "/notifications": "http://localhost:8005",
      "/chat": "http://localhost:8006",
      "/delivery": "http://localhost:8007",
      "/search": "http://localhost:8008",
      "/reputation": "http://localhost:8009",
      "/traceability": "http://localhost:8010",
    },
  },
});