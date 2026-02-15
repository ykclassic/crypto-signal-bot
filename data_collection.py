import os
import tweepy
import requests
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class DataCollector:
    def __init__(self):
        # API Keys from Environment
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
        # Initialize Sentiment Analyzer
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Safe Initialize Twitter
        self.twitter_client = None
        if self.twitter_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_token)
            except Exception as e:
                print(f"Twitter Auth failed: {e}")

    def get_sentiment(self, symbol):
        """Fetch sentiment from Twitter, fallback to NewsAPI if 402 or failed."""
        sentiment_score = 0
        sources_used = 0
        
        # 1. Attempt Twitter (X)
        if self.twitter_client:
            try:
                query = f"#{symbol} crypto -is:retweet lang:en"
                tweets = self.twitter_client.search_recent_tweets(query=query, max_results=10)
                if tweets.data:
                    for tweet in tweets.data:
                        sentiment_score += self.analyzer.polarity_scores(tweet.text)['compound']
                        sources_used += 1
            except Exception as e:
                if "402" in str(e):
                    print(f"Twitter API 402: Credits exhausted. Switching to NewsAPI for {symbol}.")
                else:
                    print(f"Twitter error for {symbol}: {e}")

        # 2. Fallback / Augment with NewsAPI
        if self.news_api_key:
            try:
                newsapi = NewsApiClient(api_key=self.news_api_key)
                articles = newsapi.get_everything(q=symbol, language='en', sort_by='relevancy', page_size=5)
                for article in articles.get('articles', []):
                    text = f"{article['title']} {article['description']}"
                    sentiment_score += self.analyzer.polarity_scores(text)['compound']
                    sources_used += 1
            except Exception as e:
                print(f"NewsAPI error: {e}")

        return sentiment_score / sources_used if sources_used > 0 else 0

    def get_market_data(self, exchange, symbol, timeframe='1h'):
        """Fetch OHLCV data from CCXT."""
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            return ohlcv
        except Exception as e:
            print(f"Market data fetch failed for {symbol}: {e}")
            return None
