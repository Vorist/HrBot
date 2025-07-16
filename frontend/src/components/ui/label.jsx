import "./styles.css";

export function Label({ htmlFor, children, className = "", ...props }) {
  return (
    <label htmlFor={htmlFor} className={`custom-label ${className}`} {...props}>
      {children}
    </label>
  );
}