import os
import logging
import pandas as pd
import time
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from database_manager import DatabaseManager

# Configuration
TRADING_PAIRS = ["BTC/USDT", "SOL/USDT", "BNB/USDT", "ETH/USDT", "LINK/USDT", "XRP/USDT", "DOGE/USDT", "SUI/USDT", "ADA/USDT"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = {
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'HF_TOKEN': os.getenv('HF_TOKEN'),
        'DB_PATH': os.getenv('DB_PATH', 'signals.db')
    }

    try:
        collector = DataCollector(config)
        analyzer = TechnicalAnalysis()
        ai_bot = AIRegimeDetector()
        db = DatabaseManager(config['DB_PATH'])

        logging.info(f"🚀 Starting Bot Cycle for {len(TRADING_PAIRS)} pairs...")
        
        results_summary = []

        for symbol in TRADING_PAIRS:
            try:
                logging.info(f"🔍 Analyzing {symbol}...")
                
                # 1. Fetch Data
                ohlcv = collector.fetch_data(symbol)
                if not ohlcv:
                    logging.warning(f"⚠️ No data for {symbol}, skipping.")
                    continue

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # 2. Indicators & AI
                df = analyzer.calculate_indicators(df)
                regime = ai_bot.detect_regime(df)
                
                current_price = df['close'].iloc[-1]
                rsi_val = df['rsi'].iloc[-1] if 'rsi' in df.columns else 0
                ema_val = df['ema_20'].iloc[-1] if 'ema_20' in df.columns else 0

                # 3. Save to SQLite
                db.save_signal(symbol, current_price, regime, rsi_val, ema_val)
                
                # 4. Collect for summary
                results_summary.append(f"{symbol}: **{regime}** (${current_price:.2f})")
                
                # Small delay to respect API rate limits
                time.sleep(0.5)

            except Exception as e:
                logging.error(f"❌ Error processing {symbol}: {e}")

        # 5. Send one batch update to Discord
        if results_summary:
            report = "📊 **Hourly Market Scan**\n" + "\n".join(results_summary)
            collector._send_discord_alert(report)

        logging.info("✅ Full Market Scan Completed.")

    except Exception as e:
        logging.error(f"❌ Critical Main Loop Failure: {e}")

if __name__ == "__main__":
    main()
