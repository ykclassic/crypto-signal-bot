import os
import tweepy
import requests
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class DataCollector:
    def __init__(self, config=None):
        """
        Modified to accept a config dict for compatibility with main.py,
        but pulls from Environment Variables as the primary source.
        """
        # API Keys: Priority 1: Environment Variables | Priority 2: config dict
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN') or (config.get('twitter_bearer_token') if config else None)
        self.news_api_key = os.getenv('NEWS_API_KEY') or (config.get('news_api_key') if config else None)
        
        # Initialize Sentiment Analyzer
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Initialize Twitter Client safely
        self.twitter_client = None
        if self.twitter_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_token)
            except Exception as e:
                print(f"Twitter Initialization failed: {e}")

    def get_sentiment(self, symbol):
        """Fetch sentiment with graceful 402 (Payment Required) handling."""
        sentiment_score = 0
        sources_used = 0
        
        # 1. Attempt Twitter (X) - Handling Credit Exhaustion
        if self.twitter_client:
            try:
                query = f"#{symbol} crypto -is:retweet lang:en"
                tweets = self.twitter_client.search_recent_tweets(query=query, max_results=10)
                if tweets and tweets.data:
                    for tweet in tweets.data:
                        sentiment_score += self.analyzer.polarity_scores(tweet.text)['compound']
                        sources_used += 1
            except Exception as e:
                if "402" in str(e):
                    print(f"Twitter API 402: Credits exhausted. Skipping Twitter for {symbol}.")
                else:
                    print(f"Twitter error for {symbol}: {e}")

        # 2. NewsAPI Fallback
        if self.news_api_key:
            try:
                newsapi = NewsApiClient(api_key=self.news_api_key)
                articles = newsapi.get_everything(q=symbol, language='en', sort_by='relevancy', page_size=5)
                if articles.get('articles'):
                    for article in articles['articles']:
                        text = f"{article.get('title', '')} {article.get('description', '')}"
                        sentiment_score += self.analyzer.polarity_scores(text)['compound']
                        sources_used += 1
            except Exception as e:
                print(f"NewsAPI error for {symbol}: {e}")

        return sentiment_score / sources_used if sources_used > 0 else 0

    def get_market_data(self, exchange, symbol, timeframe='1h'):
        """Fetch OHLCV data from CCXT."""
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            return ohlcv
        except Exception as e:
            print(f"Market data fetch failed for {symbol}: {e}")
            return None
