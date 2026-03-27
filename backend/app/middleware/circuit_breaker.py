"""
Circuit Breaker Pattern Implementation

Protects the system from cascading failures when external APIs
(Polymarket, Opinion, Kalshi, etc.) become unavailable.

States:
    CLOSED  → Normal operation, requests pass through
    OPEN    → Circuit tripped, requests fail fast with fallback
    HALF_OPEN → Testing if service recovered

Reference: Netflix Hystrix pattern

Usage:
    breaker = CircuitBreaker(name="polymarket", failure_threshold=5, recovery_timeout=60)

    try:
        result = await breaker.call(fetch_polymarket_data, params)
    except CircuitOpenError:
        # Return cached/fallback data
        result = get_cached_data()
"""

import time
import asyncio
import logging
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("predict.circuit_breaker")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when circuit is open and requests are being rejected."""
    pass


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for external API calls.

    Args:
        name: Identifier for this circuit (e.g., "polymarket", "opinion")
        failure_threshold: Number of consecutive failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery (half-open)
        success_threshold: Successes needed in half-open to close circuit
    """
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 2

    # Internal state
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: float = field(default=0)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        async with self._lock:
            self._check_state_transition()

            if self.state == CircuitState.OPEN:
                logger.warning(
                    f"[CircuitBreaker:{self.name}] OPEN - rejecting request "
                    f"(failures={self.failure_count}, recovery in "
                    f"{self.recovery_timeout - (time.time() - self.last_failure_time):.0f}s)"
                )
                raise CircuitOpenError(
                    f"Circuit '{self.name}' is open. "
                    f"Service unavailable, using fallback."
                )

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure(e)
            raise

    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self._close()
            else:
                self.failure_count = 0

    async def _on_failure(self, error: Exception):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.error(
                f"[CircuitBreaker:{self.name}] Failure #{self.failure_count}: {error}"
            )

            if self.state == CircuitState.HALF_OPEN:
                self._open()
            elif self.failure_count >= self.failure_threshold:
                self._open()

    def _check_state_transition(self):
        if (
            self.state == CircuitState.OPEN
            and time.time() - self.last_failure_time >= self.recovery_timeout
        ):
            self._half_open()

    def _open(self):
        self.state = CircuitState.OPEN
        logger.warning(
            f"[CircuitBreaker:{self.name}] → OPEN "
            f"(after {self.failure_count} failures)"
        )

    def _half_open(self):
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        logger.info(f"[CircuitBreaker:{self.name}] → HALF_OPEN (testing recovery)")

    def _close(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"[CircuitBreaker:{self.name}] → CLOSED (recovered)")

    @property
    def stats(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time,
        }


class CircuitBreakerRegistry:
    """
    Global registry of circuit breakers for all external services.

    Usage:
        registry = CircuitBreakerRegistry()
        polymarket_breaker = registry.get("polymarket")
        opinion_breaker = registry.get("opinion")
    """

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return self._breakers[name]

    def get_all_stats(self) -> list[dict]:
        return [b.stats for b in self._breakers.values()]


# Global singleton
circuit_registry = CircuitBreakerRegistry()
