import sqlite3
from datetime import datetime

class SignalDatabase:
    def __init__(self, db_path='signals.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS active_signals (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT,
                    side TEXT,
                    entry_price REAL,
                    sl REAL,
                    tp REAL,
                    timestamp TEXT
                )
            ''')

    def add_signal(self, ticker, side, entry_price, sl, tp):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO active_signals (ticker, side, entry_price, sl, tp, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ticker, side, entry_price, sl, tp, datetime.now().isoformat()))

    def get_active_signals(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM active_signals')
            return cursor.fetchall()

    def remove_signal(self, signal_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM active_signals WHERE id = ?', (signal_id,))
