import "./styles.css";

export function Textarea({ value, onChange, placeholder = "", className = "", ...props }) {
  return (
    <textarea
      className={`custom-textarea ${className}`}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      {...props}
    />
  );
}
