import "./styles.css";

export function Switch({ checked, onChange, className = "", ...props }) {
  return (
    <label className={`custom-switch ${className}`}>
      <input type="checkbox" checked={checked} onChange={onChange} {...props} />
      <span className="slider" />
    </label>
  );
}
