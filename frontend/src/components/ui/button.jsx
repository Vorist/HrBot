import React from "react";
import "./styles.css";

export function Button({ children, onClick, disabled = false, variant = "default", size = "md", className = "", ...props }) {
  return (
    <button
      className={`btn ${variant} ${size} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
