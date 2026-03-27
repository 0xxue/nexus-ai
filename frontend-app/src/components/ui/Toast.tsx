import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
  leaving?: boolean;
}

interface ToastCtx {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastCtx>({ toast: () => {} });

export const useToast = () => useContext(ToastContext);

let _toastFn: ToastCtx['toast'] = () => {};
/** Call toast() from anywhere (outside React tree) */
export const toast = (message: string, type?: ToastType) => _toastFn(message, type);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.map(t => t.id === id ? { ...t, leaving: true } : t));
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300);
    }, 3000);
  }, []);

  _toastFn = addToast;

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div style={{ position: 'fixed', top: 20, right: 20, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

/** Standalone container (no provider needed) */
export function ToastContainer() {
  return <ToastProvider>{null}</ToastProvider>;
}

const typeColors: Record<ToastType, string> = {
  success: 'var(--success)',
  error: 'var(--error)',
  info: 'var(--orange)',
};

function ToastItem({ toast: t }: { toast: Toast }) {
  return (
    <div
      className="font-mono"
      style={{
        padding: '10px 18px',
        border: '2px solid var(--ink)',
        background: 'var(--cream)',
        fontSize: 12,
        color: typeColors[t.type],
        boxShadow: `3px 3px 0 ${typeColors[t.type]}`,
        animation: t.leaving ? 'toastOut 0.3s ease forwards' : 'toastIn 0.35s ease',
        maxWidth: 320,
      }}
    >
      {t.message}
    </div>
  );
}
