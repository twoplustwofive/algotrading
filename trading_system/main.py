# main.py
import time
import schedule
from datetime import datetime, time as dt_time
import logging
from .kite_client import ZerodhaClient
from .strategy import EMAStrategy
from .risk_manager import RiskManager
from .logger import TradingLogger
from .telegram_bot import TelegramBot
from .config import Config

class TradingSystem:
    def __init__(self):
        logging.info("Initializing TradingSystem...")
        
        logging.info("Initializing ZerodhaClient...")
        start_time = time.time()
        self.kite = ZerodhaClient()
        logging.info(f"ZerodhaClient initialized in {time.time() - start_time:.2f} seconds.")
        
        logging.info("Initializing EMAStrategy...")
        start_time = time.time()
        self.strategy = EMAStrategy()
        logging.info(f"EMAStrategy initialized in {time.time() - start_time:.2f} seconds.")
        
        logging.info("Initializing RiskManager...")
        start_time = time.time()
        self.risk_manager = RiskManager()
        logging.info(f"RiskManager initialized in {time.time() - start_time:.2f} seconds.")
        
        logging.info("Initializing TradingLogger...")
        start_time = time.time()
        self.logger = TradingLogger()
        logging.info(f"TradingLogger initialized in {time.time() - start_time:.2f} seconds.")
        
        logging.info("Initializing TelegramBot...")
        start_time = time.time()
        self.telegram = TelegramBot()
        logging.info(f"TelegramBot initialized in {time.time() - start_time:.2f} seconds.")
        
        self.running = False
        logging.info("TradingSystem initialization complete.")
        
    def is_market_open(self):
        """Check if market is open"""
        # In mock trading mode, always consider market as open
        if Config.MOCK_TRADING:
            logging.debug("Mock trading enabled - market considered open")
            return True
        
        # For live trading, check actual market hours
        now = datetime.now().time()
        open_time_hour = Config.MARKET_OPEN_HOUR
        open_time_minute = Config.MARKET_OPEN_MINUTE
        close_time_hour = Config.MARKET_CLOSE_HOUR
        close_time_minute = Config.MARKET_CLOSE_MINUTE
        market_open = dt_time(open_time_hour, open_time_minute)  # 9:15 AM
        market_close = dt_time(close_time_hour, close_time_minute)  # 3:30 PM
        
        return market_open <= now <= market_close
    
    def scan_and_trade(self):
        """Main trading logic"""
        if not self.is_market_open():
            if Config.MOCK_TRADING:
                logging.info("Market is closed - but mock trading would continue if market hours were extended")
            else:
                logging.info("Market is closed")
            return
        
        # Log trading mode context
        if Config.MOCK_TRADING:
            now = datetime.now().time()
            market_open = dt_time(Config.MARKET_OPEN_HOUR, Config.MARKET_OPEN_MINUTE)
            market_close = dt_time(Config.MARKET_CLOSE_HOUR, Config.MARKET_CLOSE_MINUTE)
            
            if market_open <= now <= market_close:
                logging.info("Scanning watchlist for opportunities... [MOCK TRADING - Normal Market Hours]")
            else:
                logging.info("Scanning watchlist for opportunities... [MOCK TRADING - Outside Market Hours]")
        else:
            logging.info("Scanning watchlist for opportunities... [LIVE TRADING]")
        
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
        
        for symbol, position in list(self.strategy.positions.items()):
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
        
        # Schedule trading scans based on configured interval
        logging.info(f"Scheduling trading scans every {Config.SCAN_INTERVAL_MINUTES} minutes...")
        start_time = time.time()
        schedule.every(Config.SCAN_INTERVAL_MINUTES).minutes.do(self.scan_and_trade)
        logging.info(f"Trading scans scheduled in {time.time() - start_time:.2f} seconds.")
        
        # Schedule force exit at 3:15 PM
        logging.info("Scheduling force exit...")
        start_time = time.time()
        schedule.every().day.at("15:15").do(self.force_exit_all_positions)
        logging.info(f"Force exit scheduled in {time.time() - start_time:.2f} seconds.")
        
        # Send startup message
        logging.info("Sending startup message...")
        start_time = time.time()
        self.telegram.send_message("🚀 Trading System Started")
        logging.info(f"Startup message sent in {time.time() - start_time:.2f} seconds.")
        
        self.running = True
        logging.info("Trading system started. Entering main loop...")
        
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