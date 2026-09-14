import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Прокси на backend в dev-режиме: браузер ходит на тот же origin,
// поэтому CORS и ключи остаются проблемой только сервера.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
