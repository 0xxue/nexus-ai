"""
LangGraph Node Implementations

8 nodes in the workflow graph. Each reads from state, does work, returns updates.
Integrates: LiteLLM, LightRAG, Calculator, ChartService, FinancialFormatter.
"""

import asyncio
import json
import structlog
from pathlib import Path
from datetime import datetime

from app.core.langgraph.state import QAState
from app.services.llm import call_llm
from app.services.rag import search_apis
from app.services.data_service import DataService
from app.services.chart_service import recommend_and_generate_chart
from app.utils.calculator import Calculator
from app.utils.financial_fmt import FinancialFormatter
from app.utils.time_series import TimeSeriesBuilder

logger = structlog.get_logger()
calculator = Calculator()
formatter = FinancialFormatter()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    """Load prompt template from file."""
    path = PROMPTS_DIR / f"{name}.md"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Prompt template not found", name=name)
        return ""


# ========== Node 1: Intent Detection ==========

async def detect_intent(state: QAState) -> dict:
    """
    Decompose user query into sub-questions and classify type.
    Uses AI — replaces V2's regex-based QueryTypeDetector.
    """
    query = state["query"]
    prompt = _load_prompt("intent").replace("{current_time}", datetime.now().strftime("%Y-%m-%d %H:%M"))

    response = await call_llm(
        model="primary",
        system=prompt,
        user=query,
        response_format="json",
    )

    intents = response.get("intents", [query])
    query_type = response.get("query_type", "simple_data")
    requires_calc = response.get("requires_calculation", False)

    logger.info("Intent detected", intents=intents, query_type=query_type, requires_calc=requires_calc)

    return {
        "intents": intents,
        "query_type": query_type,
        "processing_steps": state.get("processing_steps", []) + ["intent_detected"],
    }


# ========== Node 2: Classify Data Source ==========

async def classify_source(state: QAState) -> dict:
    """
    Determine which data sources to query based on intent type.
    Routes to: API / knowledge base / database / mixed
    """
    query_type = state["query_type"]

    # Simple routing — can be enhanced with AI for ambiguous cases
    source_type = "api"
    if query_type == "knowledge":
        source_type = "knowledge_base"
    elif query_type == "report":
        source_type = "mixed"

    return {
        "processing_steps": state.get("processing_steps", []) + [f"source_classified:{source_type}"],
    }


# ========== Node 3: RAG Search ==========

async def rag_search(state: QAState) -> dict:
    """
    Semantic search for matching API endpoints / knowledge base docs.
    Replaces V2's 50+ regex patterns.
    """
    intents = state["intents"]
    all_matched = []
    max_confidence = 0.0

    for intent in intents:
        results = await search_apis(intent)
        for r in results:
            if r["name"] not in [m["name"] for m in all_matched]:
                all_matched.append(r)
            max_confidence = max(max_confidence, r.get("confidence", 0))

    logger.info("RAG search complete", matched=len(all_matched), confidence=round(max_confidence, 2))

    return {
        "matched_apis": all_matched,
        "rag_confidence": max_confidence,
        "processing_steps": state.get("processing_steps", []) + ["rag_searched"],
    }


# ========== Node 4: Fetch Data (Parallel) ==========

async def fetch_data(state: QAState) -> dict:
    """
    Call all matched APIs in parallel. Fan-out with asyncio.gather.
    Each call protected by circuit breaker + cache.
    """
    matched_apis = state["matched_apis"]
    svc = DataService()

    tasks = []
    for api in matched_apis:
        tasks.append((api["name"], svc.call_api(api["endpoint"], api.get("params", {}))))

    names = [t[0] for t in tasks]
    calls = [t[1] for t in tasks]
    responses = await asyncio.gather(*calls, return_exceptions=True)

    results = {}
    for name, response in zip(names, responses):
        if isinstance(response, Exception):
            logger.warning("API failed", api=name, error=str(response))
            results[name] = {"error": str(response)}
        else:
            results[name] = response

    success = sum(1 for v in results.values() if "error" not in v)
    quality = {
        "completeness": success / len(results) if results else 0,
        "freshness": 1.0,
        "accuracy": 1.0 if success == len(results) else 0.8,
    }

    logger.info("Data fetched", total=len(results), success=success)

    return {
        "api_results": results,
        "data_quality": quality,
        "processing_steps": state.get("processing_steps", []) + ["data_fetched"],
    }


# ========== Node 5: Check Sufficiency (Agentic RAG) ==========

async def check_sufficiency(state: QAState) -> dict:
    """
    Check if fetched data is sufficient to answer the question.
    If not, trigger additional retrieval (Agentic RAG pattern).
    """
    api_results = state["api_results"]
    quality = state.get("data_quality", {})

    completeness = quality.get("completeness", 0)

    if completeness >= 0.5:
        return {"processing_steps": state.get("processing_steps", []) + ["data_sufficient"]}

    # Data insufficient — could trigger additional search
    logger.warning("Data insufficient", completeness=completeness)
    return {
        "processing_steps": state.get("processing_steps", []) + ["data_insufficient"],
        "error": "部分数据获取失败，分析结果可能不完整",
    }


# ========== Node 6: AI Analysis (Dual Model) ==========

async def analyze(state: QAState) -> dict:
    """
    AI analyzes fetched data. Uses calculator for precise numbers.
    Low confidence → cross-validate with secondary model.
    """
    query = state["query"]
    api_results = state["api_results"]
    query_type = state["query_type"]

    # Run calculations if needed
    calc_results = _run_calculations(api_results, query_type)

    # Build analysis context
    data_context = _format_data_with_sources(api_results)
    if calc_results:
        data_context += f"\n\n计算结果：\n{json.dumps(calc_results, ensure_ascii=False, default=str)}"

    # Load analysis prompt
    prompt = _load_prompt("analysis").replace("{data}", data_context)

    # Primary model analysis
    primary = await call_llm(model="primary", system=prompt, user=query, response_format="json")

    confidence = primary.get("confidence", 0.5)
    answer = primary.get("answer", str(primary))
    sources = primary.get("sources", [])

    # Cross-validate if low confidence
    if confidence < 0.7:
        logger.info("Cross-validating", confidence=confidence)
        secondary = await call_llm(
            model="secondary",
            system="验证以下分析是否合理。如有问题请修正，如合理请补充。简洁回答。",
            user=f"问题：{query}\n分析：{answer}\n数据：{data_context[:1500]}",
        )
        answer += f"\n\n**补充验证：** {secondary}"
        confidence = min(confidence + 0.15, 1.0)

    # Format financial numbers in answer
    needs_review = confidence < 0.5

    logger.info("Analysis complete", confidence=round(confidence, 2), needs_review=needs_review)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "needs_review": needs_review,
        "processing_steps": state.get("processing_steps", []) + ["analyzed"],
    }


# ========== Node 7: Generate Chart ==========

async def generate_chart(state: QAState) -> dict:
    """Generate ECharts config based on data and query type."""
    chart = await recommend_and_generate_chart(state["api_results"], state["query_type"])
    return {
        "chart": chart,
        "processing_steps": state.get("processing_steps", []) + ["chart_generated"],
    }


# ========== Node 8: Format Response + Source Attribution ==========

async def format_response(state: QAState) -> dict:
    """
    Final formatting: add source attribution, format numbers, add metadata.
    """
    sources = []
    for api in state.get("matched_apis", []):
        sources.append({
            "type": "api",
            "name": api["name"],
            "endpoint": api["endpoint"],
            "query_time": datetime.now().isoformat(),
        })

    if state.get("error"):
        answer = state.get("answer", "") + f"\n\n⚠️ {state['error']}"
    else:
        answer = state.get("answer", "")

    return {
        "answer": answer,
        "sources": sources,
        "processing_steps": state.get("processing_steps", []) + ["formatted"],
    }


# ========== Node: Fallback ==========

async def fallback(state: QAState) -> dict:
    """When RAG can't find matching APIs."""
    query = state["query"]
    logger.warning("Fallback triggered", query=query[:50])

    response = await call_llm(
        model="primary",
        system="用户的问题无法匹配到数据接口。根据你的知识回答，但明确说明不是基于实时数据。",
        user=query,
    )

    return {
        "answer": response,
        "confidence": 0.3,
        "sources": [{"type": "ai_knowledge", "name": "AI general knowledge"}],
        "needs_review": True,
        "processing_steps": state.get("processing_steps", []) + ["fallback"],
    }


# ========== Helper Functions ==========

def _run_calculations(api_results: dict, query_type: str) -> dict:
    """Run precise calculations on fetched data using Calculator."""
    calc = {}

    # Finance calculations
    finance = api_results.get("finance_summary", {})
    if finance and "error" not in finance:
        if finance.get("balance") and finance.get("daily_burn"):
            calc["cash_runway"] = calculator.cash_runway(finance["balance"], finance["daily_burn"])
        if finance.get("revenue") and finance.get("expenses"):
            profit = float(finance["revenue"]) - float(finance["expenses"])
            calc["profit"] = {
                "revenue": formatter.format_currency(finance["revenue"]),
                "expenses": formatter.format_currency(finance["expenses"]),
                "profit": formatter.format_currency(profit),
                "margin": formatter.format_percent(
                    profit / float(finance["revenue"]) * 100 if finance["revenue"] else 0,
                    show_trend=True,
                ),
            }

    # Product expiry analysis
    expiring = api_results.get("expiring_products", {})
    if expiring and "error" not in expiring and expiring.get("products"):
        calc["expiry_analysis"] = calculator.expiry_analysis(expiring["products"])

    # User analysis
    users = api_results.get("user_stats", api_results.get("user_data", {}))
    if users and "error" not in users:
        total = users.get("total", users.get("total_users", 0))
        active = users.get("active", users.get("active_users", 0))
        new = users.get("new_today", users.get("new_users_today", 0))
        if total > 0:
            calc["user_analysis"] = calculator.user_analysis(total, active, new)

    # Trend analysis from interval data
    interval = api_results.get("product_interval", {})
    if interval and "error" not in interval and interval.get("daily_breakdown"):
        values = [d.get("count", 0) for d in interval["daily_breakdown"]]
        calc["trend"] = calculator.trend(values)
        calc["prediction"] = calculator.linear_prediction(values, future_steps=7)

        # Anomaly detection
        anomalies = TimeSeriesBuilder.detect_anomalies(values)
        if anomalies:
            calc["anomalies"] = anomalies

    return calc


def _format_data_with_sources(api_results: dict) -> str:
    """Format API results with source labels for AI context."""
    parts = []
    for name, data in api_results.items():
        if isinstance(data, dict) and "error" in data:
            parts.append(f"[{name}] ❌ 数据获取失败: {data['error']}")
        else:
            parts.append(f"[{name}] ✅\n{json.dumps(data, ensure_ascii=False, indent=2, default=str)}")
    return "\n\n".join(parts)
