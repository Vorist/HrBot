import React from 'react';
import './Select.css';

const Select = ({ options = [], value, onChange, placeholder = '', className = '' }) => {
  return (
    <select
      value={value}
      onChange={onChange}
      className={`custom-select ${className}`}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {options.map((opt, idx) => (
        <option key={idx} value={opt.value || opt}>
          {opt.label || opt}
        </option>
      ))}
    </select>
  );
};

export default Select;
