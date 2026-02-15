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
                        is_aligned INTEGER,
                        status TEXT DEFAULT 'OPEN'
                    )
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"DB Creation Error: {e}")

    def save_signal(self, symbol, price, regimes, rsi, atr, sl, tp, is_aligned):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO signals (
                        symbol, price, regime_1h, regime_4h, regime_1d, 
                        rsi, atr, stop_loss, take_profit, is_aligned
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, price, regimes['1h'], regimes['4h'], regimes['1d'], 
                      rsi, atr, sl, tp, 1 if is_aligned else 0))
                conn.commit()
        except Exception as e:
            logging.error(f"❌ DB Save Error: {e}")

    def get_open_signals(self):
        """Fetches all signals that are aligned and still marked as OPEN."""
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
        """Marks a signal as CLOSED (TP or SL hit)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE signals SET status = ? WHERE id = ?", (result, signal_id))
                conn.commit()
        except Exception as e:
            logging.error(f"❌ DB Update Error: {e}")
