# risk_manager.py
from .config import Config
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