# AI Bot Agent — Feasibility Analysis

> Technical feasibility, risk assessment, cost analysis, and timeline for the AI Bot Agent module.

---

## 1. Technical Feasibility

### 1.1 LLM Function Calling (Core Capability)

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| LLM can decide which tool to call | ✅ Proven | OpenAI/DeepSeek/Claude all support function calling natively |
| Multi-step tool chains (tool1 → tool2 → answer) | ✅ Proven | Standard AI Agent pattern, LangChain/LangGraph widely used |
| LLM responds in <5s for tool decisions | ✅ Tested | DeepSeek function calling: ~2-4s, GPT-4o: ~1-3s |
| Works with local models (Ollama) | ⚠️ Limited | Ollama supports tool calling in llama3/qwen2.5 but less reliable |

**Verdict:** Function calling is mature technology. All major LLM providers support it. DeepSeek is cheapest and fast enough.

### 1.2 WebSocket Real-time Communication

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| FastAPI WebSocket support | ✅ Native | FastAPI has built-in WebSocket with Starlette |
| Multi-user connection pool | ✅ Simple | Dict-based connection manager, well-documented pattern |
| JWT auth over WebSocket | ✅ Standard | Token passed as query param or first message |
| Reconnect on disconnect | ✅ Frontend | Standard WebSocket reconnect pattern |
| Background push (server → client) | ✅ Native | WebSocket is bidirectional by design |

**Verdict:** WebSocket is the right choice. HTTP SSE (current QA approach) is one-directional; Bot needs bidirectional for proactive push.

### 1.3 Emotion Engine

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| Map context → emotion | ✅ Simple | Rule-based mapping, no ML needed |
| VRM 3D expressions | ✅ Done | Already implemented: 7 emotions, 3 actions via BotPlugin |
| LLM can set emotion via tool | ✅ Simple | Just another tool in the toolset |
| Smooth transitions | ✅ Done | VRM plugin handles animation timing |

**Verdict:** Emotion system is already built on frontend. Backend just sends emotion name via WebSocket.

### 1.4 Scene Awareness

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| Detect page navigation | ✅ Simple | React Router change → send WebSocket event |
| Configurable scene → response | ✅ Simple | JSON/DB config, template rendering |
| Dynamic data in scene response | ✅ Existing | Reuse existing data service APIs |
| Priority-based mode filtering | ✅ Simple | Integer comparison |

**Verdict:** Scene system is pure configuration + routing. No technical risk.

### 1.5 Proactive Alerts

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| Background scheduled tasks | ✅ Standard | `asyncio.create_task` + `asyncio.sleep` loop, or APScheduler |
| Check data anomalies | ✅ Existing | Reuse data service + time series anomaly detection (already built) |
| Push to specific users | ✅ WebSocket | Connection pool lookup by user_id |

**Verdict:** All components exist. Just need to wire them together.

### 1.6 npm Package Distribution

| Requirement | Feasibility | Evidence |
|-------------|------------|---------|
| Extract React components into package | ✅ Standard | Vite library mode or tsup bundling |
| BotPlugin interface for customization | ✅ Done | Interface already defined and working |
| WebSocket client in package | ✅ Simple | Thin wrapper around native WebSocket |
| Tree-shakeable | ✅ With bundler | ESM exports + proper package.json |

**Verdict:** Standard npm package workflow. No special challenges.

---

## 2. Risk Assessment

### High Risk

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucinates tool calls (calls wrong tool) | User data modified incorrectly | Medium | Confirmation prompt for destructive operations (delete, role change). Audit log all tool calls. |
| LLM infinite loop (keeps calling tools) | Server resource exhaustion | Low | Max 5 iterations hard limit. Timeout per request. |
| WebSocket memory leak (connections not cleaned) | Server OOM over time | Medium | Heartbeat ping/pong. Auto-disconnect on timeout. Connection limit per user. |

### Medium Risk

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DeepSeek function calling quality | Wrong tool params, missed calls | Medium | Fallback to GPT-4o for complex tool decisions. Unit test each tool. |
| High latency for multi-step tool chains | Bad UX, user thinks it's frozen | Medium | Stream intermediate steps ("Calling get_stats...", "Processing..."). Show emotion changes during processing. |
| Ollama local models poor at function calling | Users with free setup can't use Bot | High | Graceful degradation: if function calling fails, fall back to keyword-based tool matching. |

### Low Risk

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| VRM model performance on low-end devices | Bot laggy on old phones | Low | Detect GPU capability. Fall back to 2D avatar or disable 3D. |
| npm package size too large (Three.js) | Slow install for users | Low | Three.js as peer dependency. Lazy load VRM plugin. |
| WebSocket blocked by corporate proxy | Bot can't connect | Low | HTTP long-polling fallback. Or use SSE for server→client. |

---

## 3. Cost Analysis

### Development Cost (Time)

| Phase | Scope | Estimated Time | Developer |
|-------|-------|---------------|-----------|
| Phase 1: Core Agent | WebSocket + Tools + Brain + Emotion | 3-5 days | 1 fullstack |
| Phase 2: Scene Awareness | Scene handler + Mode controller | 2-3 days | 1 fullstack |
| Phase 3: Proactive Alerts | Background tasks + push | 1-2 days | 1 fullstack |
| Phase 4: Persona + Voice | Config + Web Speech API | 2-3 days | 1 fullstack |
| Phase 5: npm Package | Extract + publish + docs | 3-5 days | 1 fullstack |
| **Total** | | **11-18 days** | |

### Runtime Cost (Monthly)

| Resource | Free Option | Paid Option | Notes |
|----------|-------------|-------------|-------|
| LLM (Bot Brain) | Ollama (local, $0) | DeepSeek ($0.14/1M tokens) | ~10K messages/month ≈ $1-5 |
| LLM (QA System) | Same as above | Same | Already budgeted |
| Server | Existing server | Same | No additional infra |
| TTS/STT | Browser native ($0) | OpenAI TTS ($15/1M chars) | Optional, default free |
| npm hosting | npmjs.com ($0) | Same | Free for public packages |
| **Total** | **$0** | **$5-20/month** | |

### Comparison with Alternatives

| Solution | Effort | Cost | Customization | Offline |
|----------|--------|------|--------------|---------|
| **Our AI Bot Agent** | 2-3 weeks | $0-20/mo | Full control | ✅ Ollama |
| Dify Bot | 0 (hosted) | $20+/mo | Limited | ❌ |
| Botpress | 1 week | $0-50/mo | Medium | ❌ |
| Custom from scratch (no LLM tools) | 2+ months | Same | Full | ✅ |
| ChatGPT Plugin | 1 week | $20+/mo | Limited | ❌ |

**Our approach is the best balance of cost, customization, and development time.**

---

## 4. Dependency Analysis

### Backend Dependencies (Already Installed)

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| FastAPI | 0.135+ | WebSocket endpoint | ✅ Installed |
| LiteLLM | 1.77 | Function calling to any LLM | ✅ Installed |
| structlog | 25+ | Logging | ✅ Installed |
| asyncpg | 0.31+ | Database | ✅ Installed |
| redis | 7+ | Rate limiting, caching | ✅ Installed |

### Frontend Dependencies (Already Installed)

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| React | 19 | UI framework | ✅ Installed |
| Zustand | 5+ | State management | ✅ Installed |
| Three.js | 0.161 | 3D rendering | ✅ Installed |
| @pixiv/three-vrm | 3.3.3 | VRM character | ✅ Installed |

### New Dependencies Needed

| Package | Purpose | Size |
|---------|---------|------|
| None (backend) | All existing | — |
| None (frontend) | All existing | — |

**Zero new dependencies required.** Everything is built on top of existing stack.

---

## 5. Performance Projections

| Metric | Target | Basis |
|--------|--------|-------|
| WebSocket connections per server | 1,000+ | FastAPI/Starlette handles 10K+ concurrent WS |
| Tool call latency | < 500ms | Direct API calls to internal services |
| LLM response (with tools) | 3-8s | DeepSeek function calling benchmarks |
| LLM response (direct answer) | 2-5s | Same as current QA system |
| Emotion transition | < 100ms | Frontend-only, instant |
| Memory per connection | ~50KB | WebSocket state + user context |
| Background alert check | < 1s | Simple DB queries |

### Scaling

| Users | Server | Strategy |
|-------|--------|----------|
| 1-100 | Single 2GB VPS | Current setup |
| 100-1000 | Single 4GB VPS | Uvicorn workers=4 |
| 1000-10000 | 2+ servers | Redis pub/sub for WS coordination |
| 10000+ | Kubernetes | Horizontal pod autoscaling |

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Tool calls modify data without user consent | Destructive tools (delete, role change) require explicit confirmation via "Are you sure?" response before executing |
| User impersonation via WebSocket | JWT authentication on WebSocket connection |
| Tool escalation (user role → admin tools) | RBAC check before each tool execution |
| Prompt injection (user tricks Bot into calling tools) | System prompt hardened: "ONLY use tools when explicitly requested by user" |
| Audit trail | Every tool call logged to bot_messages table with tool_name and tool_result |
| Rate limiting | Max 20 tool calls per minute per user |

---

## 7. Compatibility Matrix

| Target | Compatible | Notes |
|--------|-----------|-------|
| Chrome 90+ | ✅ | WebSocket + Web Speech API |
| Firefox 90+ | ✅ | WebSocket + limited Speech API |
| Safari 15+ | ✅ | WebSocket, Speech API on macOS only |
| Mobile Chrome | ✅ | Responsive + mobile bot size |
| Mobile Safari | ⚠️ | WebSocket works, Speech API limited |
| React 18+ | ✅ | npm package compatible |
| React 19 | ✅ | Current project version |
| Vue/Svelte | ⚠️ | Would need framework adapter (Phase 5+) |
| Node.js backend | ⚠️ | Bot server is Python; would need JS port |
| Python 3.11+ | ✅ | Current backend |

---

## 8. Success Metrics

| KPI | Phase 1 | Phase 3 | Phase 5 |
|-----|---------|---------|---------|
| Tool execution success rate | > 90% | > 95% | > 95% |
| Average response time | < 8s | < 5s | < 5s |
| Emotion accuracy | > 80% | > 90% | > 95% |
| WebSocket uptime | > 99% | > 99.5% | > 99.9% |
| User satisfaction (if tracked) | — | > 4/5 | > 4.5/5 |
| npm weekly downloads | — | — | > 100 |
| GitHub stars | — | — | > 50 |

---

## 9. Decision

### Recommendation: **PROCEED**

**Reasons:**
1. **Zero new dependencies** — everything built on existing stack
2. **Incremental delivery** — each phase is independently useful
3. **Low cost** — $0 with Ollama, $5/month with DeepSeek
4. **High differentiation** — few open-source projects have AI Agent Bot with 3D avatar + tool calling + emotion system
5. **Proven technology** — Function calling, WebSocket, VRM all mature
6. **Reusable** — npm package makes it valuable beyond this project

### What sets this apart from competitors:

| Feature | Us | Dify | Botpress | ChatGPT |
|---------|-----|------|----------|---------|
| 3D Avatar with emotions | ✅ | ❌ | ❌ | ❌ |
| Tool calling (execute system ops) | ✅ | ✅ | ⚠️ | ✅ |
| Scene-aware (page context) | ✅ | ❌ | ❌ | ❌ |
| Proactive alerts | ✅ | ❌ | ⚠️ | ❌ |
| Fully open source | ✅ | ⚠️ | ⚠️ | ❌ |
| Any LLM (including local) | ✅ | ⚠️ | ❌ | ❌ |
| Pluggable avatar system | ✅ | ❌ | ❌ | ❌ |
| npm package for integration | ✅ | ❌ | ❌ | ❌ |
| Self-hosted / air-gapped | ✅ | ❌ | ❌ | ❌ |

---

*Approved. Proceed to Phase 1 implementation.*
