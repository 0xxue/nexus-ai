"""
Retry with Exponential Backoff

Decorator for retrying failed external API calls with configurable
backoff strategy. Works independently from circuit breaker.

Circuit Breaker = stop calling a broken service entirely
Retry = try again a few times before giving up on a single request

Usage:
    @retry(max_attempts=3, base_delay=1.0, max_delay=30.0)
    async def fetch_polymarket_data():
        ...

    # Or with specific exceptions:
    @retry(max_attempts=3, retry_on=(httpx.TimeoutException, httpx.ConnectError))
    async def fetch_data():
        ...
"""

import asyncio
import logging
import functools
from typing import Tuple, Type

logger = logging.getLogger("predict.retry")


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including first try)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Multiplier for each retry (2.0 = double each time)
        retry_on: Tuple of exception types that trigger a retry
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"[Retry] {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff + jitter
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay,
                    )
                    # Add jitter (±25%) to prevent thundering herd
                    import random
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    actual_delay = max(0, delay + jitter)

                    logger.warning(
                        f"[Retry] {func.__name__} attempt {attempt}/{max_attempts} "
                        f"failed: {e}. Retrying in {actual_delay:.1f}s..."
                    )

                    await asyncio.sleep(actual_delay)

            raise last_exception

        return wrapper
    return decorator


class RetryConfig:
    """
    Predefined retry configurations for different external services.

    Usage:
        @retry(**RetryConfig.EXTERNAL_API)
        async def fetch_data(): ...
    """

    # Standard external API (moderate retry)
    EXTERNAL_API = {
        "max_attempts": 3,
        "base_delay": 1.0,
        "max_delay": 15.0,
    }

    # Flaky API (aggressive retry)
    FLAKY_API = {
        "max_attempts": 5,
        "base_delay": 0.5,
        "max_delay": 30.0,
    }

    # Database operations (quick retry)
    DATABASE = {
        "max_attempts": 2,
        "base_delay": 0.2,
        "max_delay": 2.0,
    }

    # Critical operations (conservative)
    CRITICAL = {
        "max_attempts": 3,
        "base_delay": 2.0,
        "max_delay": 60.0,
    }
