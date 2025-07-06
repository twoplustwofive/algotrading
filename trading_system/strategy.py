# strategy.py
import pandas as pd
from .config import Config
import logging

class EMAStrategy:
    def __init__(self):
        self.fast_ema_period = Config.FAST_EMA_PERIOD
        self.slow_ema_period = Config.SLOW_EMA_PERIOD
        self.positions = {}  # Track open positions
        
    def calculate_emas(self, data):
        """Calculate EMA indicators"""
        if len(data) < self.slow_ema_period:
            return None, None
        
        closes = [candle['close'] for candle in data]
        closes_array = pd.Series(closes).values
        
        fast_ema = pd.Series(closes_array).ewm(span=self.fast_ema_period, adjust=False).mean().values
        slow_ema = pd.Series(closes_array).ewm(span=self.slow_ema_period, adjust=False).mean().values
        
        return fast_ema, slow_ema
    
    def generate_signal(self, symbol, data):
        """Generate trading signal based on EMA crossover"""
        try:
            fast_ema, slow_ema = self.calculate_emas(data)
            
            if fast_ema is None or slow_ema is None:
                return None
            
            # Check if we have enough data
            if len(fast_ema) < 2 or len(slow_ema) < 2:
                return None
            
            # Current and previous EMA values
            current_fast = fast_ema[-1]
            current_slow = slow_ema[-1]
            prev_fast = fast_ema[-2]
            prev_slow = slow_ema[-2]
            
            current_price = data[-1]['close']
            
            # Check for crossover
            signal = None
            
            # Bullish crossover: Fast EMA crosses above Slow EMA
            if prev_fast <= prev_slow and current_fast > current_slow:
                if symbol not in self.positions:
                    signal = {
                        'action': 'BUY',
                        'symbol': symbol,
                        'price': current_price,
                        'fast_ema': current_fast,
                        'slow_ema': current_slow,
                        'reason': 'EMA Bullish Crossover'
                    }
            
            # Bearish crossover: Fast EMA crosses below Slow EMA
            elif prev_fast >= prev_slow and current_fast < current_slow:
                if symbol in self.positions:
                    signal = {
                        'action': 'SELL',
                        'symbol': symbol,
                        'price': current_price,
                        'fast_ema': current_fast,
                        'slow_ema': current_slow,
                        'reason': 'EMA Bearish Crossover'
                    }
            
            return signal
            
        except Exception as e:
            logging.error(f"Failed to generate signal for {symbol}: {e}")
            return None
    
    def should_exit_position(self, symbol, current_price):
        """Check if we should exit current position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        
        # Calculate stop loss and take profit levels
        if position['action'] == 'BUY':
            stop_loss = entry_price * (1 - Config.STOP_LOSS_PCT)
            take_profit = entry_price * (1 + Config.TAKE_PROFIT_PCT)
            
            if current_price <= stop_loss:
                return {
                    'action': 'SELL',
                    'symbol': symbol,
                    'price': current_price,
                    'reason': 'Stop Loss'
                }
            elif current_price >= take_profit:
                return {
                    'action': 'SELL',
                    'symbol': symbol,
                    'price': current_price,
                    'reason': 'Take Profit'
                }
        
        return None
    
    def add_position(self, symbol, action, price, quantity):
        """Add a new position"""
        self.positions[symbol] = {
            'action': action,
            'entry_price': price,
            'quantity': quantity,
            'timestamp': pd.Timestamp.now()
        }
    
    def remove_position(self, symbol):
        """Remove a position"""
        if symbol in self.positions:
            del self.positions[symbol] 