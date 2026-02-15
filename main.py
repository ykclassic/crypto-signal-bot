import logging
import os
import sys
import time
from datetime import datetime

from config import *
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from signal_logic import SignalLogic
from risk_management import RiskManagement
from discord_alert import DiscordAlerter
from database import SignalDatabase

# Better logging configuration
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution loop with robust error handling"""
    
    logger.info("=" * 60)
    logger.info("Trading System Starting...")
    logger.info("=" * 60)
    
    # Setup components
    try:
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
        
        logger.info("All components initialized successfully")
        
    except Exception as e:
        logger.critical(f"Failed to initialize components: {e}", exc_info=True)
        return
    
    current_prices = {}
    signals_generated = 0
    tickers_processed = 0
    
    try:
        for ticker in TICKERS:
            try:
                logger.info(f"Processing {ticker}...")
                
                # 1. Data Collection & Indicators
                dfs = {}
                valid_data = True
                
                for tf in TIMEFRAMES:
                    raw_data = collector.fetch_ohlcv(ticker, tf)
                    
                    # Check if data was fetched
                    if raw_data is None or raw_data.empty:
                        logger.error(f"No data returned for {ticker} {tf}")
                        valid_data = False
                        break
                    
                    # Calculate indicators
                    df_with_indicators = ta_engine.calculate_indicators(raw_data)
                    
                    # CRITICAL: Check if indicators were calculated
                    if df_with_indicators is None or df_with_indicators.empty:
                        logger.error(f"Indicator calculation failed for {ticker} {tf}")
                        valid_data = False
                        break
                    
                    dfs[tf] = df_with_indicators
                
                if not valid_data:
                    logger.warning(f"Skipping {ticker} due to missing/invalid data")
                    continue
                
                # 2. Validate we have the required timeframe
                if '1h' not in dfs:
                    logger.error(f"Missing 1h data for {ticker}")
                    continue
                
                # 3. Validate close column exists
                if 'close' not in dfs['1h'].columns:
                    logger.error(f"Missing 'close' column in 1h data for {ticker}")
                    continue
                
                # 4. Get current close price
                try:
                    current_close = float(dfs['1h']['close'].iloc[-1])
                    
                    # Validate price is reasonable
                    if current_close <= 0 or pd.isna(current_close):
                        logger.error(f"Invalid price for {ticker}: {current_close}")
                        continue
                    
                    current_prices[ticker] = current_close
                    logger.info(f"{ticker} current price: ${current_close:.2f}")
                    
                except (IndexError, KeyError, ValueError) as e:
                    logger.error(f"Error extracting price for {ticker}: {e}")
                    continue
                
                # 5. Contextual Analysis
                sentiment = collector.fetch_sentiment_data(ticker)
                regime = ai_detector.detect_regime(dfs['1h'])
                
                logger.info(f"{ticker}: Regime={regime}, Sentiment={sentiment:.2f}")
                
                # 6. Signal Generation
                signal = logic.generate_signal(ticker, dfs, regime, sentiment)
                
                if signal:
                    try:
                        sl, tp = risk.calculate_sl_tp(dfs['1h'], signal['side'], current_close)
                        
                        # Validate SL/TP
                        if signal['side'] == 'BUY':
                            if sl >= current_close or tp <= current_close:
                                logger.error(f"Invalid SL/TP for {ticker} BUY")
                                continue
                        else:
                            if sl <= current_close or tp >= current_close:
                                logger.error(f"Invalid SL/TP for {ticker} SELL")
                                continue
                        
                        db.add_signal(ticker, signal['side'], current_close, sl, tp)
                        alerter.send_new_signal(signal, current_close, sl, tp)
                        
                        signals_generated += 1
                        logger.info(f"✓ Signal generated: {ticker} {signal['side']} @ ${current_close:.2f}")
                        
                    except Exception as e:
                        logger.error(f"Error processing signal for {ticker}: {e}", exc_info=True)
                else:
                    logger.info(f"No signal for {ticker}")
                
                tickers_processed += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}", exc_info=True)
                continue
        
        # 7. Monitor Active Trades
        if current_prices:
            try:
                update = risk.check_active_signals(db, current_prices)
                if update:
                    alerter.send_update(update)
                    logger.info(f"Trade update: {update}")
            except Exception as e:
                logger.error(f"Error monitoring trades: {e}", exc_info=True)
        
        # 8. Summary
        logger.info("=" * 60)
        logger.info(f"Execution Summary:")
        logger.info(f"  Tickers processed: {tickers_processed}/{len(TICKERS)}")
        logger.info(f"  Signals generated: {signals_generated}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        
    except Exception as e:
        logger.critical(f"Unexpected error in main loop: {e}", exc_info=True)
        
    finally:
        # Cleanup
        try:
            db.close()
            logger.info("Database connection closed")
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
