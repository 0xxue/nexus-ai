"""
LangGraph Workflow — 11 Node Agentic RAG (2026 Standard)

Replaces V2's 800-line hand-written orchestrator with ~100 lines of declarative graph.

11 nodes:
  detect_intent → classify_source → rag_search → [reranker] → [route]
      → fetch_data → check_sufficiency → analyze
      → [hallucination_check] → [route] → generate_chart → format_response
  Low RAG confidence: → rewrite_query → rag_search (retry)
  Very low confidence: → fallback → END
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.langgraph.state import QAState
from app.core.langgraph.nodes import (
    detect_intent,
    classify_source,
    rag_search,
    fetch_data,
    check_sufficiency,
    analyze,
    generate_chart,
    format_response,
    fallback,
)
from app.core.langgraph.enhanced_nodes import (
    rewrite_query,
    check_hallucination,
    rerank_results,
)

RAG_CONFIDENCE_THRESHOLD = 0.6
RAG_REWRITE_THRESHOLD = 0.4


def route_after_rag(state: QAState) -> str:
    """
    Three-way routing after RAG search:
    - High confidence (>=0.6) → rerank and proceed
    - Low confidence (0.4-0.6) → rewrite query and retry
    - Very low (<0.4) → fallback
    """
    confidence = state.get("rag_confidence", 0)
    already_rewritten = "query_rewritten" in state.get("processing_steps", [])

    if confidence >= RAG_CONFIDENCE_THRESHOLD:
        return "rerank_results"
    elif confidence >= RAG_REWRITE_THRESHOLD and not already_rewritten:
        return "rewrite_query"  # Try rewriting, then re-search
    return "fallback"


def route_after_analyze(state: QAState) -> str:
    """Route to hallucination check (if data-backed) or skip."""
    if state.get("needs_review") and state.get("confidence", 0) < 0.3:
        return "format_response"
    return "check_hallucination"


def route_after_hallucination(state: QAState) -> str:
    """After hallucination check, generate chart or skip."""
    confidence = state.get("confidence", 0)
    if confidence < 0.3:
        return "format_response"
    return "generate_chart"


def build_graph() -> StateGraph:
    """
    Build the 11-node Agentic RAG workflow graph.

    V2 (hand-written, 800+ lines):
        detect → select_strategy → fetch → extract×3 → analyze → format

    V3 (LangGraph, ~100 lines, 11 nodes):
        detect_intent → classify_source → rag_search → rerank_results
            → fetch_data → check_sufficiency → analyze
            → check_hallucination → generate_chart → format_response

        + rewrite_query (retry loop for unclear queries)
        + fallback (when no data matches)

    2026 Agentic RAG features:
        ✅ Query rewriting (unclear → clear)
        ✅ Reranker (vector similarity → actual relevance)
        ✅ Hallucination detection (verify against source data)
        ✅ Agentic loop (rewrite → re-search if first attempt fails)
    """
    graph = StateGraph(QAState)

    # === 11 nodes ===
    # Core pipeline (8)
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("classify_source", classify_source)
    graph.add_node("rag_search", rag_search)
    graph.add_node("fetch_data", fetch_data)
    graph.add_node("check_sufficiency", check_sufficiency)
    graph.add_node("analyze", analyze)
    graph.add_node("generate_chart", generate_chart)
    graph.add_node("format_response", format_response)

    # Enhanced nodes (3) — Agentic RAG 2026
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("rerank_results", rerank_results)
    graph.add_node("check_hallucination", check_hallucination)

    # Fallback
    graph.add_node("fallback", fallback)

    # === Entry ===
    graph.set_entry_point("detect_intent")

    # === Edges ===
    graph.add_edge("detect_intent", "classify_source")
    graph.add_edge("classify_source", "rag_search")

    # After RAG: high confidence → rerank, low → rewrite, very low → fallback
    graph.add_conditional_edges(
        "rag_search",
        route_after_rag,
        {
            "rerank_results": "rerank_results",
            "rewrite_query": "rewrite_query",
            "fallback": "fallback",
        },
    )

    # Rewrite → re-search (agentic loop)
    graph.add_edge("rewrite_query", "rag_search")

    # Rerank → fetch data
    graph.add_edge("rerank_results", "fetch_data")

    # Data pipeline
    graph.add_edge("fetch_data", "check_sufficiency")
    graph.add_edge("check_sufficiency", "analyze")

    # After analyze → hallucination check
    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {
            "check_hallucination": "check_hallucination",
            "format_response": "format_response",
        },
    )

    # After hallucination check → chart or format
    graph.add_conditional_edges(
        "check_hallucination",
        route_after_hallucination,
        {
            "generate_chart": "generate_chart",
            "format_response": "format_response",
        },
    )

    graph.add_edge("generate_chart", "format_response")
    graph.add_edge("format_response", END)
    graph.add_edge("fallback", END)

    return graph


# Compile with checkpoint (supports resume after failure)
checkpointer = MemorySaver()
qa_graph = build_graph().compile(checkpointer=checkpointer)
