"""
Time-based analysis for trade journal analyzer.
Analyzes trading patterns by time of day, day of week, month, and session.
"""

from typing import List, Dict, Any, Tuple, Optional
from decimal import Decimal
from datetime import datetime, time, date
from dataclasses import dataclass
import statistics
from collections import defaultdict

from ..models.trade import Trade


@dataclass
class TimePatternResult:
    """Results from time-based pattern analysis."""
    
    # Performance by hour of day (24-hour format)
    by_hour: Dict[int, Dict[str, Any]]
    
    # Performance by day of week (0=Monday, 6=Sunday)
    by_weekday: Dict[int, Dict[str, Any]]
    
    # Performance by month (1-12)
    by_month: Dict[int, Dict[str, Any]]
    
    # Performance by trading session
    by_session: Dict[str, Dict[str, Any]]
    
    # Performance by time period
    by_period: Dict[str, Dict[str, Any]]
    
    # Peak performance hours
    peak_hours: List[Dict[str, Any]]
    
    # Worst performance hours
    worst_hours: List[Dict[str, Any]]
    
    # Best/worst weekdays
    best_weekday: Dict[str, Any]
    worst_weekday: Dict[str, Any]
    
    # Best/worst months
    best_month: Dict[str, Any]
    worst_month: Dict[str, Any]
    
    # Trading session definitions (local times)
    sessions: Dict[str, Tuple[time, time]]


class TimeAnalysis:
    """
    Analyzes trading patterns based on time factors.
    """
    
    # Define trading sessions (times are in UTC)
    SESSIONS = {
        "Asian": (time(0, 0), time(8, 0)),      # 00:00-08:00 UTC
        "London": (time(8, 0), time(16, 0)),   # 08:00-16:00 UTC
        "New_York": (time(13, 0), time(21, 0)), # 13:00-21:00 UTC
        "London_NY_Overlap": (time(13, 0), time(16, 0)),  # 13:00-16:00 UTC
    }
    
    # Time periods for analysis
    PERIODS = {
        "pre_market": (time(0, 0), time(8, 0)),     # Early morning
        "market_open": (time(8, 0), time(12, 0)),   # Morning session
        "midday": (time(12, 0), time(16, 0)),       # Early afternoon
        "afternoon": (time(16, 0), time(20, 0)),    # Late afternoon
        "evening": (time(20, 0), time(23, 59)),     # Evening session
    }
    
    def __init__(self, trades: List[Trade]):
        self.trades = trades
        self._closed_trades = [t for t in trades if t.is_closed]
        self._result = None
        
        # Initialize data structures
        self._hour_stats = defaultdict(lambda: {"trades": [], "pnl": Decimal("0.0"), "wins": 0, "losses": 0})
        self._weekday_stats = defaultdict(lambda: {"trades": [], "pnl": Decimal("0.0"), "wins": 0, "losses": 0})
        self._month_stats = defaultdict(lambda: {"trades": [], "pnl": Decimal("0.0"), "wins": 0, "losses": 0})
        self._session_stats = defaultdict(lambda: {"trades": [], "pnl": Decimal("0.0"), "wins": 0, "losses": 0})
        self._period_stats = defaultdict(lambda: {"trades": [], "pnl": Decimal("0.0"), "wins": 0, "losses": 0})
        
        self._analyze_all()
    
    def _analyze_all(self):
        """Perform all time-based analyses."""
        if not self._closed_trades:
            return
        
        # Analyze each trade
        for trade in self._closed_trades:
            self._analyze_trade(trade)
        
        # Calculate derived statistics
        self._calculate_derived_stats()
        
        # Find best/worst performers
        self._find_extremes()
    
    def _analyze_trade(self, trade: Trade):
        """Analyze a single trade across all time dimensions."""
        if not trade.close_time:
            return
        
        close_time = trade.close_time
        hour = close_time.hour
        weekday = close_time.weekday()  # 0=Monday, 6=Sunday
        month = close_time.month
        
        # Track hour performance
        self._hour_stats[hour]["trades"].append(trade)
        self._hour_stats[hour]["pnl"] += trade.profit
        if trade.profit > 0:
            self._hour_stats[hour]["wins"] += 1
        elif trade.profit < 0:
            self._hour_stats[hour]["losses"] += 1
        
        # Track weekday performance
        self._weekday_stats[weekday]["trades"].append(trade)
        self._weekday_stats[weekday]["pnl"] += trade.profit
        if trade.profit > 0:
            self._weekday_stats[weekday]["wins"] += 1
        elif trade.profit < 0:
            self._weekday_stats[weekday]["losses"] += 1
        
        # Track month performance
        self._month_stats[month]["trades"].append(trade)
        self._month_stats[month]["pnl"] += trade.profit
        if trade.profit > 0:
            self._month_stats[month]["wins"] += 1
        elif trade.profit < 0:
            self._month_stats[month]["losses"] += 1
        
        # Determine session
        session = self._get_session(close_time)
        if session:
            self._session_stats[session]["trades"].append(trade)
            self._session_stats[session]["pnl"] += trade.profit
            if trade.profit > 0:
                self._session_stats[session]["wins"] += 1
            elif trade.profit < 0:
                self._session_stats[session]["losses"] += 1
        
        # Determine time period
        period = self._get_period(close_time)
        if period:
            self._period_stats[period]["trades"].append(trade)
            self._period_stats[period]["pnl"] += trade.profit
            if trade.profit > 0:
                self._period_stats[period]["wins"] += 1
            elif trade.profit < 0:
                self._period_stats[period]["losses"] += 1
    
    def _get_session(self, close_time: datetime) -> Optional[str]:
        """Determine which trading session the time falls into."""
        close_hour = close_time.time()
        
        for session_name, (start_time, end_time) in self.SESSIONS.items():
            if start_time <= close_hour < end_time:
                return session_name
        
        return None
    
    def _get_period(self, close_time: datetime) -> Optional[str]:
        """Determine which time period the time falls into."""
        close_hour = close_time.time()
        
        for period_name, (start_time, end_time) in self.PERIODS.items():
            if start_time <= close_hour < end_time:
                return period_name
        
        return None
    
    def _calculate_derived_stats(self):
        """Calculate win rates and other derived statistics."""
        # Process hour stats
        for hour, stats in self._hour_stats.items():
            total_trades = len(stats["trades"])
            if total_trades > 0:
                stats["total_trades"] = total_trades
                stats["win_rate"] = stats["wins"] / total_trades if total_trades > 0 else 0.0
                stats["loss_rate"] = stats["losses"] / total_trades if total_trades > 0 else 0.0
                stats["avg_pnl"] = stats["pnl"] / Decimal(str(total_trades))
                stats["avg_trade"] = stats["avg_pnl"]  # For backward compatibility
        
        # Process weekday stats
        for weekday, stats in self._weekday_stats.items():
            total_trades = len(stats["trades"])
            if total_trades > 0:
                stats["total_trades"] = total_trades
                stats["win_rate"] = stats["wins"] / total_trades if total_trades > 0 else 0.0
                stats["loss_rate"] = stats["losses"] / total_trades if total_trades > 0 else 0.0
                stats["avg_pnl"] = stats["pnl"] / Decimal(str(total_trades))
        
        # Process month stats
        for month, stats in self._month_stats.items():
            total_trades = len(stats["trades"])
            if total_trades > 0:
                stats["total_trades"] = total_trades
                stats["win_rate"] = stats["wins"] / total_trades if total_trades > 0 else 0.0
                stats["loss_rate"] = stats["losses"] / total_trades if total_trades > 0 else 0.0
                stats["avg_pnl"] = stats["pnl"] / Decimal(str(total_trades))
        
        # Process session stats
        for session, stats in self._session_stats.items():
            total_trades = len(stats["trades"])
            if total_trades > 0:
                stats["total_trades"] = total_trades
                stats["win_rate"] = stats["wins"] / total_trades if total_trades > 0 else 0.0
                stats["loss_rate"] = stats["losses"] / total_trades if total_trades > 0 else 0.0
                stats["avg_pnl"] = stats["pnl"] / Decimal(str(total_trades))
        
        # Process period stats
        for period, stats in self._period_stats.items():
            total_trades = len(stats["trades"])
            if total_trades > 0:
                stats["total_trades"] = total_trades
                stats["win_rate"] = stats["wins"] / total_trades if total_trades > 0 else 0.0
                stats["loss_rate"] = stats["losses"] / total_trades if total_trades > 0 else 0.0
                stats["avg_pnl"] = stats["pnl"] / Decimal(str(total_trades))
    
    def _find_extremes(self):
        """Find best and worst performing time periods."""
        # Find peak hours (based on win rate and PnL)
        self._peak_hours = []
        for hour, stats in self._hour_stats.items():
            if "win_rate" in stats and stats["total_trades"] >= 3:  # Minimum trades for significance
                self._peak_hours.append({
                    "hour": hour,
                    "win_rate": stats["win_rate"],
                    "avg_pnl": float(stats["avg_pnl"]),
                    "total_trades": stats["total_trades"],
                    "total_pnl": float(stats["pnl"])
                })
        
        # Sort by win rate descending
        self._peak_hours.sort(key=lambda x: (x["win_rate"], x["avg_pnl"]), reverse=True)
        
        # Find worst hours
        self._worst_hours = sorted(
            [h for h in self._peak_hours if h["avg_pnl"] < 0],
            key=lambda x: (x["win_rate"], x["avg_pnl"])
        )
        
        # Find best/worst weekdays
        weekday_perf = []
        for weekday, stats in self._weekday_stats.items():
            if "win_rate" in stats and stats["total_trades"] >= 5:  # Minimum trades
                weekday_perf.append({
                    "weekday": weekday,
                    "name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday],
                    "win_rate": stats["win_rate"],
                    "avg_pnl": float(stats["avg_pnl"]),
                    "total_trades": stats["total_trades"],
                    "total_pnl": float(stats["pnl"])
                })
        
        if weekday_perf:
            self._best_weekday = max(weekday_perf, key=lambda x: (x["win_rate"], x["avg_pnl"]))
            self._worst_weekday = min(weekday_perf, key=lambda x: (x["win_rate"], x["avg_pnl"]))
        else:
            self._best_weekday = {}
            self._worst_weekday = {}
        
        # Find best/worst months
        month_perf = []
        for month, stats in self._month_stats.items():
            if "win_rate" in stats and stats["total_trades"] >= 5:  # Minimum trades
                month_perf.append({
                    "month": month,
                    "name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month-1],
                    "win_rate": stats["win_rate"],
                    "avg_pnl": float(stats["avg_pnl"]),
                    "total_trades": stats["total_trades"],
                    "total_pnl": float(stats["pnl"])
                })
        
        if month_perf:
            self._best_month = max(month_perf, key=lambda x: (x["win_rate"], x["avg_pnl"]))
            self._worst_month = min(month_perf, key=lambda x: (x["win_rate"], x["avg_pnl"]))
        else:
            self._best_month = {}
            self._worst_month = {}
    
    def by_hour(self) -> Dict[int, Dict[str, Any]]:
        """Get performance by hour of day."""
        return {
            hour: {
                "total_trades": stats.get("total_trades", 0),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "loss_rate": stats.get("loss_rate", 0.0),
                "total_pnl": float(stats.get("pnl", Decimal("0.0"))),
                "avg_pnl": float(stats.get("avg_pnl", Decimal("0.0")))
            }
            for hour, stats in self._hour_stats.items()
        }
    
    def by_day_of_week(self) -> Dict[int, Dict[str, Any]]:
        """Get performance by day of week."""
        return {
            weekday: {
                "name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday],
                "total_trades": stats.get("total_trades", 0),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "loss_rate": stats.get("loss_rate", 0.0),
                "total_pnl": float(stats.get("pnl", Decimal("0.0"))),
                "avg_pnl": float(stats.get("avg_pnl", Decimal("0.0")))
            }
            for weekday, stats in self._weekday_stats.items()
        }
    
    def by_month(self) -> Dict[int, Dict[str, Any]]:
        """Get performance by month."""
        return {
            month: {
                "name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month-1],
                "total_trades": stats.get("total_trades", 0),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "loss_rate": stats.get("loss_rate", 0.0),
                "total_pnl": float(stats.get("pnl", Decimal("0.0"))),
                "avg_pnl": float(stats.get("avg_pnl", Decimal("0.0")))
            }
            for month, stats in self._month_stats.items()
        }
    
    def by_session(self) -> Dict[str, Dict[str, Any]]:
        """Get performance by trading session."""
        return {
            session: {
                "total_trades": stats.get("total_trades", 0),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "loss_rate": stats.get("loss_rate", 0.0),
                "total_pnl": float(stats.get("pnl", Decimal("0.0"))),
                "avg_pnl": float(stats.get("avg_pnl", Decimal("0.0")))
            }
            for session, stats in self._session_stats.items()
        }
    
    def by_period(self) -> Dict[str, Dict[str, Any]]:
        """Get performance by time period."""
        return {
            period: {
                "total_trades": stats.get("total_trades", 0),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "win_rate": stats.get("win_rate", 0.0),
                "loss_rate": stats.get("loss_rate", 0.0),
                "total_pnl": float(stats.get("pnl", Decimal("0.0"))),
                "avg_pnl": float(stats.get("avg_pnl", Decimal("0.0")))
            }
            for period, stats in self._period_stats.items()
        }
    
    def get_peak_hours(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N performing hours."""
        return self._peak_hours[:limit]
    
    def get_worst_hours(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get worst N performing hours."""
        return self._worst_hours[:limit]
    
    def get_best_weekday(self) -> Dict[str, Any]:
        """Get best performing day of week."""
        return self._best_weekday
    
    def get_worst_weekday(self) -> Dict[str, Any]:
        """Get worst performing day of week."""
        return self._worst_weekday
    
    def get_best_month(self) -> Dict[str, Any]:
        """Get best performing month."""
        return self._best_month
    
    def get_worst_month(self) -> Dict[str, Any]:
        """Get worst performing month."""
        return self._worst_month
    
    def get_all_stats(self) -> TimePatternResult:
        """Return complete time-based analysis results."""
        return TimePatternResult(
            by_hour=self.by_hour(),
            by_weekday=self.by_day_of_week(),
            by_month=self.by_month(),
            by_session=self.by_session(),
            by_period=self.by_period(),
            peak_hours=self.get_peak_hours(5),
            worst_hours=self.get_worst_hours(5),
            best_weekday=self.get_best_weekday(),
            worst_weekday=self.get_worst_weekday(),
            best_month=self.get_best_month(),
            worst_month=self.get_worst_month(),
            sessions=self.SESSIONS
        )
    
    def summary(self) -> str:
        """Return human-readable summary of time-based analysis."""
        if not self._closed_trades:
            return "No closed trades available for time-based analysis."
        
        lines = [
            "⏰ TIME-BASED PATTERN ANALYSIS",
            "=" * 50,
            f"Total Closed Trades Analyzed: {len(self._closed_trades)}",
            ""
        ]
        
        # Best performing hours
        peak_hours = self.get_peak_hours(3)
        if peak_hours:
            lines.append("🏆 BEST PERFORMING HOURS:")
            for hour_data in peak_hours:
                hour = hour_data["hour"]
                win_rate = hour_data["win_rate"]
                avg_pnl = hour_data["avg_pnl"]
                lines.append(f"  {hour:02d}:00 - Win Rate: {win_rate:.1%} | Avg PnL: ${avg_pnl:.2f}")
            lines.append("")
        
        # Worst performing hours
        worst_hours = self.get_worst_hours(3)
        if worst_hours:
            lines.append("⚠️ WORST PERFORMING HOURS:")
            for hour_data in worst_hours:
                hour = hour_data["hour"]
                win_rate = hour_data["win_rate"]
                avg_pnl = hour_data["avg_pnl"]
                lines.append(f"  {hour:02d}:00 - Win Rate: {win_rate:.1%} | Avg PnL: ${avg_pnl:.2f}")
            lines.append("")
        
        # Best/Worst weekday
        best_weekday = self.get_best_weekday()
        worst_weekday = self.get_worst_weekday()
        if best_weekday and worst_weekday:
            lines.append("📅 DAY OF WEEK PERFORMANCE:")
            lines.append(f"  Best: {best_weekday['name']} - Win Rate: {best_weekday['win_rate']:.1%} | Avg PnL: ${best_weekday['avg_pnl']:.2f}")
            lines.append(f"  Worst: {worst_weekday['name']} - Win Rate: {worst_weekday['win_rate']:.1%} | Avg PnL: ${worst_weekday['avg_pnl']:.2f}")
            lines.append("")
        
        # Trading sessions
        session_stats = self.by_session()
        if session_stats:
            lines.append("🌍 TRADING SESSIONS:")
            for session, stats in session_stats.items():
                if stats["total_trades"] > 0:
                    win_rate = stats["win_rate"]
                    avg_pnl = stats["avg_pnl"]
                    lines.append(f"  {session}: {stats['total_trades']} trades, Win Rate: {win_rate:.1%}, Avg PnL: ${avg_pnl:.2f}")
            lines.append("")
        
        # Time periods
        period_stats = self.by_period()
        if period_stats:
            lines.append("⏳ TIME PERIODS:")
            for period, stats in period_stats.items():
                if stats["total_trades"] > 0:
                    win_rate = stats["win_rate"]
                    avg_pnl = stats["avg_pnl"]
                    lines.append(f"  {period}: {stats['total_trades']} trades, Win Rate: {win_rate:.1%}, Avg PnL: ${avg_pnl:.2f}")
        
        return "\n".join(lines)
    
    def recommendations(self) -> List[str]:
        """Generate trading recommendations based on time patterns."""
        recs = []
        
        if not self._closed_trades:
            return ["No recommendations - insufficient trade data."]
        
        # Analyze peak hours
        peak_hours = self.get_peak_hours(2)
        if peak_hours and len(peak_hours) >= 2:
            best_hour = peak_hours[0]
            if best_hour["win_rate"] >= 0.6 and best_hour["total_trades"] >= 5:
                recs.append(f"Focus on trading during {best_hour['hour']:02d}:00 - {best_hour['win_rate']:.1%} win rate across {best_hour['total_trades']} trades.")
        
        # Analyze worst hours
        worst_hours = self.get_worst_hours(2)
        if worst_hours and len(worst_hours) >= 1:
            worst_hour = worst_hours[0]
            if worst_hour["win_rate"] <= 0.4 and worst_hour["total_trades"] >= 5:
                recs.append(f"Avoid trading during {worst_hour['hour']:02d}:00 - only {worst_hour['win_rate']:.1%} win rate.")
        
        # Analyze weekdays
        best_weekday = self.get_best_weekday()
        worst_weekday = self.get_worst_weekday()
        if best_weekday and worst_weekday:
            if best_weekday.get("win_rate", 0) >= 0.55:
                recs.append(f"{best_weekday['name']} is your strongest day - schedule important trades then.")
            if worst_weekday.get("win_rate", 0) <= 0.45:
                recs.append(f"Consider reducing trading activity on {worst_weekday['name']}.")
        
        # Analyze sessions
        session_stats = self.by_session()
        best_session = None
        best_win_rate = 0.0
        
        for session, stats in session_stats.items():
            if stats["total_trades"] >= 5 and stats["win_rate"] > best_win_rate:
                best_win_rate = stats["win_rate"]
                best_session = session
        
        if best_session and best_win_rate >= 0.6:
            recs.append(f"{best_session} session shows strong performance ({best_win_rate:.1%} win rate) - focus your trading there.")
        
        return recs if recs else ["Continue current trading schedule - no strong patterns detected."]


def create_sample_trades() -> List[Trade]:
    """Create sample trades for testing time analysis."""
    from datetime import datetime
    
    trades = []
    
    # Create trades at different times for pattern analysis
    times = [
        (datetime(2024, 1, 10, 9, 0, 0), datetime(2024, 1, 10, 10, 0, 0)),  # Early morning
        (datetime(2024, 1, 10, 10, 0, 0), datetime(2024, 1, 10, 14, 0, 0)),   # Morning
        (datetime(2024, 1, 10, 14, 0, 0), datetime(2024, 1, 10, 18, 0, 0)),   # Afternoon
        (datetime(2024, 1, 10, 20, 0, 0), datetime(2024, 1, 10, 22, 0, 0)),   # Evening
        
        # Different weekdays
        (datetime(2024, 1, 11, 10, 0, 0), datetime(2024, 1, 11, 14, 0, 0)),   # Tuesday
        (datetime(2024, 1, 12, 10, 0, 0), datetime(2024, 1, 12, 14, 0, 0)),   # Wednesday
        (datetime(2024, 1, 13, 10, 0, 0), datetime(2024, 1, 13, 14, 0, 0)),   # Thursday
        (datetime(2024, 1, 14, 10, 0, 0), datetime(2024, 1, 14, 14, 0, 0)),   # Friday
        
        # Different months
        (datetime(2024, 2, 10, 10, 0, 0), datetime(2024, 2, 10, 14, 0, 0)),   # February
        (datetime(2024, 3, 10, 10, 0, 0), datetime(2024, 3, 10, 14, 0, 0)),   # March
    ]
    
    # Generate trades with varied performance
    for i, (open_time, close_time) in enumerate(times):
        profit = Decimal("50.00") if i % 3 != 0 else Decimal("-30.00")  # Some losses
        
        trades.append(Trade(
            ticket=2000 + i,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=open_time,
            open_price=Decimal("1.0800"),
            close_time=close_time,
            close_price=Decimal("1.0850"),
            profit=profit
        ))
    
    return trades


if __name__ == "__main__":
    """Example usage and testing."""
    print("🧪 Testing TimeAnalysis Module")
    print("=" * 60)
    
    # Create sample trades
    sample_trades = create_sample_trades()
    print(f"Created {len(sample_trades)} sample trades")
    
    # Create analyzer
    analyzer = TimeAnalysis(sample_trades)
    
    # Print summary
    print("\n" + analyzer.summary())
    
    # Print recommendations
    print("\n📋 RECOMMENDATIONS:")
    for rec in analyzer.recommendations():
        print(f"  • {rec}")
    
    # Print detailed stats
    print("\n📊 DETAILED STATISTICS:")
    
    print("\nBy Hour:")
    for hour, stats in analyzer.by_hour().items():
        if stats["total_trades"] > 0:
            print(f"  {hour:02d}:00 - {stats['total_trades']} trades, Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    print("\nBy Day of Week:")
    for weekday, stats in analyzer.by_day_of_week().items():
        if stats["total_trades"] > 0:
            print(f"  {stats['name']} - {stats['total_trades']} trades, Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    print("\nBy Session:")
    for session, stats in analyzer.by_session().items():
        if stats["total_trades"] > 0:
            print(f"  {session} - {stats['total_trades']} trades, Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")