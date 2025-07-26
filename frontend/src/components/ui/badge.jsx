import React from 'react';
import './Badge.css';

const Badge = ({ children, type = 'default', className = '' }) => {
  return (
    <span className={`badge badge-${type} ${className}`}>
      {children}
    </span>
  );
};

export default Badge;
