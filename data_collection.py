import os
import tweepy
import logging
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class DataCollector:
    def __init__(self, config=None):
        """
        Accepts a config dictionary from main.py.
        Prioritizes environment variables for security in GitHub Actions.
        """
        # Extract keys from config or environment
        self.config = config or {}
        exchange_keys = self.config.get('EXCHANGE_API_KEYS', {})
        
        # Twitter Setup
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN') or self.config.get('TWITTER_BEARER_TOKEN')
        self.twitter_client = None
        if self.twitter_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_token)
            except Exception as e:
                logging.error(f"Twitter Initialization failed: {e}")

        # News & Sentiment Setup
        self.news_api_key = os.getenv('NEWS_API_KEY') or self.config.get('NEWS_API_KEY')
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch_ohlcv(self, ticker, timeframe='1h'):
        """
        Fetches market data. Note: In your main.py, you need to pass 
        the exchange object, or the collector needs to manage it.
        This placeholder assumes you are using CCXT elsewhere.
        """
        # This matches the method name called in your main.py
        logging.info(f"Fetching OHLCV for {ticker} on {timeframe}")
        # Implementation depends on your exchange setup in main.py
        pass 

    def fetch_sentiment_data(self, symbol):
        """
        Renamed to match main.py. Handles Twitter 402 errors 
        by falling back to NewsAPI.
        """
        sentiment_score = 0
        sources = 0
        
        # 1. Try Twitter (X)
        if self.twitter_client:
            try:
                query = f"#{symbol} crypto -is:retweet lang:en"
                tweets = self.twitter_client.search_recent_tweets(query=query, max_results=10)
                if tweets and tweets.data:
                    for tweet in tweets.data:
                        sentiment_score += self.analyzer.polarity_scores(tweet.text)['compound']
                        sources += 1
            except Exception as e:
                if "402" in str(e):
                    logging.warning(f"Twitter 402 (Payment Required) for {symbol}. Using Fallbacks.")
                else:
                    logging.error(f"Twitter error: {e}")

        # 2. Fallback to NewsAPI
        if self.news_api_key:
            try:
                newsapi = NewsApiClient(api_key=self.news_api_key)
                articles = newsapi.get_everything(q=symbol, language='en', page_size=5)
                for art in articles.get('articles', []):
                    text = f"{art.get('title')} {art.get('description')}"
                    sentiment_score += self.analyzer.polarity_scores(text)['compound']
                    sources += 1
            except Exception as e:
                logging.error(f"NewsAPI error: {e}")

        return sentiment_score / sources if sources > 0 else 0
