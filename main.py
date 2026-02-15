import logging
import os
from config import *
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from signal_logic import SignalLogic
from risk_management import RiskManagement
from discord_alert import DiscordAlerter
from database import SignalDatabase

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Setup
    collector = DataCollector({
        'EXCHANGE_API_KEYS': EXCHANGE_API_KEYS,
        'NEWS_API_KEY': NEWS_API_KEY,
        'TWITTER_BEARER_TOKEN': TWITTER_BEARER_TOKEN
    })
    ta_engine = TechnicalAnalysis()
    ai_detector = AIRegimeDetector()
    logic = SignalLogic()
    risk = RiskManagement()
    alerter = DiscordAlerter(DISCORD_WEBHOOK_URL)
    db = SignalDatabase(DB_PATH)

    current_prices = {}

    for ticker in TICKERS:
        try:
            logging.info(f"Processing {ticker}...")
            
            # 1. Data Collection & Indicators
            dfs = {}
            for tf in TIMEFRAMES:
                raw_data = collector.fetch_ohlcv(ticker, tf)
                dfs[tf] = ta_engine.calculate_indicators(raw_data)
            
            # 2. Contextual Analysis
            sentiment = collector.fetch_sentiment_data(ticker)
            regime = ai_detector.detect_regime(dfs['1h'])
            current_close = dfs['1h']['close'].iloc[-1]
            current_prices[ticker] = current_close

            # 3. Signal Generation
            signal = logic.generate_signal(ticker, dfs, regime, sentiment)
            
            if signal:
                sl, tp = risk.calculate_sl_tp(dfs['1h'], signal['side'], current_close)
                db.add_signal(ticker, signal['side'], current_close, sl, tp)
                alerter.send_new_signal(signal, current_close, sl, tp)
                logging.info(f"Signal found for {ticker}: {signal['side']}")

            # 4. Monitoring Active Trades
            update = risk.check_active_signals(db, current_prices)
            if update:
                alerter.send_update(update)
                logging.info(update)

        except Exception as e:
            logging.error(f"Critical error on {ticker}: {e}", exc_info=True)

if __name__ == "__main__":
    main()
