import "./styles.css";

export function Select({ value, onChange, options = [], className = "", ...props }) {
  return (
    <select
      className={`custom-select ${className}`}
      value={value}
      onChange={onChange}
      {...props}
    >
      {options.map((opt, idx) => (
        <option key={idx} value={opt.value || opt}>
          {opt.label || opt}
        </option>
      ))}
    </select>
  );
}
