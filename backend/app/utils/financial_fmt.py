"""
Financial Data Formatter

Professional formatting for financial data display.
Supports currencies, percentages, trends, and number simplification.

Examples:
    format_currency(1234567.89)     → "¥1,234,567.89"
    format_percent(12.5, trend=True) → "↑12.50%"
    format_number(1500000)           → "150万"
    format_trend(0.125)              → "↑12.5%"
"""

from decimal import Decimal
from typing import Optional


class FinancialFormatter:
    """Format financial data for display in reports and charts."""

    CURRENCIES = {
        "CNY": {"symbol": "¥", "name": "人民币", "decimals": 2},
        "USD": {"symbol": "$", "name": "美元", "decimals": 2},
        "EUR": {"symbol": "€", "name": "欧元", "decimals": 2},
        "USDT": {"symbol": "₮", "name": "USDT", "decimals": 2},
    }

    TREND_ICONS = {
        "up": "↑",
        "down": "↓",
        "flat": "→",
    }

    @staticmethod
    def format_currency(value, currency: str = "CNY", show_symbol: bool = True) -> str:
        """Format as currency: ¥1,234,567.89"""
        config = FinancialFormatter.CURRENCIES.get(currency, FinancialFormatter.CURRENCIES["CNY"])
        d = config["decimals"]
        formatted = f"{float(value):,.{d}f}"
        if show_symbol:
            return f"{config['symbol']}{formatted}"
        return formatted

    @staticmethod
    def format_percent(value, decimals: int = 2, show_trend: bool = False) -> str:
        """Format as percentage: 12.50% or ↑12.50%"""
        formatted = f"{float(value):.{decimals}f}%"
        if show_trend:
            icon = "↑" if float(value) > 0 else "↓" if float(value) < 0 else "→"
            return f"{icon}{formatted}"
        return formatted

    @staticmethod
    def format_trend(value, as_percent: bool = True) -> str:
        """Format trend with icon: ↑12.5% or ↓3.2%"""
        v = float(value)
        icon = "↑" if v > 0 else "↓" if v < 0 else "→"
        if as_percent:
            return f"{icon}{abs(v):.1f}%"
        return f"{icon}{abs(v):,.2f}"

    @staticmethod
    def format_number(value, locale: str = "zh") -> str:
        """
        Simplify large numbers.
        Chinese: 1500000 → "150万", 120000000 → "1.2亿"
        English: 1500000 → "1.5M", 120000000 → "120M"
        """
        v = float(value)
        abs_v = abs(v)
        sign = "-" if v < 0 else ""

        if locale == "zh":
            if abs_v >= 100_000_000:
                return f"{sign}{abs_v / 100_000_000:.1f}亿"
            elif abs_v >= 10_000:
                return f"{sign}{abs_v / 10_000:.1f}万"
            else:
                return f"{sign}{abs_v:,.0f}"
        else:
            if abs_v >= 1_000_000_000:
                return f"{sign}{abs_v / 1_000_000_000:.1f}B"
            elif abs_v >= 1_000_000:
                return f"{sign}{abs_v / 1_000_000:.1f}M"
            elif abs_v >= 1_000:
                return f"{sign}{abs_v / 1_000:.1f}K"
            else:
                return f"{sign}{abs_v:,.0f}"

    @staticmethod
    def format_days(days: int) -> str:
        """Format days into human-readable: 45天 or 6周2天"""
        if days < 0:
            return "无限"
        if days < 7:
            return f"{days}天"
        weeks = days // 7
        remaining = days % 7
        if remaining == 0:
            return f"{weeks}周"
        return f"{weeks}周{remaining}天"

    @staticmethod
    def status_badge(status: str) -> str:
        """Return status with emoji badge."""
        badges = {
            "healthy": "🟢 健康",
            "warning": "🟡 警告",
            "critical": "🔴 危险",
            "up": "📈 上升",
            "down": "📉 下降",
            "flat": "➡️ 持平",
        }
        return badges.get(status, status)

    @staticmethod
    def format_table_row(data: dict, columns: list[str]) -> list[str]:
        """Format a dict as a table row."""
        return [str(data.get(col, "-")) for col in columns]
