import unittest
from decimal import Decimal
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analyzers.basic_stats import BasicStats
from src.models.trade import Trade


class TestBasicStatsConsecutive(unittest.TestCase):
    def _make_trade(self, ticket: int, close_time: datetime, profit: str) -> Trade:
        open_time = close_time - timedelta(hours=1)
        return Trade(
            ticket=ticket,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=open_time,
            open_price=Decimal("1.0000"),
            close_time=close_time,
            close_price=Decimal("1.0000"),
            profit=Decimal(profit),
        )

    def test_consecutive_wins_losses_and_breakeven_reset(self):
        # Sequence by close_time:
        # W, W, BE, L, L, L, W  -> max wins=2, max losses=3
        t0 = datetime(2024, 1, 1, 10, 0, 0)
        trades = [
            self._make_trade(1, t0 + timedelta(minutes=1), "10"),
            self._make_trade(2, t0 + timedelta(minutes=2), "5"),
            self._make_trade(3, t0 + timedelta(minutes=3), "0"),
            self._make_trade(4, t0 + timedelta(minutes=4), "-1"),
            self._make_trade(5, t0 + timedelta(minutes=5), "-2"),
            self._make_trade(6, t0 + timedelta(minutes=6), "-3"),
            self._make_trade(7, t0 + timedelta(minutes=7), "4"),
        ]

        stats = BasicStats(trades).get_stats()
        self.assertEqual(stats.max_consecutive_wins, 2)
        self.assertEqual(stats.max_consecutive_losses, 3)

    def test_consecutive_counts_empty(self):
        stats = BasicStats([]).get_stats()
        self.assertEqual(stats.max_consecutive_wins, 0)
        self.assertEqual(stats.max_consecutive_losses, 0)


if __name__ == "__main__":
    unittest.main()
