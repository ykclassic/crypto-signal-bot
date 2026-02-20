import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path='signals.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates table and auto-adds missing columns for schema updates."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS signals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol TEXT,
                        price REAL,
                        regime_1h TEXT, regime_4h TEXT, regime_1d TEXT,
                        rsi REAL, adx REAL, atr REAL,
                        is_aligned INTEGER,
                        status TEXT,
                        reason TEXT,
                        hour_of_day INTEGER
                    )
                ''')
                # Schema Migration Logic
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(signals)")
                columns = [col[1] for col in cursor.fetchall()]
                
                required_columns = {
                    'status': 'TEXT',
                    'reason': 'TEXT',
                    'hour_of_day': 'INTEGER'
                }
                
                for col_name, col_type in required_columns.items():
                    if col_name not in columns:
                        logging.info(f"🛠️ Migrating DB: Adding column '{col_name}'")
                        conn.execute(f"ALTER TABLE signals ADD COLUMN {col_name} {col_type}")
        except Exception as e:
            logging.error(f"❌ DB Init/Migration Error: {e}")

    def save_signal(self, symbol, price, regimes, df_row, sl, tp, is_aligned, status, reason, hour_of_day):
        """Saves a scan result (Elite or Rejected) to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO signals (
                        symbol, price, regime_1h, regime_4h, regime_1d, 
                        rsi, adx, atr, is_aligned, status, reason, hour_of_day
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, price, regimes['1h'], regimes['4h'], regimes['1d'],
                    df_row['rsi'], df_row['adx'], df_row['atr'], 
                    1 if is_aligned else 0, status, reason, hour_of_day
                ))
                logging.info(f"💾 Saved {status} audit for {symbol}")
        except Exception as e:
            logging.error(f"❌ DB Save Error for {symbol}: {e}")
