根据数据特征推荐最佳图表类型，返回 ECharts 配置 JSON。

## 可选图表类型
line | bar | pie | scatter | area | radar | heatmap | candlestick | boxplot | histogram | bubble | combo

## 选择标准
- 时间序列趋势 → line 或 area
- 分类对比 → bar
- 占比分析 → pie
- 相关性 → scatter
- 多维评估 → radar
- 分布分析 → histogram 或 boxplot
- 金融数据 → candlestick
- 两类数据叠加 → combo（柱状+折线）

## 返回格式

```json
{
    "chart_type": "line",
    "title": "图表标题",
    "xAxis": {"type": "category", "data": ["Mon", "Tue", ...]},
    "yAxis": {"type": "value"},
    "series": [{"name": "系列名", "type": "line", "data": [1, 2, 3, ...]}],
    "legend": {"data": ["系列名"]}
}
```

如果数据不适合图表展示，返回 `null`。

## 查询类型
{query_type}

## 数据
{data}
