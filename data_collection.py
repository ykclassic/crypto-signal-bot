import ccxt
import requests
import logging
import time

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.exchange_name = "BITGET"
        
        # Initialize Bitget with mandatory password (passphrase)
        self.exchange = ccxt.bitget({
            'apiKey': config.get('BITGET_API_KEY'),
            'secret': config.get('BITGET_SECRET'),
            'password': config.get('BITGET_PASSWORD'),  # Critical for Bitget
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # Ensure we are targeting Spot markets
                'adjustForTimeDifference': True
            }
        })

        # Fallback Exchange (Gate.io)
        self.fallback_exchange = ccxt.gateio({
            'apiKey': config.get('GATEIO_API_KEY'),
            'secret': config.get('GATEIO_SECRET'),
            'enableRateLimit': True
        })

        self._validate_connections()

    def _validate_connections(self):
        """Verifies if the API keys are actually working."""
        try:
            self.exchange.fetch_balance()
            logging.info(f"✅ Primary Exchange ({self.exchange_name}) Connected Successfully.")
        except Exception as e:
            logging.error(f"❌ Primary Exchange ({self.exchange_name}) Failed: {e}")
            self.exchange = self.fallback_exchange
            self.exchange_name = "GATEIO"
            logging.warning(f"🔄 Switched to Fallback: {self.exchange_name}")

    def fetch_data(self, symbol, timeframe='1h', limit=100):
        """Fetches OHLCV data from the active exchange."""
        try:
            # Bitget uses 'BTC/USDT' format; Gate.io is compatible
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                raise ValueError(f"Empty data received for {symbol}")
            return ohlcv
        except Exception as e:
            logging.error(f"❌ Error fetching {symbol} from {self.exchange_name}: {e}")
            return None

    def _send_discord_alert(self, message):
        """Standard Discord Webhook notification."""
        url = self.config.get('DISCORD_WEBHOOK_URL')
        if not url:
            return
        
        payload = {"content": message}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"⚠️ Discord Alert Failed: {e}")

    def get_current_price(self, symbol):
        """Fetches the latest ticker price."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logging.error(f"❌ Error fetching price for {symbol}: {e}")
            return None
