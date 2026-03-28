import { useState, useEffect } from 'react';
import client from '../../api/client';
import { toast } from '../../components/ui/Toast';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Users, Shield, Activity, MessageSquare, Bot, FileText, AlertTriangle } from 'lucide-react';

type Tab = 'users' | 'audit' | 'monitor' | 'bot';

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('users');

  const tabs: { id: Tab; label: string; icon: any }[] = [
    { id: 'users', label: 'USERS', icon: Users },
    { id: 'audit', label: 'AUDIT', icon: Shield },
    { id: 'monitor', label: 'MONITOR', icon: Activity },
    { id: 'bot', label: 'BOT TOOLS', icon: Bot },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '20px 32px 0', flexShrink: 0 }}>
        <h1 className="font-display" style={{ fontSize: 44, letterSpacing: 6, color: 'var(--ink)', lineHeight: 1 }}>ADMIN</h1>
        <p className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', letterSpacing: 1, marginTop: 4 }}>// SYSTEM MANAGEMENT</p>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4, marginTop: 16 }}>
          {tabs.map(t => {
            const Icon = t.icon;
            return (
              <button key={t.id} onClick={() => setTab(t.id)} className="font-mono"
                style={{
                  padding: '8px 16px', border: `2px solid ${tab === t.id ? 'var(--orange)' : 'var(--line)'}`,
                  background: tab === t.id ? 'rgba(212, 82, 26, 0.06)' : 'transparent',
                  color: tab === t.id ? 'var(--orange)' : 'var(--mid)',
                  fontSize: 10, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
                  letterSpacing: 1, transition: 'all 0.2s',
                }}>
                <Icon size={12} /> {t.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px 32px 32px' }}>
        {tab === 'users' && <UsersPanel />}
        {tab === 'audit' && <AuditPanel />}
        {tab === 'monitor' && <MonitorPanel />}
        {tab === 'bot' && <BotToolsPanel />}
      </div>
    </div>
  );
}

// ══════════════════════════════════════
// Users Panel
// ══════════════════════════════════════

function UsersPanel() {
  const [users, setUsers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [roleModal, setRoleModal] = useState<{ userId: number; username: string; currentRole: string } | null>(null);
  const [newRole, setNewRole] = useState('');

  useEffect(() => {
    client.get('/admin/users').then((data: any) => {
      setUsers(data.users || []);
      setTotal(data.total || 0);
    }).catch(() => toast('Failed to load users (admin only)', 'error'));
  }, []);

  const handleChangeRole = async () => {
    if (!roleModal || !newRole) return;
    try {
      await client.put(`/admin/users/${roleModal.userId}/role?role=${newRole}`);
      toast(`${roleModal.username} → ${newRole}`, 'success');
      setRoleModal(null);
      // Refresh
      const data: any = await client.get('/admin/users');
      setUsers(data.users || []);
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'Failed', 'error');
    }
  };

  const handleDelete = async (userId: number, username: string) => {
    if (!confirm(`Delete user "${username}"? This cannot be undone.`)) return;
    try {
      await client.delete(`/admin/users/${userId}`);
      toast(`${username} deleted`, 'info');
      setUsers(users.filter(u => u.id !== userId));
    } catch (err: any) {
      toast(err?.response?.data?.detail || 'Failed', 'error');
    }
  };

  const roleColor = (role: string) => role === 'admin' ? 'orange' : role === 'readonly' ? 'gray' : 'green';

  return (
    <div>
      <div className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', marginBottom: 12 }}>
        {total} users total
      </div>
      <div style={{ border: '2px solid var(--ink)' }}>
        {/* Header */}
        <div style={{ display: 'flex', padding: '10px 16px', borderBottom: '2px solid var(--ink)', background: 'var(--paper)' }}>
          <span className="font-mono" style={{ flex: 1, fontSize: 10, letterSpacing: 1 }}>USERNAME</span>
          <span className="font-mono" style={{ width: 200, fontSize: 10, letterSpacing: 1 }}>EMAIL</span>
          <span className="font-mono" style={{ width: 80, fontSize: 10, letterSpacing: 1 }}>ROLE</span>
          <span className="font-mono" style={{ width: 120, fontSize: 10, letterSpacing: 1 }}>ACTIONS</span>
        </div>
        {/* Rows */}
        {users.map(u => (
          <div key={u.id} className="animate-slide-in" style={{ display: 'flex', padding: '10px 16px', borderBottom: '1px solid var(--line)', alignItems: 'center' }}>
            <span style={{ flex: 1, fontSize: 13 }}>{u.username}</span>
            <span className="font-mono" style={{ width: 200, fontSize: 11, color: 'var(--mid)' }}>{u.email}</span>
            <span style={{ width: 80 }}><Badge color={roleColor(u.role)}>{u.role}</Badge></span>
            <span style={{ width: 120, display: 'flex', gap: 4 }}>
              <Button size="sm" variant="outline" onClick={() => { setRoleModal({ userId: u.id, username: u.username, currentRole: u.role }); setNewRole(u.role); }}>ROLE</Button>
              <Button size="sm" variant="ghost" onClick={() => handleDelete(u.id, u.username)} style={{ color: 'var(--error)' }}>DEL</Button>
            </span>
          </div>
        ))}
      </div>

      {/* Role change modal */}
      <Modal open={!!roleModal} onClose={() => setRoleModal(null)} title="CHANGE ROLE"
        actions={<>
          <Button variant="outline" onClick={() => setRoleModal(null)}>CANCEL</Button>
          <Button onClick={handleChangeRole}>SAVE</Button>
        </>}>
        <div style={{ marginBottom: 12 }}>
          Changing role for <strong>{roleModal?.username}</strong>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['admin', 'user', 'readonly'].map(r => (
            <button key={r} onClick={() => setNewRole(r)} className="font-mono"
              style={{
                padding: '8px 16px', border: `2px solid ${newRole === r ? 'var(--orange)' : 'var(--line)'}`,
                background: newRole === r ? 'rgba(212, 82, 26, 0.06)' : 'transparent',
                color: newRole === r ? 'var(--orange)' : 'var(--ink)',
                fontSize: 11, cursor: 'pointer', textTransform: 'uppercase',
              }}>
              {r}
            </button>
          ))}
        </div>
      </Modal>
    </div>
  );
}

// ══════════════════════════════════════
// Audit Panel
// ══════════════════════════════════════

function AuditPanel() {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    client.get('/admin/audit-logs?limit=50').then((data: any) => {
      setLogs(data.logs || []);
      setTotal(data.total || 0);
    }).catch(() => {});
  }, []);

  return (
    <div>
      <div className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', marginBottom: 12 }}>
        {total} audit entries
      </div>
      <div style={{ border: '2px solid var(--ink)' }}>
        <div style={{ display: 'flex', padding: '10px 16px', borderBottom: '2px solid var(--ink)', background: 'var(--paper)' }}>
          <span className="font-mono" style={{ width: 140, fontSize: 10, letterSpacing: 1 }}>TIME</span>
          <span className="font-mono" style={{ width: 80, fontSize: 10, letterSpacing: 1 }}>USER</span>
          <span className="font-mono" style={{ width: 100, fontSize: 10, letterSpacing: 1 }}>ACTION</span>
          <span className="font-mono" style={{ flex: 1, fontSize: 10, letterSpacing: 1 }}>QUERY</span>
          <span className="font-mono" style={{ width: 60, fontSize: 10, letterSpacing: 1 }}>CONF</span>
        </div>
        {logs.length === 0 ? (
          <div className="font-mono" style={{ padding: 20, textAlign: 'center', color: 'var(--dim)', fontSize: 11 }}>No audit logs yet</div>
        ) : logs.map((log, i) => (
          <div key={i} className="animate-slide-in" style={{ display: 'flex', padding: '8px 16px', borderBottom: '1px solid var(--line)', alignItems: 'center' }}>
            <span className="font-mono" style={{ width: 140, fontSize: 10, color: 'var(--dim)' }}>
              {log.created_at ? new Date(log.created_at).toLocaleString() : '-'}
            </span>
            <span style={{ width: 80, fontSize: 11 }}>{log.user_id || '-'}</span>
            <span style={{ width: 100 }}><Badge color="orange">{log.action}</Badge></span>
            <span style={{ flex: 1, fontSize: 11, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {log.query || log.answer_preview || '-'}
            </span>
            <span className="font-mono" style={{ width: 60, fontSize: 10, color: 'var(--dim)' }}>
              {log.confidence ? `${log.confidence}%` : '-'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════
// Monitor Panel
// ══════════════════════════════════════

function MonitorPanel() {
  const [health, setHealth] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    client.get('/health/detailed').then(setHealth).catch(() => {});
    client.get('/stats').then(setStats).catch(() => {});
  }, []);

  const refresh = () => {
    client.get('/health/detailed').then(setHealth).catch(() => {});
    client.get('/stats').then(setStats).catch(() => {});
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="font-mono" style={{ fontSize: 10, color: 'var(--dim)' }}>// REAL-TIME SYSTEM HEALTH</span>
        <Button size="sm" variant="outline" onClick={refresh}>REFRESH</Button>
      </div>

      {/* Health Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <HealthCard label="DATABASE" status={health?.dependencies?.postgresql} />
        <HealthCard label="REDIS" status={health?.dependencies?.redis} />
        <HealthCard label="OVERALL" status={health?.status} />
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ border: '2px solid var(--ink)', padding: 16 }}>
          <div className="font-display" style={{ fontSize: 16, letterSpacing: 3, marginBottom: 12 }}>SYSTEM STATS</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            <StatItem icon={Users} label="Users" value={stats.total_users} />
            <StatItem icon={MessageSquare} label="Conversations" value={stats.total_conversations} />
            <StatItem icon={FileText} label="Messages" value={stats.total_messages} />
            <StatItem icon={FileText} label="KB Documents" value={stats.total_documents} />
            <StatItem icon={Shield} label="Collections" value={stats.total_collections} />
            <StatItem icon={Activity} label="Uptime" value={`${Math.floor((stats.uptime_seconds || 0) / 60)}m`} />
          </div>
        </div>
      )}
    </div>
  );
}

function HealthCard({ label, status }: { label: string; status?: string }) {
  const isOk = status === 'healthy' || status === 'ok';
  return (
    <div className="animate-card-in" style={{ border: '2px solid var(--ink)', padding: 16, textAlign: 'center' }}>
      <div style={{ fontSize: 28, marginBottom: 8 }}>{isOk ? '🟢' : status ? '🔴' : '⚪'}</div>
      <div className="font-display" style={{ fontSize: 14, letterSpacing: 2 }}>{label}</div>
      <div className="font-mono" style={{ fontSize: 10, color: isOk ? 'var(--success)' : 'var(--error)', marginTop: 4 }}>
        {status || 'Unknown'}
      </div>
    </div>
  );
}

function StatItem({ icon: Icon, label, value }: { icon: any; label: string; value: any }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <Icon size={14} color="var(--orange)" />
      <div>
        <div className="font-mono" style={{ fontSize: 9, color: 'var(--dim)' }}>{label}</div>
        <div className="font-display" style={{ fontSize: 20 }}>{value ?? 0}</div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════
// Bot Tools Panel
// ══════════════════════════════════════

function BotToolsPanel() {
  const tools = [
    { name: 'get_system_stats', desc: 'Get system statistics', role: 'user', category: 'Data' },
    { name: 'get_metrics_summary', desc: 'Get business metrics', role: 'user', category: 'Data' },
    { name: 'get_user_stats', desc: 'Get user statistics', role: 'user', category: 'Data' },
    { name: 'get_expiring_items', desc: 'Get expiring items', role: 'user', category: 'Data' },
    { name: 'create_kb_collection', desc: 'Create knowledge base', role: 'user', category: 'KB' },
    { name: 'list_kb_collections', desc: 'List knowledge bases', role: 'user', category: 'KB' },
    { name: 'search_knowledge_base', desc: 'Search documents', role: 'user', category: 'KB' },
    { name: 'list_conversations', desc: 'List conversations', role: 'user', category: 'Chat' },
    { name: 'delete_conversation', desc: 'Delete conversation', role: 'user', category: 'Chat' },
    { name: 'ask_qa_system', desc: 'Ask QA system', role: 'user', category: 'Chat' },
    { name: 'list_users', desc: 'List all users', role: 'admin', category: 'Admin' },
    { name: 'change_user_role', desc: 'Change user role', role: 'admin', category: 'Admin' },
    { name: 'health_check', desc: 'Check system health', role: 'user', category: 'System' },
  ];

  const [enabled, setEnabled] = useState<Record<string, boolean>>(() => {
    const saved = localStorage.getItem('bot_tools_config');
    if (saved) return JSON.parse(saved);
    return Object.fromEntries(tools.map(t => [t.name, true]));
  });

  const toggle = (name: string) => {
    const next = { ...enabled, [name]: !enabled[name] };
    setEnabled(next);
    localStorage.setItem('bot_tools_config', JSON.stringify(next));
    toast(`${name}: ${next[name] ? 'enabled' : 'disabled'}`, 'info');
  };

  const categories = [...new Set(tools.map(t => t.category))];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="font-mono" style={{ fontSize: 10, color: 'var(--dim)' }}>
        // BOT CAN CALL THESE TOOLS VIA LLM FUNCTION CALLING
      </div>

      {categories.map(cat => (
        <div key={cat} style={{ border: '2px solid var(--ink)', padding: 16 }}>
          <div className="font-display" style={{ fontSize: 14, letterSpacing: 2, marginBottom: 12 }}>{cat.toUpperCase()}</div>
          {tools.filter(t => t.category === cat).map(tool => (
            <div key={tool.name} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0',
              borderBottom: '1px solid var(--line)',
            }}>
              <input type="checkbox" checked={enabled[tool.name] !== false}
                onChange={() => toggle(tool.name)}
                style={{ width: 16, height: 16, accentColor: 'var(--orange)' }} />
              <div style={{ flex: 1 }}>
                <div className="font-mono" style={{ fontSize: 12 }}>{tool.name}</div>
                <div style={{ fontSize: 11, color: 'var(--mid)' }}>{tool.desc}</div>
              </div>
              <Badge color={tool.role === 'admin' ? 'orange' : 'green'}>{tool.role}</Badge>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
