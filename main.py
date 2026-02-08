import time
import logging
from config import *
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from signal_logic import SignalLogic
from risk_management import RiskManagement
from discord_alert import DiscordAlerter
from database import SignalDatabase

logging.basicConfig(level=LOG_LEVEL)

def main():
    # Override config with env vars if set (for GitHub Actions)
    import os
    if 'EXCHANGE_API_KEYS_XT_APIKEY' in os.environ:
        EXCHANGE_API_KEYS['xt']['apiKey'] = os.environ['EXCHANGE_API_KEYS_XT_APIKEY']
        EXCHANGE_API_KEYS['xt']['secret'] = os.environ['EXCHANGE_API_KEYS_XT_SECRET']
        EXCHANGE_API_KEYS['bitget']['apiKey'] = os.environ['EXCHANGE_API_KEYS_BITGET_APIKEY']
        EXCHANGE_API_KEYS['bitget']['secret'] = os.environ['EXCHANGE_API_KEYS_BITGET_SECRET']
        EXCHANGE_API_KEYS['gateio']['apiKey'] = os.environ['EXCHANGE_API_KEYS_GATEIO_APIKEY']
        EXCHANGE_API_KEYS['gateio']['secret'] = os.environ['EXCHANGE_API_KEYS_GATEIO_SECRET']
        NEWS_API_KEY = os.environ['NEWS_API_KEY']
        DISCORD_WEBHOOK_URL = os.environ['DISCORD_WEBHOOK_URL']
        TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']

    collector = DataCollector({'EXCHANGE_API_KEYS': EXCHANGE_API_KEYS, 'NEWS_API_KEY': NEWS_API_KEY})
    ta = TechnicalAnalysis()
    ai = AIRegimeDetector()
    signal_logic = SignalLogic()
    risk = RiskManagement()
    alerter = DiscordAlerter(DISCORD_WEBHOOK_URL)
    db = SignalDatabase(DB_PATH)

    # Run one cycle (instead of while True loop)
    current_prices = {}
    for ticker in TICKERS:
        try:
            # Fetch data
            dfs = {tf: ta.calculate_indicators(collector.fetch_ohlcv(ticker, tf)) for tf in TIMEFRAMES}
            sentiment = collector.fetch_sentiment_data(ticker)
            regime = ai.detect_regime(dfs['1h'])
            
            # Generate signal
            signal = signal_logic.generate_signal(ticker, dfs, regime, sentiment)
            if signal:
                entry = dfs['1h']['close'].iloc[-1]
                sl, tp = risk.calculate_sl_tp(dfs['1h'], signal['side'], entry)
                db.add_signal(ticker, signal['side'], entry, sl, tp)
                alerter.send_new_signal(signal, entry, sl, tp)
            
            current_prices[ticker] = dfs['1h']['close'].iloc[-1]
            
            # Check active signals
            update = risk.check_active_signals(db, current_prices)
            if update:
                alerter.send_update(update)
                
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")

if __name__ == "__main__":
    main()
