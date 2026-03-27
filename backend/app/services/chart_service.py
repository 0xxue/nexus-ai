"""
Chart Service — 12 types of ECharts visualization + AI recommendation

Returns ECharts JSON config for frontend rendering.
V2 used Matplotlib (server-side images), V3 uses ECharts (client-side interactive).

Supported: line, bar, pie, scatter, area, radar, heatmap,
           candlestick, boxplot, histogram, bubble, combo
"""

import structlog
from typing import Optional
from app.services.llm import call_llm

logger = structlog.get_logger()

CHART_TYPES = [
    "line", "bar", "pie", "scatter", "area", "radar",
    "heatmap", "candlestick", "boxplot", "histogram", "bubble", "combo",
]

# Quick recommendation rules (before AI, for speed)
QUERY_TYPE_CHART_MAP = {
    "simple_data": "bar",
    "comparison": "bar",
    "prediction": "line",
    "aggregation": "pie",
    "knowledge": None,  # No chart for knowledge questions
    "report": "combo",
}


async def recommend_and_generate_chart(data: dict, query_type: str) -> Optional[dict]:
    """
    Two-step chart generation:
    1. Rule-based quick recommendation (fast, no AI call)
    2. AI refinement if data is complex (optional)

    Returns ECharts-compatible JSON config or None.
    """
    if not data or all("error" in v for v in data.values() if isinstance(v, dict)):
        return None

    # Skip charts for knowledge questions
    if query_type == "knowledge":
        return None

    # Try rule-based first
    chart_type = QUERY_TYPE_CHART_MAP.get(query_type, "bar")

    # For complex data, ask AI to refine
    try:
        # Load prompt template
        prompt_path = "app/core/prompts/chart.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            prompt_template = f"推荐图表类型，返回 ECharts JSON。可选：{CHART_TYPES}"

        prompt = prompt_template.replace("{query_type}", query_type).replace("{data}", str(data)[:2000])

        response = await call_llm(
            model="secondary",
            system=prompt,
            user=f"请为以下数据生成 ECharts 配置",
            response_format="json",
        )

        if response and isinstance(response, dict) and response.get("chart_type"):
            logger.info("AI chart recommendation", chart_type=response["chart_type"])
            return response

    except Exception as e:
        logger.warning("AI chart recommendation failed, using rule-based", error=str(e))

    # Fallback: generate basic chart config
    return generate_basic_chart(data, chart_type)


def generate_basic_chart(data: dict, chart_type: str = "bar") -> Optional[dict]:
    """
    Generate basic ECharts config without AI.
    Handles common data patterns.
    """
    # Extract first non-error dataset
    for name, dataset in data.items():
        if isinstance(dataset, dict) and "error" not in dataset:
            # Try to build chart from data structure
            if isinstance(dataset.get("data"), list):
                items = dataset["data"]
                if items and isinstance(items[0], dict):
                    # List of dicts → use first two fields as x/y
                    keys = list(items[0].keys())
                    if len(keys) >= 2:
                        x_key, y_key = keys[0], keys[1]
                        return {
                            "chart_type": chart_type,
                            "title": name.replace("_", " ").title(),
                            "xAxis": {"type": "category", "data": [str(item[x_key]) for item in items]},
                            "yAxis": {"type": "value"},
                            "series": [{"name": y_key, "type": chart_type, "data": [item[y_key] for item in items]}],
                        }

    return None
