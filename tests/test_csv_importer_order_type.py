from datetime import datetime
import sys

import pandas as pd

sys.path.insert(0, ".")

from src.importers.csv_importer import CSVImporter


def test_import_trades_normalizes_numeric_and_text_order_types(monkeypatch):
    def fake_read_csv(path):
        return pd.DataFrame(
            [
                {
                    "ticket": 1,
                    "symbol": "EURUSD",
                    "order_type": 0,
                    "volume": 0.1,
                    "open_time": datetime(2025, 1, 1, 9, 0),
                    "open_price": 1.1000,
                },
                {
                    "ticket": 2,
                    "symbol": "GBPUSD",
                    "order_type": "short",
                    "volume": 0.1,
                    "open_time": datetime(2025, 1, 1, 10, 0),
                    "open_price": 1.2500,
                },
            ]
        )

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    importer = CSVImporter("sample.csv")
    trades = importer.import_trades()

    assert len(trades) == 2
    assert trades[0].order_type == "BUY"
    assert trades[1].order_type == "SELL"
