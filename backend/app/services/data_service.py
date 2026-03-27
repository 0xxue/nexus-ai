"""
Data Service — 8 internal business API endpoints

Wraps data access with:
- Redis multi-layer caching (L1: 30s hot, L2: 5min stale fallback)
- Circuit breaker per endpoint
- Retry with exponential backoff

In production, these call real internal APIs (HTTP).
For demo/testing, returns realistic mock data.
"""

import structlog
from typing import Optional
from datetime import datetime, timedelta
from app.services.cache import cache_get, cache_set
from app.middleware.circuit_breaker import circuit_registry
from app.middleware.retry import retry, RetryConfig

logger = structlog.get_logger()


class DataService:
    """
    Business data access layer.
    Each method maps to an internal API endpoint.
    """

    async def call_api(self, endpoint: str, params: dict = None) -> dict:
        """Generic API caller with cache + circuit breaker."""
        cache_key = f"data:{endpoint}:{hash(str(params or {}))}"

        # L1 cache
        cached = await cache_get(cache_key)
        if cached:
            return cached

        # Call with circuit breaker
        breaker = circuit_registry.get(endpoint.split("/")[-1])
        try:
            result = await breaker.call(self._fetch, endpoint, params or {})
            # Update cache
            await cache_set(cache_key, result, ttl=30)
            await cache_set(f"stale:{cache_key}", result, ttl=300)  # L2 stale cache
            return result
        except Exception as e:
            # Fallback to stale cache
            stale = await cache_get(f"stale:{cache_key}")
            if stale:
                logger.warning("Using stale cache", endpoint=endpoint)
                return {**stale, "_stale": True}
            raise

    @retry(**RetryConfig.EXTERNAL_API)
    async def _fetch(self, endpoint: str, params: dict) -> dict:
        """
        Actual API call. In production, replace with httpx calls to internal services.
        For demo, returns realistic mock data.
        """
        # TODO: Replace with real HTTP calls in production
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"http://internal-api{endpoint}", params=params)
        #     return response.json()

        return self._mock_data(endpoint, params)

    # ========== 8 Business API Methods ==========

    async def get_system_overview(self) -> dict:
        """API 1: System overview — total users, active, funds, health."""
        return await self.call_api("/data/system/overview")

    async def get_daily_data(self, date: str = None) -> dict:
        """API 2: Daily operational data."""
        return await self.call_api("/data/daily", {"date": date})

    async def get_expiring_products(self, date: str = None) -> dict:
        """API 3: Products expiring on a specific date."""
        return await self.call_api("/data/products/expiring", {"date": date})

    async def get_product_interval(self, start_date: str = None, end_date: str = None) -> dict:
        """API 4: Products expiring in a date range."""
        return await self.call_api("/data/products/interval", {"start_date": start_date, "end_date": end_date})

    async def get_user_data(self) -> dict:
        """API 5: User statistics."""
        return await self.call_api("/data/users/stats")

    async def get_vip_distribution(self) -> dict:
        """API 6: VIP level distribution."""
        return await self.call_api("/data/users/vip")

    async def get_finance_summary(self, period: str = "daily") -> dict:
        """API 7: Financial summary — income, expenses, profit, runway."""
        return await self.call_api("/data/finance/summary", {"period": period})

    async def get_product_stats(self, start_date: str = None, end_date: str = None) -> dict:
        """API 8: Product statistics and trends."""
        return await self.call_api("/data/products/stats", {"start_date": start_date, "end_date": end_date})

    # ========== Mock Data (for demo/testing) ==========

    def _mock_data(self, endpoint: str, params: dict) -> dict:
        """Realistic mock data for each endpoint."""
        today = datetime.now().strftime("%Y-%m-%d")

        mocks = {
            "/data/system/overview": {
                "total_users": 12580,
                "active_users": 3456,
                "new_users_today": 89,
                "total_funds": 8500000.00,
                "daily_consumption": 125000.00,
                "system_health": "healthy",
                "query_time": today,
            },
            "/data/daily": {
                "date": params.get("date", today),
                "new_users": 89,
                "active_users": 3456,
                "transactions": 1234,
                "revenue": 456000.00,
                "expenses": 312000.00,
            },
            "/data/products/expiring": {
                "date": params.get("date", today),
                "total": 23,
                "products": [
                    {"name": f"产品-{i}", "amount": 50000 + i * 10000, "expire_date": today}
                    for i in range(5)
                ],
                "total_amount": 850000.00,
            },
            "/data/products/interval": {
                "start_date": params.get("start_date", today),
                "end_date": params.get("end_date", today),
                "total": 45,
                "daily_breakdown": [
                    {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 5 + i, "amount": 100000 + i * 20000}
                    for i in range(7)
                ],
            },
            "/data/users/stats": {
                "total": 12580,
                "active": 3456,
                "new_today": 89,
                "retention_7d": 72.5,
                "retention_30d": 45.8,
                "growth_rate": 5.2,
            },
            "/data/users/vip": {
                "levels": [
                    {"level": "VIP1", "count": 5000, "percentage": 39.7},
                    {"level": "VIP2", "count": 3500, "percentage": 27.8},
                    {"level": "VIP3", "count": 2500, "percentage": 19.9},
                    {"level": "VIP4", "count": 1000, "percentage": 7.9},
                    {"level": "VIP5", "count": 580, "percentage": 4.6},
                ],
            },
            "/data/finance/summary": {
                "period": params.get("period", "daily"),
                "revenue": 456000.00,
                "expenses": 312000.00,
                "profit": 144000.00,
                "balance": 8500000.00,
                "daily_burn": 125000.00,
                "runway_days": 68,
                "runway_status": "healthy",
            },
            "/data/products/stats": {
                "total_products": 580,
                "active_products": 456,
                "new_products_this_week": 23,
                "expiring_this_week": 15,
                "trend": [
                    {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "active": 450 + i * 2, "new": 3 + i}
                    for i in range(7)
                ],
            },
        }

        # Normalize endpoint — strip /api/v1 prefix if present
        normalized = endpoint.replace("/api/v1", "")
        return mocks.get(normalized, {"error": f"Unknown endpoint: {endpoint}"})
