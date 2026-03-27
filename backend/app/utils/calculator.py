"""
Unified Financial Calculator

12 types of precise calculations using Decimal for financial accuracy.
AI can't do math reliably — this module handles all numerical computations.

Migrated from V2's UnifiedCalculator, adapted for V3 architecture.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import structlog

logger = structlog.get_logger()


class Calculator:
    """
    High-precision financial calculator.
    All monetary calculations use Decimal to avoid floating-point errors.
    """

    def __init__(self, precision: int = 2):
        self.precision = precision

    def _d(self, value) -> Decimal:
        """Convert to Decimal safely."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _round(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal(f"0.{'0' * self.precision}"), rounding=ROUND_HALF_UP)

    # ========== Basic Statistics ==========

    def average(self, values: list) -> Decimal:
        """Calculate average of a list of values."""
        if not values:
            return Decimal("0")
        total = sum(self._d(v) for v in values)
        return self._round(total / len(values))

    def growth_rate(self, old_value, new_value) -> Decimal:
        """Calculate growth rate: (new - old) / old * 100."""
        old = self._d(old_value)
        new = self._d(new_value)
        if old == 0:
            return Decimal("0")
        rate = (new - old) / old * 100
        return self._round(rate)

    def trend(self, values: list) -> dict:
        """Analyze trend from a list of values."""
        if len(values) < 2:
            return {"direction": "insufficient_data", "change": Decimal("0")}
        first = self._d(values[0])
        last = self._d(values[-1])
        change = last - first
        rate = self.growth_rate(first, last) if first != 0 else Decimal("0")
        direction = "up" if change > 0 else "down" if change < 0 else "flat"
        return {
            "direction": direction,
            "change": self._round(change),
            "rate": rate,
            "start": self._round(first),
            "end": self._round(last),
        }

    def comparison(self, value_a, value_b) -> dict:
        """Compare two values."""
        a = self._d(value_a)
        b = self._d(value_b)
        diff = a - b
        rate = self.growth_rate(b, a) if b != 0 else Decimal("0")
        return {
            "value_a": self._round(a),
            "value_b": self._round(b),
            "difference": self._round(diff),
            "rate": rate,
            "larger": "a" if a > b else "b" if b > a else "equal",
        }

    # ========== Financial Calculations ==========

    def compound_interest(self, principal, rate, periods: int, compounds_per_period: int = 1) -> dict:
        """
        Compound interest calculation.
        A = P(1 + r/n)^(nt)
        """
        p = self._d(principal)
        r = self._d(rate) / 100
        n = self._d(compounds_per_period)
        t = self._d(periods)

        amount = p * (1 + r / n) ** (n * t)
        interest = amount - p

        return {
            "principal": self._round(p),
            "rate": self._round(self._d(rate)),
            "periods": periods,
            "final_amount": self._round(amount),
            "total_interest": self._round(interest),
        }

    def roi(self, investment, revenue) -> dict:
        """Return on Investment: (revenue - investment) / investment * 100."""
        inv = self._d(investment)
        rev = self._d(revenue)
        if inv == 0:
            return {"roi": Decimal("0"), "profit": Decimal("0")}
        profit = rev - inv
        roi_pct = profit / inv * 100
        return {
            "investment": self._round(inv),
            "revenue": self._round(rev),
            "profit": self._round(profit),
            "roi": self._round(roi_pct),
        }

    def cash_runway(self, balance, daily_burn) -> dict:
        """
        How many days can the fund last?
        runway = balance / daily_burn
        """
        bal = self._d(balance)
        burn = self._d(daily_burn)
        if burn == 0:
            return {"days": -1, "status": "no_burn"}
        days = bal / burn
        return {
            "balance": self._round(bal),
            "daily_burn": self._round(burn),
            "days_remaining": int(days),
            "weeks_remaining": int(days / 7),
            "status": "critical" if days < 7 else "warning" if days < 30 else "healthy",
        }

    def financial_ratio(self, numerator, denominator, ratio_name: str = "ratio") -> dict:
        """Generic financial ratio calculation."""
        n = self._d(numerator)
        d = self._d(denominator)
        if d == 0:
            return {ratio_name: Decimal("0"), "status": "division_by_zero"}
        ratio = n / d
        return {ratio_name: self._round(ratio)}

    # ========== Prediction ==========

    def linear_prediction(self, values: list, future_steps: int = 7) -> dict:
        """
        Simple linear trend prediction.
        Fits a line through the data and extrapolates.
        """
        if len(values) < 2:
            return {"error": "Need at least 2 data points"}

        n = len(values)
        x_vals = list(range(n))
        y_vals = [self._d(v) for v in values]

        # Linear regression: y = mx + b
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(self._d(x) * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(self._d(x) ** 2 for x in x_vals)

        denominator = self._d(n) * sum_x2 - self._d(sum_x) ** 2
        if denominator == 0:
            return {"error": "Cannot fit line (all x values same)"}

        m = (self._d(n) * sum_xy - self._d(sum_x) * sum_y) / denominator
        b = (sum_y - m * self._d(sum_x)) / self._d(n)

        predictions = []
        for i in range(n, n + future_steps):
            pred = m * self._d(i) + b
            predictions.append(self._round(pred))

        return {
            "slope": self._round(m),
            "intercept": self._round(b),
            "predictions": predictions,
            "trend": "up" if m > 0 else "down" if m < 0 else "flat",
        }

    # ========== Business Analytics ==========

    def expiry_analysis(self, products: list) -> dict:
        """Analyze product expiry distribution."""
        total = len(products)
        if total == 0:
            return {"total": 0, "summary": "No products"}

        total_amount = sum(self._d(p.get("amount", 0)) for p in products)
        avg_amount = total_amount / total

        return {
            "total_products": total,
            "total_amount": self._round(total_amount),
            "average_amount": self._round(avg_amount),
        }

    def user_analysis(self, total_users: int, active_users: int, new_users: int) -> dict:
        """User engagement metrics."""
        active_rate = self._d(active_users) / self._d(total_users) * 100 if total_users > 0 else Decimal("0")
        new_rate = self._d(new_users) / self._d(total_users) * 100 if total_users > 0 else Decimal("0")
        return {
            "total": total_users,
            "active": active_users,
            "new": new_users,
            "active_rate": self._round(active_rate),
            "new_rate": self._round(new_rate),
        }

    def aggregate(self, values: list, operation: str = "sum") -> Decimal:
        """Generic aggregation: sum, avg, min, max, count."""
        if not values:
            return Decimal("0")
        decimals = [self._d(v) for v in values]
        match operation:
            case "sum":
                return self._round(sum(decimals))
            case "avg":
                return self._round(sum(decimals) / len(decimals))
            case "min":
                return self._round(min(decimals))
            case "max":
                return self._round(max(decimals))
            case "count":
                return Decimal(str(len(values)))
            case _:
                return self._round(sum(decimals))
