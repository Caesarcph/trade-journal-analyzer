#!/usr/bin/env python3
"""
Test suite for PerformanceScorer module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analyzers.performance_scorer import PerformanceScorer, create_sample_usage
from src.models.trade import Trade
from datetime import datetime, timedelta
from decimal import Decimal


def create_test_trades() -> list[Trade]:
    """Create test trades for performance scoring."""
    now = datetime.now()

    trades = [
        # Winning trades
        Trade(
            ticket=1001,
            symbol="EURUSD",
            order_type="BUY",
            volume=1.0,
            open_time=now - timedelta(hours=4),
            open_price=Decimal("1.0850"),
            close_time=now - timedelta(hours=2),
            close_price=Decimal("1.0870"),
            sl=Decimal("1.0830"),
            tp=Decimal("1.0900"),
            commission=Decimal("5.0"),
            swap=Decimal("0.0"),
            profit=Decimal("200.0"),
            magic=12345,
            comment="Good setup, followed rules",
        ),
        Trade(
            ticket=1002,
            symbol="GBPUSD",
            order_type="SELL",
            volume=1.0,
            open_time=now - timedelta(hours=6),
            open_price=Decimal("1.2650"),
            close_time=now - timedelta(hours=1),
            close_price=Decimal("1.2620"),
            sl=Decimal("1.2680"),
            tp=Decimal("1.2600"),
            commission=Decimal("5.0"),
            swap=Decimal("0.0"),
            profit=Decimal("300.0"),
            magic=12345,
            comment="Resistance bounce play",
        ),
        # Losing trades
        Trade(
            ticket=1003,
            symbol="USDJPY",
            order_type="BUY",
            volume=1.0,
            open_time=now - timedelta(hours=8),
            open_price=Decimal("151.50"),
            close_time=now - timedelta(hours=3),
            close_price=Decimal("151.30"),
            sl=Decimal("151.20"),
            tp=Decimal("152.00"),
            commission=Decimal("5.0"),
            swap=Decimal("0.0"),
            profit=Decimal("-200.0"),
            magic=12345,
            comment="Missed reversal",
        ),
        Trade(
            ticket=1004,
            symbol="XAUUSD",
            order_type="SELL",
            volume=0.1,
            open_time=now - timedelta(hours=10),
            open_price=Decimal("1980.0"),
            close_time=now - timedelta(hours=5),
            close_price=Decimal("1985.0"),
            sl=Decimal("1990.0"),
            tp=Decimal("1970.0"),
            commission=Decimal("5.0"),
            swap=Decimal("0.0"),
            profit=Decimal("-50.0"),
            magic=12345,
            comment="Gold spike caught",
        ),
        # Winning trade with long duration
        Trade(
            ticket=1005,
            symbol="BTCUSD",
            order_type="BUY",
            volume=0.01,
            open_time=now - timedelta(days=2),
            open_price=Decimal("45000.0"),
            close_time=now - timedelta(days=1),
            close_price=Decimal("45500.0"),
            sl=Decimal("44500.0"),
            tp=Decimal("46000.0"),
            commission=Decimal("5.0"),
            swap=Decimal("0.0"),
            profit=Decimal("500.0"),
            magic=12345,
            comment="Crypto swing",
        ),
    ]

    return trades


def test_performance_score_calculation():
    """Test calculation of overall performance score."""
    print("🧪 Testing PerformanceScore calculation...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)
    
    score = scorer.calculate_overall_score()
    
    print(f"✅ Overall Score: {score.overall_score}/100")
    print(f"✅ Letter Grade: {score.letter_grade}")
    print(f"✅ Win Rate Score: {score.win_rate_score}/100")
    print(f"✅ Risk Score: {score.risk_score}/100")
    print(f"✅ Profit Factor Score: {score.profit_factor_score}/100")
    
    assert 0 <= score.overall_score <= 100, f"Score out of range: {score.overall_score}"
    assert score.letter_grade in ["A", "B", "C", "D", "F"], f"Invalid grade: {score.letter_grade}"
    assert len(score.strengths) >= 0, "Should have strengths list"
    assert len(score.weaknesses) >= 0, "Should have weaknesses list"
    
    print("✅ PerformanceScore calculation test passed!\n")


def test_trade_grading():
    """Test individual trade grading functionality."""
    print("🧪 Testing TradeGrade calculation...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)
    
    # Test grading a winning trade
    winning_trade = trades[0]
    grade = scorer.grade_individual_trade(winning_trade)
    
    print(f"✅ Trade ID: {grade.trade_id}")
    print(f"✅ Symbol: {grade.symbol}")
    print(f"✅ Grade: {grade.grade}")
    print(f"✅ Score: {grade.score}/100")
    print(f"✅ Breakdown: {grade.breakdown}")
    
    assert grade.trade_id == str(winning_trade.ticket), f"Trade ID mismatch"
    assert grade.symbol == winning_trade.symbol, f"Symbol mismatch"
    assert grade.grade in ["A", "B", "C", "D", "F"], f"Invalid grade: {grade.grade}"
    assert 0 <= grade.score <= 100, f"Score out of range: {grade.score}"
    
    print("✅ TradeGrade calculation test passed!\n")


def test_grading_all_trades():
    """Test grading all trades at once."""
    print("🧪 Testing grade_all_trades...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)
    
    all_grades = scorer.grade_all_trades()
    
    print(f"✅ Number of trades graded: {len(all_grades)}")
    
    for i, grade in enumerate(all_grades):
        print(f"  Trade {i+1}: {grade.symbol} - {grade.grade} ({grade.score}/100)")
    
    assert len(all_grades) == len(trades), f"Expected {len(trades)} grades, got {len(all_grades)}"
    
    print("✅ grade_all_trades test passed!\n")


def test_performance_report():
    """Test performance report generation."""
    print("🧪 Testing performance report generation...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)
    
    report = scorer.generate_performance_report()
    
    print("✅ Report Generated:")
    print("-" * 50)
    print(report[:500])  # Print first 500 characters
    print("-" * 50)
    
    assert len(report) > 0, "Report should not be empty"
    assert "Overall Score:" in report, "Report should contain overall score"
    assert "STRENGTHS:" in report, "Report should contain strengths section"
    assert "WEAKNESSES:" in report, "Report should contain weaknesses section"
    
    print("✅ Performance report test passed!\n")


def test_letter_grade_conversion():
    """Test letter grade conversion logic."""
    print("🧪 Testing letter grade conversion...")
    from src.analyzers.performance_scorer import PerformanceScorer
    
    test_cases = [
        (95, "A"),
        (85, "B"),
        (75, "C"),
        (65, "D"),
        (55, "F"),
        (0, "F"),
        (100, "A"),
        (90, "A"),
        (80, "B"),
        (70, "C"),
        (60, "D"),
        (59, "F"),
    ]
    
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)
    
    for score, expected_grade in test_cases:
        grade = scorer._get_letter_grade(score)
        assert grade == expected_grade, f"For score {score}, expected {expected_grade}, got {grade}"
    
    print("✅ Letter grade conversion test passed!\n")


def test_score_calculation_methods():
    """Test individual score calculation methods."""
    print("🧪 Testing individual score calculation methods...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)

    # Test win rate score
    win_rate_score = scorer._calculate_win_rate_score()
    print(f"✅ Win Rate Score: {win_rate_score}")
    assert 0 <= win_rate_score <= 100, f"Win rate score out of range: {win_rate_score}"

    # Test risk score
    risk_score = scorer._calculate_risk_score()
    print(f"✅ Risk Score: {risk_score}")
    assert 0 <= risk_score <= 100, f"Risk score out of range: {risk_score}"

    # Test profit factor score
    profit_factor_score = scorer._calculate_profit_factor_score()
    print(f"✅ Profit Factor Score: {profit_factor_score}")
    assert 0 <= profit_factor_score <= 100, f"Profit factor score out of range: {profit_factor_score}"

    print("✅ Individual score calculation test passed!\n")


def test_grade_distribution():
    """Test grade distribution summary."""
    print("🧪 Testing grade distribution...")
    trades = create_test_trades()
    scorer = PerformanceScorer(trades)

    grades = scorer.grade_all_trades()
    dist = scorer.grade_distribution(grades)

    # Basic schema checks
    for k in ["A", "B", "C", "D", "F"]:
        assert k in dist, f"Missing grade key: {k}"
        assert "count" in dist[k] and "pct" in dist[k], f"Missing fields for grade {k}"
        assert dist[k]["count"] >= 0
        assert 0.0 <= dist[k]["pct"] <= 1.0

    total_count = sum(dist[k]["count"] for k in dist)
    assert total_count == len(trades), f"Expected {len(trades)} total, got {total_count}"

    print("✅ Grade distribution test passed!\n")


def main():
    """Run all tests."""
    print("🚀 Running PerformanceScorer Test Suite\n")
    print("=" * 60)
    
    try:
        test_performance_score_calculation()
        test_trade_grading()
        test_grading_all_trades()
        test_performance_report()
        test_letter_grade_conversion()
        test_score_calculation_methods()
        test_grade_distribution()

        # Test sample usage
        print("🧪 Testing create_sample_usage...")
        sample_report = create_sample_usage()
        print("✅ Sample usage test passed!")
        print("-" * 50)
        print("Sample Report Preview:")
        print(sample_report[:300])
        print("..." if len(sample_report) > 300 else "")
        print("-" * 50)
        
        print("\n🎉 All tests passed successfully!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())