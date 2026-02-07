"""
Basic statistics calculator for trade journal analysis.
Calculates win rate, profit factor, expectancy, drawdown, and other key metrics.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass

from ..models.trade import Trade


@dataclass
class BasicStatsResult:
    """Result container for basic statistics."""
    total_trades: int
    closed_trades: int
    win_trades: int
    loss_trades: int
    breakeven_trades: int
    open_trades: int
    
    # Performance metrics
    win_rate: float  # Percentage
    profit_factor: float
    total_net_profit: Decimal
    total_gross_profit: Decimal
    total_gross_loss: Decimal
    avg_win: Decimal
    avg_loss: Decimal
    avg_trade: Decimal
    expectancy: Decimal  # Expected profit per trade
    
    # Risk metrics
    max_drawdown: float  # Percentage
    max_drawdown_amount: Decimal
    max_consecutive_wins: int
    max_consecutive_losses: int
    
    # Additional metrics
    largest_win: Decimal
    largest_loss: Decimal
    profit_per_day: Decimal
    profit_per_trade: Dict[str, Decimal]  # By symbol
    
    # Time-based metrics
    avg_trade_duration: float  # Seconds
    avg_win_duration: float
    avg_loss_duration: float


class BasicStats:
    """
    Calculates basic statistics from a list of trades.
    """
    
    def __init__(self, trades: List[Trade]):
        self.trades = trades
        self._closed_trades = [t for t in trades if t.is_closed]
        self._open_trades = [t for t in trades if not t.is_closed]
        
        # Categorize trades
        self._winning_trades = [t for t in self._closed_trades if t.profit > 0]
        self._losing_trades = [t for t in self._closed_trades if t.profit < 0]
        self._breakeven_trades = [t for t in self._closed_trades if t.profit == 0]
        
        # Calculate once and cache
        self._result = self._calculate_stats()
    
    def _calculate_stats(self) -> BasicStatsResult:
        """Calculate all basic statistics."""
        
        # Basic counts
        total_trades = len(self.trades)
        closed_trades = len(self._closed_trades)
        win_trades = len(self._winning_trades)
        loss_trades = len(self._losing_trades)
        breakeven_trades = len(self._breakeven_trades)
        open_trades = len(self._open_trades)
        
        # Performance calculations
        win_rate = win_trades / closed_trades if closed_trades > 0 else 0.0
        
        total_gross_profit = sum((t.profit for t in self._winning_trades), Decimal("0.0"))
        total_gross_loss = abs(sum((t.profit for t in self._losing_trades), Decimal("0.0")))
        total_net_profit = sum((t.profit for t in self._closed_trades), Decimal("0.0"))
        
        # Profit factor (total profits / total losses)
        profit_factor = float(total_gross_profit / total_gross_loss) if total_gross_loss != 0 else float('inf')
        
        # Average win/loss
        avg_win = total_gross_profit / win_trades if win_trades > 0 else Decimal("0.0")
        avg_loss = total_gross_loss / loss_trades if loss_trades > 0 else Decimal("0.0")
        
        # Expectancy formula: (win% * avg_win) - (loss% * avg_loss)
        win_percentage = Decimal(str(win_rate))
        loss_percentage = Decimal(str(1 - win_rate))
        expectancy = (win_percentage * avg_win) - (loss_percentage * avg_loss)
        avg_trade = total_net_profit / closed_trades if closed_trades > 0 else Decimal("0.0")
        
        # Largest win/loss
        largest_win = max((t.profit for t in self._winning_trades), default=Decimal("0.0"))
        largest_loss = min((t.profit for t in self._losing_trades), default=Decimal("0.0"))
        
        # Calculate max drawdown
        max_drawdown, max_drawdown_amount = self._calculate_drawdown()
        
        # Consecutive wins/losses
        max_consecutive_wins, max_consecutive_losses = self._calculate_consecutive()
        
        # Profit per day
        profit_per_day = self._calculate_profit_per_day()
        
        # Profit by symbol
        profit_per_trade = self._calculate_profit_by_symbol()
        
        # Trade durations
        avg_trade_duration, avg_win_duration, avg_loss_duration = self._calculate_durations()
        
        return BasicStatsResult(
            total_trades=total_trades,
            closed_trades=closed_trades,
            win_trades=win_trades,
            loss_trades=loss_trades,
            breakeven_trades=breakeven_trades,
            open_trades=open_trades,
            
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_net_profit=total_net_profit,
            total_gross_profit=total_gross_profit,
            total_gross_loss=total_gross_loss,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_trade=avg_trade,
            expectancy=expectancy,
            
            max_drawdown=max_drawdown,
            max_drawdown_amount=max_drawdown_amount,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses,
            
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_per_day=profit_per_day,
            profit_per_trade=profit_per_trade,
            
            avg_trade_duration=avg_trade_duration,
            avg_win_duration=avg_win_duration,
            avg_loss_duration=avg_loss_duration
        )
    
    def _calculate_drawdown(self) -> tuple[float, Decimal]:
        """Calculate maximum drawdown as percentage and amount."""
        if not self._closed_trades:
            return 0.0, Decimal("0.0")
        
        # Sort trades by close time
        sorted_trades = sorted(self._closed_trades, key=lambda t: t.close_time)
        
        running_balance = Decimal("0.0")
        peak = Decimal("0.0")
        max_drawdown_amount = Decimal("0.0")
        
        for trade in sorted_trades:
            running_balance += trade.profit
            if running_balance > peak:
                peak = running_balance
            
            drawdown = peak - running_balance
            if drawdown > max_drawdown_amount:
                max_drawdown_amount = drawdown
        
        # Calculate percentage drawdown if we had a peak
        if peak > 0:
            max_drawdown_pct = float((max_drawdown_amount / peak) * Decimal("100.0"))
        else:
            max_drawdown_pct = 0.0
            
        return max_drawdown_pct, max_drawdown_amount
    
    def _calculate_consecutive(self) -> tuple[int, int]:
        """Calculate maximum consecutive wins and losses."""
        if not self._closed_trades:
            return 0, 0
        
        # Sort trades by close time
        sorted_trades = sorted(self._closed_trades, key=lambda t: t.close_time)
        
        current_wins = 0
        current_losses = 0
        max_wins = 0
        max_losses = 0
        
        for trade in sorted_trades:
            if trade.profit > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif trade.profit < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:
                # Breakeven trade resets both streaks
                current_wins = 0
                current_losses = 0
        
        return max_wins, max_losses
    
    def _calculate_profit_per_day(self) -> Decimal:
        """Calculate average profit per trading day."""
        if not self._closed_trades:
            return Decimal("0.0")
        
        # Get unique trading days
        trading_days = set()
        for trade in self._closed_trades:
            if trade.close_time:
                trading_days.add(trade.close_time.date())
        
        days_count = len(trading_days)
        if days_count == 0:
            return Decimal("0.0")
        
        total_profit = sum((t.profit for t in self._closed_trades), Decimal("0.0"))
        return total_profit / Decimal(str(days_count))
    
    def _calculate_profit_by_symbol(self) -> Dict[str, Decimal]:
        """Calculate total profit by symbol."""
        profit_by_symbol = {}
        
        for trade in self._closed_trades:
            symbol = trade.symbol
            if symbol not in profit_by_symbol:
                profit_by_symbol[symbol] = Decimal("0.0")
            profit_by_symbol[symbol] += trade.profit
        
        return profit_by_symbol
    
    def _calculate_durations(self) -> tuple[float, float, float]:
        """Calculate average trade durations."""
        if not self._closed_trades:
            return 0.0, 0.0, 0.0
        
        # All closed trades
        durations = []
        for trade in self._closed_trades:
            if trade.duration is not None:
                durations.append(trade.duration)
        
        # Winning trades
        win_durations = []
        for trade in self._winning_trades:
            if trade.duration is not None:
                win_durations.append(trade.duration)
        
        # Losing trades
        loss_durations = []
        for trade in self._losing_trades:
            if trade.duration is not None:
                loss_durations.append(trade.duration)
        
        avg_trade_duration = statistics.mean(durations) if durations else 0.0
        avg_win_duration = statistics.mean(win_durations) if win_durations else 0.0
        avg_loss_duration = statistics.mean(loss_durations) if loss_durations else 0.0
        
        return avg_trade_duration, avg_win_duration, avg_loss_duration
    
    def get_stats(self) -> BasicStatsResult:
        """Return calculated statistics."""
        return self._result
    
    def summary(self) -> str:
        """Return a human-readable summary of statistics."""
        stats = self._result
        
        summary_lines = [
            "📊 TRADE JOURNAL STATISTICS SUMMARY",
            "=" * 50,
            f"Total Trades: {stats.total_trades} (Closed: {stats.closed_trades}, Open: {stats.open_trades})",
            f"Win/Loss/Breakeven: {stats.win_trades}/{stats.loss_trades}/{stats.breakeven_trades}",
            f"Win Rate: {stats.win_rate:.1%}",
            "",
            f"Total Net Profit: ${stats.total_net_profit:,.2f}",
            f"Total Gross Profit: ${stats.total_gross_profit:,.2f}",
            f"Total Gross Loss: ${stats.total_gross_loss:,.2f}",
            f"Profit Factor: {stats.profit_factor:.2f}",
            "",
            f"Average Win: ${stats.avg_win:,.2f}",
            f"Average Loss: ${stats.avg_loss:,.2f}",
            f"Average Trade: ${stats.avg_trade:,.2f}",
            f"Expectancy: ${stats.expectancy:,.2f}/trade",
            "",
            f"Largest Win: ${stats.largest_win:,.2f}",
            f"Largest Loss: ${stats.largest_loss:,.2f}",
            f"Max Drawdown: {stats.max_drawdown:.1f}% (${stats.max_drawdown_amount:,.2f})",
            "",
            f"Max Consecutive Wins: {stats.max_consecutive_wins}",
            f"Max Consecutive Losses: {stats.max_consecutive_losses}",
            f"Profit per Trading Day: ${stats.profit_per_day:,.2f}",
            "",
            f"Average Trade Duration: {stats.avg_trade_duration / 3600:.1f} hours",
            f"Average Win Duration: {stats.avg_win_duration / 3600:.1f} hours",
            f"Average Loss Duration: {stats.avg_loss_duration / 3600:.1f} hours",
            "",
            "Profit by Symbol:"
        ]
        
        for symbol, profit in stats.profit_per_trade.items():
            summary_lines.append(f"  {symbol}: ${profit:,.2f}")
        
        return "\n".join(summary_lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary format."""
        stats = self._result
        return {
            "total_trades": stats.total_trades,
            "closed_trades": stats.closed_trades,
            "win_trades": stats.win_trades,
            "loss_trades": stats.loss_trades,
            "breakeven_trades": stats.breakeven_trades,
            "open_trades": stats.open_trades,
            
            "win_rate": float(stats.win_rate),
            "profit_factor": stats.profit_factor,
            "total_net_profit": float(stats.total_net_profit),
            "total_gross_profit": float(stats.total_gross_profit),
            "total_gross_loss": float(stats.total_gross_loss),
            "avg_win": float(stats.avg_win),
            "avg_loss": float(stats.avg_loss),
            "avg_trade": float(stats.avg_trade),
            "expectancy": float(stats.expectancy),
            
            "max_drawdown": stats.max_drawdown,
            "max_drawdown_amount": float(stats.max_drawdown_amount),
            "max_consecutive_wins": stats.max_consecutive_wins,
            "max_consecutive_losses": stats.max_consecutive_losses,
            
            "largest_win": float(stats.largest_win),
            "largest_loss": float(stats.largest_loss),
            "profit_per_day": float(stats.profit_per_day),
            "profit_per_trade": {k: float(v) for k, v in stats.profit_per_trade.items()},
            
            "avg_trade_duration": stats.avg_trade_duration,
            "avg_win_duration": stats.avg_win_duration,
            "avg_loss_duration": stats.avg_loss_duration
        }


def create_sample_trades() -> List[Trade]:
    """Create sample trades for testing."""
    from datetime import datetime
    
    trades = []
    
    # Sample winning trades
    trades.append(Trade(
        ticket=1001,
        symbol="EURUSD",
        order_type="BUY",
        volume=0.1,
        open_time=datetime(2024, 1, 10, 10, 0, 0),
        open_price=Decimal("1.0800"),
        close_time=datetime(2024, 1, 10, 15, 0, 0),
        close_price=Decimal("1.0850"),
        profit=Decimal("50.00")
    ))
    
    trades.append(Trade(
        ticket=1002,
        symbol="GBPUSD",
        order_type="SELL",
        volume=0.1,
        open_time=datetime(2024, 1, 11, 11, 0, 0),
        open_price=Decimal("1.2600"),
        close_time=datetime(2024, 1, 11, 16, 0, 0),
        close_price=Decimal("1.2550"),
        profit=Decimal("50.00")
    ))
    
    # Sample losing trade
    trades.append(Trade(
        ticket=1003,
        symbol="USDJPY",
        order_type="BUY",
        volume=0.1,
        open_time=datetime(2024, 1, 12, 9, 0, 0),
        open_price=Decimal("150.00"),
        close_time=datetime(2024, 1, 12, 14, 0, 0),
        close_price=Decimal("149.50"),
        profit=Decimal("-30.00")
    ))
    
    # Sample breakeven trade
    trades.append(Trade(
        ticket=1004,
        symbol="XAUUSD",
        order_type="BUY",
        volume=0.01,
        open_time=datetime(2024, 1, 13, 8, 0, 0),
        open_price=Decimal("1980.00"),
        close_time=datetime(2024, 1, 13, 12, 0, 0),
        close_price=Decimal("1980.00"),
        profit=Decimal("0.00")
    ))
    
    # Sample open trade
    trades.append(Trade(
        ticket=1005,
        symbol="EURUSD",
        order_type="BUY",
        volume=0.1,
        open_time=datetime(2024, 1, 14, 10, 0, 0),
        open_price=Decimal("1.0750"),
        profit=Decimal("25.00")  # Current floating profit
    ))
    
    return trades


if __name__ == "__main__":
    """Example usage."""
    # Create sample trades
    sample_trades = create_sample_trades()
    
    # Calculate statistics
    analyzer = BasicStats(sample_trades)
    stats = analyzer.get_stats()
    
    # Print summary
    print(analyzer.summary())
    
    # Print dictionary format
    print("\n📊 Dictionary format:")
    print(analyzer.to_dict())