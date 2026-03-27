import { useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import client from '../../api/client';
import { Activity, Users, DollarSign, Clock } from 'lucide-react';

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res: any = await client.get('/data/system/overview');
      setOverview(res);
    } catch {}
  };

  const stats = overview ? [
    { icon: Users, label: '总用户', value: overview.total_users?.toLocaleString() || '—', color: 'bg-blue-50 text-blue-600' },
    { icon: Activity, label: '活跃用户', value: overview.active_users?.toLocaleString() || '—', color: 'bg-green-50 text-green-600' },
    { icon: DollarSign, label: '资金余额', value: overview.total_funds ? `¥${(overview.total_funds / 10000).toFixed(0)}万` : '—', color: 'bg-yellow-50 text-yellow-700' },
    { icon: Clock, label: '可运行天数', value: overview.daily_consumption ? `${Math.floor(overview.total_funds / overview.daily_consumption)}天` : '—', color: 'bg-purple-50 text-purple-600' },
  ] : [];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">数据看板</h1>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {stats.map((s, i) => (
          <div key={i} className="bg-white rounded-xl p-5 border">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${s.color}`}>
              <s.icon size={20} />
            </div>
            <div className="text-2xl font-bold">{s.value}</div>
            <div className="text-sm text-gray-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-5 border">
          <h3 className="font-semibold mb-4">用户趋势（近7天）</h3>
          <ReactECharts
            option={{
              tooltip: { trigger: 'axis' },
              xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
              yAxis: { type: 'value' },
              series: [
                { name: '活跃用户', type: 'line', smooth: true, data: [3200, 3350, 3400, 3500, 3456, 3600, 3700], areaStyle: { opacity: 0.1 } },
                { name: '新增用户', type: 'bar', data: [65, 72, 80, 95, 89, 100, 110] },
              ],
              legend: { data: ['活跃用户', '新增用户'] },
              grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            }}
            style={{ height: '300px' }}
          />
        </div>

        <div className="bg-white rounded-xl p-5 border">
          <h3 className="font-semibold mb-4">资金消耗趋势</h3>
          <ReactECharts
            option={{
              tooltip: { trigger: 'axis' },
              xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
              yAxis: { type: 'value', axisLabel: { formatter: '{value}万' } },
              series: [
                { name: '日消耗', type: 'line', smooth: true, data: [12, 11.5, 13, 12.5, 12, 11, 10.5],
                  markLine: { data: [{ type: 'average', name: '平均' }] } },
              ],
              grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            }}
            style={{ height: '300px' }}
          />
        </div>
      </div>
    </div>
  );
}
