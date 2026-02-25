"""
SQLite database storage for trade journal analyzer.

This module provides persistent storage for trade data using SQLite.
It handles serialization/deserialization of Trade objects to/from the database.

Features:
    - Automatic schema creation
    - Trade CRUD operations (Create, Read)
    - Type conversion between Decimal/datetime and SQLite types

Example:
    >>> from storage.database import TradeDatabase
    >>> from models.trade import Trade
    >>> db = TradeDatabase("my_trades.db")
    >>> db.save_trade(my_trade)
    >>> trades = db.get_trades()
"""

import sqlite3
from typing import List
from decimal import Decimal
from datetime import datetime
from src.models.trade import Trade


class TradeDatabase:
    """
    SQLite database interface for storing and retrieving trades.

    Manages a local SQLite database for persistent trade storage.
    Handles automatic schema creation and type conversions.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: str = "trades.db"):
        """
        Initialize the database connection and create schema if needed.

        Args:
            db_path: Path to the SQLite database file. Defaults to 'trades.db'.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                ticket INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                volume REAL NOT NULL,
                open_time TIMESTAMP NOT NULL,
                open_price REAL NOT NULL,
                close_time TIMESTAMP,
                close_price REAL,
                sl REAL,
                tp REAL,
                commission REAL,
                swap REAL,
                profit REAL,
                magic INTEGER,
                comment TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_trade(self, trade: Trade):
        """Save a trade to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO trades (
                    ticket, symbol, order_type, volume, open_time, open_price,
                    close_time, close_price, sl, tp, commission, swap, profit, magic, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.ticket,
                trade.symbol,
                trade.order_type,
                trade.volume,
                trade.open_time,
                float(trade.open_price),
                trade.close_time,
                float(trade.close_price) if trade.close_price is not None else None,
                float(trade.sl) if trade.sl is not None else None,
                float(trade.tp) if trade.tp is not None else None,
                float(trade.commission),
                float(trade.swap),
                float(trade.profit),
                trade.magic,
                trade.comment
            ))
            conn.commit()
        finally:
            conn.close()

    def get_trades(self) -> List[Trade]:
        """Retrieve all trades."""
        # Detect types to handle TIMESTAMP -> datetime automatic conversion
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM trades')
            rows = cursor.fetchall()
            trades = []
            for row in rows:
                (ticket, symbol, order_type, volume, open_time, open_price,
                 close_time, close_price, sl, tp, commission, swap, profit, magic, comment) = row

                # Fallback if automatic detection fails (sometimes depends on connection flags/formats)
                if isinstance(open_time, str):
                    try:
                        open_time = datetime.fromisoformat(open_time)
                    except ValueError:
                        # Fallback for formats without T or space separation quirks
                        pass 
                if isinstance(close_time, str) and close_time:
                    try:
                        close_time = datetime.fromisoformat(close_time)
                    except ValueError:
                        pass

                t = Trade(
                    ticket=ticket,
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    open_time=open_time,
                    open_price=Decimal(str(open_price)),
                    close_time=close_time,
                    close_price=Decimal(str(close_price)) if close_price is not None else None,
                    sl=Decimal(str(sl)) if sl is not None else None,
                    tp=Decimal(str(tp)) if tp is not None else None,
                    commission=Decimal(str(commission)),
                    swap=Decimal(str(swap)),
                    profit=Decimal(str(profit)),
                    magic=magic,
                    comment=comment
                )
                trades.append(t)
            return trades
        finally:
            conn.close()
