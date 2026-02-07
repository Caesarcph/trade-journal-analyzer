#!/usr/bin/env python3
"""
Test script for time analysis module.
"""

import sys
sys.path.insert(0, '.')

from src.models.trade import Trade
from src.analyzers.time_analysis import TimeAnalysis, create_sample_trades


def test_basic_functionality():
    """Test basic functionality of TimeAnalysis."""
    print("🧪 Testing TimeAnalysis Basic Functionality")
    print("=" * 60)
    
    # Create sample trades
    sample_trades = create_sample_trades()
    print(f"Created {len(sample_trades)} sample trades")
    
    # Create analyzer
    analyzer = TimeAnalysis(sample_trades)
    
    # Test summary
    summary = analyzer.summary()
    print("\n📋 SUMMARY:")
    print(summary)
    
    # Test recommendations
    recommendations = analyzer.recommendations()
    print("\n💡 RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"  • {rec}")
    
    # Test detailed stats
    print("\n📊 DETAILED STATISTICS:")
    
    print("\nBy Hour Analysis:")
    hour_stats = analyzer.by_hour()
    for hour, stats in sorted(hour_stats.items()):
        if stats["total_trades"] > 0:
            print(f"  {hour:02d}:00 - Trades: {stats['total_trades']}, "
                  f"Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    print("\nBy Day of Week Analysis:")
    weekday_stats = analyzer.by_day_of_week()
    for weekday, stats in sorted(weekday_stats.items()):
        if stats["total_trades"] > 0:
            print(f"  {stats['name']} - Trades: {stats['total_trades']}, "
                  f"Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    print("\nBy Session Analysis:")
    session_stats = analyzer.by_session()
    for session, stats in sorted(session_stats.items()):
        if stats["total_trades"] > 0:
            print(f"  {session} - Trades: {stats['total_trades']}, "
                  f"Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    print("\nBy Period Analysis:")
    period_stats = analyzer.by_period()
    for period, stats in sorted(period_stats.items()):
        if stats["total_trades"] > 0:
            print(f"  {period} - Trades: {stats['total_trades']}, "
                  f"Win Rate: {stats['win_rate']:.1%}, Avg PnL: ${stats['avg_pnl']:.2f}")
    
    # Test peak hours
    print("\n🏆 PEAK HOURS:")
    peak_hours = analyzer.get_peak_hours(3)
    for i, hour_data in enumerate(peak_hours, 1):
        hour = hour_data["hour"]
        win_rate = hour_data["win_rate"]
        avg_pnl = hour_data["avg_pnl"]
        print(f"  {i}. {hour:02d}:00 - Win Rate: {win_rate:.1%}, Avg PnL: ${avg_pnl:.2f}")
    
    # Test best/worst weekday
    print("\n📅 BEST/WORST WEEKDAY:")
    best_weekday = analyzer.get_best_weekday()
    worst_weekday = analyzer.get_worst_weekday()
    if best_weekday:
        print(f"  Best: {best_weekday['name']} - Win Rate: {best_weekday['win_rate']:.1%}, "
              f"Avg PnL: ${best_weekday['avg_pnl']:.2f}")
    if worst_weekday:
        print(f"  Worst: {worst_weekday['name']} - Win Rate: {worst_weekday['win_rate']:.1%}, "
              f"Avg PnL: ${worst_weekday['avg_pnl']:.2f}")
    
    # Test all stats retrieval
    print("\n📈 COMPLETE STATS OBJECT:")
    all_stats = analyzer.get_all_stats()
    print(f"  Analyzed {len(sample_trades)} trades")
    print(f"  Hours analyzed: {len(all_stats.by_hour)}")
    print(f"  Weekdays analyzed: {len(all_stats.by_weekday)}")
    print(f"  Sessions analyzed: {len(all_stats.by_session)}")
    print(f"  Peak hours identified: {len(all_stats.peak_hours)}")
    
    return True


def test_edge_cases():
    """Test edge cases."""
    print("\n\n🧪 Testing Edge Cases")
    print("=" * 60)
    
    from decimal import Decimal
    
    # Test with empty trades list
    print("\n1. Testing with empty trades list:")
    analyzer_empty = TimeAnalysis([])
    summary_empty = analyzer_empty.summary()
    print(f"   Summary: {summary_empty[:50]}...")
    
    # Test with single trade
    print("\n2. Testing with single trade:")
    single_trade = Trade(
        ticket=3001,
        symbol="EURUSD",
        order_type="BUY",
        volume=0.1,
        open_time=create_sample_trades()[0].open_time,
        open_price=Decimal("1.0800"),
        close_time=create_sample_trades()[0].close_time,
        close_price=Decimal("1.0850"),
        profit=Decimal("50.00")
    )
    analyzer_single = TimeAnalysis([single_trade])
    print(f"   Summary length: {len(analyzer_single.summary())} characters")
    
    # Test recommendation generation
    print("\n3. Testing recommendations with minimal data:")
    recs_single = analyzer_single.recommendations()
    print(f"   Recommendations: {recs_single}")
    
    return True


def test_integration():
    """Test integration with other modules."""
    print("\n\n🧪 Testing Integration")
    print("=" * 60)
    
    from src.analyzers.basic_stats import BasicStats
    
    # Create sample trades
    sample_trades = create_sample_trades()
    
    # Test integration with BasicStats
    print("\n1. Integration with BasicStats:")
    basic_stats = BasicStats(sample_trades)
    time_analysis = TimeAnalysis(sample_trades)
    
    print(f"   BasicStats analyzed {len(sample_trades)} trades")
    print(f"   TimeAnalysis analyzed {len([t for t in sample_trades if t.is_closed])} closed trades")
    
    # Combined analysis
    print("\n2. Combined analysis example:")
    print("   Combining time patterns with basic statistics:")
    
    basic_result = basic_stats.get_stats()
    time_result = time_analysis.get_all_stats()
    
    print(f"   Total net profit: ${basic_result.total_net_profit:.2f}")
    if time_result.peak_hours:
        print(f"   Best hour: {time_result.peak_hours[0]['hour']:02d}:00 "
              f"(Win Rate: {time_result.peak_hours[0]['win_rate']:.1%})")
    else:
        print(f"   No peak hours identified")
    
    return True


def main():
    """Run all tests."""
    print("🧪 Starting TimeAnalysis Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_basic_functionality()
        test_edge_cases()
        test_integration()
        
        print("\n✅ All tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())