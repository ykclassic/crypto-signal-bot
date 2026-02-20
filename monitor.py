import os
import logging
import sqlite3
import pandas as pd
from data_collection import DataCollector
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def patch_db_manager(db_instance):
    """Dynamically adds missing methods to DatabaseManager to avoid AttributeError."""
    def get_open_signals():
        try:
            with sqlite3.connect(db_instance.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Targets 'ELITE' signals for performance tracking
                cursor.execute("SELECT * FROM signals WHERE status = 'ELITE'")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"❌ Monitor Patch Error (get_open_signals): {e}")
            return []

    def update_signal_status(signal_id, new_status, reason):
        try:
            with sqlite3.connect(db_instance.db_path) as conn:
                conn.execute(
                    "UPDATE signals SET status = ?, reason = ? WHERE id = ?",
                    (new_status, reason, signal_id)
                )
                conn.commit()
        except Exception as e:
            logging.error(f"❌ Monitor Patch Error (update_status): {e}")

    # Attach methods if they don't exist
    if not hasattr(db_instance, 'get_open_signals'):
        db_instance.get_open_signals = get_open_signals
    if not hasattr(db_instance, 'update_signal_status'):
        db_instance.update_signal_status = update_signal_status

def monitor_trades():
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': os.getenv('DB_PATH', 'signals.db')
    }

    db = DatabaseManager(config['DB_PATH'])
    patch_db_manager(db) # Apply the fix locally
    
    collector = DataCollector(config)
    
    # Verify Bitget connection directly
    if not config['BITGET_API_KEY']:
        logging.warning("⚠️ Monitor running without BITGET_API_KEY. Check workflow ENV.")

    open_trades = db.get_open_signals()
    
    if not open_trades:
        logging.info("📝 No active ELITE signals to monitor.")
        return

    for trade in open_trades:
        symbol = trade['symbol']
        entry_price = trade['price']
        
        try:
            ticker = collector.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            pnl = ((current_price - entry_price) / entry_price) * 100
            
            logging.info(f"📊 {symbol} | Entry: {entry_price} | Now: {current_price} | PnL: {pnl:.2f}%")
            
            if pnl >= 3.0:
                db.update_signal_status(trade['id'], "TP_HIT", f"Gain: {pnl:.2f}%")
            elif pnl <= -1.5:
                db.update_signal_status(trade['id'], "SL_HIT", f"Loss: {pnl:.2f}%")
                
        except Exception as e:
            logging.error(f"❌ Error checking {symbol}: {e}")

if __name__ == "__main__":
    monitor_trades()
