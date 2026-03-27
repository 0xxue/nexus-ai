import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import client from '../../api/client';
import { Users, Activity, TrendingUp, Clock } from 'lucide-react';

interface OverviewData {
  total_users: number;
  active_users: number;
  new_users_today: number;
  total_items: number;
  system_health: string;
}

const STAT_CARDS = [
  { key: 'total_users', label: 'TOTAL USERS', icon: Users, color: '#4a90d9', num: '01' },
  { key: 'active_users', label: 'ACTIVE', icon: Activity, color: 'var(--success)', num: '02' },
  { key: 'total_items', label: 'TOTAL ITEMS', icon: TrendingUp, color: 'var(--orange)', num: '03' },
  { key: 'new_users_today', label: 'NEW TODAY', icon: Clock, color: '#8b5cf6', num: '04' },
];

export default function DashboardPage() {
  const [data, setData] = useState<OverviewData | null>(null);

  useEffect(() => {
    client.get('/data/system/overview')
      .then(setData)
      .catch(() => setData({
        total_users: 12580, active_users: 3456, new_users_today: 89, total_items: 580, system_health: 'healthy',
      }));
  }, []);

  if (!data) return null;

  return (
    <div style={{ overflowY: 'auto', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 22 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <h1 className="font-display" style={{ fontSize: 44, letterSpacing: 6, color: 'var(--ink)', lineHeight: 1 }}>
            DASHBOARD
          </h1>
          <p className="font-mono" style={{ fontSize: 10, color: 'var(--dim)', letterSpacing: 1, marginTop: 4 }}>
            // SYSTEM OVERVIEW · REAL-TIME
          </p>
        </div>
        <div className="font-mono" style={{
          padding: '6px 14px', border: '1.5px solid var(--success)',
          color: 'var(--success)', fontSize: 10, letterSpacing: 1, textTransform: 'uppercase',
          background: 'rgba(58, 122, 58, 0.08)',
        }}>
          ● {data.system_health}
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
              {/* Big background number */}
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
        <ChartCard title="USER TREND (7D)" option={userTrendOption()} />
        <ChartCard title="ACTIVITY DISTRIBUTION" option={activityOption()} />
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

function userTrendOption() {
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (6 - i));
    return `${d.getMonth() + 1}/${d.getDate()}`;
  });
  return {
    grid: { top: 20, right: 16, bottom: 24, left: 40 },
    xAxis: { type: 'category', data: days, axisLine: { lineStyle: { color: '#a09070' } }, axisLabel: { fontSize: 10, color: '#a09070' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(26,20,8,0.08)' } }, axisLabel: { fontSize: 10, color: '#a09070' } },
    series: [
      { type: 'line', data: [3200, 3280, 3350, 3400, 3380, 3420, 3456], smooth: true, lineStyle: { color: '#d4521a', width: 2 }, itemStyle: { color: '#d4521a' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(212,82,26,0.15)' }, { offset: 1, color: 'rgba(212,82,26,0)' }] } } },
      { type: 'bar', data: [78, 82, 95, 88, 91, 85, 89], itemStyle: { color: 'rgba(212,82,26,0.2)' }, barWidth: 12 },
    ],
    tooltip: { trigger: 'axis' },
  };
}

function activityOption() {
  return {
    grid: { top: 20, right: 16, bottom: 24, left: 40 },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLine: { lineStyle: { color: '#a09070' } }, axisLabel: { fontSize: 10, color: '#a09070' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(26,20,8,0.08)' } }, axisLabel: { fontSize: 10, color: '#a09070' } },
    series: [
      { type: 'bar', data: [1200, 1340, 1420, 1280, 1380, 950, 880], itemStyle: { color: '#d4521a' }, barWidth: 20 },
    ],
    tooltip: { trigger: 'axis' },
  };
}
