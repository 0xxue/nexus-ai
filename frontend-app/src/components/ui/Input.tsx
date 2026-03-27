import { type InputHTMLAttributes, type TextareaHTMLAttributes, forwardRef } from 'react';

const inputStyle: React.CSSProperties = {
  width: '100%',
  background: 'none',
  border: '2px solid var(--ink)',
  outline: 'none',
  padding: '10px 12px',
  fontFamily: "'IBM Plex Mono', monospace",
  fontSize: 13,
  color: 'var(--ink)',
};

const focusColor = 'var(--orange)';

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{ ...inputStyle, ...props.style }}
      onFocus={e => { e.target.style.borderColor = focusColor; props.onFocus?.(e); }}
      onBlur={e => { e.target.style.borderColor = 'var(--ink)'; props.onBlur?.(e); }}
    />
  );
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  (props, ref) => (
    <textarea
      ref={ref}
      {...props}
      style={{
        ...inputStyle,
        resize: 'none',
        lineHeight: 1.5,
        ...props.style,
      }}
      onFocus={e => { e.target.style.borderColor = focusColor; props.onFocus?.(e); }}
      onBlur={e => { e.target.style.borderColor = 'var(--ink)'; props.onBlur?.(e); }}
    />
  )
);
