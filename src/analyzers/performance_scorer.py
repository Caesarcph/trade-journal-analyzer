"""
Performance scoring system for trade journal analysis.
Provides overall performance score (0-100) and individual trade grades.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import datetime
from enum import Enum

from ..models.trade import Trade
from .basic_stats import BasicStats


@dataclass
class PerformanceScore:
    """Overall performance score."""
    overall_score: float
    letter_grade: str
    win_rate_score: float
    risk_score: float
    profit_factor_score: float
    recommendations: List[str]
    strengths: List[str]
    weaknesses: List[str]
    score_breakdown: Dict[str, float]


@dataclass
class TradeGrade:
    """Grade for an individual trade."""
    trade_id: str
    symbol: str
    grade: str  # A, B, C, D, F
    score: float  # 0-100
    breakdown: Dict[str, float]  # Scores by category
    feedback: List[str]  # Suggestions for improvement
    summary: str  # Brief summary


class TradeGradeLetter(Enum):
    """Letter grades for trades."""
    A = 90
    B = 80
    C = 70
    D = 60
    F = 50


class PerformanceScorer:
    """
    Calculates performance scores for trading performance evaluation.
    Provides both overall portfolio scores and individual trade grading.
    """
    
    def __init__(self, trades: List[Trade]):
        self.trades = trades
        self.basic_stats = BasicStats(trades)
        self.stats_result = self.basic_stats.get_stats()
    
    def calculate_overall_score(self) -> PerformanceScore:
        """Calculate overall performance score based on multiple factors."""
        # Calculate component scores
        win_rate_score = self._calculate_win_rate_score()
        risk_score = self._calculate_risk_score()
        profit_factor_score = self._calculate_profit_factor_score()
        
        # Weighted average of components (weights can be adjusted)
        overall_score = (
            win_rate_score * 0.4 +
            risk_score * 0.3 +
            profit_factor_score * 0.3
        )
        
        # Determine letter grade
        letter_grade = self._get_letter_grade(overall_score)
        
        # Generate recommendations, strengths, and weaknesses
        recommendations, strengths, weaknesses = self._generate_insights()
        
        score_breakdown = {
            "win_rate": win_rate_score,
            "risk_management": risk_score,
            "profit_factor": profit_factor_score
        }
        
        return PerformanceScore(
            overall_score=round(overall_score, 2),
            letter_grade=letter_grade,
            win_rate_score=round(win_rate_score, 2),
            risk_score=round(risk_score, 2),
            profit_factor_score=round(profit_factor_score, 2),
            recommendations=recommendations,
            strengths=strengths,
            weaknesses=weaknesses,
            score_breakdown=score_breakdown
        )
    
    def _calculate_win_rate_score(self) -> float:
        """Calculate score based on win rate (0-100 scale)."""
        win_rate = self.stats_result.win_rate
        
        # Scoring based on win rate:
        # - Above 60%: Excellent
        # - 50-60%: Good
        # - 40-50%: Fair
        # - Below 40%: Needs work
        if win_rate >= 0.6:
            return 90 + (win_rate - 0.6) * 100  # Scale from 90-100 for >60%
        elif win_rate >= 0.5:
            return 70 + ((win_rate - 0.5) / 0.1) * 20  # Scale from 70-90 for 50-60%
        elif win_rate >= 0.4:
            return 50 + ((win_rate - 0.4) / 0.1) * 20  # Scale from 50-70 for 40-50%
        else:
            return 30 + (win_rate / 0.4) * 20  # Scale from 30-50 for <40%
    
    def _calculate_risk_score(self) -> float:
        """Calculate score based on risk management metrics."""
        # Consider expectancy and average win/loss ratio
        expectancy = float(self.stats_result.expectancy)
        avg_win = float(self.stats_result.avg_win)
        avg_loss = float(self.stats_result.avg_loss)
        
        # Calculate risk-reward ratio
        risk_reward_ratio = avg_win / avg_loss if avg_loss != 0 else float('inf')
        
        # Base score on expectancy (higher is better)
        # Positive expectancy gets higher scores
        expectancy_score = 50  # Base score
        if expectancy > 0:
            # Normalize expectancy score (assuming reasonable ranges)
            normalized_expectancy = min(expectancy / 100, 1.0)  # Cap at 100% of 100 points
            expectancy_score = 50 + min(normalized_expectancy * 50, 50)  # Max 100
        elif expectancy < 0:
            expectancy_score = max(10, 50 + expectancy * 0.1)  # Lower score for negative expectancy
        
        # Adjust based on risk-reward ratio
        if risk_reward_ratio >= 2.0:
            risk_reward_bonus = 20
        elif risk_reward_ratio >= 1.5:
            risk_reward_bonus = 10
        elif risk_reward_ratio >= 1.0:
            risk_reward_bonus = 5
        else:
            risk_reward_bonus = -10  # Penalty for bad risk-reward ratio
        
        final_score = expectancy_score + risk_reward_bonus
        return max(0, min(100, final_score))  # Clamp between 0 and 100
    
    def _calculate_profit_factor_score(self) -> float:
        """Calculate score based on profit factor."""
        profit_factor = self.stats_result.profit_factor
        
        # Score based on profit factor:
        # - Above 2.0: Excellent
        # - 1.5-2.0: Good
        # - 1.2-1.5: Fair
        # - Below 1.2: Poor
        if profit_factor >= 2.0:
            return 90 + ((profit_factor - 2.0) / 2.0) * 10  # Scale to max 100
        elif profit_factor >= 1.5:
            return 70 + ((profit_factor - 1.5) / 0.5) * 20  # Scale from 70-90
        elif profit_factor >= 1.2:
            return 50 + ((profit_factor - 1.2) / 0.3) * 20  # Scale from 50-70
        else:
            return max(10, profit_factor * 30)  # Scale from 10-50 for <1.2
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_insights(self) -> tuple[List[str], List[str], List[str]]:
        """Generate recommendations, strengths, and weaknesses based on stats."""
        recommendations = []
        strengths = []
        weaknesses = []
        
        # Evaluate win rate
        if self.stats_result.win_rate >= 0.6:
            strengths.append("Excellent win rate (>60%)")
        elif self.stats_result.win_rate >= 0.5:
            strengths.append("Good win rate (>50%)")
        elif self.stats_result.win_rate >= 0.4:
            weaknesses.append("Win rate could be improved (try to exceed 50%)")
            recommendations.append("Focus on entry criteria to improve win rate")
        else:
            weaknesses.append("Low win rate (<40%)")
            recommendations.append("Analyze entry/exit strategies to improve win rate")
        
        # Evaluate profit factor
        if self.stats_result.profit_factor >= 2.0:
            strengths.append("Strong profit factor (>2.0)")
        elif self.stats_result.profit_factor >= 1.5:
            strengths.append("Decent profit factor")
        else:
            weaknesses.append("Low profit factor (<1.5)")
            recommendations.append("Improve profit factor by increasing winners or reducing losers")
        
        # Evaluate expectancy
        if float(self.stats_result.expectancy) > 0:
            strengths.append("Positive expectancy (profitable over time)")
        else:
            weaknesses.append("Negative expectancy (unprofitable over time)")
            recommendations.append("Work on improving expectancy through risk management")
        
        # Evaluate risk management
        avg_win = float(self.stats_result.avg_win)
        avg_loss = float(self.stats_result.avg_loss)
        if avg_win > 0 and avg_loss > 0:
            risk_reward = avg_win / avg_loss
            if risk_reward >= 2.0:
                strengths.append(f"Excellent risk-reward ratio ({risk_reward:.2f}:1)")
            elif risk_reward >= 1.5:
                strengths.append(f"Good risk-reward ratio ({risk_reward:.2f}:1)")
            else:
                weaknesses.append(f"Room for improvement in risk-reward ratio ({risk_reward:.2f}:1)")
                recommendations.append("Consider adjusting stop-losses and take-profit levels")
        
        # Evaluate drawdown
        if self.stats_result.max_drawdown <= 10:
            strengths.append("Well-controlled drawdown")
        elif self.stats_result.max_drawdown <= 20:
            weaknesses.append("Moderate drawdown - monitor closely")
        else:
            weaknesses.append(f"High drawdown ({self.stats_result.max_drawdown:.1f}%)")
            recommendations.append("Implement stricter risk controls to reduce drawdown")
        
        # Ensure no duplicates
        strengths = list(set(strengths))
        weaknesses = list(set(weaknesses))
        recommendations = list(set(recommendations))
        
        return recommendations, strengths, weaknesses
    
    def grade_individual_trade(self, trade: Trade) -> TradeGrade:
        """Grade an individual trade based on various criteria."""
        # Calculate base score based on profit/loss
        profit = float(trade.profit)
        max_possible_profit = float(max(abs(t.profit) for t in self.trades if t.profit > 0) if any(t.profit > 0 for t in self.trades) else 100)
        max_possible_loss = float(min(abs(t.profit) for t in self.trades if t.profit < 0) if any(t.profit < 0 for t in self.trades) else 100)
        
        if profit > 0:
            # Profitable trade scoring
            profit_score = min(100, (profit / max_possible_profit) * 70 + 30)
        elif profit < 0:
            # Losing trade scoring (lower score for bigger losses)
            loss_proportion = abs(profit) / max_possible_loss
            profit_score = max(0, 50 - (loss_proportion * 50))
        else:
            # Breakeven trade
            profit_score = 50
        
        # Calculate duration score (longer holding periods for profitable trades may be better)
        if trade.duration:
            duration_hours = trade.duration / 3600  # Convert to hours
            if profit > 0:
                # For profitable trades, moderate duration is good (not too short, not too long)
                if 1 <= duration_hours <= 8:
                    duration_score = 10
                elif 0.5 <= duration_hours < 1 or 8 < duration_hours <= 24:
                    duration_score = 5
                else:
                    duration_score = 0
            else:
                # For losing trades, shorter duration might be better (quicker exits)
                if duration_hours <= 2:
                    duration_score = 5
                elif duration_hours <= 8:
                    duration_score = 2
                else:
                    duration_score = 0
        else:
            duration_score = 0
        
        # Calculate risk-reward potential score (if we have stop-loss / take-profit info)
        # Supports both naming conventions:
        # - Trade.sl / Trade.tp (current model)
        # - Trade.stop_loss / Trade.take_profit (legacy/alternate)
        risk_reward_score = 0
        stop_loss = getattr(trade, "sl", None) or getattr(trade, "stop_loss", None)
        take_profit = getattr(trade, "tp", None) or getattr(trade, "take_profit", None)

        if stop_loss is not None and take_profit is not None:
            # open_price may be Decimal; convert differences to float safely
            sl_diff = abs(float(trade.open_price) - float(stop_loss))
            tp_diff = abs(float(take_profit) - float(trade.open_price))

            if sl_diff > 0:
                rr_ratio = tp_diff / sl_diff
                if rr_ratio >= 2:
                    risk_reward_score = 15
                elif rr_ratio >= 1.5:
                    risk_reward_score = 10
                elif rr_ratio >= 1:
                    risk_reward_score = 5
                else:
                    risk_reward_score = 0
        
        # Combine scores
        total_score = min(100, profit_score + duration_score + risk_reward_score)
        
        # Determine grade
        grade = self._get_letter_grade(total_score)
        
        # Generate feedback
        feedback = []
        if profit > 0:
            feedback.append(f"Profitable trade with ${profit:.2f} gain")
        elif profit < 0:
            feedback.append(f"Losing trade with ${abs(profit):.2f} loss")
        else:
            feedback.append("Breakeven trade")
        
        if risk_reward_score > 0:
            feedback.append("Good risk-reward setup")
        
        # Create summary
        direction = "LONG" if trade.order_type.upper().startswith('B') else "SHORT"
        summary = f"{direction} {trade.symbol} - {grade} Grade ({total_score:.1f}/100)"
        
        breakdown = {
            "profitability": profit_score,
            "duration": duration_score,
            "risk_reward": risk_reward_score
        }
        
        return TradeGrade(
            trade_id=str(trade.ticket),
            symbol=trade.symbol,
            grade=grade,
            score=round(total_score, 2),
            breakdown=breakdown,
            feedback=feedback,
            summary=summary
        )
    
    def grade_all_trades(self) -> List[TradeGrade]:
        """Grade all trades in the portfolio."""
        return [self.grade_individual_trade(trade) for trade in self.trades]
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        overall_score = self.calculate_overall_score()
        
        report_lines = [
            "🏆 PERFORMANCE ANALYSIS REPORT",
            "=" * 50,
            f"Overall Score: {overall_score.overall_score}/100 ({overall_score.letter_grade})",
            "",
            "📊 SCORE BREAKDOWN:",
            f"  Win Rate Score: {overall_score.win_rate_score}/100",
            f"  Risk Management Score: {overall_score.risk_score}/100",
            f"  Profit Factor Score: {overall_score.profit_factor_score}/100",
            "",
            "✅ STRENGTHS:",
        ]
        
        for strength in overall_score.strengths:
            report_lines.append(f"  • {strength}")
        
        report_lines.extend([
            "",
            "⚠️  WEAKNESSES:",
        ])
        
        for weakness in overall_score.weaknesses:
            report_lines.append(f"  • {weakness}")
        
        report_lines.extend([
            "",
            "💡 RECOMMENDATIONS:",
        ])
        
        for recommendation in overall_score.recommendations:
            report_lines.append(f"  • {recommendation}")
        
        return "\n".join(report_lines)


def create_sample_usage() -> str:
    """Create sample usage of the PerformanceScorer."""
    from .basic_stats import create_sample_trades
    
    # Create sample trades
    sample_trades = create_sample_trades()
    
    # Initialize performance scorer
    scorer = PerformanceScorer(sample_trades)
    
    # Calculate overall score
    overall_score = scorer.calculate_overall_score()
    
    # Grade all trades
    trade_grades = scorer.grade_all_trades()
    
    # Generate report
    report = scorer.generate_performance_report()
    
    return report


if __name__ == "__main__":
    # Example usage
    print(create_sample_usage())