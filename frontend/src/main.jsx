// frontend/src/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// ✅ Підключення кастомного CSS без Tailwind
import "./index.css";

// 🔍 Знаходимо елемент з id="root"
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("❌ Не знайдено елемент з id='root' у index.html");
}

// 🚀 Рендер додатку
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
