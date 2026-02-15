import os
import logging
import time
from data_collection import DataCollector
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def monitor_trades():
    config = {
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
        'DB_PATH': 'signals.db'
    }

    db = DatabaseManager(config['DB_PATH'])
    collector = DataCollector(config)
    
    open_trades = db.get_open_signals()
    if not open_trades:
        logging.info("No active trades to monitor.")
        return

    for trade in open_trades:
        symbol = trade['symbol']
        entry_price = trade['price']
        sl = trade['stop_loss']
        tp = trade['take_profit']
        
        # Fetch latest price
        ticker = collector.exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        direction = trade['regime_1h']
        hit_tp = (direction == "BULLISH" and current_price >= tp) or (direction == "BEARISH" and current_price <= tp)
        hit_sl = (direction == "BULLISH" and current_price <= sl) or (direction == "BEARISH" and current_price >= sl)

        if hit_tp:
            msg = f"✅ **TAKE PROFIT HIT** - {symbol}\nProfit realized from Entry: ${entry_price:,.2f} to TP: ${tp:,.2f}"
            collector._send_discord_alert(msg)
            db.close_signal(trade['id'], 'CLOSED_TP')
        elif hit_sl:
            msg = f"❌ **STOP LOSS HIT** - {symbol}\nTrade exited at SL: ${sl:,.2f}"
            collector._send_discord_alert(msg)
            db.close_signal(trade['id'], 'CLOSED_SL')
        
        time.sleep(1) # Rate limit protection

if __name__ == "__main__":
    monitor_trades()
