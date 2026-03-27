"""
RAG Service - Semantic API routing via LightRAG

Replaces V2's 50+ regex patterns in query_api_mappings.json
with semantic vector search over API descriptions.

How it works:
1. At startup: API descriptions are indexed into LightRAG (embedding → vector store)
2. At query time: User question → embedding → find most similar API descriptions
3. Returns matched APIs with confidence scores

"到期" ≈ "结束" ≈ "截止" → all match get_product_end_data
"""

import os
import structlog
from typing import Optional
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from app.core.config import get_settings

logger = structlog.get_logger()

# API knowledge base - descriptions of all available data endpoints
API_DESCRIPTIONS = [
    {
        "name": "system_overview",
        "endpoint": "/api/v1/data/system/overview",
        "description": (
            "查询系统整体运营数据概览。"
            "包括总用户数、活跃用户数、新增用户、总资金、日均消耗、系统健康状态。"
            "适用场景：了解系统整体情况、数据概览、运营数据、系统状态、今天的数据"
        ),
    },
    {
        "name": "expiring_products",
        "endpoint": "/api/v1/data/products/expiring",
        "description": (
            "查询指定日期到期的产品列表。"
            "支持查询即将到期、快结束、快截止、要到期、已经到期的产品。"
            "返回产品名称、到期时间、涉及金额、状态。"
            "适用场景：查到期产品、结束的产品、截止的产品、过期产品。"
            "参数：日期（今天、明天、昨天、本周、上周、某具体日期）"
        ),
        "params": {"date": "dynamic"},
    },
    {
        "name": "product_stats",
        "endpoint": "/api/v1/data/products/stats",
        "description": (
            "查询产品统计数据，支持时间范围筛选。"
            "包括产品数量变化趋势、新增产品、到期产品、活跃产品占比。"
            "适用场景：产品分析、趋势对比、周报月报、最近一段时间的产品数据"
        ),
        "params": {"start_date": "dynamic", "end_date": "dynamic"},
    },
    {
        "name": "finance_summary",
        "endpoint": "/api/v1/data/finance/summary",
        "description": (
            "查询财务摘要数据。"
            "包括收入、支出、利润、资金余额、日均消耗、资金可用天数。"
            "适用场景：资金状况、收支分析、资金还能撑多久、财务报表、钱够不够"
        ),
        "params": {"period": "daily|weekly|monthly"},
    },
    {
        "name": "user_stats",
        "endpoint": "/api/v1/data/users/stats",
        "description": (
            "查询用户统计数据。"
            "包括注册用户数、活跃用户数、留存率、新增趋势、用户分布。"
            "适用场景：用户分析、增长数据、留存分析、有多少用户"
        ),
    },
]

# LightRAG instance
_rag: Optional[LightRAG] = None


async def _llm_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs):
    """LLM function for LightRAG, using DeepSeek via OpenAI-compatible API."""
    settings = get_settings()
    return await openai_complete_if_cache(
        model="deepseek-chat",
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com/v1",
        **kwargs,
    )


async def _embed_func(texts: list[str], **kwargs):
    """
    Local embedding using sentence-transformers.
    No API key needed, runs on CPU, good enough for small knowledge bases.
    Uses paraphrase-multilingual-MiniLM-L12-v2 (supports Chinese + English).
    """
    import numpy as np
    from sentence_transformers import SentenceTransformer

    if not hasattr(_embed_func, "_model"):
        _embed_func._model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Loaded local embedding model: paraphrase-multilingual-MiniLM-L12-v2")

    embeddings = _embed_func._model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings)


async def init_rag():
    """
    Initialize RAG knowledge base at application startup.
    Index all API descriptions into LightRAG vector store.
    """
    global _rag
    settings = get_settings()

    working_dir = settings.rag_working_dir
    os.makedirs(working_dir, exist_ok=True)

    try:
        _rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=_llm_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=384,  # paraphrase-multilingual-MiniLM-L12-v2 output dim
                max_token_size=512,
                func=_embed_func,
            ),
        )

        # Build documents from API descriptions
        documents = []
        for api in API_DESCRIPTIONS:
            doc = (
                f"API接口名称: {api['name']}\n"
                f"接口地址: {api['endpoint']}\n"
                f"功能描述: {api['description']}\n"
            )
            if "params" in api:
                doc += f"参数: {api['params']}\n"
            documents.append(doc)

        # Initialize storage
        await _rag.initialize_storages()

        # Insert all API docs
        combined = "\n---\n".join(documents)
        await _rag.ainsert(combined)

        logger.info("LightRAG initialized", api_count=len(documents), working_dir=working_dir)

    except Exception as e:
        logger.error("LightRAG init failed, falling back to keyword matching", error=str(e))
        _rag = None


async def search_apis(query: str, top_k: int = 3) -> list[dict]:
    """
    Search for matching APIs using semantic similarity.

    Args:
        query: User's question or sub-intent
        top_k: Maximum number of results

    Returns:
        List of matched APIs with confidence scores:
        [{"name": "...", "endpoint": "...", "confidence": 0.85, "params": {...}}]
    """
    if _rag:
        return await _search_with_rag(query, top_k)
    else:
        logger.warning("LightRAG not available, using keyword fallback")
        return _search_with_keywords(query, top_k)


async def _search_with_rag(query: str, top_k: int) -> list[dict]:
    """Semantic search using LightRAG hybrid mode (keyword + vector)."""
    try:
        result = await _rag.aquery(
            query,
            param=QueryParam(mode="hybrid", top_k=top_k),
        )

        result_text = str(result).lower()

        # Match RAG results back to API definitions
        matched = []
        for api in API_DESCRIPTIONS:
            name_lower = api["name"].lower()
            desc_keywords = api["description"][:30].lower()

            if name_lower in result_text or desc_keywords in result_text:
                matched.append({
                    "name": api["name"],
                    "endpoint": api["endpoint"],
                    "confidence": 0.85,
                    "params": api.get("params", {}),
                })

        # If RAG returned something but we couldn't match exact API names,
        # try a more lenient matching
        if not matched and result_text.strip():
            # Score each API by keyword overlap with RAG result
            for api in API_DESCRIPTIONS:
                keywords = api["description"].replace("。", " ").replace("、", " ").split()
                score = sum(1 for kw in keywords if kw in result_text)
                if score >= 2:
                    matched.append({
                        "name": api["name"],
                        "endpoint": api["endpoint"],
                        "confidence": min(score * 0.15, 0.9),
                        "params": api.get("params", {}),
                    })

        if matched:
            matched.sort(key=lambda x: x["confidence"], reverse=True)
            logger.info("RAG matched", query=query[:50], apis=[m["name"] for m in matched[:top_k]])
            return matched[:top_k]

        # Nothing matched
        logger.warning("RAG returned no matches", query=query[:50])
        return [{
            "name": "system_overview",
            "endpoint": "/api/v1/data/system/overview",
            "confidence": 0.3,
            "params": {},
        }]

    except Exception as e:
        logger.error("RAG search failed", error=str(e))
        return _search_with_keywords(query, top_k)


def _search_with_keywords(query: str, top_k: int) -> list[dict]:
    """
    Fallback keyword matching when LightRAG is not available.
    """
    keywords_map = {
        "system_overview": ["概览", "整体", "数据", "情况", "状态", "运营", "总览"],
        "expiring_products": ["到期", "结束", "截止", "过期", "快到期", "快结束", "快截止"],
        "product_stats": ["产品统计", "产品分析", "趋势", "对比", "变化", "产品数据"],
        "finance_summary": ["资金", "收入", "支出", "利润", "财务", "撑多久", "余额", "钱"],
        "user_stats": ["用户", "注册", "活跃", "留存", "增长", "多少人"],
    }

    matched = []
    for api in API_DESCRIPTIONS:
        keywords = keywords_map.get(api["name"], [])
        score = sum(1 for kw in keywords if kw in query)
        if score > 0:
            matched.append({
                "name": api["name"],
                "endpoint": api["endpoint"],
                "confidence": min(score * 0.3, 0.9),
                "params": api.get("params", {}),
            })

    matched.sort(key=lambda x: x["confidence"], reverse=True)
    return matched[:top_k] if matched else [{
        "name": "system_overview",
        "endpoint": "/api/v1/data/system/overview",
        "confidence": 0.2,
        "params": {},
    }]
