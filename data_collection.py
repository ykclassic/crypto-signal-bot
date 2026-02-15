import ccxt
import logging
import requests
import os

class DataCollector:
    def __init__(self, config):
        self.webhook_url = config.get('DISCORD_WEBHOOK_URL')
        self.exchange = self._initialize_exchange(config)

    def _initialize_exchange(self, config):
        priority_exchanges = [
            {'id': 'bitget', 'key': 'BITGET_API_KEY', 'secret': 'BITGET_SECRET', 'pass': 'BITGET_PASSWORD'},
            {'id': 'gate', 'key': 'GATEIO_API_KEY', 'secret': 'GATEIO_SECRET'}
        ]

        for i, ex in enumerate(priority_exchanges):
            exchange_id = ex['id']
            api_key = config.get(ex['key'])
            secret = config.get(ex['secret'])
            password = config.get(ex.get('pass', ''))

            if not api_key or not secret:
                logging.warning(f"Skipping {exchange_id}: Missing environment variables.")
                continue

            try:
                exchange_class = getattr(ccxt, exchange_id)
                params = {
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                }
                if password: params['password'] = password # Required for Bitget

                exchange_instance = exchange_class(params)
                
                # Try a public call first to check network
                exchange_instance.fetch_ticker('BTC/USDT')
                # Then try the private call that is currently failing
                exchange_instance.fetch_balance()
                
                logging.info(f"✅ Connected to {exchange_id.upper()}")
                return exchange_instance
                
            except Exception as e:
                # This will print the EXACT error from the exchange in your logs
                logging.error(f"❌ {exchange_id} Auth Error: {str(e)}")
                continue

        raise ConnectionError("CRITICAL: Connection failed for both Bitget and Gate.io.")
