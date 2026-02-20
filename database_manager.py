import sqlite3
import logging
import os

class DatabaseManager:
    def __init__(self, db_path='signals.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the database and ensures all modern columns exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if the table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
                table_exists = cursor.fetchone()

                if table_exists:
                    # Check if 'regime_1h' exists. If not, the table is too old to migrate easily.
                    cursor.execute("PRAGMA table_info(signals)")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if 'regime_1h' not in columns:
                        logging.warning("⚠️ Database schema is critically outdated. Rebuilding table...")
                        # In a live trading environment, we'd migrate. For setup, we rebuild for stability.
                        cursor.execute("DROP TABLE signals")
                
                # Create the modern table structure
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
                        adx REAL, 
                        atr REAL,
                        is_aligned INTEGER,
                        status TEXT,
                        reason TEXT,
                        hour_of_day INTEGER
                    )
                ''')
                conn.commit()
                logging.info("✅ Database Schema is up to date.")
        except Exception as e:
            logging.error(f"❌ DB Initialization Error: {e}")

    def save_signal(self, symbol, price, regimes, df_row, sl, tp, is_aligned, status, reason, hour_of_day):
        """Saves audit data to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO signals (
                        symbol, price, regime_1h, regime_4h, regime_1d, 
                        rsi, adx, atr, is_aligned, status, reason, hour_of_day
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, price, 
                    regimes.get('1h', 'UNKNOWN'), 
                    regimes.get('4h', 'UNKNOWN'), 
                    regimes.get('1d', 'UNKNOWN'),
                    df_row['rsi'], df_row['adx'], df_row['atr'], 
                    1 if is_aligned else 0, status, reason, hour_of_day
                ))
                logging.info(f"💾 {symbol} logged as {status}")
        except Exception as e:
            logging.error(f"❌ DB Save Error for {symbol}: {e}")
