"""
Drawdown analyzer for trade journal analysis.
Calculates detailed drawdown metrics, including equity curves, drawdown periods, and recovery times.
"""

from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

from ..models.trade import Trade


@dataclass
class DrawdownPeriod:
    """Represents a specific period of drawdown."""
    start_date: datetime
    end_date: Optional[datetime]  # None if currently in drawdown
    peak_equity: Decimal
    trough_equity: Decimal
    max_depth: Decimal      # Absolute amount
    max_depth_pct: float    # Percentage from peak
    duration: timedelta     # Duration of drawdown
    recovery_date: Optional[datetime] = None # When equity surpassed peak


@dataclass
class DrawdownResult:
    """Result container for drawdown analysis."""
    current_drawdown: Decimal
    current_drawdown_pct: float
    max_drawdown: Decimal
    max_drawdown_pct: float
    average_drawdown: Decimal
    average_drawdown_pct: float
    drawdown_periods: List[DrawdownPeriod]
    longest_drawdown_duration: timedelta
    average_recovery_time: timedelta
    is_in_drawdown: bool


class DrawdownAnalyzer:
    """
    Analyzes drawdown characteristics from a list of trades.
    """
    
    def __init__(self, trades: List[Trade], initial_balance: Decimal = Decimal("10000.00")):
        """
        Initialize with trades and optional initial balance (default $10,000 for calculation context).
        Initial balance is used for % calculations relative to total account equity.
        """
        self.trades = [t for t in trades if t.is_closed]
        # Sort by close time is crucial for equity curve
        self.trades.sort(key=lambda t: t.close_time)
        self.initial_balance = initial_balance
        self._equity_curve = self._calculate_equity_curve()
        self._drawdown_periods = self._identify_drawdown_periods()
        
    def _calculate_equity_curve(self) -> List[Tuple[datetime, Decimal]]:
        """Calculate equity curve (time, balance) points."""
        curve = []
        current_balance = self.initial_balance
        
        # Start point
        if self.trades:
            start_date = self.trades[0].close_time - timedelta(minutes=1) # Just before first trade
            curve.append((start_date, current_balance))
        
        for trade in self.trades:
            current_balance += trade.profit
            curve.append((trade.close_time, current_balance))
            
        return curve

    def _identify_drawdown_periods(self) -> List[DrawdownPeriod]:
        """Identify all distinct drawdown periods."""
        if not self._equity_curve:
            return []
            
        periods = []
        peak_balance = self.initial_balance
        peak_time = self._equity_curve[0][0]
        
        current_drawdown_start = None
        trough_balance = peak_balance
        
        in_drawdown = False
        
        for time, balance in self._equity_curve:
            if balance > peak_balance:
                # If we were in a drawdown, it has ended (recovered)
                if in_drawdown and current_drawdown_start:
                    periods.append(DrawdownPeriod(
                        start_date=current_drawdown_start,
                        end_date=time,
                        peak_equity=peak_balance,
                        trough_equity=trough_balance,
                        max_depth=peak_balance - trough_balance,
                        max_depth_pct=float((peak_balance - trough_balance) / peak_balance * 100) if peak_balance > 0 else 0.0,
                        duration=time - current_drawdown_start,
                        recovery_date=time
                    ))
                    in_drawdown = False
                
                # New peak
                peak_balance = balance
                peak_time = time
                trough_balance = balance # Reset trough
                
            elif balance < peak_balance:
                # We are in drawdown
                if not in_drawdown:
                    in_drawdown = True
                    current_drawdown_start = peak_time
                    trough_balance = balance
                else:
                    # Check if this is a new trough
                    if balance < trough_balance:
                        trough_balance = balance

        # Handle active drawdown at the end
        if in_drawdown:
             # End date is last trade time (or None to signify ongoing?)
             # Let's use last trade time for duration calculation purposes
             last_time = self._equity_curve[-1][0]
             periods.append(DrawdownPeriod(
                start_date=current_drawdown_start,
                end_date=None, # Ongoing
                peak_equity=peak_balance,
                trough_equity=trough_balance,
                max_depth=peak_balance - trough_balance,
                max_depth_pct=float((peak_balance - trough_balance) / peak_balance * 100) if peak_balance > 0 else 0.0,
                duration=last_time - current_drawdown_start,
                recovery_date=None
            ))
            
        return periods

    def get_analysis(self) -> DrawdownResult:
        """Return comprehensive drawdown analysis."""
        if not self.trades:
            return DrawdownResult(
                Decimal(0), 0.0, Decimal(0), 0.0, Decimal(0), 0.0, [], timedelta(0), timedelta(0), False
            )

        periods = self._drawdown_periods
        
        # Max Drawdown
        if periods:
            max_dd_period = max(periods, key=lambda p: p.max_depth)
            max_dd = max_dd_period.max_depth
            max_dd_pct = max_dd_period.max_depth_pct
            
            avg_dd = statistics.mean([p.max_depth for p in periods])
            avg_dd_pct = statistics.mean([p.max_depth_pct for p in periods])
            
            longest_dd = max(periods, key=lambda p: p.duration).duration
            
            recovered_periods = [p for p in periods if p.recovery_date is not None]
            if recovered_periods:
                avg_recovery = sum((p.duration for p in recovered_periods), timedelta(0)) / len(recovered_periods)
            else:
                avg_recovery = timedelta(0)
        else:
            max_dd = Decimal(0)
            max_dd_pct = 0.0
            avg_dd = Decimal(0)
            avg_dd_pct = 0.0
            longest_dd = timedelta(0)
            avg_recovery = timedelta(0)

        # Current status
        current_balance = self._equity_curve[-1][1]
        peak_balance = max([b for t, b in self._equity_curve]) if self._equity_curve else self.initial_balance
        
        current_dd = peak_balance - current_balance
        current_dd_pct = float(current_dd / peak_balance * 100) if peak_balance > 0 else 0.0
        is_in_dd = current_dd > 0

        return DrawdownResult(
            current_drawdown=current_dd,
            current_drawdown_pct=current_dd_pct,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            average_drawdown=avg_dd,
            average_drawdown_pct=avg_dd_pct,
            drawdown_periods=periods,
            longest_drawdown_duration=longest_dd,
            average_recovery_time=avg_recovery,
            is_in_drawdown=is_in_dd
        )
    
    def summary(self) -> str:
        """Return human-readable summary."""
        res = self.get_analysis()
        
        lines = [
            "📉 DRAWDOWN ANALYSIS",
            "=" * 50,
            f"Current Drawdown: ${res.current_drawdown:,.2f} ({res.current_drawdown_pct:.2f}%)",
            f"Status: {'🔴 In Drawdown' if res.is_in_drawdown else '🟢 At/Near Peak'}",
            "",
            f"Maximum Drawdown: ${res.max_drawdown:,.2f} ({res.max_drawdown_pct:.2f}%)",
            f"Average Drawdown: ${res.average_drawdown:,.2f} ({res.average_drawdown_pct:.2f}%)",
            "",
            f"Longest Drawdown Duration: {res.longest_drawdown_duration}",
            f"Avg Recovery Time: {res.average_recovery_time}",
            f"Total Drawdown Periods: {len(res.drawdown_periods)}"
        ]
        
        if res.drawdown_periods:
            lines.append("\nTop 3 Deepest Drawdowns:")
            sorted_periods = sorted(res.drawdown_periods, key=lambda p: p.max_depth, reverse=True)[:3]
            for i, p in enumerate(sorted_periods, 1):
                rec_str = f"Recovered: {p.recovery_date}" if p.recovery_date else "Ongoing"
                lines.append(f"  {i}. -${p.max_depth:,.2f} ({p.max_depth_pct:.2f}%) | {p.duration} | {rec_str}")
                
        return "\n".join(lines)
