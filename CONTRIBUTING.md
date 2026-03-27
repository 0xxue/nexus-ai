# Contributing

## Setup

```bash
cd backend
pip install -e ".[dev]"
cp .env.example .env
make dev
```

## Testing

```bash
make test          # All tests
make test-cov      # With coverage
```

## Code Style

- Python: ruff (auto-format)
- Commit: Conventional Commits (feat/fix/docs/test/chore)

## Adding a New Data Source

1. Add method to `app/services/data_service.py`
2. Add API description to `app/services/rag.py` → `API_DESCRIPTIONS`
3. Add tests

## Adding a New LangGraph Node

1. Write node function in `app/core/langgraph/nodes.py`
2. Register in `app/core/langgraph/graph.py`
3. Add tests
