import "./styles.css";

export function Card({ children, className = "", ...props }) {
  return (
    <div className={`custom-card ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardContent({ children, className = "", ...props }) {
  return (
    <div className={`custom-card-content ${className}`} {...props}>
      {children}
    </div>
  );
}
