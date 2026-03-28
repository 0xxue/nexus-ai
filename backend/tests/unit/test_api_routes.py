"""Tests for API route registration."""

import pytest


class TestRoutes:
    """Verify all API routes are registered."""

    def test_qa_routes(self):
        from app.api.v1.qa import router
        paths = {r.path for r in router.routes}
        assert "/ask" in paths
        assert "/stream" in paths
        assert "/conversations" in paths
        assert "/conversations/{conv_id}" in paths
        assert "/conversations/{conv_id}/summary" in paths

    def test_bot_routes(self):
        from app.api.v1.bot import router
        paths = {r.path for r in router.routes}
        assert "/messages" in paths
        assert "/scenes" in paths
        assert "/preferences" in paths
        assert "/stats" in paths
        assert "/tts" in paths
        assert "/tts/voices" in paths
        assert "/cleanup" in paths

    def test_main_router_includes_all(self):
        from app.api.v1.router import api_router
        # Check that sub-routers are mounted
        route_strs = str([r.path for r in api_router.routes])
        for prefix in ["/auth", "/qa", "/data", "/kb", "/admin", "/bot"]:
            assert prefix in route_strs, f"Missing {prefix} in main router"

    def test_auth_routes(self):
        from app.api.v1.auth import router
        paths = {r.path for r in router.routes}
        assert "/login" in paths
        assert "/register" in paths
