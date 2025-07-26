// frontend/src/components/ui/textarea.jsx
import React from 'react';
import './Textarea.css'; // якщо є стилі

export function Textarea({ value, onChange, placeholder, ...props }) {
  return (
    <textarea
      className="custom-textarea"
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      {...props}
    />
  );
}
