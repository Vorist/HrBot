// frontend/vite.config.js

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), // Поддержка '@/components/...'
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    open: true,
    proxy: {
      // Все запросы /api/* идут на FastAPI (localhost:8000)
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        // pathRewrite: { "^/api": "" }, // НЕ включать!
      },
    },
  },
  plugins: [
    react({
      jsxRuntime: "automatic",
    }),
  ],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    target: "esnext",
  },
});
