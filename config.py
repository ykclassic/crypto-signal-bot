# Configuration file for API keys and settings
import os

# API Keys (Replace with your actual keys)
EXCHANGE_API_KEYS = {
    'xt': {'apiKey': 'your_xt_api_key', 'secret': 'your_xt_secret'},
    'bitget': {'apiKey': 'your_bitget_api_key', 'secret': 'your_bitget_secret'},
    'gateio': {'apiKey': 'your_gateio_api_key', 'secret': 'your_gateio_secret'}
}
NEWS_API_KEY = 'your_newsapi_key'
DISCORD_WEBHOOK_URL = 'your_discord_webhook_url'
TWITTER_BEARER_TOKEN = 'your_twitter_bearer_token'  # For tweepy if needed

# Other settings
TICKERS = ['BTC/USDT', 'ETH/USDT']  # Focus tickers
TIMEFRAMES = ['1h', '4h', '1d']
DB_PATH = 'signals.db'
LOG_LEVEL = 'INFO'
