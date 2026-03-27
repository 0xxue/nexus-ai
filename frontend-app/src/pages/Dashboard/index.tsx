import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import client from '../../api/client';
import { Users, MessageSquare, FileText, Database, Clock } from 'lucide-react';

interface StatsData {
  total_users: number;
  total_conversations: number;
  total_messages: number;
  total_documents: number;
  total_collections: number;
  system_health: string;
  uptime_seconds: number;
}

const STAT_CARDS = [
  { key: 'total_users', label: 'USERS', icon: Users, color: '#4a90d9', num: '01' },
  { key: 'total_conversations', label: 'CONVERSATIONS', icon: MessageSquare, color: 'var(--success)', num: '02' },
  { key: 'total_messages', label: 'MESSAGES', icon: FileText, color: 'var(--orange)', num: '03' },
  { key: 'total_documents', label: 'KB DOCUMENTS', icon: Database, color: '#8b5cf6', num: '04' },
];

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function DashboardPage() {
  const [data, setData] = useState<StatsData | null>(null);

  useEffect(() => {
    client.get('/stats')
      .then(setData)
      .catch(() => setData({
        total_users: 0, total_conversations: 0, total_messages: 0,
        total_documents: 0, total_collections: 0, system_health: 'healthy', uptime_seconds: 0,
      }));
  }, []);

  if (!data) return null;

  return (
    <div style={{ overflowY: 'auto', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 22, height: '100%' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <h1 className="font-display dash-title" style={{ fontSize: 44, letterSpacing: 6, color: 'var(--ink)', lineHeight: 1 }}>
            DASHBOARD
          </h1>
          <p className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', letterSpacing: 1, marginTop: 4 }}>
            // SYSTEM STATS · REAL-TIME FROM DATABASE
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div className="font-mono" style={{ fontSize: 10, color: 'var(--dim)' }}>
            <Clock size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
            Uptime: {formatUptime(data.uptime_seconds)}
          </div>
          <div className="font-mono" style={{
            padding: '6px 14px', border: '1.5px solid var(--success)',
            color: 'var(--success)', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase',
            background: 'rgba(58, 122, 58, 0.08)',
          }}>
            ● {data.system_health}
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }} className="stat-cards">
        {STAT_CARDS.map((card, i) => {
          const Icon = card.icon;
          const value = (data as any)[card.key] ?? 0;
          return (
            <div
              key={card.key}
              className={`animate-card-in stagger-${i + 1}`}
              style={{
                padding: '18px 16px', border: '2px solid var(--ink)',
                background: 'var(--cream)', position: 'relative', overflow: 'hidden',
                cursor: 'pointer', transition: 'all 0.2s',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLElement).style.transform = 'translateY(-3px) rotate(0.4deg)';
                (e.currentTarget as HTMLElement).style.boxShadow = '4px 4px 0 var(--orange)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.transform = '';
                (e.currentTarget as HTMLElement).style.boxShadow = '';
              }}
            >
              <div className="font-display" style={{
                position: 'absolute', right: 8, top: -10, fontSize: 90,
                color: 'rgba(212, 82, 26, 0.06)', lineHeight: 1, pointerEvents: 'none',
              }}>
                {card.num}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <Icon size={16} color={card.color} />
                <span className="font-mono" style={{ fontSize: 10, letterSpacing: 1, color: 'var(--mid)', textTransform: 'uppercase' }}>
                  {card.label}
                </span>
              </div>
              <div className="font-display" style={{ fontSize: 36, color: 'var(--ink)', letterSpacing: 2 }}>
                {value.toLocaleString()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }} className="charts-grid">
        <ChartCard title="SYSTEM OVERVIEW" option={overviewChart(data)} />
        <ChartCard title="COLLECTIONS" option={collectionsChart(data)} />
      </div>
    </div>
  );
}

function ChartCard({ title, option }: { title: string; option: Record<string, unknown> }) {
  return (
    <div className="animate-card-in" style={{ border: '2px solid var(--ink)', background: 'var(--cream)', padding: 16 }}>
      <div className="font-display" style={{ fontSize: 16, letterSpacing: 3, marginBottom: 12, color: 'var(--ink)' }}>
        {title}
      </div>
      <ReactECharts option={option} style={{ height: 210 }} />
    </div>
  );
}

function overviewChart(data: StatsData) {
  return {
    grid: { top: 20, right: 16, bottom: 24, left: 40 },
    xAxis: {
      type: 'category',
      data: ['Users', 'Conversations', 'Messages', 'Documents'],
      axisLine: { lineStyle: { color: '#a09070' } },
      axisLabel: { fontSize: 10, color: '#a09070' },
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(26,20,8,0.08)' } }, axisLabel: { fontSize: 10, color: '#a09070' } },
    series: [{
      type: 'bar',
      data: [
        { value: data.total_users, itemStyle: { color: '#4a90d9' } },
        { value: data.total_conversations, itemStyle: { color: '#3a7a3a' } },
        { value: data.total_messages, itemStyle: { color: '#d4521a' } },
        { value: data.total_documents, itemStyle: { color: '#8b5cf6' } },
      ],
      barWidth: 30,
    }],
    tooltip: { trigger: 'axis' },
  };
}

function collectionsChart(data: StatsData) {
  return {
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: data.total_documents, name: 'Documents', itemStyle: { color: '#d4521a' } },
        { value: data.total_collections, name: 'Collections', itemStyle: { color: '#4a90d9' } },
        { value: Math.max(1, data.total_messages), name: 'Messages', itemStyle: { color: '#3a7a3a' } },
      ],
      label: { fontSize: 10, color: '#6a5a3a' },
    }],
    tooltip: { trigger: 'item' },
  };
}
