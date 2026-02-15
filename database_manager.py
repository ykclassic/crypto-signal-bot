import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="signals.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    price REAL,
                    regime TEXT,
                    rsi REAL,
                    ema REAL
                )
            ''')
            conn.commit()

    def save_signal(self, symbol, price, regime, rsi, ema):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO signals (timestamp, symbol, price, regime, rsi, ema)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), symbol, price, regime, rsi, ema))
            conn.commit()
