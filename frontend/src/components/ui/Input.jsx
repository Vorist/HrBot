import "./styles.css";

export function Input({ value, onChange, type = "text", placeholder = "", className = "", ...props }) {
  return (
    <input
      type={type}
      className={`custom-input ${className}`}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      {...props}
    />
  );
}