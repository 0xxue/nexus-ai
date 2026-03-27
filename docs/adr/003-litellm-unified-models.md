# ADR-003: LiteLLM Unified Model Interface

**Status:** Accepted

## Context
V2 had separate ClaudeClient (200+ lines) and OpenAIClient (200+ lines). Adding DeepSeek would require writing another client.

## Decision
Use LiteLLM as unified interface. One-line model switching via .env. Support Claude, GPT, DeepSeek, Ollama local, any OpenAI-compatible API.

## Consequences
- **Positive:** Add new model = change one env var. Built-in fallback chain, token counting, budget control
- **Negative:** LiteLLM dependency (mitigated by pinning to pre-attack version <=1.77.5)
- **Note:** LiteLLM supply chain attack on 2026-03-24 (v1.82.7/1.82.8). We pin to safe range.
