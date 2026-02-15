import sqlite3
import logging
from datetime import datetime

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
                        hour_of_day INTEGER,
                        symbol TEXT,
                        price REAL,
                        regime_1h TEXT,
                        regime_4h TEXT,
                        regime_1d TEXT,
                        rsi REAL,
                        adx REAL,
                        atr REAL,
                        vol_ratio REAL,
                        pcnt_change REAL,
                        stop_loss REAL,
                        take_profit REAL,
                        is_aligned INTEGER,
                        status TEXT DEFAULT 'OPEN'
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"DB Creation Error: {e}")

    def save_signal(self, symbol, price, regimes, df_row, sl, tp, is_aligned):
        """
        Saves an ML-Ready record with timestamp context and volume data.
        """
        try:
            current_hour = datetime.now().hour
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO signals (
                        hour_of_day, symbol, price, regime_1h, regime_4h, regime_1d, 
                        rsi, adx, atr, vol_ratio, pcnt_change, stop_loss, take_profit, is_aligned
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    current_hour, symbol, price, regimes['1h'], regimes['4h'], regimes['1d'], 
                    df_row['rsi'], df_row['adx'], df_row['atr'], 
                    df_row['vol_ratio'], df_row['pcnt_change'], sl, tp, 1 if is_aligned else 0
                ))
                conn.commit()
            logging.info(f"✅ ML-Ready Data persisted for {symbol}")
        except Exception as e:
            logging.error(f"❌ DB Save Error for {symbol}: {e}")

    def get_open_signals(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM signals WHERE is_aligned = 1 AND status = 'OPEN'")
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"❌ DB Fetch Error: {e}")
            return []

    def close_signal(self, signal_id, result):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE signals SET status = ? WHERE id = ?", (result, signal_id))
                conn.commit()
        except Exception as e:
            logging.error(f"❌ DB Update Error: {e}")
