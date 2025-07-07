#!/usr/bin/env python3
"""
Test script to verify mock trading market hours behavior
"""
import os
import sys
from datetime import datetime, time as dt_time

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system.config import Config
from trading_system.main import TradingSystem

def test_market_hours():
    """Test market hours logic with mock trading on/off"""
    
    print("=" * 60)
    print("TESTING MARKET HOURS LOGIC")
    print("=" * 60)
    
    # Create trading system instance
    trading_system = TradingSystem()
    
    # Get current time info
    now = datetime.now().time()
    market_open = dt_time(Config.MARKET_OPEN_HOUR, Config.MARKET_OPEN_MINUTE)
    market_close = dt_time(Config.MARKET_CLOSE_HOUR, Config.MARKET_CLOSE_MINUTE)
    
    is_actually_market_hours = market_open <= now <= market_close
    
    print(f"Current time: {now}")
    print(f"Market hours: {market_open} - {market_close}")
    print(f"Currently in actual market hours: {is_actually_market_hours}")
    print(f"Mock trading enabled: {Config.MOCK_TRADING}")
    print()
    
    # Test current configuration
    is_market_open = trading_system.is_market_open()
    print(f"is_market_open() returns: {is_market_open}")
    
    if Config.MOCK_TRADING:
        if is_market_open:
            print("✅ SUCCESS: Mock trading mode correctly considers market as open")
        else:
            print("❌ ERROR: Mock trading mode should consider market as always open")
    else:
        if is_market_open == is_actually_market_hours:
            print("✅ SUCCESS: Live trading mode correctly follows actual market hours")
        else:
            print("❌ ERROR: Live trading mode not following actual market hours")
    
    print()
    print("Testing scan_and_trade method behavior:")
    print("-" * 40)
    
    # Test scan_and_trade method (this will log the appropriate messages)
    trading_system.scan_and_trade()
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    test_market_hours() 