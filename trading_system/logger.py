# logger.py
import logging
import os
import csv
from datetime import datetime
from .config import Config

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
        os.makedirs('logs', exist_ok=True)
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