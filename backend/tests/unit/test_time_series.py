"""Unit tests for time series builder."""

from app.utils.time_series import TimeSeriesBuilder as ts


class TestFillMissing:
    def test_fill_gaps(self):
        data = [
            {"date": "2025-01-01", "value": 10},
            {"date": "2025-01-03", "value": 30},
        ]
        filled = ts.fill_missing_dates(data)
        assert len(filled) == 3
        assert filled[1]["value"] == 0
        assert filled[1]["_filled"] is True


class TestTrend:
    def test_up(self):
        assert ts.detect_trend([1, 2, 3, 4, 5, 6, 7, 8]) == "up"

    def test_down(self):
        assert ts.detect_trend([8, 7, 6, 5, 4, 3, 2, 1]) == "down"

    def test_flat(self):
        assert ts.detect_trend([5, 5, 5, 5, 5, 5, 5, 5]) == "flat"

    def test_insufficient(self):
        assert ts.detect_trend([1, 2]) == "insufficient_data"


class TestAnomalies:
    def test_detect_spike(self):
        values = [10, 11, 10, 12, 10, 100, 11, 10]  # 100 is anomaly
        anomalies = ts.detect_anomalies(values)
        assert len(anomalies) >= 1
        assert anomalies[0]["direction"] == "high"

    def test_no_anomalies(self):
        values = [10, 11, 10, 12, 10, 11, 10, 12]
        anomalies = ts.detect_anomalies(values)
        assert len(anomalies) == 0


class TestMovingAverage:
    def test_basic(self):
        values = [1, 2, 3, 4, 5, 6, 7]
        ma = ts.moving_average(values, window=3)
        assert ma[2] == 2.0  # (1+2+3)/3
        assert ma[-1] == 6.0  # (5+6+7)/3


class TestPeriodComparison:
    def test_growth(self):
        result = ts.period_comparison([10, 20, 30], [5, 10, 15])
        assert result["direction"] == "up"
        assert result["change"] == 30.0

    def test_decline(self):
        result = ts.period_comparison([5, 10], [15, 20])
        assert result["direction"] == "down"
