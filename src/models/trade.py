from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Trade:
    """
    Represents a single trade transaction.
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
    
    @property
    def duration(self) -> Optional[float]:
        """Returns trade duration in seconds if closed."""
        if self.close_time and self.open_time:
            return (self.close_time - self.open_time).total_seconds()
        return None

    @property
    def is_closed(self) -> bool:
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
