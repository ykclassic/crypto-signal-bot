import os
import tweepy
import logging
import ccxt
import pandas as pd
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class DataCollector:
    def __init__(self, config=None):
        self.config = config or {}
        # Initialize Exchange (Assuming XT as default, can be dynamic)
        self.exchange = ccxt.xt({
            'apiKey': os.getenv('XT_API_KEY'),
            'secret': os.getenv('XT_SECRET'),
        })
        
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.twitter_client = None
        if self.twitter_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_token)
            except Exception as e:
                logging.error(f"Twitter Init failed: {e}")

        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch_ohlcv(self, ticker, timeframe='1h'):
        """Actually fetches data from the exchange and returns a DataFrame."""
        try:
            # CCXT fetch_ohlcv returns list of lists
            bars = self.exchange.fetch_ohlcv(ticker, timeframe=timeframe, limit=100)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logging.error(f"Failed to fetch OHLCV for {ticker}: {e}")
            return None # This is what caused your crash; main.py needs a check!

    def fetch_sentiment_data(self, symbol):
        sentiment_score = 0
        sources = 0
        # Twitter handling with 402 check
        if self.twitter_client:
            try:
                tweets = self.twitter_client.search_recent_tweets(query=f"{symbol} crypto", max_results=10)
                if tweets and tweets.data:
                    for t in tweets.data:
                        sentiment_score += self.analyzer.polarity_scores(t.text)['compound']
                        sources += 1
            except Exception as e:
                if "402" in str(e):
                    logging.warning(f"Twitter 402 for {symbol}. Falling back.")
        
        # NewsAPI Fallback
        if self.news_api_key:
            try:
                newsapi = NewsApiClient(api_key=self.news_api_key)
                articles = newsapi.get_everything(q=symbol, language='en', page_size=5)
                for art in articles.get('articles', []):
                    text = f"{art.get('title')} {art.get('description')}"
                    sentiment_score += self.analyzer.polarity_scores(text)['compound']
                    sources += 1
            except Exception: pass

        return sentiment_score / sources if sources > 0 else 0
