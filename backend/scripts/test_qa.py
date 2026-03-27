#!/usr/bin/env python3
"""
QA System Integration Test Script

Tests all aspects of the system:
1. API Health & Connectivity
2. Data Endpoints (mock data)
3. QA Ask (single-shot) — various query types
4. QA Stream (SSE) — streaming responses
5. Answer Quality Assessment
6. Multi-language Support
7. Response Time

Usage:
    python scripts/test_qa.py
"""

import json
import time
import httpx
import asyncio
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://43.153.166.137:8000"
API = f"{BASE_URL}/api/v1"

# Colors
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
B = '\033[94m'
W = '\033[0m'
BOLD = '\033[1m'

results = []


def log(msg, color=W):
    print(f"{color}{msg}{W}")


def section(title):
    print(f"\n{'='*60}")
    log(f"  {title}", BOLD)
    print('='*60)


def record(name, passed, detail="", time_ms=0):
    results.append({"name": name, "passed": passed, "detail": detail, "time_ms": time_ms})
    icon = f"{G}✓{W}" if passed else f"{R}✗{W}"
    time_str = f" ({time_ms}ms)" if time_ms else ""
    print(f"  {icon} {name}{time_str}")
    if detail and not passed:
        print(f"    {R}→ {detail[:200]}{W}")
    elif detail and passed:
        print(f"    {B}→ {detail[:200]}{W}")


async def main():
    async with httpx.AsyncClient(timeout=60) as client:

        # ═══════════════════════════════════════
        section("1. API Health & Connectivity")
        # ═══════════════════════════════════════

        t0 = time.time()
        try:
            r = await client.get(f"{API}/health")
            ms = int((time.time() - t0) * 1000)
            data = r.json()
            record("Health endpoint", data.get("status") == "ok", f"status={data}", time_ms=ms)
        except Exception as e:
            record("Health endpoint", False, str(e))

        # ═══════════════════════════════════════
        section("2. Data Endpoints (Mock Data)")
        # ═══════════════════════════════════════

        data_endpoints = [
            ("/data/system/overview", "System Overview"),
            ("/data/users/stats", "User Stats"),
            ("/data/items/expiring?date=today", "Items Expiring"),
            ("/data/metrics/summary", "Summary Metrics"),
            ("/data/categories/distribution", "Category Distribution"),
            ("/data/items/stats", "Item Stats"),
        ]

        for path, name in data_endpoints:
            t0 = time.time()
            try:
                r = await client.get(f"{API}{path}")
                ms = int((time.time() - t0) * 1000)
                data = r.json()
                has_error = "error" in data if isinstance(data, dict) else False
                detail = json.dumps(data, ensure_ascii=False)[:150] if not has_error else data.get("error", "")
                record(f"Data: {name}", r.status_code == 200 and not has_error, detail, time_ms=ms)
            except Exception as e:
                record(f"Data: {name}", False, str(e))

        # ═══════════════════════════════════════
        section("3. QA Ask — Query Types")
        # ═══════════════════════════════════════

        qa_tests = [
            {
                "name": "System Overview (EN)",
                "query": "Show me the system overview",
                "expect_keywords": ["user", "active", "health"],
                "min_confidence": 0.3,
            },
            {
                "name": "System Overview (CN)",
                "query": "系统整体数据情况怎么样",
                "expect_keywords": ["用户", "活跃"],
                "min_confidence": 0.3,
            },
            {
                "name": "User Stats",
                "query": "How many users are active?",
                "expect_keywords": ["user", "active", "3"],
                "min_confidence": 0.3,
            },
            {
                "name": "Metrics Summary",
                "query": "What are the current budget metrics?",
                "expect_keywords": ["revenue", "cost", "budget"],
                "min_confidence": 0.3,
            },
            {
                "name": "Expiring Items",
                "query": "What items are expiring today?",
                "expect_keywords": ["expir", "item", "today"],
                "min_confidence": 0.3,
            },
            {
                "name": "General Knowledge Fallback",
                "query": "What is machine learning?",
                "expect_keywords": ["learn", "model", "data"],
                "min_confidence": 0.1,
            },
        ]

        for test in qa_tests:
            t0 = time.time()
            try:
                r = await client.post(f"{API}/qa/ask", json={"query": test["query"]})
                ms = int((time.time() - t0) * 1000)
                data = r.json()

                answer = data.get("answer", "")
                confidence = data.get("confidence", 0)
                sources = data.get("sources", [])
                has_error = "error" in data and "answer" not in data

                # Quality checks
                answer_lower = answer.lower()
                keyword_hits = sum(1 for kw in test["expect_keywords"] if kw.lower() in answer_lower)
                keyword_total = len(test["expect_keywords"])
                conf_ok = confidence >= test["min_confidence"]
                answer_length = len(answer)

                passed = not has_error and keyword_hits > 0 and answer_length > 20
                detail = (
                    f"conf={confidence:.2f} | "
                    f"keywords={keyword_hits}/{keyword_total} | "
                    f"len={answer_length} | "
                    f"sources={[s.get('name','?') if isinstance(s,dict) else s for s in sources[:2]]}"
                )

                record(f"QA: {test['name']}", passed, detail, time_ms=ms)

                # Print answer preview
                preview = answer.replace('\n', ' ')[:150]
                print(f"    {Y}Answer: {preview}...{W}")

            except Exception as e:
                record(f"QA: {test['name']}", False, str(e))

        # ═══════════════════════════════════════
        section("4. QA Stream (SSE)")
        # ═══════════════════════════════════════

        t0 = time.time()
        try:
            chunks = []
            steps = []
            async with client.stream("POST", f"{API}/qa/stream", json={"query": "user growth trend"}) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        evt = json.loads(payload)
                        if "step" in evt:
                            steps.append(evt["step"])
                        if "answer" in evt:
                            chunks.append(evt["answer"])
                        if "error" in evt:
                            chunks.append(f"ERROR: {evt['error']}")
                    except:
                        pass

            ms = int((time.time() - t0) * 1000)
            has_answer = len(chunks) > 0 and not any("ERROR" in c for c in chunks)
            detail = f"steps={steps} | answer_chunks={len(chunks)} | final_len={len(chunks[-1]) if chunks else 0}"
            record("SSE Stream", has_answer, detail, time_ms=ms)
            if chunks:
                preview = chunks[-1].replace('\n', ' ')[:150]
                print(f"    {Y}Answer: {preview}...{W}")

        except Exception as e:
            record("SSE Stream", False, str(e))

        # ═══════════════════════════════════════
        section("5. Multi-language Response Check")
        # ═══════════════════════════════════════

        lang_tests = [
            ("English query", "What is the system status?", lambda a: any(c.isascii() for c in a[:50])),
            ("Chinese query", "系统状态怎么样？", lambda a: any('\u4e00' <= c <= '\u9fff' for c in a[:100])),
        ]

        for name, query, check_fn in lang_tests:
            t0 = time.time()
            try:
                r = await client.post(f"{API}/qa/ask", json={"query": query})
                ms = int((time.time() - t0) * 1000)
                answer = r.json().get("answer", "")
                lang_match = check_fn(answer)
                record(f"Lang: {name}", lang_match, f"answer_start={answer[:80]}", time_ms=ms)
            except Exception as e:
                record(f"Lang: {name}", False, str(e))

        # ═══════════════════════════════════════
        section("6. Error Handling")
        # ═══════════════════════════════════════

        # Empty query
        try:
            r = await client.post(f"{API}/qa/ask", json={"query": ""})
            record("Empty query rejected", r.status_code == 422, f"status={r.status_code}")
        except Exception as e:
            record("Empty query rejected", False, str(e))

        # Invalid endpoint
        try:
            r = await client.get(f"{API}/nonexistent")
            record("404 handling", r.status_code == 404, f"status={r.status_code}")
        except Exception as e:
            record("404 handling", False, str(e))

    # ═══════════════════════════════════════
    section("RESULTS SUMMARY")
    # ═══════════════════════════════════════

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    avg_time = sum(r["time_ms"] for r in results if r["time_ms"]) / max(1, sum(1 for r in results if r["time_ms"]))

    print(f"\n  Total:  {total}")
    log(f"  Passed: {passed}", G)
    if failed:
        log(f"  Failed: {failed}", R)
    print(f"  Avg response time: {avg_time:.0f}ms")

    print(f"\n  {'Pass rate:':<20} {passed}/{total} ({passed/total*100:.0f}%)")

    if failed:
        print(f"\n  {R}Failed tests:{W}")
        for r in results:
            if not r["passed"]:
                print(f"    ✗ {r['name']}: {r['detail'][:100]}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
