# kite_client.py
from kiteconnect import KiteConnect
from .config import Config
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
        """Get historical data for a symbol.
        In MOCK_TRADING mode (default) or when API credentials are missing, this
        function generates synthetic candlestick data so that the rest of the
        system—strategy logic, risk management, etc.—can run without requiring
        real market data. The synthetic data is NOT suitable for making live
        trading decisions but is sufficient for demonstration / development.
        """
        # If we're in mock mode, quickly return dummy candles
        if Config.MOCK_TRADING:
            from datetime import datetime, timedelta
            import random

            now = datetime.now()
            candles = []
            price = random.uniform(100, 500)  # base price
            for i in range(days * 24 * 12):  # days * hours/day * 12 five-min bars
                dt = now - timedelta(minutes=5 * i)
                # Simple random walk for price
                price += random.uniform(-1, 1)
                o = price + random.uniform(-0.5, 0.5)
                c = price + random.uniform(-0.5, 0.5)
                h = max(o, c) + random.uniform(0, 0.3)
                l = min(o, c) - random.uniform(0, 0.3)
                candles.append({
                    'date': dt,
                    'open': round(o, 2),
                    'high': round(h, 2),
                    'low': round(l, 2),
                    'close': round(c, 2),
                    'volume': random.randint(1000, 10000)
                })
            return list(reversed(candles))

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