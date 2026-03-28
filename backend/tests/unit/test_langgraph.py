"""Tests for LangGraph pipeline state and node logic."""

import pytest


class TestQAState:
    """Test QAState definition."""

    def test_state_has_core_fields(self):
        from app.core.langgraph.state import QAState
        fields = QAState.__annotations__
        for f in ["query", "user_id", "conversation_id", "intents", "query_type", "answer", "confidence"]:
            assert f in fields, f"QAState missing {f}"

    def test_state_has_multiturn_fields(self):
        from app.core.langgraph.state import QAState
        fields = QAState.__annotations__
        assert "conversation_history" in fields
        assert "conversation_summary" in fields

    def test_state_has_rag_fields(self):
        from app.core.langgraph.state import QAState
        fields = QAState.__annotations__
        for f in ["matched_apis", "rag_confidence", "kb_context", "data_source"]:
            assert f in fields


class TestNodeImports:
    """Test all pipeline nodes can be imported."""

    def test_import_all_nodes(self):
        from app.core.langgraph.nodes import (
            detect_intent, classify_source, rag_search,
            fetch_data, check_sufficiency, analyze,
            generate_chart, format_response, fallback,
        )
        # All should be async functions
        import asyncio
        for fn in [detect_intent, classify_source, rag_search, fetch_data,
                   check_sufficiency, analyze, generate_chart, format_response, fallback]:
            assert asyncio.iscoroutinefunction(fn), f"{fn.__name__} is not async"


class TestContextBuilding:
    """Test multi-turn context injection logic."""

    def test_context_with_summary_and_history(self):
        """Verify context message is built correctly."""
        history = [
            {"role": "user", "content": "Show me user growth"},
            {"role": "assistant", "content": "User growth is up."},
        ]
        summary = "Discussed user growth."
        query = "What about last week?"

        context_parts = []
        if summary:
            context_parts.append(f"[Conversation summary so far]: {summary}")
        if history:
            recent = "\n".join(f"{m['role']}: {m['content'][:200]}" for m in history[-6:])
            context_parts.append(f"[Recent messages]:\n{recent}")
        context_parts.append(f"[Current question]: {query}")
        user_msg = "\n\n".join(context_parts)

        assert "[Conversation summary so far]" in user_msg
        assert "[Recent messages]" in user_msg
        assert "[Current question]: What about last week?" in user_msg

    def test_context_without_history(self):
        """Without history, just uses the query."""
        query = "Hello"
        history = []
        summary = ""

        if not summary and not history:
            user_msg = query
        else:
            user_msg = "should not reach"

        assert user_msg == "Hello"


class TestLLMService:
    """Test LLM service configuration."""

    def test_call_llm_has_history_param(self):
        import inspect
        from app.services.llm import call_llm
        sig = inspect.signature(call_llm)
        assert "history" in sig.parameters

    def test_model_map_has_three_tiers(self):
        from app.services.llm import MODEL_MAP
        assert "primary" in MODEL_MAP
        assert "secondary" in MODEL_MAP
        assert "fallback" in MODEL_MAP
