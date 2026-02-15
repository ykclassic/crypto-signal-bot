import os
import logging
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Load Environment Variables
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
        # Initialize Components
        collector = DataCollector(config)
        analyzer = TechnicalAnalysis()
        ai_bot = AIRegimeDetector()

        logging.info("🚀 Starting Bot Cycle...")
        
        # 1. Collect Data
        raw_data = collector.fetch_data("BTC/USDT")
        
        # ... Rest of your trading logic ...
        logging.info("✅ Cycle Completed Successfully.")

    except Exception as e:
        logging.error(f"❌ Main Loop Error: {e}")

if __name__ == "__main__":
    main()
