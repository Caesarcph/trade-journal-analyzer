"""
CSV importer for trade journal analyzer.

This module provides functionality to import trading data from CSV files
with automatic column mapping and flexible data parsing.

Features:
    - Auto-detection of common column name variations
    - Support for multiple broker CSV formats
    - Graceful handling of missing or malformed data
    - Conversion to standardized Trade objects

Example:
    >>> from importers import CSVImporter
    >>> importer = CSVImporter("trades.csv")
    >>> trades = importer.import_trades()
    
    >>> # With custom column mapping
    >>> mapping = {"order_type": "Side", "profit": "PnL"}
    >>> importer = CSVImporter("trades.csv", column_mapping=mapping)
    >>> trades = importer.import_trades()
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
import logging
try:
    # Prefer absolute import when running from repo root (tests/dev).
    from src.models.trade import Trade  # type: ignore
except Exception:  # pragma: no cover
    # Fallback for legacy usage where `src` is on PYTHONPATH.
    from models.trade import Trade  # type: ignore

logger = logging.getLogger(__name__)


def _norm_col(name: str) -> str:
    """Normalize a column name for best-effort matching (no extra deps)."""
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace("/", "")
        .replace(".", "")
    )


def _auto_column_mapping(columns: List[str]) -> Dict[str, str]:
    """Infer a Trade-field -> CSV-header mapping from column names."""
    aliases: Dict[str, List[str]] = {
        "order_type": ["type", "side", "direction"],
        "open_time": ["opentime", "entrytime", "entrydate", "dateopen"],
        "open_price": ["openprice", "entryprice", "priceopen"],
        "close_time": ["closetime", "exittime", "exitdate", "dateclose"],
        "close_price": ["closeprice", "exitprice", "priceclose"],
        "volume": ["lots", "size", "qty", "quantity"],
        "profit": ["pnl", "pl", "netprofit"],
        "comment": ["notes", "note", "remark"],
    }

    norm_to_original = {_norm_col(c): c for c in columns}
    mapping: Dict[str, str] = {}

    # Try direct match first, then aliases.
    for key in [
        "ticket",
        "symbol",
        "order_type",
        "volume",
        "open_time",
        "open_price",
        "close_time",
        "close_price",
        "sl",
        "tp",
        "commission",
        "swap",
        "profit",
        "magic",
        "comment",
    ]:
        direct = norm_to_original.get(_norm_col(key))
        if direct:
            mapping[key] = direct
            continue
        for a in aliases.get(key, []):
            hit = norm_to_original.get(_norm_col(a))
            if hit:
                mapping[key] = hit
                break

    return mapping

def _normalize_order_type(raw_value: object) -> str:
    """Normalize broker-specific order type values to BUY/SELL.

    Falls back to BUY to preserve backward compatibility.
    """
    if raw_value is None:
        return "BUY"

    value = str(raw_value).strip().upper()
    if value in {"BUY", "B", "LONG", "0", "OP_BUY"}:
        return "BUY"
    if value in {"SELL", "S", "SHORT", "1", "OP_SELL"}:
        return "SELL"
    return "BUY"

class CSVImporter:
    """
    Imports trades from CSV files.
    """
    
    def __init__(self, filepath: str, column_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize CSVImporter.

        Args:
            filepath: Path to the CSV file.
            column_mapping: Dict mapping Trade attribute names to CSV column names.
                            Defaults to assuming CSV headers match attribute names.
        """
        self.filepath = filepath
        self.column_mapping = column_mapping or {}

    def import_trades(self) -> List[Trade]:
        """
        Read a CSV/Excel file and convert rows to Trade objects.

        Notes:
            - ``.csv`` files are read with ``pandas.read_csv``.
            - ``.xls``/``.xlsx`` files are read with ``pandas.read_excel``.
            - Any other extension falls back to ``read_csv`` for backward compatibility.
        """
        try:
            lower_path = self.filepath.lower()
            if lower_path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(self.filepath)
            else:
                df = pd.read_csv(self.filepath)
        except FileNotFoundError:
            logger.error(f"File not found: {self.filepath}")
            return []
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return []

        # If no explicit mapping is provided, try to infer one from headers.
        if not self.column_mapping:
            self.column_mapping = _auto_column_mapping(list(df.columns))

        trades = []

        for index, row in df.iterrows():
            try:
                trade_data = {}
                
                # Helper to get value using mapping or default key
                def get_val(key):
                    col_name = self.column_mapping.get(key, key) # Default to key itself
                    if col_name in row and not pd.isna(row[col_name]):
                        return row[col_name]
                    return None

                # Required fields
                ticket_val = get_val('ticket')
                if ticket_val is None:
                    # Use a pseudo-ticket for rows without broker ticket id.
                    ticket_val = index + 1
                
                symbol = get_val('symbol')
                if not symbol:
                    continue # Skip invalid rows

                open_time_val = get_val('open_time')
                if open_time_val:
                    open_time = pd.to_datetime(open_time_val).to_pydatetime()
                else:
                    continue # Open time required

                # Construct Trade object
                trade = Trade(
                    ticket=int(ticket_val),
                    symbol=str(symbol),
                    order_type=_normalize_order_type(get_val('order_type')),
                    volume=float(get_val('volume') or 0.0),
                    open_time=open_time,
                    open_price=Decimal(str(get_val('open_price') or 0.0)),
                    
                    close_time=pd.to_datetime(get_val('close_time')).to_pydatetime() if get_val('close_time') else None,
                    close_price=Decimal(str(get_val('close_price'))) if get_val('close_price') else None,
                    sl=Decimal(str(get_val('sl'))) if get_val('sl') else None,
                    tp=Decimal(str(get_val('tp'))) if get_val('tp') else None,
                    commission=Decimal(str(get_val('commission') or 0.0)),
                    swap=Decimal(str(get_val('swap') or 0.0)),
                    profit=Decimal(str(get_val('profit') or 0.0)),
                    magic=int(get_val('magic')) if get_val('magic') else None,
                    comment=str(get_val('comment')) if get_val('comment') else None
                )
                trades.append(trade)
                
            except Exception as e:
                logger.warning(f"Failed to parse row {index}: {e}")
                continue

        return trades
