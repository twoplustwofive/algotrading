# Minimal Agentic Intraday Trading System - Complete Implementation

## 1. Tech Stack

**Core Technologies:**
- **Language**: Python 3.8+
- **Libraries**: 
  - `kiteconnect` (Zerodha API)
  - `pandas` (Data manipulation)
  - `ta-lib` (Technical indicators)
  - `requests` (HTTP requests)
  - `python-dotenv` (Environment variables)
  - `schedule` (Task scheduling)
- **Scheduling**: Python `schedule` library with continuous loop
- **Data Storage**: Simple CSV files for logging
- **Deployment**: Single Python script running locally

## 2. Strategy: 5-Minute EMA Crossover

**Strategy Details:**
- **Timeframe**: 5-minute candles
- **Indicators**: 
  - Fast EMA: 9 periods
  - Slow EMA: 21 periods
- **Entry Rules**:
  - Buy when Fast EMA crosses above Slow EMA
  - Sell when Fast EMA crosses below Slow EMA
- **Exit Rules**:
  - Stop Loss: 1% from entry price
  - Take Profit: 2% from entry price
  - Force exit at 3:15 PM (before market close)

**Why This Strategy:**
- Simple to implement and understand
- Works well in trending markets
- Clear entry/exit signals
- Suitable for intraday trading

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING SYSTEM FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   FETCH     │    │   ANALYZE   │    │   EXECUTE   │     │
│  │   DATA      │───▶│   SIGNALS   │───▶│   TRADES    │     │
│  │             │    │             │    │             │     │
│  │• Live OHLC  │    │• Calculate  │    │• Place      │     │
│  │• 5min bars  │    │  EMAs       │    │  Orders     │     │
│  │• Watchlist  │    │• Check      │    │• Manage     │     │
│  │             │    │  Crossover  │    │  Positions  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    LOG      │    │    RISK     │    │   ALERTS    │     │
│  │  TRADES     │    │ MANAGEMENT  │    │   SYSTEM    │     │
│  │             │    │             │    │             │     │
│  │• CSV File   │    │• Position   │    │• Console    │     │
│  │• Console    │    │  Sizing     │    │• Telegram   │     │
│  │• Performance│    │• Stop Loss  │    │• Errors     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 4. Complete Implementation

### 4.1 Project Structure
```
trading_system/
├── main.py                 # Main trading script
├── config.py              # Configuration and settings
├── kite_client.py         # Zerodha API wrapper
├── strategy.py            # EMA crossover strategy
├── risk_manager.py        # Risk management
├── logger.py              # Logging utilities
├── telegram_bot.py        # Telegram alerts (optional)
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
└── logs/                  # Log files directory
    ├── trades.csv
    └── system.log
```

### 4.2 Requirements File
```txt
# requirements.txt
kiteconnect==4.2.0
pandas==2.0.3
TA-Lib==0.4.25
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0
python-telegram-bot==20.5
```

### 4.3 Environment Configuration
```bash
# .env file
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_REQUEST_TOKEN=your_request_token_here
ZERODHA_ACCESS_TOKEN=your_access_token_here

# Optional: Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Trading Configuration
CAPITAL=50000
RISK_PER_TRADE=0.02
MAX_POSITIONS=3
MOCK_TRADING=True
```

### 4.4 Configuration Module
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Zerodha API Configuration
    ZERODHA_API_KEY = os.getenv('ZERODHA_API_KEY')
    ZERODHA_API_SECRET = os.getenv('ZERODHA_API_SECRET')
    ZERODHA_REQUEST_TOKEN = os.getenv('ZERODHA_REQUEST_TOKEN')
    ZERODHA_ACCESS_TOKEN = os.getenv('ZERODHA_ACCESS_TOKEN')
    
    # Trading Configuration
    CAPITAL = float(os.getenv('CAPITAL', 50000))
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', 0.02))
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 3))
    MOCK_TRADING = os.getenv('MOCK_TRADING', 'True').lower() == 'true'
    
    # Strategy Configuration
    FAST_EMA_PERIOD = 9
    SLOW_EMA_PERIOD = 21
    STOP_LOSS_PCT = 0.01
    TAKE_PROFIT_PCT = 0.02
    
    # Watchlist
    WATCHLIST = ['RELIANCE', 'TCS', 'HDFC', 'ICICIBANK', 'INFY']
    
    # Telegram (Optional)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/system.log'
    TRADES_FILE = 'logs/trades.csv'
```

### 4.5 Zerodha API Client
```python
# kite_client.py
from kiteconnect import KiteConnect
from config import Config
import logging

class ZerodhaClient:
    def __init__(self):
        self.kite = KiteConnect(api_key=Config.ZERODHA_API_KEY)
        self.setup_session()
        
    def setup_session(self):
        """Setup Kite session with access token"""
        try:
            if Config.ZERODHA_ACCESS_TOKEN:
                self.kite.set_access_token(Config.ZERODHA_ACCESS_TOKEN)
                logging.info("Kite session established with access token")
            else:
                # Generate session using request token
                data = self.kite.generate_session(
                    Config.ZERODHA_REQUEST_TOKEN, 
                    api_secret=Config.ZERODHA_API_SECRET
                )
                self.kite.set_access_token(data["access_token"])
                logging.info("New Kite session generated")
                print(f"Access Token: {data['access_token']}")
                print("Save this token to your .env file as ZERODHA_ACCESS_TOKEN")
        except Exception as e:
            logging.error(f"Failed to setup Kite session: {e}")
            raise
    
    def get_historical_data(self, symbol, interval="5minute", days=30):
        """Get historical data for a symbol"""
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = self.kite.historical_data(
                instrument_token=self.get_instrument_token(symbol),
                from_date=start_date,
                to_date=end_date,
                interval=interval
            )
            return data
        except Exception as e:
            logging.error(f"Failed to get historical data for {symbol}: {e}")
            return []
    
    def get_instrument_token(self, symbol):
        """Get instrument token for a symbol"""
        try:
            instruments = self.kite.instruments("NSE")
            for instrument in instruments:
                if instrument['tradingsymbol'] == symbol:
                    return instrument['instrument_token']
            return None
        except Exception as e:
            logging.error(f"Failed to get instrument token for {symbol}: {e}")
            return None
    
    def get_ltp(self, symbol):
        """Get last traded price"""
        try:
            instrument_token = self.get_instrument_token(symbol)
            if instrument_token:
                ltp_data = self.kite.ltp([instrument_token])
                return ltp_data[str(instrument_token)]['last_price']
            return None
        except Exception as e:
            logging.error(f"Failed to get LTP for {symbol}: {e}")
            return None
    
    def place_order(self, symbol, transaction_type, quantity, order_type="MIS", price=None):
        """Place an order"""
        try:
            if Config.MOCK_TRADING:
                logging.info(f"MOCK ORDER: {transaction_type} {quantity} {symbol} @ {price}")
                return f"MOCK_ORDER_{symbol}_{transaction_type}"
            
            order_params = {
                'variety': self.kite.VARIETY_REGULAR,
                'exchange': self.kite.EXCHANGE_NSE,
                'tradingsymbol': symbol,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'product': self.kite.PRODUCT_MIS,
                'order_type': self.kite.ORDER_TYPE_MARKET if not price else self.kite.ORDER_TYPE_LIMIT,
                'validity': self.kite.VALIDITY_DAY
            }
            
            if price:
                order_params['price'] = price
            
            order_id = self.kite.place_order(**order_params)
            logging.info(f"Order placed: {order_id}")
            return order_id
            
        except Exception as e:
            logging.error(f"Failed to place order: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            logging.error(f"Failed to get positions: {e}")
            return {'day': [], 'net': []}
    
    def get_orders(self):
        """Get order history"""
        try:
            return self.kite.orders()
        except Exception as e:
            logging.error(f"Failed to get orders: {e}")
            return []
```

### 4.6 EMA Crossover Strategy
```python
# strategy.py
import pandas as pd
import talib
from config import Config
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
        
        fast_ema = talib.EMA(closes_array, timeperiod=self.fast_ema_period)
        slow_ema = talib.EMA(closes_array, timeperiod=self.slow_ema_period)
        
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
```

### 4.7 Risk Management
```python
# risk_manager.py
from config import Config
import logging

class RiskManager:
    def __init__(self):
        self.capital = Config.CAPITAL
        self.risk_per_trade = Config.RISK_PER_TRADE
        self.max_positions = Config.MAX_POSITIONS
        self.daily_loss_limit = 0.05  # 5% daily loss limit
        self.daily_pnl = 0
        
    def calculate_position_size(self, symbol, entry_price, stop_loss_price):
        """Calculate position size based on risk management"""
        try:
            # Calculate risk amount
            risk_amount = self.capital * self.risk_per_trade
            
            # Calculate price difference
            price_diff = abs(entry_price - stop_loss_price)
            
            if price_diff == 0:
                return 0
            
            # Calculate quantity
            quantity = int(risk_amount / price_diff)
            
            # Ensure minimum quantity
            if quantity < 1:
                quantity = 1
            
            logging.info(f"Position size for {symbol}: {quantity} shares")
            return quantity
            
        except Exception as e:
            logging.error(f"Failed to calculate position size: {e}")
            return 0
    
    def can_take_position(self, current_positions_count):
        """Check if we can take a new position"""
        # Check position limit
        if current_positions_count >= self.max_positions:
            logging.warning("Maximum positions reached")
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -(self.capital * self.daily_loss_limit):
            logging.warning("Daily loss limit exceeded")
            return False
        
        return True
    
    def update_daily_pnl(self, pnl):
        """Update daily P&L"""
        self.daily_pnl += pnl
        logging.info(f"Daily P&L updated: {self.daily_pnl}")
```

### 4.8 Logging System
```python
# logger.py
import logging
import os
import csv
from datetime import datetime
from config import Config

class TradingLogger:
    def __init__(self):
        self.setup_logging()
        self.setup_trade_logging()
    
    def setup_logging(self):
        """Setup system logging"""
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def setup_trade_logging(self):
        """Setup trade logging CSV"""
        if not os.path.exists(Config.TRADES_FILE):
            with open(Config.TRADES_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'symbol', 'action', 'quantity', 
                    'price', 'reason', 'pnl', 'status'
                ])
    
    def log_trade(self, symbol, action, quantity, price, reason, pnl=0, status='EXECUTED'):
        """Log a trade to CSV"""
        try:
            with open(Config.TRADES_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(), symbol, action, quantity, 
                    price, reason, pnl, status
                ])
            
            logging.info(f"Trade logged: {action} {quantity} {symbol} @ {price} - {reason}")
            
        except Exception as e:
            logging.error(f"Failed to log trade: {e}")
```

### 4.9 Telegram Bot (Optional)
```python
# telegram_bot.py
import requests
from config import Config
import logging

class TelegramBot:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        
    def send_message(self, message):
        """Send message to Telegram"""
        if not self.enabled:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message
            }
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logging.info("Telegram message sent successfully")
            else:
                logging.error(f"Failed to send Telegram message: {response.text}")
                
        except Exception as e:
            logging.error(f"Telegram error: {e}")
    
    def send_trade_alert(self, symbol, action, quantity, price, reason):
        """Send trade alert"""
        message = f"🚨 TRADE ALERT\n\n"
        message += f"Symbol: {symbol}\n"
        message += f"Action: {action}\n"
        message += f"Quantity: {quantity}\n"
        message += f"Price: ₹{price:.2f}\n"
        message += f"Reason: {reason}\n"
        message += f"Time: {datetime.now().strftime('%H:%M:%S')}"
        
        self.send_message(message)
    
    def send_daily_report(self, total_trades, total_pnl):
        """Send daily performance report"""
        message = f"📊 DAILY REPORT\n\n"
        message += f"Total Trades: {total_trades}\n"
        message += f"Total P&L: ₹{total_pnl:.2f}\n"
        message += f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        
        self.send_message(message)
```

### 4.10 Main Trading Script
```python
# main.py
import time
import schedule
from datetime import datetime, time as dt_time
import logging
from kite_client import ZerodhaClient
from strategy import EMAStrategy
from risk_manager import RiskManager
from logger import TradingLogger
from telegram_bot import TelegramBot
from config import Config

class TradingSystem:
    def __init__(self):
        self.kite = ZerodhaClient()
        self.strategy = EMAStrategy()
        self.risk_manager = RiskManager()
        self.logger = TradingLogger()
        self.telegram = TelegramBot()
        self.running = False
        
    def is_market_open(self):
        """Check if market is open"""
        now = datetime.now().time()
        market_open = dt_time(9, 15)  # 9:15 AM
        market_close = dt_time(15, 30)  # 3:30 PM
        
        return market_open <= now <= market_close
    
    def scan_and_trade(self):
        """Main trading logic"""
        if not self.is_market_open():
            logging.info("Market is closed")
            return
        
        logging.info("Scanning watchlist for opportunities...")
        
        for symbol in Config.WATCHLIST:
            try:
                # Get historical data
                data = self.kite.get_historical_data(symbol, interval="5minute", days=5)
                
                if not data:
                    logging.warning(f"No data for {symbol}")
                    continue
                
                # Check for exit signals first
                current_price = data[-1]['close']
                exit_signal = self.strategy.should_exit_position(symbol, current_price)
                
                if exit_signal:
                    self.execute_trade(exit_signal)
                    continue
                
                # Generate entry signal
                signal = self.strategy.generate_signal(symbol, data)
                
                if signal:
                    # Check if we can take position
                    current_positions = len(self.strategy.positions)
                    if self.risk_manager.can_take_position(current_positions):
                        self.execute_trade(signal)
                    else:
                        logging.info(f"Cannot take position for {symbol} - risk limits")
                
            except Exception as e:
                logging.error(f"Error processing {symbol}: {e}")
    
    def execute_trade(self, signal):
        """Execute a trade based on signal"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            price = signal['price']
            
            # Calculate position size
            if action == 'BUY':
                stop_loss_price = price * (1 - Config.STOP_LOSS_PCT)
                quantity = self.risk_manager.calculate_position_size(symbol, price, stop_loss_price)
            else:
                # For sell orders, get quantity from existing position
                if symbol in self.strategy.positions:
                    quantity = self.strategy.positions[symbol]['quantity']
                else:
                    logging.warning(f"No position found for {symbol} to sell")
                    return
            
            if quantity <= 0:
                logging.warning(f"Invalid quantity for {symbol}")
                return
            
            # Place order
            order_id = self.kite.place_order(
                symbol=symbol,
                transaction_type=action,
                quantity=quantity
            )
            
            if order_id:
                # Update position tracking
                if action == 'BUY':
                    self.strategy.add_position(symbol, action, price, quantity)
                else:
                    self.strategy.remove_position(symbol)
                
                # Log trade
                self.logger.log_trade(
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    price=price,
                    reason=signal['reason']
                )
                
                # Send alert
                self.telegram.send_trade_alert(symbol, action, quantity, price, signal['reason'])
                
                logging.info(f"Trade executed: {action} {quantity} {symbol} @ {price}")
            
        except Exception as e:
            logging.error(f"Failed to execute trade: {e}")
    
    def force_exit_all_positions(self):
        """Force exit all positions before market close"""
        logging.info("Force exiting all positions...")
        
        for symbol, position in self.strategy.positions.items():
            try:
                current_price = self.kite.get_ltp(symbol)
                if current_price:
                    signal = {
                        'symbol': symbol,
                        'action': 'SELL',
                        'price': current_price,
                        'reason': 'Force Exit - Market Close'
                    }
                    self.execute_trade(signal)
            except Exception as e:
                logging.error(f"Failed to force exit {symbol}: {e}")
    
    def start(self):
        """Start the trading system"""
        logging.info("Starting trading system...")
        
        # Schedule trading scans every 5 minutes
        schedule.every(5).minutes.do(self.scan_and_trade)
        
        # Schedule force exit at 3:15 PM
        schedule.every().day.at("15:15").do(self.force_exit_all_positions)
        
        # Send startup message
        self.telegram.send_message("🚀 Trading System Started")
        
        self.running = True
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("Shutting down...")
                self.running = False
                break
            except Exception as e:
                logging.error(f"System error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    trading_system = TradingSystem()
    trading_system.start()
```

## 5. Setup Instructions

### 5.1 Installation
```bash
# Create project directory
mkdir trading_system
cd trading_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir logs
```

### 5.2 Zerodha API Setup
1. **Get API Key**: Login to Kite Connect developer console
2. **Create App**: Get API key and secret
3. **Generate Request Token**: Use login URL to get request token
4. **Get Access Token**: First run will generate access token

### 5.3 Configuration
```bash
# Create .env file
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

### 5.4 Running the System
```bash
# Run in mock mode first
python main.py

# For live trading, set MOCK_TRADING=False in .env
```

## 6. Testing/Simulation

### 6.1 Mock Mode
- Set `MOCK_TRADING=True` in .env
- System will log trades without placing real orders
- Perfect for testing strategy logic

### 6.2 Historical Backtesting (Optional)
```python
# backtest.py
import pandas as pd
from strategy import EMAStrategy
from kite_client import ZerodhaClient

def simple_backtest(symbol, days=30):
    """Simple backtest implementation"""
    kite = ZerodhaClient()
    strategy = EMAStrategy()
    
    # Get historical data
    data = kite.get_historical_data(symbol, days=days)
    
    if not data:
        return None
    
    trades = []
    capital = 50000
    
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
    print(f"Total trades: {len(trades)}")
    for trade in trades:
        print(trade)
```

## 7. Security Best Practices

### 7.1 API Key Management
```python
# Never hardcode API keys
# Use environment variables
# Rotate keys regularly
# Use read-only keys when possible

# .env file (never commit to version control)
ZERODHA_API_KEY=your_key_here
ZERODHA_API_SECRET=your_secret_here
```

### 7.2 File Permissions
```bash
# Secure .env file
chmod 600 .env

# Secure log files
chmod 600 logs/*
```

## 8. Monitoring and Debugging

### 8.1 Console Output
```bash
# Run with verbose logging
python main.py

# Monitor logs in real-time
tail -f logs/system.log
```

### 8.2 Trade Analysis
```python
# analyze_trades.py
import pandas as pd

def analyze_performance():
    """Analyze trading performance from CSV"""
    df = pd.read_csv('logs/trades.csv')
    
    # Calculate metrics
    total_trades = len(df)
    buy_trades = len(df[df['action'] == 'BUY'])
    sell_trades = len(df[df['action