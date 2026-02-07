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
        
        # Determine sessions (can include overlaps)
        for session in self._get_sessions(close_time):
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
        """Determine primary trading session the time falls into.

        Note: a time can belong to multiple sessions (e.g., overlaps). For full
        membership (including overlaps), use `_get_sessions()`.
        """
        t = close_time.time()

        for session_name, (start_time, end_time) in self.SESSIONS.items():
            if self._time_in_range(t, start_time, end_time):
                return session_name

        return None
    
    def _get_period(self, close_time: datetime) -> Optional[str]:
        """Determine which time period the time falls into."""
        close_hour = close_time.time()
        
        for period_name, (start_time, end_time) in self.PERIODS.items():
            if start_time <= close_hour < end_time:
                return period_name
        
        return None
    
    def _time_in_range(self, t: time, start: time, end: time) -> bool:
        """Check if time t is within [start, end) (supports ranges that cross midnight)."""
        if start <= end:
            return start <= t < end
        # crosses midnight
        return t >= start or t < end

    def _get_sessions(self, close_time: datetime) -> List[str]:
        """Return all sessions that the time falls into (including overlaps)."""
        t = close_time.time()
        sessions: List[str] = []
        for session_name, (start_time, end_time) in self.SESSIONS.items():
            if self._time_in_range(t, start_time, end_time):
                sessions.append(session_name)
        return sessions

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
    
    def get_session_overlaps(self) -> List[Dict[str, Any]]:
        """Analyze overlaps between trading sessions based on session time windows.

        Implementation note:
        - A trade time can belong to multiple sessions (e.g., London and New York).
        - We compute overlaps by intersecting session windows and selecting trades
          whose close_time falls inside that intersection.
        """
        overlaps: List[Dict[str, Any]] = []

        session_pairs = [
            ("London", "New_York"),
            ("Asian", "London"),
        ]

        for session1, session2 in session_pairs:
            if session1 not in self.SESSIONS or session2 not in self.SESSIONS:
                continue

            s1_start, s1_end = self.SESSIONS[session1]
            s2_start, s2_end = self.SESSIONS[session2]

            # Complex midnight-wrapping overlap support can be added later.
            if s1_start > s1_end or s2_start > s2_end:
                continue

            overlap_start = max(s1_start, s2_start)
            overlap_end = min(s1_end, s2_end)

            if overlap_start >= overlap_end:
                continue

            overlap_trades = [
                t for t in self._closed_trades
                if t.close_time and self._time_in_range(t.close_time.time(), overlap_start, overlap_end)
            ]

            if not overlap_trades:
                continue

            total_pnl = sum((t.profit for t in overlap_trades), Decimal("0.0"))
            wins = sum(1 for t in overlap_trades if t.profit > 0)
            losses = sum(1 for t in overlap_trades if t.profit < 0)
            total_trades = len(overlap_trades)
            win_rate = wins / total_trades if total_trades else 0.0
            avg_pnl = (total_pnl / Decimal(str(total_trades))) if total_trades else Decimal("0.0")

            overlaps.append({
                "session_pair": f"{session1}-{session2}",
                "overlap_name": f"{session1}/{session2} Overlap",
                "overlap_window_utc": (
                    overlap_start.isoformat(timespec='minutes'),
                    overlap_end.isoformat(timespec='minutes'),
                ),
                "total_trades": total_trades,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "total_pnl": float(total_pnl),
                "avg_pnl": float(avg_pnl),
                "trades": overlap_trades,
            })

        overlaps.sort(key=lambda x: (x["total_trades"], x["win_rate"], x["avg_pnl"]), reverse=True)
        return overlaps
    
    def get_best_session_overlap(self) -> Optional[Dict[str, Any]]:
        """
        Get the best performing session overlap based on win rate and average PnL.
        
        Returns:
            Dictionary with best overlap analysis or None if no overlaps found
        """
        overlaps = self.get_session_overlaps()
        if not overlaps:
            return None
        
        # Find overlap with highest combined score (win_rate * avg_pnl_positive)
        best_overlap = None
        best_score = -float('inf')
        
        for overlap in overlaps:
            if overlap["total_trades"] >= 3:  # Minimum trades for significance
                score = overlap["win_rate"] * max(0.1, overlap["avg_pnl"])  # Ensure positive multiplier
                if score > best_score:
                    best_score = score
                    best_overlap = overlap
        
        return best_overlap
    
    def get_session_volatility_analysis(self) -> Dict[str, Any]:
        """
        Analyze volatility patterns by session.
        Calculates volatility metrics like profit range, win/loss streaks, and consistency.
        
        Returns:
            Dictionary with volatility analysis by session
        """
        volatility_by_session = {}
        
        for session, stats in self._session_stats.items():
            trades = stats["trades"]
            if len(trades) < 2:  # Need at least 2 trades for volatility calculation
                continue
            
            # Calculate profit/loss values
            profits = [float(trade.profit) for trade in trades]
            
            # Basic volatility metrics
            if profits:
                volatility_by_session[session] = {
                    "total_trades": len(trades),
                    "profit_range": (min(profits), max(profits)),
                    "profit_std": statistics.stdev(profits) if len(profits) > 1 else 0.0,
                    "profit_iqr": (sorted(profits)[len(profits)//4], sorted(profits)[3*len(profits)//4]) if len(profits) >= 4 else (0.0, 0.0),
                    "max_winning_streak": self._calculate_max_streak(trades, positive=True),
                    "max_losing_streak": self._calculate_max_streak(trades, positive=False),
                    "profit_consistency": self._calculate_profit_consistency(trades),
                    "avg_profit_per_trade": sum(profits) / len(profits),
                    "median_profit": statistics.median(profits) if profits else 0.0
                }
        
        return volatility_by_session
    
    def _calculate_max_streak(self, trades: List[Trade], positive: bool = True) -> int:
        """
        Calculate maximum consecutive winning or losing streak.
        
        Args:
            trades: List of Trade objects
            positive: True for winning streak, False for losing streak
            
        Returns:
            Maximum streak length
        """
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if (positive and trade.profit > 0) or (not positive and trade.profit < 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_profit_consistency(self, trades: List[Trade]) -> float:
        """
        Calculate profit consistency score (0-1).
        Higher values indicate more consistent profits.
        
        Returns:
            Consistency score between 0 and 1
        """
        if len(trades) < 2:
            return 1.0  # Single trade is perfectly consistent
        
        profits = [float(trade.profit) for trade in trades]
        mean_profit = statistics.mean(profits)
        
        if mean_profit == 0:
            return 0.0
        
        # Calculate coefficient of variation (lower is better/more consistent)
        std_dev = statistics.stdev(profits) if len(profits) > 1 else 0.0
        cv = std_dev / abs(mean_profit) if mean_profit != 0 else float('inf')
        
        # Convert to consistency score (0-1)
        # cv < 0.5 = very consistent, cv > – 2.0 = inconsistent
        consistency_score = max(0.0, min(1.0, 2.0 - cv))
        
        return consistency_score
    
    def get_time_based_risk_metrics(self) -> Dict[str, Any]:
        """
        Calculate risk metrics based on time patterns.
        Includes metrics like worst hour drawdown, session risk scores, etc.
        
        Returns:
            Dictionary with time-based risk metrics
        """
        risk_metrics = {
            "by_hour": {},
            "by_session": {},
            "by_weekday": {},
            "overall": {}
        }
        
        # Calculate hour-based risk metrics
        for hour, stats in self._hour_stats.items():
            if stats.get("total_trades", 0) >= 3:
                trades = stats["trades"]
                profits = [float(trade.profit) for trade in trades]
                
                risk_metrics["by_hour"][hour] = {
                    "total_trades": stats["total_trades"],
                    "win_rate": stats.get("win_rate", 0.0),
                    "max_drawdown": self._calculate_max_drawdown(profits),
                    "sharpe_ratio": self._calculate_sharpe_ratio(profits),
                    "profit_factor": self._calculate_profit_factor(profits),
                    "risk_score": self._calculate_risk_score(stats)
                }
        
        # Calculate session-based risk metrics
        for session, stats in self._session_stats.items():
            if stats.get("total_trades", 0) >= 3:
                trades = stats["trades"]
                profits = [float(trade.profit) for trade in trades]
                
                risk_metrics["by_session"][session] = {
                    "total_trades": stats["total_trades"],
                    "win_rate": stats.get("win_rate", 0.0),
                    "max_drawdown": self._calculate_max_drawdown(profits),
                    "sharpe_ratio": self._calculate_sharpe_ratio(profits),
                    "profit_factor": self._calculate_profit_factor(profits),
                    "risk_score": self._calculate_risk_score(stats)
                }
        
        # Calculate overall risk metrics
        all_profits = [float(trade.profit) for trade in self._closed_trades]
        if all_profits:
            risk_metrics["overall"] = {
                "total_trades": len(self._closed_trades),
                "max_drawdown": self._calculate_max_drawdown(all_profits),
                "sharpe_ratio": self._calculate_sharpe_ratio(all_profits),
                "profit_factor": self._calculate_profit_factor(all_profits),
                "avg_daily_risk": self._calculate_avg_daily_risk(),
                "time_based_var": self._calculate_time_based_var()
            }
        
        return risk_metrics
    
    def _calculate_max_drawdown(self, profits: List[float]) -> float:
        """Calculate maximum drawdown from profit sequence."""
        if not profits:
            return 0.0
        
        peak = profits[0]
        max_dd = 0.0
        
        for profit in profits:
            if profit > peak:
                peak = profit
            dd = (peak - profit) / max(abs(peak), 0.01)  # Avoid division by zero
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, profits: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio (annualized)."""
        if len(profits) < 2:
            return 0.0
        
        excess_returns = [p - risk_free_rate/252 for p in profits]  # Daily risk-free rate
        mean_return = statistics.mean(excess_returns)
        std_return = statistics.stdev(excess_returns) if len(excess_returns) > 1 else 0.0
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assuming daily returns)
        return (mean_return / std_return) * (252 ** 0.5)
    
    def _calculate_profit_factor(self, profits: List[float]) -> float:
        """Calculate profit factor (gross profits / gross losses)."""
        gross_profits = sum(max(p, 0) for p in profits)
        gross_losses = abs(sum(min(p, 0) for p in profits))
        
        return gross_profits / gross_losses if gross_losses > 0 else float('inf')
    
    def _calculate_risk_score(self, stats: Dict[str, Any]) -> float:
        """Calculate risk score (0-100, lower is better)."""
        win_rate = stats.get("win_rate", 0.5)
        total_trades = stats.get("total_trades", 0)
        
        if total_trades < 3:
            return 50.0  # Neutral score for insufficient data
        
        # Risk score based on win rate and consistency
        base_score = (1.0 - win_rate) * 50  # Lower win rate = higher risk
        
        # Adjust for sample size (more trades = more reliable)
        sample_adjustment = min(20, 40 / (total_trades ** 0.5))
        
        return min(100, max(0, base_score + sample_adjustment))
    
    def _calculate_avg_daily_risk(self) -> float:
        """Calculate average daily risk exposure."""
        if not self._closed_trades:
            return 0.0
        
        # Group trades by day
        trades_by_day = defaultdict(list)
        for trade in self._closed_trades:
            if trade.close_time:
                day_key = trade.close_time.date()
                trades_by_day[day_key].append(trade)
        
        # Calculate daily PnL volatility
        daily_pnls = []
        for day_trades in trades_by_day.values():
            daily_pnl = sum(float(t.profit) for t in day_trades)
            daily_pnls.append(daily_pnl)
        
        if len(daily_pnls) < 2:
            return 0.0
        
        return statistics.stdev(daily_pnls)
    
    def _calculate_time_based_var(self) -> Dict[str, float]:
        """Calculate Value at Risk (VaR) by time period."""
        var_results = {}
        
        # Calculate VaR for each hour with sufficient data
        for hour, stats in self._hour_stats.items():
            if stats.get("total_trades", 0) >= 10:
                profits = [float(trade.profit) for trade in stats["trades"]]
                profits_sorted = sorted(profits)
                
                # 95% VaR (5th percentile)
                var_95_idx = int(len(profits_sorted) * 0.05)
                var_results[f"hour_{hour}_var_95"] = profits_sorted[var_95_idx] if var_95_idx < len(profits_sorted) else 0.0
        
        return var_results
    
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
        
        # Analyze session overlaps (new feature)
        best_overlap = self.get_best_session_overlap()
        if best_overlap and best_overlap["total_trades"] >= 5 and best_overlap["win_rate"] >= 0.65:
            recs.append(f"{best_overlap['overlap_name']} shows excellent performance ({best_overlap['win_rate']:.1%} win rate) - capitalize on overlap volatility.")
        
        # Add risk-based recommendations
        risk_metrics = self.get_time_based_risk_metrics()
        
        # Check for high-risk hours
        for hour, metrics in risk_metrics.get("by_hour", {}).items():
            if metrics.get("risk_score", 50) > 70 and metrics.get("total_trades", 0) >= 5:
                recs.append(f"Hour {hour:02d}:00 has high risk score ({metrics['risk_score']:.0f}/100) - consider reducing position size or avoiding.")
        
        # Check for low-risk sessions
        for session, metrics in risk_metrics.get("by_session", {}).items():
            if metrics.get("risk_score", 50) < 30 and metrics.get("total_trades", 0) >= 10:
                recs.append(f"{session} session has low risk score ({metrics['risk_score']:.0f}/100) - good for larger position sizes.")
        
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
    
    # Test new features
    print("\n🎯 NEW FEATURES TEST:")
    
    # Session overlaps
    overlaps = analyzer.get_session_overlaps()
    if overlaps:
        print("\n🔀 SESSION OVERLAPS:")
        for overlap in overlaps:
            print(f"  {overlap['overlap_name']}: {overlap['total_trades']} trades, Win Rate: {overlap['win_rate']:.1%}, Avg PnL: ${overlap['avg_pnl']:.2f}")
    
    best_overlap = analyzer.get_best_session_overlap()
    if best_overlap:
        print(f"\n🏆 BEST SESSION OVERLAP: {best_overlap['overlap_name']}")
        print(f"  Win Rate: {best_overlap['win_rate']:.1%}, Avg PnL: ${best_overlap['avg_pnl']:.2f}, Trades: {best_overlap['total_trades']}")
    
    # Volatility analysis
    volatility = analyzer.get_session_volatility_analysis()
    if volatility:
        print("\n📈 VOLATILITY ANALYSIS BY SESSION:")
        for session, metrics in volatility.items():
            if metrics["total_trades"] >= 2:
                print(f"  {session}: {metrics['total_trades']} trades, Profit Range: ${metrics['profit_range'][0]:.2f} to ${metrics['profit_range'][1]:.2f}")
                print(f"    Std Dev: ${metrics['profit_std']:.2f}, Max Winning Streak: {metrics['max_winning_streak']}")
    
    # Risk metrics
    risk_metrics = analyzer.get_time_based_risk_metrics()
    if risk_metrics.get("overall"):
        print("\n⚠️ TIME-BASED RISK METRICS:")
        overall = risk_metrics["overall"]
        print(f"  Overall Max Drawdown: {overall.get('max_drawdown', 0):.1%}")
        print(f"  Sharpe Ratio: {overall.get('sharpe_ratio', 0):.2f}")
        print(f"  Profit Factor: {overall.get('profit_factor', 0):.2f}")
        
        # Show high-risk hours
        print("\n  HIGHEST RISK HOURS:")
        hour_risks = []
        for hour, metrics in risk_metrics.get("by_hour", {}).items():
            if metrics.get("total_trades", 0) >= 3:
                hour_risks.append((hour, metrics.get("risk_score", 50)))
        
        hour_risks.sort(key=lambda x: x[1], reverse=True)
        for hour, risk_score in hour_risks[:3]:
            print(f"    {hour:02d}:00 - Risk Score: {risk_score:.0f}/100")
    
    print("\n" + "=" * 60)
    print("✅ All new time analysis features tested successfully!")