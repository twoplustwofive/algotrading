# Minimal Agentic Intraday Trading System

A complete Python-based algorithmic trading system implementing EMA crossover strategy for intraday trading on Indian stock markets via Zerodha Kite Connect API.

## 🚀 Features

- **EMA Crossover Strategy**: 9-period and 21-period exponential moving averages
- **Risk Management**: Position sizing, stop-loss, take-profit, daily loss limits
- **Mock Trading Mode**: Test strategies without real money
- **Real-time Monitoring**: Live market data analysis every 5 minutes
- **Telegram Alerts**: Optional trade notifications
- **Comprehensive Logging**: CSV trade logs and system logs
- **Automatic Exit**: Force close positions before market close

## 📋 Strategy Details

- **Timeframe**: 5-minute candles
- **Entry Signal**: Fast EMA (9) crosses above Slow EMA (21) = BUY
- **Exit Signal**: Fast EMA (9) crosses below Slow EMA (21) = SELL
- **Stop Loss**: 1% from entry price
- **Take Profit**: 2% from entry price
- **Force Exit**: 3:15 PM before market close
- **Watchlist**: RELIANCE, TCS, HDFC, ICICIBANK, INFY

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Zerodha Kite Connect API account

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/algotrading.git
cd algotrading
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### Environment Variables (.env)
```bash
# Zerodha API Credentials
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=your_access_token_here

# Trading Configuration
CAPITAL=50000
RISK_PER_TRADE=0.02
MAX_POSITIONS=3
MOCK_TRADING=True

# Optional: Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 🚀 Usage

### Mock Trading (Recommended for testing)
```bash
# Set MOCK_TRADING=True in .env
python -m trading_system.main
```

### Backtest Strategy
```bash
python -m trading_system.backtest
```

### Live Trading (Real money - use with caution!)
```bash
# Set MOCK_TRADING=False in .env after thorough testing
python -m trading_system.main
```

## 📁 Project Structure

```
trading_system/
├── __init__.py           # Package initialization
├── main.py              # Main trading system orchestrator
├── config.py            # Configuration management
├── kite_client.py       # Zerodha API wrapper
├── strategy.py          # EMA crossover strategy
├── risk_manager.py      # Risk management logic
├── logger.py            # Logging utilities
├── telegram_bot.py      # Telegram notifications
└── backtest.py          # Backtesting module

requirements.txt         # Python dependencies
.env.example            # Environment variables template
.gitignore              # Git ignore rules
README.md               # This file
```

## 📊 Risk Management

- **Position Sizing**: 2% risk per trade
- **Maximum Positions**: 3 concurrent positions
- **Daily Loss Limit**: 5% of capital
- **Stop Loss**: 1% from entry
- **Take Profit**: 2% from entry

## 📈 Monitoring

### System Logs
```bash
tail -f logs/system.log
```

### Trade History
```bash
cat logs/trades.csv
```

## ⚠️ Important Disclaimers

1. **This is for educational purposes only**
2. **Past performance does not guarantee future results**
3. **Always test in mock mode first**
4. **Never risk more than you can afford to lose**
5. **Trading involves substantial risk of loss**

## 🔧 Configuration

### Strategy Parameters (config.py)
- `FAST_EMA_PERIOD = 9`
- `SLOW_EMA_PERIOD = 21`
- `STOP_LOSS_PCT = 0.01`
- `TAKE_PROFIT_PCT = 0.02`

### Watchlist
Default stocks: RELIANCE, TCS, HDFC, ICICIBANK, INFY
Modify `WATCHLIST` in `config.py` to change symbols.

## 🤖 Telegram Integration (Optional)

1. Create a bot via @BotFather on Telegram
2. Get your chat ID
3. Add credentials to .env file
4. Receive real-time trade alerts

## 🧪 Testing

The system includes synthetic data generation for testing without API access:
- Generates realistic OHLC data
- Allows strategy testing offline
- Perfect for development and debugging

## 📞 Support

For issues or questions:
1. Check the logs in `logs/system.log`
2. Verify your API credentials
3. Ensure market hours (9:15 AM - 3:30 PM IST)
4. Test in mock mode first

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Zerodha for providing the Kite Connect API
- TA-Lib for technical analysis functions
- Python trading community for inspiration

---

**Remember: Trading is risky. This system is for educational purposes. Always test thoroughly before using real money.** 