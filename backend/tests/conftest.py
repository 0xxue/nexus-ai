"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_analysis():
    return {
        "answer": "系统运营稳定，总用户12580。",
        "confidence": 0.85,
        "sources": [{"type": "api", "name": "system_overview"}],
        "key_metrics": [{"name": "总用户", "value": "12,580", "trend": "up"}],
        "suggestions": ["加大获客"],
    }
