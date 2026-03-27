import { type ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'ghost';
  size?: 'sm' | 'md';
}

export function Button({ variant = 'primary', size = 'md', style, children, ...props }: ButtonProps) {
  const base: React.CSSProperties = {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: size === 'sm' ? 10 : 12,
    letterSpacing: 1,
    textTransform: 'uppercase',
    cursor: 'pointer',
    transition: 'all 0.2s',
    border: '2px solid var(--ink)',
    padding: size === 'sm' ? '6px 12px' : '10px 18px',
  };

  const variants: Record<string, React.CSSProperties> = {
    primary: { background: 'var(--orange)', color: 'var(--cream)', borderColor: 'var(--orange)' },
    outline: { background: 'var(--cream)', color: 'var(--ink)' },
    ghost: { background: 'transparent', color: 'var(--mid)', border: 'none', padding: size === 'sm' ? '4px 8px' : '8px 12px' },
  };

  return (
    <button style={{ ...base, ...variants[variant], ...style }} {...props}>
      {children}
    </button>
  );
}
