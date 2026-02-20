from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Trade:
    """
    Represents a single trade transaction.

    Attributes:
        ticket: Unique identifier (e.g. from MT5)
        symbol: Trading symbol (e.g. 'EURUSD', 'XAUUSD')
        order_type: 'BUY' or 'SELL'
        volume: Trade volume in lots
        open_time: Trade open timestamp
        open_price: Entry price
        close_time: Trade close timestamp (None if open)
        close_price: Exit price (None if open)
        sl: Stop loss price
        tp: Take profit price
        commission: Commission charged
        swap: Swap/rollover fee
        profit: Net profit/loss
        magic: EA magic number (if applicable)
        comment: Trade comment/note
    """
    ticket: int  # Unique identifier (e.g. from MT5)
    symbol: str
    order_type: str  # 'BUY' or 'SELL'
    volume: float
    open_time: datetime
    open_price: Decimal

    # Optional fields (might be open trade)
    close_time: Optional[datetime] = None
    close_price: Optional[Decimal] = None

    sl: Optional[Decimal] = None
    tp: Optional[Decimal] = None

    commission: Decimal = Decimal("0.0")
    swap: Decimal = Decimal("0.0")
    profit: Decimal = Decimal("0.0")

    magic: Optional[int] = None
    comment: Optional[str] = None

    def __repr__(self) -> str:
        """Return a string representation of the trade for debugging."""
        status = "CLOSED" if self.is_closed else "OPEN"
        return (
            f"Trade(ticket={self.ticket}, symbol={self.symbol}, "
            f"type={self.order_type}, {status}, profit={self.profit})"
        )

    def __str__(self) -> str:
        """Return a human-readable summary of the trade."""
        direction = "LONG" if self.is_buy else "SHORT"
        status = "CLOSED" if self.is_closed else "OPEN"
        profit_str = f"${self.profit:.2f}" if self.is_closed else "N/A"
        return f"#{self.ticket} {self.symbol} {direction} {status} PnL: {profit_str}"

    @property
    def direction(self) -> str:
        """Return trade direction as 'LONG' or 'SHORT'."""
        return "LONG" if self.is_buy else "SHORT"

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy (long) trade."""
        return self.order_type.upper() == "BUY"

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell (short) trade."""
        return self.order_type.upper() == "SELL"

    @property
    def duration(self) -> Optional[float]:
        """Returns trade duration in seconds if closed."""
        if self.close_time and self.open_time:
            return (self.close_time - self.open_time).total_seconds()
        return None

    @property
    def duration_hours(self) -> Optional[float]:
        """Returns trade duration in hours if closed."""
        duration = self.duration
        return duration / 3600 if duration is not None else None

    @property
    def is_closed(self) -> bool:
        """Check if the trade is closed."""
        return self.close_time is not None

    @property
    def result(self) -> str:
        """Returns 'WIN', 'LOSS', or 'BREAKEVEN'."""
        if not self.is_closed:
            return "OPEN"
        if self.profit > 0:
            return "WIN"
        elif self.profit < 0:
            return "LOSS"
        else:
            return "BREAKEVEN"

    @property
    def pips(self) -> Optional[float]:
        """
        Calculate price movement in pips.

        For most forex pairs (4 decimal places): 1 pip = 0.0001
        For JPY pairs (2 decimal places): 1 pip = 0.01
        For XAUUSD (gold, 2 decimal places): 1 pip = 0.01 (10 cents)

        Returns:
            Price movement in pips (positive for profitable direction),
            or None if trade is not closed.
        """
        if not self.is_closed or self.close_price is None:
            return None

        price_diff = float(self.close_price - self.open_price)

        # Determine pip size based on symbol
        symbol_upper = self.symbol.upper()
        if "JPY" in symbol_upper:
            # JPY pairs: 2 decimal places, 1 pip = 0.01
            pip_size = 0.01
        elif "XAU" in symbol_upper or "XAG" in symbol_upper:
            # Precious metals: typically 2 decimal places
            pip_size = 0.01
        else:
            # Standard forex: 4 decimal places, 1 pip = 0.0001
            pip_size = 0.0001

        # Adjust for direction: positive pips means price moved in our favor
        if self.is_buy:
            pips = price_diff / pip_size
        else:
            pips = -price_diff / pip_size

        return round(pips, 2)

    @property
    def pips_value(self) -> Optional[Decimal]:
        """
        Calculate profit/loss in pips as a Decimal.

        Similar to `pips` property but returns Decimal for precision.
        Returns None if trade is not closed.
        """
        if not self.is_closed or self.close_price is None:
            return None

        price_diff = self.close_price - self.open_price

        # Determine pip size based on symbol
        symbol_upper = self.symbol.upper()
        if "JPY" in symbol_upper:
            pip_size = Decimal("0.01")
        elif "XAU" in symbol_upper or "XAG" in symbol_upper:
            pip_size = Decimal("0.01")
        else:
            pip_size = Decimal("0.0001")

        if self.is_buy:
            return (price_diff / pip_size).quantize(Decimal("0.01"))
        else:
            return (-price_diff / pip_size).quantize(Decimal("0.01"))
