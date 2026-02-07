import unittest
from decimal import Decimal
from datetime import datetime
import sys
from pathlib import Path

# Ensure src is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analyzers.time_analysis import TimeAnalysis, create_sample_trades


class TestTimeAnalysisOverlaps(unittest.TestCase):
    def test_london_ny_overlap_detected(self):
        trades = create_sample_trades()
        ta = TimeAnalysis(trades)

        overlaps = ta.get_session_overlaps()
        self.assertTrue(overlaps, "Expected at least one session overlap")

        # London/New_York overlap should exist for sample trades (13:00-16:00 UTC)
        names = {o["overlap_name"] for o in overlaps}
        self.assertIn("London/New_York Overlap", names)

        best = ta.get_best_session_overlap()
        self.assertIsNotNone(best)
        self.assertGreaterEqual(best["total_trades"], 1)

    def test_sessions_include_overlap_bucket(self):
        trades = create_sample_trades()
        ta = TimeAnalysis(trades)
        session_stats = ta.by_session()

        # Sample data includes multiple trades around 14:00 UTC -> should land in overlap bucket
        self.assertIn("London_NY_Overlap", session_stats)
        self.assertGreater(session_stats["London_NY_Overlap"]["total_trades"], 0)


if __name__ == "__main__":
    unittest.main()
