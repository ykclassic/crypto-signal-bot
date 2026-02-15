import ccxt
import logging

class DataCollector:
    def __init__(self, config):
        self.exchange = self._initialize_exchange(config)

    def _initialize_exchange(self, config):
        """Attempts to connect to Bitget first, then Gate.io as fallback."""
        priority_exchanges = [
            {'id': 'bitget', 'key': 'BITGET_API_KEY', 'secret': 'BITGET_SECRET'},
            {'id': 'gate', 'key': 'GATEIO_API_KEY', 'secret': 'GATEIO_SECRET'}
        ]

        for ex in priority_exchanges:
            exchange_id = ex['id']
            api_key = config.get(ex['key'])
            secret = config.get(ex['secret'])

            if not api_key or not secret:
                logging.warning(f"Skipping {exchange_id}: Credentials missing in environment.")
                continue

            try:
                # Use getattr to safely fetch the class from ccxt
                exchange_class = getattr(ccxt, exchange_id)
                exchange_instance = exchange_class({
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                
                # Verify connection with a lightweight private call
                exchange_instance.fetch_balance()
                logging.info(f"✅ Successfully connected to {exchange_id.upper()}")
                return exchange_instance
                
            except Exception as e:
                logging.error(f"❌ Connection to {exchange_id} failed: {e}")
                continue

        raise ConnectionError("CRITICAL: Failed to connect to both Bitget and Gate.io. Check Secrets.")
