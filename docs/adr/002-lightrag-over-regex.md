# ADR-002: LightRAG over Regex Pattern Matching

**Status:** Accepted

## Context
V2 used 50+ regex patterns to route user queries to API endpoints. New phrasings required adding new regex. "到期" worked but "结束" didn't.

## Decision
Replace with LightRAG semantic search. API descriptions indexed as documents. User queries matched by embedding similarity.

## Consequences
- **Positive:** Any phrasing works ("到期" ≈ "结束" ≈ "截止"), zero maintenance for new phrasings
- **Negative:** Requires embedding model (local sentence-transformers is free), slightly slower than regex
