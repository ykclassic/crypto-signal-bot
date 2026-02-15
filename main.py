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
ADX_THRESHOLD = 25  
ATR_SL_MULT = 2.0
ATR_TP_MULT = 4.0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_high_quality(df, regime):
    current_rsi = df['rsi'].iloc[-1]
    current_adx = df.get('adx', pd.Series([0])).iloc[-1]
    if current_adx < ADX_THRESHOLD: return False, "Low Trend Strength"
    if regime == "BULLISH" and current_rsi > 70: return False, "Overbought"
    if regime == "BEARISH" and current_rsi < 30: return False, "Oversold"
    return True, "High Quality"

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

        quality_signals = []

        for symbol in TRADING_PAIRS:
            try:
                tf_data = {tf: collector.fetch_data(symbol, tf, 100) for tf in ['1d', '4h', '1h']}
                if not all(tf_data.values()): continue

                regimes, dfs = {}, {}
                for tf, raw in tf_data.items():
                    df = analyzer.calculate_indicators(pd.DataFrame(raw, columns=['timestamp','open','high','low','close','volume']))
                    regimes[tf] = ai_bot.detect_regime(df)
                    dfs[tf] = df

                is_aligned = (regimes['1h'] == regimes['4h'] == regimes['1d'])
                high_quality, reason = is_high_quality(dfs['1h'], regimes['1h'])
                
                df_1h = dfs['1h']
                row_1h = df_1h.iloc[-1]
                price = row_1h['close']
                
                sl = price - (row_1h['atr'] * ATR_SL_MULT) if regimes['1h'] == "BULLISH" else price + (row_1h['atr'] * ATR_SL_MULT)
                tp = price + (row_1h['atr'] * ATR_TP_MULT) if regimes['1h'] == "BULLISH" else price - (row_1h['atr'] * ATR_TP_MULT)

                # Persist with full ML features
                db.save_signal(symbol, price, regimes, row_1h, sl, tp, (is_aligned and high_quality))

                if is_aligned and high_quality:
                    quality_signals.append(
                        f"🌟 **HIGH CONVICTION: {regimes['1h']}** - {symbol}\n"
                        f"∟ Entry: ${price:,.2f} | SL: ${sl:,.2f} | TP: ${tp:,.2f}"
                    )
                time.sleep(1)

            except Exception as e:
                logging.error(f"❌ Error on {symbol}: {e}")

        if quality_signals:
            collector._send_discord_alert("💎 **ELITE MARKET SIGNALS**\n" + "\n\n".join(quality_signals))
        else:
            collector._send_discord_alert("🛠️ Your bot is still busy forging quality setups for you.")

    except Exception as e:
        logging.error(f"❌ Critical Failure: {e}")

if __name__ == "__main__":
    main()
