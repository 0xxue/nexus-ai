# ADR-001: LangGraph over Custom Orchestrator

**Status:** Accepted

## Context
V2 used an 800-line hand-written orchestrator with if/else routing. Hard to maintain, no parallelism, no checkpoint.

## Decision
Replace with LangGraph state graph (~80 lines). 8 nodes with conditional edges.

## Consequences
- **Positive:** Parallel execution (fan-out), checkpoint/resume, visual debugging via LangSmith, easy to add nodes
- **Negative:** LangGraph dependency, learning curve for contributors
