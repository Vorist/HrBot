import React from 'react';
import './Label.css';

const Label = ({ children, htmlFor = '', className = '' }) => {
  return (
    <label htmlFor={htmlFor} className={`custom-label ${className}`}>
      {children}
    </label>
  );
};

export default Label;
