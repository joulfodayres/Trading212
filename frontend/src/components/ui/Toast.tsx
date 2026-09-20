import React from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

const toastIcons = {
  success: <CheckCircle size={20} />,
  error: <AlertCircle size={20} />,
  warning: <AlertCircle size={20} />,
  info: <Info size={20} />,
};

interface ToastItemProps {
  toast: Toast;
  onClose: (id: string) => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(
      () => onClose(toast.id),
      toast.duration || 5000
    );
    return () => clearTimeout(timer);
  }, [toast, onClose]);

  return (
    <div className={`toast toast-${toast.type}`}>
      {toastIcons[toast.type]}
      <span className="flex-1">{toast.message}</span>
      <button
        onClick={() => onClose(toast.id)}
        className="toast-close"
      >
        <X size={16} />
      </button>
    </div>
  );
};

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onClose }) => {
  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <ToastItem
          key={toast.id}
          toast={toast}
          onClose={onClose}
        />
      ))}
    </div>
  );
};

// Hook to use toasts
let toastId = 0;
let listeners: ((toasts: Toast[]) => void)[] = [];
let toasts: Toast[] = [];

export const useToast = () => {
  const [, setToasts] = React.useState<Toast[]>([]);

  React.useEffect(() => {
    const listener = (newToasts: Toast[]) => {
      setToasts(newToasts);
    };
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  }, []);

  const addToast = (type: ToastType, message: string, duration?: number) => {
    const id = `toast-${toastId++}`;
    toasts = [...toasts, { id, type, message, duration }];
    listeners.forEach((listener) => listener([...toasts]));
  };

  const removeToast = (id: string) => {
    toasts = toasts.filter((t) => t.id !== id);
    listeners.forEach((listener) => listener([...toasts]));
  };

  return {
    success: (message: string, duration?: number) => addToast('success', message, duration),
    error: (message: string, duration?: number) => addToast('error', message, duration),
    warning: (message: string, duration?: number) => addToast('warning', message, duration),
    info: (message: string, duration?: number) => addToast('info', message, duration),
    toasts,
    removeToast,
  };
};

// Wrapper component to provide toasts in the app
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  React.useEffect(() => {
    const listener = (newToasts: Toast[]) => setToasts(newToasts);
    listeners = [listener];
    return () => {
      listeners = [];
    };
  }, []);

  return (
    <>
      {children}
      <ToastContainer
        toasts={toasts}
        onClose={(id) => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }}
      />
    </>
  );
};
