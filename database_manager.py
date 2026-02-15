import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path="signals.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol TEXT,
                        price REAL,
                        regime_1h TEXT,
                        regime_4h TEXT,
                        regime_1d TEXT,
                        rsi REAL,
                        atr REAL,
                        stop_loss REAL,
                        take_profit REAL,
                        is_aligned INTEGER
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"DB Creation Error: {e}")

    def save_signal(self, symbol, price, regimes, rsi, atr, sl, tp, is_aligned):
        """
        Saves a comprehensive signal record including MTF status and ATR levels.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO signals (
                        symbol, price, regime_1h, regime_4h, regime_1d, 
                        rsi, atr, stop_loss, take_profit, is_aligned
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, price, regimes['1h'], regimes['4h'], regimes['1d'], 
                    rsi, atr, sl, tp, 1 if is_aligned else 0
                ))
                conn.commit()
            logging.info(f"✅ Data persisted for {symbol}")
        except Exception as e:
            logging.error(f"❌ DB Write Error for {symbol}: {e}")
