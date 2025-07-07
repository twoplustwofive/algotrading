# telegram_bot.py
import requests
from .config import Config
import logging
from datetime import datetime

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
            response = requests.post(url, data=data, timeout=10)
            
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