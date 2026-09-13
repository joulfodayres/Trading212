import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = '', ...props }, ref) => {
    return (
      <div className="form-group">
        {label && (
          <label className="form-label">
            {label}
            {props.required && <span className="text-t212-error">*</span>}
          </label>
        )}
        <input
          ref={ref}
          className={`input ${error ? 'border-t212-error focus:ring-t212-error' : ''} ${className}`}
          {...props}
        />
        {error && <div className="form-error">{error}</div>}
        {hint && !error && <div className="text-t212-muted text-xs mt-1">{hint}</div>}
      </div>
    );
  }
);

Input.displayName = 'Input';
