// frontend/src/main.jsx

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// ✅ Підключення власного стилю (без Tailwind)
import "./index.css";

// 🔍 Отримуємо root-елемент з index.html
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("❌ Елемент з id='root' не знайдено у index.html");
}

// 🚀 Створення root і рендер у StrictMode
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
