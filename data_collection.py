import logging
import pandas as pd
import ccxt
import requests

class DataCollector:
    def __init__(self, config):
        """Initializes the DataCollector with API keys and webhook settings."""
        self.config = config
        self.webhook_url = config.get('DISCORD_WEBHOOK_URL')
        self.exchange = self._connect_exchange()

    def _connect_exchange(self):
        """Initializes the primary exchange (Bitget) with Gate.io fallback."""
        try:
            exchange = ccxt.bitget({
                'apiKey': self.config.get('BITGET_API_KEY'),
                'secret': self.config.get('BITGET_SECRET'),
                'password': self.config.get('BITGET_PASSWORD'),
                'enableRateLimit': True,
            })
            exchange.check_required_credentials()
            logging.info("✅ Primary Exchange (BITGET) Connected Successfully.")
            return exchange
        except Exception as e:
            logging.error(f"❌ Primary Exchange (BITGET) Failed: {e}")
            logging.info("🔄 Switched to Fallback: GATEIO")
            try:
                fallback = ccxt.gateio({
                    'apiKey': self.config.get('GATEIO_API_KEY'),
                    'secret': self.config.get('GATEIO_SECRET'),
                    'enableRateLimit': True,
                })
                return fallback
            except Exception as ex:
                logging.error(f"❌ Fallback Exchange Failed: {ex}")
                return None

    def fetch_data(self, symbol, timeframe, limit=100):
        """Fetches historical OHLCV data for a given symbol and timeframe."""
        if not self.exchange:
            logging.error("❌ No exchange connected. Cannot fetch data.")
            return None
            
        try:
            # fetch_ohlcv returns a list of [timestamp, open, high, low, close, volume]
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not ohlcv:
                return None
            return ohlcv
        except Exception as e:
            logging.error(f"❌ Error fetching {symbol} on {timeframe}: {e}")
            return None

    def _send_discord_alert(self, message):
        """Sends a basic, plain-text alert to Discord."""
        if not self.webhook_url:
            logging.warning("⚠️ Webhook URL not set. Skipping basic alert.")
            return
            
        payload = {"content": message}
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"❌ Basic Alert Error: {e}")

    def send_formatted_alert(self, symbol, entry, sl, tp, rsi, adx):
        """Sends a professional-grade embedded trading signal to Discord."""
        if not self.webhook_url:
            logging.warning("⚠️ Webhook URL not set. Skipping formatted alert.")
            return

        payload = {
            "embeds": [{
                "title": f"🚀 ELITE SIGNAL: {symbol}",
                "color": 5763719,  # Green color in decimal
                "fields": [
                    {"name": "🎯 Entry Price", "value": f"${entry:,.4f}", "inline": True},
                    {"name": "🛑 Stop Loss", "value": f"${sl:,.4f}", "inline": True},
                    {"name": "💰 Take Profit", "value": f"${tp:,.4f}", "inline": True},
                    {"name": "📊 Indicators", "value": f"RSI: {rsi:.1f} | ADX: {adx:.1f}", "inline": False}
                ],
                "footer": {"text": "Gemini AI Trading Core v3.0"}
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logging.info(f"✅ Formatted alert sent for {symbol}.")
        except Exception as e:
            logging.error(f"❌ Formatted Alert Error: {e}")
