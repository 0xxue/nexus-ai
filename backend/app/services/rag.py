"""
RAG Service - Semantic API routing via LightRAG + keyword fallback

How it works:
1. At startup: API descriptions indexed into LightRAG
2. At query time: semantic search → keyword fallback → smart default
3. Always tries to fetch real data before falling back to general AI

To customize: update API_DESCRIPTIONS and keywords_map for your domain.
"""

import os
import structlog
from typing import Optional
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc
from app.core.config import get_settings

logger = structlog.get_logger()

# ══════════════════════════════════════════════════
# API Knowledge Base — customize for your domain
# ══════════════════════════════════════════════════

API_DESCRIPTIONS = [
    {
        "name": "system_overview",
        "endpoint": "/api/v1/data/system/overview",
        "description": "System-wide operational overview: total users, active users, new users, items, health status.",
        "keywords": ["overview", "status", "health", "dashboard", "system", "overall", "how",
                      "概览", "整体", "状态", "情况", "总览", "数据", "怎么样", "如何"],
    },
    {
        "name": "items_expiring",
        "endpoint": "/api/v1/data/items/expiring",
        "description": "Items expiring on a specific date (products, licenses, subscriptions, contracts).",
        "keywords": ["expir", "ending", "deadline", "overdue", "due", "soon",
                      "到期", "结束", "截止", "过期", "快到"],
        "params": {"date": "dynamic"},
    },
    {
        "name": "item_stats",
        "endpoint": "/api/v1/data/items/stats",
        "description": "Item statistics: quantity trends, new items, expiring items, active items over time.",
        "keywords": ["stats", "trend", "analysis", "compare", "report", "item", "product",
                      "统计", "分析", "趋势", "对比", "报告", "产品"],
        "params": {"start_date": "dynamic", "end_date": "dynamic"},
    },
    {
        "name": "summary_metrics",
        "endpoint": "/api/v1/data/metrics/summary",
        "description": "Summary metrics: revenue, costs, profit, budget remaining, daily spend, runway days.",
        "keywords": ["budget", "revenue", "cost", "spend", "profit", "money", "metric", "kpi", "financial",
                      "资金", "收入", "支出", "利润", "预算", "费用", "钱", "多久"],
        "params": {"period": "daily|weekly|monthly"},
    },
    {
        "name": "user_stats",
        "endpoint": "/api/v1/data/users/stats",
        "description": "User statistics: total users, active users, retention rate, growth trend.",
        "keywords": ["user", "active", "retention", "growth", "register", "member", "people",
                      "用户", "注册", "活跃", "留存", "增长", "多少人", "会员"],
    },
]

_rag: Optional[LightRAG] = None


async def _llm_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs):
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
    import numpy as np
    from sentence_transformers import SentenceTransformer
    if not hasattr(_embed_func, "_model"):
        _embed_func._model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Loaded local embedding model")
    return np.array(_embed_func._model.encode(texts, normalize_embeddings=True))


async def init_rag():
    global _rag
    settings = get_settings()
    working_dir = settings.rag_working_dir
    os.makedirs(working_dir, exist_ok=True)

    try:
        _rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=_llm_func,
            embedding_func=EmbeddingFunc(embedding_dim=384, max_token_size=512, func=_embed_func),
        )
        documents = []
        for api in API_DESCRIPTIONS:
            doc = f"API: {api['name']}\nEndpoint: {api['endpoint']}\nDescription: {api['description']}\nKeywords: {', '.join(api.get('keywords', []))}\n"
            documents.append(doc)

        await _rag.initialize_storages()
        await _rag.ainsert("\n---\n".join(documents))
        logger.info("LightRAG initialized", api_count=len(documents))
    except Exception as e:
        logger.error("LightRAG init failed", error=str(e))
        _rag = None


async def search_apis(query: str, top_k: int = 3) -> list[dict]:
    """
    Search for matching APIs. Strategy:
    1. Try LightRAG semantic search
    2. Always also run keyword matching
    3. Merge results, take best confidence
    4. If nothing matches, return system_overview as default
    """
    results = []

    # Always run keyword matching (fast, reliable)
    kw_results = _search_with_keywords(query, top_k)
    results.extend(kw_results)

    # Try RAG if available
    if _rag:
        try:
            rag_results = await _search_with_rag(query, top_k)
            # Merge: keep higher confidence for same API
            for rr in rag_results:
                existing = next((r for r in results if r["name"] == rr["name"]), None)
                if existing:
                    existing["confidence"] = max(existing["confidence"], rr["confidence"])
                else:
                    results.append(rr)
        except Exception as e:
            logger.warning("RAG search failed, using keywords only", error=str(e))

    # Deduplicate and sort
    seen = set()
    unique = []
    for r in sorted(results, key=lambda x: x["confidence"], reverse=True):
        if r["name"] not in seen:
            seen.add(r["name"])
            unique.append(r)

    if unique:
        logger.info("API search results", query=query[:50], apis=[(m["name"], round(m["confidence"], 2)) for m in unique[:top_k]])
        return unique[:top_k]

    # Absolute fallback
    return [{
        "name": "system_overview",
        "endpoint": "/api/v1/data/system/overview",
        "confidence": 0.7,
        "params": {},
    }]


async def _search_with_rag(query: str, top_k: int) -> list[dict]:
    result = await _rag.aquery(query, param=QueryParam(mode="hybrid", top_k=top_k))
    result_text = str(result).lower()

    matched = []
    for api in API_DESCRIPTIONS:
        name_lower = api["name"].lower()
        if name_lower in result_text:
            matched.append({
                "name": api["name"],
                "endpoint": api["endpoint"],
                "confidence": 0.85,
                "params": api.get("params", {}),
            })
            continue
        # Check if keywords from description appear in RAG result
        keywords = api.get("keywords", [])
        hits = sum(1 for kw in keywords if kw.lower() in result_text)
        if hits >= 2:
            matched.append({
                "name": api["name"],
                "endpoint": api["endpoint"],
                "confidence": min(0.5 + hits * 0.1, 0.9),
                "params": api.get("params", {}),
            })

    return matched


def _search_with_keywords(query: str, top_k: int) -> list[dict]:
    """Fast keyword matching — always runs."""
    matched = []
    query_lower = query.lower()

    for api in API_DESCRIPTIONS:
        keywords = api.get("keywords", [])
        hits = sum(1 for kw in keywords if kw in query_lower)
        if hits > 0:
            # More hits = higher confidence (0.4 base + 0.15 per hit, max 0.9)
            confidence = min(0.4 + hits * 0.15, 0.9)
            matched.append({
                "name": api["name"],
                "endpoint": api["endpoint"],
                "confidence": confidence,
                "params": api.get("params", {}),
            })

    matched.sort(key=lambda x: x["confidence"], reverse=True)
    return matched[:top_k]
