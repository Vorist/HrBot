// frontend/vite.config.js

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// 📦 Конфігурація Vite
export default defineConfig({
  plugins: [
    react({
      // 💡 Активує fast refresh + dev warnings
      jsxRuntime: "automatic",
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"), // 🧭 Дозволяє імпорти типу "@/components/..."
    },
  },
  server: {
    port: 5173,       // 🌐 Порт для локального dev-сервера
    open: true,       // 🚀 Автоматично відкривати браузер
    cors: true,       // ✅ Дозволити CORS
  },
  build: {
    outDir: "dist",        // 📂 Куди зберігати production-збірку
    emptyOutDir: true,     // 🧹 Чистити папку перед білдом
    sourcemap: true,       // 🐞 Додати мапи для дебагу у проді
    target: "esnext",      // 📈 Можна використовувати сучасний JS
  },
});
