// frontend/src/components/ui/card.jsx
import React from 'react';
import './Card.css'; // якщо є стилі

export function Card({ children, className = '', ...props }) {
  return (
    <div className={`custom-card ${className}`} {...props}>
      {children}
    </div>
  );
}
