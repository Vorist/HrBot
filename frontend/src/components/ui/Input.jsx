// frontend/src/components/ui/Input.jsx
import React from 'react';
import './Input.css'; // якщо є стилі

export function Input({ value, onChange, placeholder, ...props }) {
  return (
    <input
      className="custom-input"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      {...props}
    />
  );
}
