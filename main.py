import os
import logging
import pandas as pd
import time
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from database_manager import DatabaseManager

# Configuration
TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "LINK/USDT", "XRP/USDT", "FET/USDT", "DOGE/USDT"]
ADX_THRESHOLD = 25  

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_credentials():
    """Validates that secrets are actually loaded into the environment."""
    keys = ['BITGET_API_KEY', 'BITGET_SECRET', 'BITGET_PASSWORD', 'DISCORD_WEBHOOK_URL']
    for key in keys:
        status = "✅ FOUND" if os.getenv(key) else "❌ MISSING"
        logging.info(f"Credential Check: {key} is {status}")

def analyze_setup(row, regimes):
    if not (regimes['1h'] == regimes['4h'] == regimes['1d']):
        return False, f"Gap: {regimes['1d']}/{regimes['4h']}/{regimes['1h']}"
    if row['adx'] < ADX_THRESHOLD:
        return False, f"Weak Trend: ADX {row['adx']:.1f}"
    if regimes['1h'] == "BULLISH" and row['rsi'] > 70:
        return False, f"Overbought: RSI {row['rsi']:.1f}"
    if regimes['1h'] == "BEARISH" and row['rsi'] < 30:
        return False, f"Oversold: RSI {row['rsi']:.1f}"
    return True, "✅ ELITE SETUP"

def main():
    check_credentials()
    
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': 'signals.db'
    }

    collector = DataCollector(config)
    analyzer = TechnicalAnalysis()
    ai_bot = AIRegimeDetector()
    db = DatabaseManager(config['DB_PATH'])

    quality_signals = []

    for symbol in TRADING_PAIRS:
        try:
            logging.info(f"🔍 Analyzing {symbol}...")
            tf_data = {tf: collector.fetch_data(symbol, tf, 100) for tf in ['1d', '4h', '1h']}
            
            if not all(tf_data.values()): continue

            regimes, dfs = {}, {}
            for tf, raw in tf_data.items():
                df = pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume'])
                df = analyzer.calculate_indicators(df)
                regimes[tf] = ai_bot.detect_regime(df)
                dfs[tf] = df

            row_1h = dfs['1h'].iloc[-1]
            is_passed, reason = analyze_setup(row_1h, regimes)
            
            db.save_signal(
                symbol=symbol, price=row_1h['close'], regimes=regimes, 
                df_row=row_1h, sl=0, tp=0, is_aligned=is_passed,
                status="ELITE" if is_passed else "REJECTED",
                reason=reason, hour_of_day=pd.Timestamp.now().hour
            )

            if is_passed:
                quality_signals.append(f"💎 **ELITE {symbol}**: {reason}")

        except Exception as e:
            logging.error(f"❌ Error in {symbol} loop: {e}")

    if quality_signals:
        collector._send_discord_alert("\n".join(quality_signals))
    else:
        logging.info("Heartbeat: No signals found.")

if __name__ == "__main__":
    main()
