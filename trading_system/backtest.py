# backtest.py
import pandas as pd
from .strategy import EMAStrategy
from .kite_client import ZerodhaClient


def simple_backtest(symbol, days=30):
    """Simple backtest implementation"""
    kite = ZerodhaClient()
    strategy = EMAStrategy()
    
    # Get historical data
    data = kite.get_historical_data(symbol, days=days)
    
    if not data:
        return None
    
    trades = []
    
    for i in range(len(data) - 1):
        current_data = data[:i+1]
        signal = strategy.generate_signal(symbol, current_data)
        
        if signal:
            trades.append({
                'timestamp': data[i]['date'],
                'action': signal['action'],
                'price': signal['price'],
                'reason': signal['reason']
            })
    
    return trades


# Run backtest
if __name__ == "__main__":
    trades = simple_backtest('RELIANCE', days=30)
    if trades is not None:
        print(f"Total trades: {len(trades)}")
        for trade in trades:
            print(trade)
    else:
        print("No trades generated - check data source") 