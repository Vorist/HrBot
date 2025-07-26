import React from 'react';
import './Switch.css';

const Switch = ({ checked, onChange, label = '', className = '' }) => {
  return (
    <label className={`custom-switch ${className}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="switch-input"
      />
      <span className="switch-slider" />
      {label && <span className="switch-label">{label}</span>}
    </label>
  );
};

export default Switch;
