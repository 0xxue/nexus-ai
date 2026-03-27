import ReactECharts from 'echarts-for-react';

interface Props {
  config: Record<string, unknown>;
}

export function ChartRenderer({ config }: Props) {
  if (!config || !config.series) return null;

  const option = {
    tooltip: { trigger: 'axis' },
    legend: (config.legend as object) || {},
    xAxis: (config.xAxis as object) || { type: 'category' },
    yAxis: (config.yAxis as object) || { type: 'value' },
    series: config.series || [],
    title: config.title ? { text: config.title, left: 'center', textStyle: { fontSize: 14 } } : undefined,
    grid: { left: 40, right: 16, bottom: 24, top: 20, containLabel: false },
  };

  return <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />;
}

// Keep default export for backward compatibility
export default ChartRenderer;
