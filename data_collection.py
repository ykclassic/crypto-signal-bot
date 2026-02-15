import ccxt
import logging

class DataCollector:
    def __init__(self, config):
        self.exchange = self._initialize_exchange(config)

    def _initialize_exchange(self, config):
        """Attempts to connect to Bitget first, then Gate.io."""
        # Define the exchanges to try in order of priority
        # bitget and gate are the standard CCXT IDs
        priority_exchanges = [
            {'id': 'bitget', 'key': 'BITGET_API_KEY', 'secret': 'BITGET_SECRET'},
            {'id': 'gate', 'key': 'GATE_API_KEY', 'secret': 'GATE_SECRET'}
        ]

        for ex in priority_exchanges:
            exchange_id = ex['id']
            api_key = config.get(ex['key'])
            secret = config.get(ex['secret'])

            if not api_key or not secret:
                logging.warning(f"Skipping {exchange_id}: API credentials missing.")
                continue

            try:
                # Use getattr to safely fetch the class from ccxt
                exchange_class = getattr(ccxt, exchange_id)
                exchange_instance = exchange_class({
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'} # Focus on Spot markets
                })
                
                # Test connection (optional, but recommended)
                exchange_instance.fetch_balance()
                logging.info(f"✅ Successfully connected to {exchange_id.upper()}")
                return exchange_instance
                
            except Exception as e:
                logging.error(f"❌ Connection to {exchange_id} failed: {e}")
                continue

        raise ConnectionError("Could not connect to Bitget or Gate.io. Check your credentials.")

    def fetch_data(self, symbol="BTC/USDT"):
        """Fetches OHLCV data using the active exchange."""
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None
