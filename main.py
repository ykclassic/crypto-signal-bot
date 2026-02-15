import os
import logging
import pandas as pd
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from database_manager import DatabaseManager  # Import your new file

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
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

        logging.info("🚀 Starting Bot Cycle...")
        
        # 1. Fetch Data
        ohlcv = collector.fetch_data("BTC/USDT")
        if not ohlcv:
            return

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # 2. Analyze
        df = analyzer.calculate_indicators(df)
        regime = ai_bot.detect_regime(df)
        
        # Get latest values for DB
        current_price = df['close'].iloc[-1]
        rsi_val = df['rsi'].iloc[-1] if 'rsi' in df.columns else 0
        ema_val = df['ema_20'].iloc[-1] if 'ema_20' in df.columns else 0

        # 3. Save to SQLite
        db.save_signal("BTC/USDT", current_price, regime, rsi_val, ema_val)
        logging.info(f"💾 Signal saved: {regime} at ${current_price}")

        # 4. Discord Alert
        status_msg = f"✅ **Cycle Complete**: BTC at ${current_price:.2f} | Regime: {regime}"
        collector._send_discord_alert(status_msg)

    except Exception as e:
        logging.error(f"❌ Main Loop Error: {e}")

if __name__ == "__main__":
    main()
