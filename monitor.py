import os
import logging
import pandas as pd
from data_collection import DataCollector
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def monitor_trades():
    # Explicitly mapping secrets for the monitor process
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': os.getenv('DB_PATH', 'signals.db')
    }

    # Verify credentials before starting
    if not config['BITGET_API_KEY']:
        logging.error("❌ Bitget API Key missing in Monitor environment!")

    db = DatabaseManager(config['DB_PATH'])
    collector = DataCollector(config)
    
    open_trades = db.get_open_signals()
    
    if not open_trades:
        logging.info("📝 No active ELITE signals to monitor currently.")
        return

    for trade in open_trades:
        symbol = trade['symbol']
        entry_price = trade['price']
        trade_id = trade['id']
        
        try:
            ticker = collector.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            pnl = ((current_price - entry_price) / entry_price) * 100
            
            logging.info(f"📊 Monitoring {symbol} | Entry: {entry_price} | Now: {current_price} | PnL: {pnl:.2f}%")
            
            # Example logic: Update status if price moves significantly
            if pnl >= 2.0:
                db.update_signal_status(trade_id, "MONITORED_GAIN", f"Price up {pnl:.2f}%")
            elif pnl <= -2.0:
                db.update_signal_status(trade_id, "MONITORED_LOSS", f"Price down {pnl:.2f}%")
                
        except Exception as e:
            logging.error(f"❌ Failed to check {symbol}: {e}")

if __name__ == "__main__":
    monitor_trades()
