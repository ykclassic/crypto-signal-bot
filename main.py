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
ATR_SL_MULT = 2.0  # Stop Loss at 2x ATR
ATR_TP_MULT = 4.0  # Take Profit at 4x ATR (1:2 Risk/Reward)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    config = {
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'HF_TOKEN': os.getenv('HF_TOKEN'),
        'DB_PATH': 'signals.db'
    }

    try:
        collector = DataCollector(config)
        analyzer = TechnicalAnalysis()
        ai_bot = AIRegimeDetector()
        db = DatabaseManager(config['DB_PATH'])

        logging.info("🚀 Starting Advanced MTF & ATR Scan...")
        results_summary = []

        for symbol in TRADING_PAIRS:
            try:
                # 1. Fetch Multi-Timeframe Data
                tf_data = {
                    '1d': collector.fetch_data(symbol, '1d', 100),
                    '4h': collector.fetch_data(symbol, '4h', 100),
                    '1h': collector.fetch_data(symbol, '1h', 100)
                }

                if not all(tf_data.values()):
                    logging.warning(f"⚠️ Missing timeframe data for {symbol}")
                    continue

                # 2. Analyze Regimes
                regimes = {}
                processed_dfs = {}
                for tf, raw in tf_data.items():
                    df = pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume'])
                    df = analyzer.calculate_indicators(df)
                    regimes[tf] = ai_bot.detect_regime(df)
                    processed_dfs[tf] = df

                # 3. Confirmation Logic
                is_aligned = (regimes['1h'] == regimes['4h'] == regimes['1d'])
                
                # Execution data from 1H
                df_1h = processed_dfs['1h']
                current_price = df_1h['close'].iloc[-1]
                current_atr = df_1h['atr'].iloc[-1]
                current_rsi = df_1h['rsi'].iloc[-1]

                # 4. ATR-Based Level Calculation
                sl, tp = None, None
                if is_aligned:
                    if regimes['1h'] == "BULLISH":
                        sl = current_price - (current_atr * ATR_SL_MULT)
                        tp = current_price + (current_atr * ATR_TP_MULT)
                    elif regimes['1h'] == "BEARISH":
                        sl = current_price + (current_atr * ATR_SL_MULT)
                        tp = current_price - (current_atr * ATR_TP_MULT)

                # 5. Save to Database
                db.save_signal(symbol, current_price, regimes, current_rsi, current_atr, sl, tp, is_aligned)

                # 6. Prepare Discord Alert
                if is_aligned and sl and tp:
                    msg = (f"🔥 **MTF SIGNAL: {regimes['1h']}** - {symbol}\n"
                           f"∟ Entry (1H): ${current_price:,.2f}\n"
                           f"∟ ATR SL: ${sl:,.2f} | ATR TP: ${tp:,.2f}\n"
                           f"∟ 1D: {regimes['1d']} | 4H: {regimes['4h']} | 1H: {regimes['1h']}")
                    results_summary.append(msg)
                
                time.sleep(1) # Safety delay for API

            except Exception as e:
                logging.error(f"❌ Error on {symbol}: {e}")

        # Final Discord Reporting
        if results_summary:
            collector._send_discord_alert("🎯 **CONFIRMED ACTIONABLE SIGNALS**\n" + "\n\n".join(results_summary))
        else:
            logging.info("ℹ️ No MTF alignment found this cycle.")

    except Exception as e:
        logging.error(f"❌ Critical Failure: {e}")

if __name__ == "__main__":
    main()
