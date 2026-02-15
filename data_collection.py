import ccxt
import logging

class DataCollector:
    def __init__(self, config):
        # We try the standard lowercase 'xt' first
        exchange_id = 'xt'
        
        try:
            # Check if 'xt' exists in the library
            if exchange_id in ccxt.exchanges:
                exchange_class = getattr(ccxt, exchange_id)
            else:
                # Fallback to 'xtcom' if 'xt' isn't found
                logging.warning("ccxt.xt not found, trying ccxt.xtcom")
                exchange_class = getattr(ccxt, 'xtcom')
                
            self.exchange = exchange_class({
                'apiKey': config.get('XT_API_KEY'),
                'secret': config.get('XT_SECRET'),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'} # Ensure you're on Spot market
            })
            logging.info(f"Successfully connected to {self.exchange.id}")
            
        except AttributeError as e:
            logging.error(f"Critical Error: Could not find XT exchange in CCXT. {e}")
            raise
