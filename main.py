import logging
import os
import sys
from config import *
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from signal_logic import SignalLogic
from risk_management import RiskManagement
from discord_alert import DiscordAlerter
from database import SignalDatabase

# Configure logging to output to both console and the file expected by the workflow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    # 1. Initialize Components
    # We pass the full config to remain compatible with your existing setup
    collector = DataCollector({
        'EXCHANGE_API_KEYS': EXCHANGE_API_KEYS,
        'NEWS_API_KEY': NEWS_API_KEY,
        'TWITTER_BEARER_TOKEN': TWITTER_BEARER_TOKEN
    })
    
    ta_engine = TechnicalAnalysis()
    ai_detector = AIRegimeDetector()
    logic = SignalLogic()
    risk = RiskManagement()
    alerter = DiscordAlerter(os.getenv('DISCORD_WEBHOOK_URL'))
    db = SignalDatabase(os.getenv('DB_PATH', './signals.db'))

    current_prices = {}

    for ticker in TICKERS:
        try:
            logging.info(f"--- Processing {ticker} ---")
            
            # 2. Data Collection with Safety Check
            dfs = {}
            data_error = False
            for tf in TIMEFRAMES:
                raw_data = collector.fetch_ohlcv(ticker, tf)
                if raw_data is None or raw_data.empty:
                    logging.warning(f"No data returned for {ticker} on {tf}. Skipping.")
                    data_error = True
                    break
                # Ensure we use the 2026 classic TA fork
                dfs[tf] = ta_engine.calculate_indicators(raw_data)
            
            if data_error: continue

            # 3. Contextual Analysis
            sentiment = collector.fetch_sentiment_data(ticker)
            regime = ai_detector.detect_regime(dfs['1h'])
            
            current_close = dfs['1h']['close'].iloc[-1]
            current_prices[ticker] = current_close

            # 4. Signal Generation & Risk Management
            signal = logic.generate_signal(ticker, dfs, regime, sentiment)
            
            if signal:
                sl, tp = risk.calculate_sl_tp(dfs['1h'], signal['side'], current_close)
                db.add_signal(ticker, signal['side'], current_close, sl, tp)
                alerter.send_new_signal(signal, current_close, sl, tp)
                logging.info(f"✅ SIGNAL GENERATED: {ticker} {signal['side']}")

            # 5. Continuous Monitoring
            update = risk.check_active_signals(db, current_prices)
            if update:
                alerter.send_update(update)
                logging.info(f"📢 UPDATE: {update}")

        except Exception as e:
            logging.error(f"❌ Critical failure on {ticker}: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
