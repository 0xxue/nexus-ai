import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import ChatPage from './pages/Chat';
import KnowledgeBasePage from './pages/KnowledgeBase';
import DashboardPage from './pages/Dashboard';
import { MessageSquare, Database, BarChart3 } from 'lucide-react';

function Sidebar() {
  const links = [
    { to: '/chat', icon: MessageSquare, label: '对话' },
    { to: '/kb', icon: Database, label: '知识库' },
    { to: '/dashboard', icon: BarChart3, label: '看板' },
  ];

  return (
    <div className="w-16 bg-gray-900 flex flex-col items-center py-4 gap-2">
      <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold mb-4">
        AI
      </div>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            `w-12 h-12 rounded-xl flex flex-col items-center justify-center gap-0.5 transition-colors ${
              isActive ? 'bg-gray-700 text-white' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
            }`
          }
        >
          <link.icon size={20} />
          <span className="text-[10px]">{link.label}</span>
        </NavLink>
      ))}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/kb" element={<KnowledgeBasePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
