"""Unit tests for the financial calculator."""

import pytest
from decimal import Decimal
from app.utils.calculator import Calculator


@pytest.fixture
def calc():
    return Calculator(precision=2)


class TestBasicStats:

    def test_average(self, calc):
        assert calc.average([10, 20, 30]) == Decimal("20.00")

    def test_average_empty(self, calc):
        assert calc.average([]) == Decimal("0")

    def test_growth_rate(self, calc):
        assert calc.growth_rate(100, 120) == Decimal("20.00")

    def test_growth_rate_negative(self, calc):
        assert calc.growth_rate(100, 80) == Decimal("-20.00")

    def test_growth_rate_zero_base(self, calc):
        assert calc.growth_rate(0, 100) == Decimal("0")

    def test_trend_up(self, calc):
        result = calc.trend([10, 20, 30, 40, 50])
        assert result["direction"] == "up"
        assert result["change"] == Decimal("40.00")

    def test_trend_down(self, calc):
        result = calc.trend([50, 40, 30, 20, 10])
        assert result["direction"] == "down"

    def test_comparison(self, calc):
        result = calc.comparison(150, 100)
        assert result["difference"] == Decimal("50.00")
        assert result["larger"] == "a"


class TestFinancial:

    def test_compound_interest(self, calc):
        result = calc.compound_interest(10000, 10, 1)
        assert result["final_amount"] == Decimal("11000.00")
        assert result["total_interest"] == Decimal("1000.00")

    def test_roi(self, calc):
        result = calc.roi(10000, 15000)
        assert result["profit"] == Decimal("5000.00")
        assert result["roi"] == Decimal("50.00")

    def test_cash_runway_healthy(self, calc):
        result = calc.cash_runway(1000000, 10000)
        assert result["days_remaining"] == 100
        assert result["status"] == "healthy"

    def test_cash_runway_critical(self, calc):
        result = calc.cash_runway(50000, 10000)
        assert result["days_remaining"] == 5
        assert result["status"] == "critical"

    def test_cash_runway_zero_burn(self, calc):
        result = calc.cash_runway(1000000, 0)
        assert result["status"] == "no_burn"


class TestPrediction:

    def test_linear_prediction(self, calc):
        result = calc.linear_prediction([10, 20, 30, 40, 50], future_steps=3)
        assert result["trend"] == "up"
        assert len(result["predictions"]) == 3
        assert result["predictions"][0] >= Decimal("50")

    def test_linear_prediction_insufficient(self, calc):
        result = calc.linear_prediction([10])
        assert "error" in result


class TestAggregation:

    def test_sum(self, calc):
        assert calc.aggregate([10, 20, 30], "sum") == Decimal("60.00")

    def test_avg(self, calc):
        assert calc.aggregate([10, 20, 30], "avg") == Decimal("20.00")

    def test_min(self, calc):
        assert calc.aggregate([10, 20, 30], "min") == Decimal("10.00")

    def test_max(self, calc):
        assert calc.aggregate([10, 20, 30], "max") == Decimal("30.00")

    def test_count(self, calc):
        assert calc.aggregate([10, 20, 30], "count") == Decimal("3")
