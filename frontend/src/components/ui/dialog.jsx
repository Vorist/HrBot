import "./styles.css";

export function Dialog({ isOpen, onClose, children, className = "", ...props }) {
  if (!isOpen) return null;

  return (
    <div className="custom-dialog-backdrop" onClick={onClose}>
      <div className={`custom-dialog ${className}`} onClick={(e) => e.stopPropagation()} {...props}>
        {children}
      </div>
    </div>
  );
}