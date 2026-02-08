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
    config = globals()  # Load from config.py
    collector = DataCollector(config)
    ta = TechnicalAnalysis()
    ai = AIRegimeDetector()
    signal_logic = SignalLogic()
    risk = RiskManagement()
    alerter = DiscordAlerter(config['DISCORD_WEBHOOK_URL'])
    db = SignalDatabase(config['DB_PATH'])

    while True:
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
        
        time.sleep(3600)  # Wait 1 hour

if __name__ == "__main__":
    main()
