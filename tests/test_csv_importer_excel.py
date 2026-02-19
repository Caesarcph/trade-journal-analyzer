from datetime import datetime
from decimal import Decimal
import sys

import pandas as pd

sys.path.insert(0, ".")

from src.importers.csv_importer import CSVImporter


def test_import_trades_uses_read_excel_for_xlsx(monkeypatch):
    called = {"excel": False}

    def fake_read_excel(path):
        called["excel"] = True
        return pd.DataFrame(
            [
                {
                    "ticket": 1,
                    "symbol": "EURUSD",
                    "order_type": "BUY",
                    "volume": 0.1,
                    "open_time": datetime(2025, 1, 1, 9, 0),
                    "open_price": 1.1000,
                    "profit": 12.5,
                }
            ]
        )

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    importer = CSVImporter("sample.xlsx")
    trades = importer.import_trades()

    assert called["excel"] is True
    assert len(trades) == 1
    assert trades[0].symbol == "EURUSD"
    assert trades[0].profit == Decimal("12.5")
