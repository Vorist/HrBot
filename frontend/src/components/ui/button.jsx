// frontend/src/components/ui/button.jsx
import React from 'react';
import './Button.css'; // якщо є стилі

export function Button({ children, onClick, type = 'button', className = '', ...props }) {
  return (
    <button
      type={type}
      onClick={onClick}
      className={`custom-button ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
