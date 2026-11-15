import unittest

import pandas as pd

from analysis import AnalysisError, calculate_risk_metrics


class CalculateRiskMetricsTests(unittest.TestCase):
    def test_calculates_return_drawdown_and_low_risk(self) -> None:
        history = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0, 103.0]},
            index=pd.date_range("2025-01-01", periods=4),
        )

        metrics = calculate_risk_metrics(
            history,
            symbol=" test ",
            period="1mo",
            risk_tolerance="Low",
        )

        self.assertEqual(metrics.symbol, "TEST")
        self.assertAlmostEqual(metrics.total_return, 0.03)
        self.assertAlmostEqual(metrics.max_drawdown, 0.0)
        self.assertEqual(metrics.risk_level, "Low")

    def test_identifies_high_volatility_and_drawdown(self) -> None:
        history = pd.DataFrame(
            {"Close": [100.0, 50.0, 100.0, 50.0]},
            index=pd.date_range("2025-01-01", periods=4),
        )

        metrics = calculate_risk_metrics(
            history,
            symbol="TEST",
            period="3mo",
            risk_tolerance="Medium",
        )

        self.assertEqual(metrics.risk_level, "High")
        self.assertAlmostEqual(metrics.max_drawdown, -0.5)
        self.assertAlmostEqual(metrics.total_return, -0.5)

    def test_rejects_insufficient_price_history(self) -> None:
        history = pd.DataFrame(
            {"Close": [100.0, 101.0]},
            index=pd.date_range("2025-01-01", periods=2),
        )

        with self.assertRaises(AnalysisError):
            calculate_risk_metrics(
                history,
                symbol="TEST",
                period="1mo",
                risk_tolerance="Low",
            )


if __name__ == "__main__":
    unittest.main()
