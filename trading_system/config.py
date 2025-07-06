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