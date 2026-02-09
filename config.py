# Configuration file for API keys and settings
import os

# API Keys (Load from env vars if available, else use placeholders)
EXCHANGE_API_KEYS = {
    'xt': {
        'apiKey': os.getenv('XT_API_KEY', 'your_xt_api_key'),
        'secret': os.getenv('XT_SECRET', 'your_xt_secret')
    },
    'bitget': {
        'apiKey': os.getenv('BITGET_API_KEY', 'your_bitget_api_key'),
        'secret': os.getenv('BITGET_SECRET', 'your_bitget_secret')
    },
    'gateio': {
        'apiKey': os.getenv('GATEIO_API_KEY', 'your_gateio_api_key'),
        'secret': os.getenv('GATEIO_SECRET', 'your_gateio_secret')
    }
}
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_newsapi_key')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'your_discord_webhook_url')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'your_twitter_bearer_token')  # For tweepy

# Other settings
TICKERS = ['BTC/USDT', 'ETH/USDT']  # Focus tickers
TIMEFRAMES = ['1h', '4h', '1d']
DB_PATH = 'signals.db'
LOG_LEVEL = 'INFO'  # Added back for logging
