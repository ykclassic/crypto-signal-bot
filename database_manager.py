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
                        regime TEXT,
                        rsi REAL,
                        ema REAL
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"DB Creation Error: {e}")

    def save_signal(self, symbol, price, regime, rsi, ema):
        try:
            # We use isolation_level=None to force immediate writing
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO signals (symbol, price, regime, rsi, ema)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, price, regime, rsi, ema))
            conn.commit()
            conn.close()
            logging.info(f"✅ Hard-saved {symbol} to disk.")
        except Exception as e:
            logging.error(f"❌ DB Write Error for {symbol}: {e}")
