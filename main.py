import os
import logging
import pandas as pd
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': 'signals.db'
    }

    collector = DataCollector(config)
    analyzer = TechnicalAnalysis()
    ai_bot = AIRegimeDetector()
    db = DatabaseManager(config['DB_PATH'])

    for symbol in ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "LINK/USDT", "XRP/USDT", "FET/USDT", "DOGE/USDT"]:
        try:
            logging.info(f"🔍 Analyzing {symbol}...")
            tf_data = {tf: collector.fetch_data(symbol, tf, 100) for tf in ['1d', '4h', '1h']}
            if not all(tf_data.values()): continue

            # Analyze Regimes
            regimes, dfs = {}, {}
            for tf, raw in tf_data.items():
                df = analyzer.calculate_indicators(pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume']))
                regimes[tf] = ai_bot.detect_regime(df)
                dfs[tf] = df

            row_1h = dfs['1h'].iloc[-1]
            atr = row_1h['atr']
            entry_price = row_1h['close']

            # Check for ELITE Setup (Alignment + ADX > 25)
            is_aligned = (regimes['1h'] == regimes['4h'] == regimes['1d'] == 'BULLISH')
            is_strong = row_1h['adx'] > 25

            if is_aligned and is_strong:
                # Dynamic SL/TP Calculation
                sl = entry_price - (1.5 * atr)
                tp = entry_price + (3.0 * atr)
                
                status = "ELITE"
                reason = "✅ Triple-Timeframe Bullish Alignment"
                
                # Send Enhanced Discord Alert
                collector.send_formatted_alert(symbol, entry_price, sl, tp, row_1h['rsi'], row_1h['adx'])
            else:
                sl, tp = 0, 0
                status = "REJECTED"
                reason = f"Trend Gap or Weak ADX ({row_1h['adx']:.1f})"

            db.save_signal(symbol, entry_price, regimes, row_1h, sl, tp, is_aligned, status, reason, pd.Timestamp.now().hour)

        except Exception as e:
            logging.error(f"❌ Error in {symbol}: {e}")

if __name__ == "__main__":
    main()
