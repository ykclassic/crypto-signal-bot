import ccxt
import logging
import requests
import os

class DataCollector:
    def __init__(self, config):
        self.webhook_url = config.get('DISCORD_WEBHOOK_URL')
        # We initialize this as None first to ensure the class exists before logic runs
        self.exchange = None 
        self.exchange = self._initialize_exchange(config)

    def _send_discord_alert(self, message):
        """Sends a quick notification to Discord."""
        if not self.webhook_url:
            return
        try:
            payload = {"content": f"⚠️ **Bot Alert:** {message}"}
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")

    def _initialize_exchange(self, config):
        """Attempts Bitget, then Gate.io as fallback."""
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
                logging.warning(f"Skipping {exchange_id}: Missing credentials.")
                continue

            try:
                exchange_class = getattr(ccxt, exchange_id)
                params = {
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                }
                if password: params['password'] = password

                instance = exchange_class(params)
                instance.fetch_balance() # Verify login
                
                if i > 0:
                    self._send_discord_alert(f"Primary exchange failed. Switched to: **{exchange_id.upper()}**")
                
                logging.info(f"✅ Connected to {exchange_id.upper()}")
                return instance
                
            except Exception as e:
                logging.error(f"❌ {exchange_id} Auth Error: {str(e)}")
                continue

        raise ConnectionError("CRITICAL: Failed to connect to any exchange.")

    def fetch_data(self, symbol="BTC/USDT"):
        """Standard OHLCV fetch."""
        if not self.exchange: return None
        return self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
