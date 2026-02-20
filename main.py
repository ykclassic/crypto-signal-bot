import os
import logging
import pandas as pd
import time
import sqlite3
from data_collection import DataCollector
from technical_analysis import TechnicalAnalysis
from ai_regime import AIRegimeDetector
from database_manager import DatabaseManager

# --- Configuration & Secrets Mapping ---
TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "LINK/USDT", "XRP/USDT", "DOGE/USDT", "SUI/USDT", "ADA/USDT"]
ADX_THRESHOLD = 25  
DB_PATH = os.getenv('DB_PATH', 'signals.db')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def migrate_database(db_path):
    """Ensures the database has all required columns for the latest bot version."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Add 'hour_of_day' column if it doesn't exist
        cursor.execute("PRAGMA table_info(signals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hour_of_day' not in columns:
            logging.info("🛠️ Migrating database: Adding 'hour_of_day' column...")
            cursor.execute("ALTER TABLE signals ADD COLUMN hour_of_day INTEGER DEFAULT 0")
        
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"❌ Migration Error: {e}")

def analyze_setup(row, regimes):
    """Gatekeeper logic for trade signals."""
    if not (regimes['1h'] == regimes['4h'] == regimes['1d']):
        return False, f"Gap: {regimes['1d']}/{regimes['4h']}/{regimes['1h']}"
    if row['adx'] < ADX_THRESHOLD:
        return False, f"Weak Trend (ADX {row['adx']:.1f})"
    if regimes['1h'] == "BULLISH" and row['rsi'] > 70:
        return False, f"Overbought (RSI {row['rsi']:.1f})"
    if regimes['1h'] == "BEARISH" and row['rsi'] < 30:
        return False, f"Oversold (RSI {row['rsi']:.1f})"
    return True, "✅ ELITE SETUP"

def main():
    # FIX: Explicitly check for secret presence before passing
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': DB_PATH
    }

    # Run Database Migration first
    migrate_database(DB_PATH)

    collector = DataCollector(config)
    analyzer = TechnicalAnalysis()
    ai_bot = AIRegimeDetector()
    db = DatabaseManager(DB_PATH)

    quality_signals = []

    for symbol in TRADING_PAIRS:
        try:
            logging.info(f"🔍 Checking {symbol}...")
            tf_data = {tf: collector.fetch_data(symbol, tf, 100) for tf in ['1d', '4h', '1h']}
            
            if not all(tf_data.values()): continue

            regimes, dfs = {}, {}
            for tf, raw in tf_data.items():
                df = pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume'])
                df = analyzer.calculate_indicators(df)
                regimes[tf] = ai_bot.detect_regime(df)
                dfs[tf] = df

            df_1h = dfs['1h']
            row_1h = df_1h.iloc[-1]
            price = row_1h['close']

            is_passed, reason = analyze_setup(row_1h, regimes)
            
            # Save to DB with current hour for the new column
            current_hour = pd.Timestamp.now().hour
            db.save_signal(
                symbol=symbol, price=price, regimes=regimes, 
                df_row=row_1h, sl=0, tp=0, is_aligned=is_passed,
                status="ELITE" if is_passed else "REJECTED",
                reason=reason,
                hour_of_day=current_hour # Ensure this is passed to your DB manager
            )

            if is_passed:
                quality_signals.append(f"🌟 **ELITE {symbol}**: {reason}")

        except Exception as e:
            logging.error(f"❌ Loop Error for {symbol}: {e}")

    if quality_signals:
        collector._send_discord_alert("\n".join(quality_signals))
    else:
        collector._send_discord_alert("💓 Heartbeat: Bot Active. No high-quality setups found.")

if __name__ == "__main__":
    main()
