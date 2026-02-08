#!/usr/bin/env python3
"""
Test script for Drawdown analyzer.
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random

sys.path.insert(0, '.')

from src.models.trade import Trade
from src.analyzers.drawdown import DrawdownAnalyzer

def create_drawdown_scenario_trades() -> list[Trade]:
    """
    Create a sequence of trades that simulates:
    1. A winning streak (Peak 1)
    2. A drawdown period (Drawdown 1)
    3. Recovery to new peak (Peak 2)
    4. A deeper drawdown (Drawdown 2)
    """
    trades = []
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    
    # 1. Winning streak (5 trades, +$50 each) => Balance: $10,250
    for i in range(5):
        trades.append(Trade(
            ticket=1000 + i,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=base_time + timedelta(hours=i),
            open_price=Decimal("1.1000"),
            close_time=base_time + timedelta(hours=i) + timedelta(minutes=30),
            close_price=Decimal("1.1050"),
            profit=Decimal("50.00")
        ))
    
    # 2. Drawdown 1 (3 trades, -$40 each) => Balance: $10,130 (Peak was $10,250, DD: $120)
    for i in range(3):
        trades.append(Trade(
            ticket=2000 + i,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=base_time + timedelta(days=1, hours=i),
            open_price=Decimal("1.1000"),
            close_time=base_time + timedelta(days=1, hours=i) + timedelta(minutes=30),
            close_price=Decimal("1.0960"),
            profit=Decimal("-40.00")
        ))
        
    # 3. Recovery (4 trades, +$50 each) => Balance: $10,330 (New Peak)
    for i in range(4):
        trades.append(Trade(
            ticket=3000 + i,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=base_time + timedelta(days=2, hours=i),
            open_price=Decimal("1.1000"),
            close_time=base_time + timedelta(days=2, hours=i) + timedelta(minutes=30),
            close_price=Decimal("1.1050"),
            profit=Decimal("50.00")
        ))
        
    # 4. Deep Drawdown (5 trades, -$60 each) => Balance: $10,030 (Peak was $10,330, DD: $300)
    for i in range(5):
        trades.append(Trade(
            ticket=4000 + i,
            symbol="EURUSD",
            order_type="BUY",
            volume=0.1,
            open_time=base_time + timedelta(days=3, hours=i),
            open_price=Decimal("1.1000"),
            close_time=base_time + timedelta(days=3, hours=i) + timedelta(minutes=30),
            close_price=Decimal("1.0940"),
            profit=Decimal("-60.00")
        ))
        
    return trades

def main():
    """Test the DrawdownAnalyzer."""
    print("🧪 Testing DrawdownAnalyzer")
    print("=" * 50)
    
    # Create sample trades
    sample_trades = create_drawdown_scenario_trades()
    print(f"Created {len(sample_trades)} sample trades")
    
    # Create analyzer
    analyzer = DrawdownAnalyzer(sample_trades, initial_balance=Decimal("10000.00"))
    
    # Get analysis
    res = analyzer.get_analysis()
    
    # Print summary
    print("\n📊 Drawdown Summary:")
    print("-" * 30)
    print(analyzer.summary())
    
    # Verification
    print("\n🔍 Verification:")
    print("-" * 30)
    
    print(f"Max Drawdown: ${res.max_drawdown} (Expected ~$300.00)")
    assert abs(res.max_drawdown - Decimal("300.00")) < Decimal("0.01"), f"Expected 300.00, got {res.max_drawdown}"
    
    print(f"Current Drawdown: ${res.current_drawdown} (Expected ~$300.00)")
    assert abs(res.current_drawdown - Decimal("300.00")) < Decimal("0.01"), f"Expected 300.00, got {res.current_drawdown}"
    
    print(f"Is In Drawdown: {res.is_in_drawdown} (Expected True)")
    assert res.is_in_drawdown is True
    
    # Check periods
    print(f"Number of Drawdown Periods: {len(res.drawdown_periods)} (Expected 2)")
    assert len(res.drawdown_periods) == 2
    
    first_dd = res.drawdown_periods[0]
    print(f"First DD Depth: ${first_dd.max_depth} (Expected ~$120.00)")
    assert abs(first_dd.max_depth - Decimal("120.00")) < Decimal("0.01")
    
    print(f"First DD Recovered: {first_dd.recovery_date is not None} (Expected True)")
    assert first_dd.recovery_date is not None
    
    second_dd = res.drawdown_periods[1]
    print(f"Second DD Depth: ${second_dd.max_depth} (Expected ~$300.00)")
    assert abs(second_dd.max_depth - Decimal("300.00")) < Decimal("0.01")
    
    print(f"Second DD Recovered: {second_dd.recovery_date is not None} (Expected False)")
    assert second_dd.recovery_date is None

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    main()