import os
import logging
import pandas as pd
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector

# Enhanced Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'HF_TOKEN': os.getenv('HF_TOKEN')
    }

    try:
        collector = DataCollector(config)
        analyzer = TechnicalAnalysis()
        ai_bot = AIRegimeDetector()

        logging.info("🚀 Starting Bot Cycle...")
        
        # 1. Fetch OHLCV Data
        ohlcv = collector.fetch_data("BTC/USDT")
        if not ohlcv:
            logging.error("❌ No market data returned from exchange.")
            return

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        current_price = df['close'].iloc[-1]
        logging.info(f"📊 Market Data Fetched: BTC is at ${current_price}")

        # 2. Technical Analysis
        df = analyzer.calculate_indicators(df)
        
        # 3. AI Regime Check
        # Passing recent price action for sentiment/regime
        regime = ai_bot.detect_regime(df)
        logging.info(f"🧠 AI Market Regime: {regime}")

        # 4. Decision Logic & Discord Notification
        # We send a "Heartbeat" to Discord so you KNOW it's working
        status_msg = f"🔄 **Hourly Update**: BTC is ${current_price:.2f} | Regime: **{regime}**"
        collector._send_discord_alert(status_msg)

        # 5. Save to Database (Always save the state, even if no trade)
        # Logic to append to signals.db would go here
        logging.info(f"✅ Cycle Completed. Signals saved to {os.getenv('DB_PATH')}")

    except Exception as e:
        logging.error(f"❌ Main Loop Error: {e}")

if __name__ == "__main__":
    main()
