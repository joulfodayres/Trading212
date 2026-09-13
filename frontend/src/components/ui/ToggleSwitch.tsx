import React from 'react';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
}

export const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked,
  onChange,
  disabled = false,
  label
}) => {
  return (
    <label className="flex items-center gap-3 cursor-pointer">
      <div className={`toggle-switch ${checked ? 'on' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => !disabled && onChange(e.target.checked)}
          disabled={disabled}
        />
        <span className="toggle-slider" />
      </div>
      {label && <span className="text-t212-primary">{label}</span>}
    </label>
  );
};
