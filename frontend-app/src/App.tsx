import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ChatPage from './pages/Chat';
import KnowledgeBasePage from './pages/KnowledgeBase';
import DashboardPage from './pages/Dashboard';
import { ToastContainer } from './components/ui/Toast';
import { BotContainer } from './components/bot/BotContainer';
import { MessageSquare, Database, BarChart3, Settings } from 'lucide-react';

/* ══════════════════════════════════════
   NEXUS Sidebar
══════════════════════════════════════ */

function Sidebar() {
  const links = [
    { to: '/chat', icon: MessageSquare, label: 'Chat' },
    { to: '/kb', icon: Database, label: 'Know' },
    { to: '/dashboard', icon: BarChart3, label: 'Dash' },
  ];

  return (
    <>
      {/* Desktop sidebar */}
      <nav className="sidebar-desktop" style={{
        width: 80, height: '100%', borderRight: '2px solid var(--ink)',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        padding: '24px 0', background: 'var(--cream)', position: 'relative',
      }}>
        {/* Vertical title */}
        <div className="font-display" style={{
          writingMode: 'vertical-rl', textOrientation: 'mixed',
          transform: 'rotate(180deg)', fontSize: 28, letterSpacing: 8,
          color: 'var(--ink)', marginBottom: 'auto',
        }}>
          NEXUS
        </div>

        {/* Nav items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 'auto', paddingBottom: 8 }}>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              style={({ isActive }) => ({
                width: 48, height: 48, display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', gap: 2,
                border: '2px solid transparent', borderRadius: 4, cursor: 'pointer',
                transition: 'all 0.2s', color: isActive ? 'var(--orange)' : 'var(--mid)',
                borderColor: isActive ? 'var(--orange)' : 'transparent',
                background: isActive ? 'rgba(212, 82, 26, 0.08)' : 'transparent',
                textDecoration: 'none',
              })}
            >
              <link.icon size={18} />
              <span className="font-mono" style={{ fontSize: 8, letterSpacing: 1, textTransform: 'uppercase' }}>
                {link.label}
              </span>
            </NavLink>
          ))}
        </div>

        {/* Status indicator */}
        <div className="font-mono" style={{
          position: 'absolute', bottom: 12, fontSize: 9, color: 'var(--dim)',
          writingMode: 'vertical-rl', transform: 'rotate(180deg)', letterSpacing: 1,
        }}>
          <span style={{ color: '#22c55e' }}>●</span> ONLINE
        </div>
      </nav>

      {/* Mobile bottom bar */}
      <nav className="sidebar-mobile" style={{
        width: '100%', height: 56, borderTop: '2px solid var(--ink)',
        flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around',
        padding: '0 8px', background: 'var(--cream)', order: 1,
      }}>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            style={({ isActive }) => ({
              width: 44, height: 44, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', gap: 2,
              border: '2px solid transparent', borderRadius: 4,
              color: isActive ? 'var(--orange)' : 'var(--mid)',
              borderColor: isActive ? 'var(--orange)' : 'transparent',
              textDecoration: 'none',
            })}
          >
            <link.icon size={18} />
            <span className="font-mono" style={{ fontSize: 8 }}>{link.label}</span>
          </NavLink>
        ))}
      </nav>
    </>
  );
}

/* ══════════════════════════════════════
   Top Strip
══════════════════════════════════════ */

function TopStrip() {
  const location = useLocation();
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(t);
  }, []);

  const titles: Record<string, string> = {
    '/chat': 'MISSION: DATA QUERY',
    '/kb': 'KNOWLEDGE BASE OPS',
    '/dashboard': 'SYSTEM DASHBOARD',
  };

  return (
    <div style={{
      height: 42, borderBottom: '2px solid var(--ink)', display: 'flex',
      alignItems: 'center', padding: '0 20px', background: 'var(--cream)',
      flexShrink: 0,
    }}>
      <span className="font-display" style={{ fontSize: 16, letterSpacing: 4, color: 'var(--ink)' }}>
        {titles[location.pathname] || 'NEXUS SYSTEM'}
      </span>
      <div style={{ flex: 1 }} />
      <span className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', letterSpacing: 1 }}>
        {time}
      </span>
    </div>
  );
}

/* ══════════════════════════════════════
   App Root
══════════════════════════════════════ */

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ position: 'fixed', inset: 0, zIndex: 2, display: 'flex' }}>
        <Sidebar />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <TopStrip />
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <Routes>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/kb" element={<KnowledgeBasePage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </div>
        </div>
      </div>
      <BotContainer />
      <ToastContainer />
    </BrowserRouter>
  );
}
