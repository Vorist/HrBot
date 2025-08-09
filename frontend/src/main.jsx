// frontend/src/main.jsx

import React, { Component } from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";
import App from "./App";
import "./index.css";

// ——————————————————————————————————————————————————————————
// 1. Configure Axios default base URL (uses Vite env or falls back to /api)
axios.defaults.baseURL = import.meta.env.VITE_API_URL || "/api";
// Example in `.env` you can set: VITE_API_URL=http://localhost:8000/api
// ——————————————————————————————————————————————————————————

// 2. Simple ErrorBoundary component
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(err) {
    return { hasError: true, error: err };
  }

  componentDidCatch(err, info) {
    // You could log to an external service here
    console.error("Uncaught error:", err, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24, textAlign: "center" }}>
          <h1>😞 Щось пішло не так.</h1>
          <p>{this.state.error?.toString()}</p>
          <button onClick={() => window.location.reload()}>🔄 Перезавантажити</button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ——————————————————————————————————————————————————————————
// 3. Mount the application
const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("❌ Елемент з id='root' не знайдено у index.html");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
