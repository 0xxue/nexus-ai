import ReactECharts from 'echarts-for-react';

interface Props {
  config: Record<string, any>;
}

export default function ChartRenderer({ config }: Props) {
  if (!config || !config.series) return null;

  const option = {
    tooltip: { trigger: 'axis' },
    legend: config.legend || {},
    xAxis: config.xAxis || { type: 'category' },
    yAxis: config.yAxis || { type: 'value' },
    series: config.series || [],
    title: config.title ? { text: config.title, left: 'center', textStyle: { fontSize: 14 } } : undefined,
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  };

  return (
    <div className="mt-4 border rounded-lg p-2 bg-white">
      <ReactECharts option={option} style={{ height: '350px' }} />
    </div>
  );
}
