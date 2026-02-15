import sqlite3
import pandas as pd
import ccxt
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class Backtester:
    def __init__(self, db_path="signals.db"):
        self.db_path = db_path
        self.exchange = ccxt.gateio()

    def run_test(self):
        try:
            # 1. Load data from DB
            conn = sqlite3.connect(self.db_path)
            # Only test signals that were "Aligned" (High Quality)
            query = "SELECT * FROM signals WHERE is_aligned = 1"
            df_signals = pd.read_sql_query(query, conn)
            conn.close()

            if df_signals.empty:
                print("🚫 No high-quality signals found in database to test.")
                return

            print(f"📈 Testing {len(df_signals)} historical signals...")
            
            results = []
            for _, signal in df_signals.iterrows():
                result = self._evaluate_signal(signal)
                results.append(result)
                time.sleep(0.2) # Rate limit protection

            # 2. Calculate Stats
            self._print_report(results)

        except Exception as e:
            print(f"❌ Backtest Error: {e}")

    def _evaluate_signal(self, signal):
        symbol = signal['symbol']
        entry_price = signal['price']
        tp = signal['take_profit']
        sl = signal['stop_loss']
        timestamp = signal['timestamp']
        direction = signal['regime_1h']

        # Convert timestamp to milliseconds for CCXT
        since = int(pd.to_datetime(timestamp).timestamp() * 1000)
        
        try:
            # Fetch subsequent 48 hours of 1h data to see outcome
            candles = self.exchange.fetch_ohlcv(symbol, timeframe='1h', since=since, limit=48)
            
            for candle in candles:
                high = candle[2]
                low = candle[3]

                if direction == "BULLISH":
                    if high >= tp: return "WIN"
                    if low <= sl: return "LOSS"
                else: # BEARISH
                    if low <= tp: return "WIN"
                    if high >= sl: return "LOSS"
            
            return "EXPIRED" # Neither hit in 48 hours
        except:
            return "ERROR"

    def _print_report(self, results):
        wins = results.count("WIN")
        losses = results.count("LOSS")
        expired = results.count("EXPIRED")
        total = wins + losses
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        print("\n" + "="*30)
        print("📊 BACKTEST PERFORMANCE REPORT")
        print("="*30)
        print(f"Total Signals:  {len(results)}")
        print(f"Wins:           {wins}")
        print(f"Losses:         {losses}")
        print(f"Expired/Open:   {expired}")
        print(f"Win Rate:       {win_rate:.2f}%")
        print("="*30)

if __name__ == "__main__":
    tester = Backtester()
    tester.run_test()
