import ccxt
import logging
import requests
import os

class DataCollector:
    def __init__(self, config):
        self.webhook_url = config.get('DISCORD_WEBHOOK_URL')
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
        """Attempts Bitget, then Gate.io as fallback with notification."""
        priority_exchanges = [
            {'id': 'bitget', 'key': 'BITGET_API_KEY', 'secret': 'BITGET_SECRET'},
            {'id': 'gate', 'key': 'GATEIO_API_KEY', 'secret': 'GATEIO_SECRET'}
        ]

        for i, ex in enumerate(priority_exchanges):
            exchange_id = ex['id']
            api_key = config.get(ex['key'])
            secret = config.get(ex['secret'])

            if not api_key or not secret:
                continue

            try:
                exchange_class = getattr(ccxt, exchange_id)
                exchange_instance = exchange_class({
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                
                # Test the connection
                exchange_instance.fetch_balance()
                
                # If we are on the second exchange (Gate.io), send a fallback alert
                if i > 0:
                    self._send_discord_alert(f"Primary exchange failed. Switched to fallback: **{exchange_id.upper()}**")
                
                logging.info(f"✅ Connected to {exchange_id.upper()}")
                return exchange_instance
                
            except Exception as e:
                logging.error(f"❌ {exchange_id} connection failed: {e}")
                if i == 0:
                    logging.info("Attempting fallback exchange...")
                continue

        error_msg = "CRITICAL: Connection failed for both Bitget and Gate.io."
        self._send_discord_alert(error_msg)
        raise ConnectionError(error_msg)
