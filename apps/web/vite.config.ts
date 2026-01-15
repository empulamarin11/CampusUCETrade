import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": { target: "http://localhost:8001", changeOrigin: true },
      "/users": { target: "http://localhost:8002", changeOrigin: true },
    },
  },
});
