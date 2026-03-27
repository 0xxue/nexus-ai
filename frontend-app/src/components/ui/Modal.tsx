import { type ReactNode } from 'react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  actions?: ReactNode;
}

export function Modal({ open, onClose, title, children, actions }: ModalProps) {
  if (!open) return null;

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 8000,
        background: 'rgba(26, 20, 8, 0.6)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        animation: 'fadeIn 0.2s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: 360, padding: 28, border: '2px solid var(--ink)',
          background: 'var(--cream)', boxShadow: '8px 8px 0 var(--orange)',
          animation: 'cardIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <h3 className="font-display" style={{ fontSize: 24, letterSpacing: 3, marginBottom: 16, color: 'var(--ink)' }}>
          {title}
        </h3>
        <div style={{ marginBottom: 20 }}>{children}</div>
        {actions && (
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
