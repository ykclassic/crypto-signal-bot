import ccxt
import tweepy
import pandas as pd
import logging
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.exchanges = {
            'xt': ccxt.xt({'apiKey': config['EXCHANGE_API_KEYS']['xt']['apiKey'], 
                           'secret': config['EXCHANGE_API_KEYS']['xt']['secret']}),
            'bitget': ccxt.bitget({'apiKey': config['EXCHANGE_API_KEYS']['bitget']['apiKey'], 
                                   'secret': config['EXCHANGE_API_KEYS']['bitget']['secret']}),
            'gateio': ccxt.gateio({'apiKey': config['EXCHANGE_API_KEYS']['gateio']['apiKey'], 
                                   'secret': config['EXCHANGE_API_KEYS']['gateio']['secret']})
        }
        self.newsapi = NewsApiClient(api_key=config['NEWS_API_KEY'])
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.twitter_client = tweepy.Client(bearer_token=config['TWITTER_BEARER_TOKEN'])

    def fetch_ohlcv(self, ticker, timeframe, limit=100):
        for name, exchange in self.exchanges.items():
            try:
                data = exchange.fetch_ohlcv(ticker, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
            except Exception as e:
                logger.warning(f"Failed to fetch from {name}: {e}")
        raise Exception(f"All exchanges failed for {ticker}")

    def fetch_sentiment_data(self, ticker):
        sentiment_score = 0
        count = 0
        try:
            query = f"{ticker} lang:en"
            tweets = self.twitter_client.search_recent_tweets(query=query, max_results=10)
            if tweets.data:
                for tweet in tweets.data:
                    score = self.sentiment_analyzer.polarity_scores(tweet.text)['compound']
                    sentiment_score += score
                    count += 1
        except Exception as e:
            logger.warning(f"Twitter fetch failed: {e}")

        try:
            articles = self.newsapi.get_everything(q=ticker, language='en', page_size=10)
            for article in articles['articles']:
                score = self.sentiment_analyzer.polarity_scores(article['title'])['compound']
                sentiment_score += score
                count += 1
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")

        return sentiment_score / count if count > 0 else 0
