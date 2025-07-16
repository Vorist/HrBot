import "./styles.css";

export function Badge({ children, className = "", ...props }) {
  return (
    <span className={`custom-badge ${className}`} {...props}>
      {children}
    </span>
  );
}
