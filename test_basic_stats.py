#!/usr/bin/env python3
"""
Test script for BasicStats analyzer.
"""

import sys
sys.path.insert(0, '.')

from src.analyzers.basic_stats import BasicStats, create_sample_trades

def main():
    """Test the BasicStats analyzer."""
    print("🧪 Testing BasicStats Analyzer")
    print("=" * 50)
    
    # Create sample trades
    sample_trades = create_sample_trades()
    print(f"Created {len(sample_trades)} sample trades")
    
    # Create analyzer
    analyzer = BasicStats(sample_trades)
    
    # Get statistics
    stats = analyzer.get_stats()
    
    # Print summary
    print("\n📊 Statistics Summary:")
    print("-" * 30)
    print(analyzer.summary())
    
    # Test to_dict method
    print("\n📋 Dictionary format:")
    print("-" * 30)
    import json
    stats_dict = analyzer.to_dict()
    print(json.dumps(stats_dict, indent=2, default=str))
    
    # Test edge cases
    print("\n⚠️ Testing edge cases:")
    print("-" * 30)
    
    # Empty trades list
    from src.models.trade import Trade
    empty_analyzer = BasicStats([])
    empty_stats = empty_analyzer.get_stats()
    print(f"Empty trades: Total trades = {empty_stats.total_trades}")
    print(f"Empty trades: Win rate = {empty_stats.win_rate}")
    
    # Trades with only losses
    losing_trades = [
        Trade(
            ticket=2001,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=create_sample_trades()[0].open_time,
            open_price=Decimal("1.0800"),
            close_time=create_sample_trades()[0].close_time,
            close_price=Decimal("1.0750"),
            profit=Decimal("-50.00")
        )
    ]
    
    loss_analyzer = BasicStats(losing_trades)
    loss_stats = loss_analyzer.get_stats()
    print(f"Only losses: Win rate = {loss_stats.win_rate}")
    print(f"Only losses: Profit factor = {loss_stats.profit_factor}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    from decimal import Decimal
    main()