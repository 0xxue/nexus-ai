interface BadgeProps {
  children: React.ReactNode;
  color?: 'orange' | 'green' | 'red' | 'gray';
}

const colors = {
  orange: { bg: 'rgba(212, 82, 26, 0.1)', border: 'var(--orange)', text: 'var(--orange)' },
  green: { bg: 'rgba(58, 122, 58, 0.1)', border: 'var(--success)', text: 'var(--success)' },
  red: { bg: 'rgba(138, 32, 32, 0.1)', border: 'var(--error)', text: 'var(--error)' },
  gray: { bg: 'rgba(160, 144, 112, 0.1)', border: 'var(--dim)', text: 'var(--dim)' },
};

export function Badge({ children, color = 'orange' }: BadgeProps) {
  const c = colors[color];
  return (
    <span className="font-mono" style={{
      display: 'inline-block',
      padding: '2px 8px',
      border: `1px solid ${c.border}`,
      background: c.bg,
      color: c.text,
      fontSize: 10,
      letterSpacing: 0.5,
      textTransform: 'uppercase',
    }}>
      {children}
    </span>
  );
}
