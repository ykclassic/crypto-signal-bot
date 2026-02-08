import ccxt
import snscrape.modules.twitter as sntwitter
import requests
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.exchanges = {
            'xt': ccxt.xt(config['EXCHANGE_API_KEYS']['xt']),
            'bitget': ccxt.bitget(config['EXCHANGE_API_KEYS']['bitget']),
            'gateio': ccxt.gateio(config['EXCHANGE_API_KEYS']['gateio'])
        }
        self.newsapi = NewsApiClient(api_key=config['NEWS_API_KEY'])
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def fetch_ohlcv(self, ticker, timeframe, limit=100):
        """Fetch OHLCV data from exchanges, trying multiple if one fails."""
        for name, exchange in self.exchanges.items():
            try:
                data = exchange.fetch_ohlcv(ticker, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
            except Exception as e:
                logger.warning(f"Failed to fetch from {name}: {e}")
        raise Exception("All exchanges failed to fetch OHLCV data.")

    def fetch_sentiment_data(self, ticker):
        """Fetch sentiment from Twitter and News."""
        sentiment_score = 0
        count = 0

        # Twitter scraping (last 100 tweets)
        try:
            query = f"{ticker} lang:en"
            tweets = sntwitter.TwitterSearchScraper(query).get_items()
            for tweet in list(tweets)[:100]:
                score = self.sentiment_analyzer.polarity_scores(tweet.rawContent)['compound']
                sentiment_score += score
                count += 1
        except Exception as e:
            logger.warning(f"Twitter fetch failed: {e}")

        # News headlines (last 10)
        try:
            articles = self.newsapi.get_everything(q=ticker, language='en', page_size=10)
            for article in articles['articles']:
                score = self.sentiment_analyzer.polarity_scores(article['title'])['compound']
                sentiment_score += score
                count += 1
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")

        return sentiment_score / count if count > 0 else 0  # Average sentiment (-1 to 1)
