# Cryptocurrency Signal Generation Bot

A production-ready Python application that fetches live cryptocurrency data, performs technical and fundamental analysis, and generates trade signals via AI/ML models. Signals are alerted to Discord but **do not execute trades**. Built for educational and informational purposes only – always do your own research before trading.

## Features
- **Live Data Fetching**: Integrates with XT, Bitget, and Gate.io via `ccxt` for OHLCV data. Scrapes Twitter and news for sentiment analysis.
- **Technical Analysis**: Calculates indicators like EMA, RSI, MACD, Ichimoku, Bollinger Bands, and more using `pandas-ta`.
- **AI/ML Integration**: Uses LSTM/GRU models (TensorFlow) for price prediction and HuggingFace Transformers for sentiment scoring. Includes fallback heuristics.
- **Signal Generation**: Consensus-based signals across 1H, 4H, and 1D timeframes, classified as Scalping, Day Trading, or Swing Trading.
- **Risk Management**: Calculates entry, stop-loss (SL), and take-profit (TP) levels. Tracks active signals and monitors for hits.
- **Discord Alerts**: Sends rich embed notifications for new signals and updates (TP/SL hits).
- **Persistence**: Uses SQLite to store and track active signals.
- **Modular Design**: Clean, well-commented code split into modules for easy maintenance.

## Tech Stack
- **Language**: Python 3.9+
- **Libraries**: `ccxt`, `pandas`, `pandas-ta`, `numpy`, `tensorflow`, `transformers`, `discord.py`, `tweepy`, `snscrape`, `newsapi-python`, `vaderSentiment`
- **Database**: SQLite
- **APIs**: XT, Bitget, Gate.io, NewsAPI, Twitter (via scraping)

## Installation & Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/crypto-signal-bot.git
   cd crypto-signal-bot
