#!/usr/bin/env python3
"""
Startup script for the trading system that properly initializes logging first
"""
import logging
import os
from trading_system.config import Config
from trading_system.main import TradingSystem

def setup_initial_logging():
    """Setup initial logging before starting the system"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=" * 50)
    logging.info("TRADING SYSTEM STARTUP")
    logging.info("=" * 50)
    logging.info(f"Scan Interval: {Config.SCAN_INTERVAL_MINUTES} minutes")
    logging.info(f"Mock Trading: {Config.MOCK_TRADING}")
    logging.info(f"Market Open Hour: {Config.MARKET_OPEN_HOUR}")
    logging.info(f"Capital: ${Config.CAPITAL:,.2f}")
    logging.info(f"Max Positions: {Config.MAX_POSITIONS}")
    logging.info("-" * 50)

def main():
    """Main startup function"""
    try:
        # Setup logging first
        setup_initial_logging()
        
        # Initialize and start the trading system
        logging.info("Creating TradingSystem instance...")
        trading_system = TradingSystem()
        
        logging.info("Starting trading system...")
        trading_system.start()
        
    except KeyboardInterrupt:
        logging.info("Shutdown requested by user")
    except Exception as e:
        logging.error(f"Fatal error during startup: {e}")
        raise

if __name__ == "__main__":
    main() 