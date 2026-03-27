# AI QA System

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-0.4-FF6F00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LiteLLM-1.77-412991?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LightRAG-Semantic-4FC08D?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PostgreSQL-16+pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
</p>

<p align="center">
  Open-source enterprise AI QA platform with Agentic RAG (11-node LangGraph). Ask questions in natural language, get data-driven answers with charts and source attribution. Freely switch between any LLM.
</p>

<p align="center">
  🔗 <a href="https://demo-mu-jade.vercel.app/indexv2.html">Live Demo (3D Bot)</a> | <a href="https://demo-mu-jade.vercel.app">Classic</a> | <a href="https://demo-mu-jade.vercel.app/e-2-with-bot.html">Style 2</a> | <a href="https://demo-mu-jade.vercel.app/g-2-with-bot.html">Style 3</a>
  <br/>
  <sub>⚠️ UI demo — backend API required for real AI responses, falls back to demo data when offline</sub>
</p>

> **Note:** Inspired by real-world production experience. All business-specific code has been generalized and no proprietary information is included. Built for financial analytics — easily adaptable to any industry by modifying API descriptions, prompt templates, and data sources.

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#model-freedom">Model Freedom</a> •
  <a href="#中文说明">中文说明</a>
</p>

---

## Features

- **Natural Language QA** — Ask "资金还能撑多久" and get precise answers with data
- **LangGraph Orchestration** — 8-node stateful workflow with parallel execution, checkpoints, and conditional routing
- **RAG Semantic Search** — LightRAG replaces regex with semantic matching. "到期" ≈ "结束" ≈ "截止"
- **Model Freedom** — Switch between Claude/GPT/DeepSeek/Ollama via `.env`. No API key needed (Ollama local)
- **Knowledge Base** — Upload PDF/Word/Excel, auto-chunk, embed, and search
- **Multi-turn Dialogue** — Conversation history with context awareness
- **12 Chart Types** — AI recommends best visualization, returns ECharts JSON
- **Precise Calculations** — Decimal-based financial calculator (compound interest, ROI, cash runway)
- **Source Attribution** — Every answer cites where the data came from
- **Report Export** — Markdown / HTML / PDF with 5 themes
- **Enterprise Middleware** — Circuit breaker, rate limiter, distributed tracing, structured logging
- **RBAC + Audit** — Role-based access control with full audit trail

---

## Architecture

```
Frontend (React) → FastAPI (async) → LangGraph (8 nodes)
                                          │
                    ┌─────────────────────┼──────────────────────┐
                    ↓                     ↓                      ↓
              LightRAG              Internal APIs          Knowledge Base
              (semantic routing)    (8 endpoints)          (PDF/Word/Excel)
                    │                     │                      │
                    └─────────────────────┼──────────────────────┘
                                          ↓
                                    LiteLLM (any model)
                                    Claude ↔ GPT ↔ DeepSeek ↔ Ollama

Data: PostgreSQL + pgvector | Redis | Prometheus + Grafana
```

### LangGraph Workflow (8 Nodes)

```
detect_intent → classify_source → rag_search → [confidence?]
                                                    │
                                          ┌─────────┴──────────┐
                                     [≥0.6]                  [<0.6]
                                          ↓                      ↓
                                    fetch_data              fallback
                                          ↓
                                check_sufficiency
                                          ↓
                                      analyze (dual-model cross-validation)
                                          ↓
                                   generate_chart
                                          ↓
                                  format_response (source attribution)
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Redis 7+ (optional — works without it)
- Ollama (optional — for free local models)

### Install & Run

```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env    # Edit with your config
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker compose up -d
# API: http://localhost:8000/docs
# Grafana: http://localhost:3001
```

---

## Model Freedom

Switch LLM and embedding providers with one line in `.env`:

```env
# Cloud models (need API key)
PRIMARY_MODEL=anthropic/claude-sonnet-4-20250514
PRIMARY_MODEL=openai/gpt-4o
PRIMARY_MODEL=deepseek/deepseek-chat

# Local models (free, no API key needed)
PRIMARY_MODEL=ollama/llama3
OLLAMA_BASE_URL=http://localhost:11434

# Embedding (also switchable)
EMBEDDING_PROVIDER=local    # Free, CPU, default
EMBEDDING_PROVIDER=ollama   # Free, local
EMBEDDING_PROVIDER=openai   # Paid, best quality
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (async) + Pydantic v2 |
| Orchestration | LangGraph (8-node state graph) |
| LLM | LiteLLM (Claude/GPT/DeepSeek/Ollama/any) |
| RAG | LightRAG (semantic hybrid search) |
| Embedding | sentence-transformers / Ollama / OpenAI (switchable) |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 (multi-layer) |
| Middleware | Circuit breaker, rate limiter, tracing, audit |
| Monitoring | Prometheus + Grafana |
| CI/CD | GitHub Actions |

---

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/qa/ask` | Single-shot QA |
| `POST /api/v1/qa/stream` | SSE streaming QA |
| `GET /api/v1/qa/conversations` | Conversation list |
| `POST /api/v1/kb/collections` | Create knowledge base |
| `POST /api/v1/kb/collections/{id}/documents` | Upload document |
| `POST /api/v1/kb/search` | Semantic search |
| `GET /api/v1/data/*` | 8 business data endpoints |
| `GET /api/v1/admin/stats` | Usage statistics |
| `GET /api/v1/health` | Health check |

Full docs: `http://localhost:8000/docs`

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

46 unit tests covering calculator, formatter, time series.

---

## License

MIT

---

# 中文说明

## 企业 AI 智能问答系统

开源的企业内部 AI 问答平台。员工用自然语言提问，系统自动查数据/文档/API，AI 生成分析报告+图表。

### 核心能力

- **自然语言问答** — 问"资金还能撑多久"，系统精确计算并回答
- **LangGraph 编排** — 8 节点状态图，支持并行、断点续传、条件路由
- **RAG 语义检索** — "到期"≈"结束"≈"截止"，任意说法都能匹配
- **模型自由切换** — Claude/GPT/DeepSeek/Ollama，.env 一行切换
- **知识库** — 上传 PDF/Word/Excel，自动分块索引，语义搜索
- **12 种图表** — AI 推荐最佳图表类型，返回 ECharts 配置
- **精确计算** — Decimal 高精度金融计算器（复利/ROI/现金跑道）
- **答案溯源** — 每条回答标注数据来源
- **报告导出** — Markdown / HTML / PDF，5 种主题

### 技术亮点

| V2 → V3 升级 | 效果 |
|-------------|------|
| 800 行编排器 → LangGraph 80 行 | 代码量减少 90% |
| 50+ 正则 → LightRAG 语义搜索 | 任意说法都能匹配 |
| 双 Client 400 行 → LiteLLM 1 行 | 一行切模型 |
| Flask 同步 → FastAPI 异步 | 并发能力 10 倍 |

### 快速开始

```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

默认用本地 embedding（免费），LLM 配置 .env 里的 `PRIMARY_MODEL`。

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/0xxue">0xxuebao</a></sub>
</p>
