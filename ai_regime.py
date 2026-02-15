import logging
import pandas as pd
from transformers import pipeline

class AIRegimeDetector:
    def __init__(self):
        """
        Initializes the AI model using TensorFlow (tf) to avoid PyTorch dependencies.
        """
        try:
            # framework="tf" is mandatory because the runner lacks PyTorch
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="tf"
            )
            logging.info("AIRegimeDetector: Successfully loaded model with TensorFlow.")
        except Exception as e:
            logging.error(f"AIRegimeDetector: Could not load AI model: {e}")
            self.sentiment_pipeline = None

    def detect_regime(self, df):
        """
        Determines market regime. Matches the call in main.py.
        """
        if df is None or df.empty or 'close' not in df.columns:
            return "UNKNOWN"
            
        try:
            # Technical regime detection as a primary logic
            last_close = df['close'].iloc[-1]
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            
            if last_close > sma_20:
                return "BULLISH"
            elif last_close < sma_20:
                return "BEARISH"
            return "RANGING"
        except Exception as e:
            logging.error(f"Error in regime detection logic: {e}")
            return "UNKNOWN"

    def get_sentiment(self, text):
        """
        Analyzes text sentiment. RoBERTa labels: 
        LABEL_0 -> Negative, LABEL_1 -> Neutral, LABEL_2 -> Positive
        """
        if not self.sentiment_pipeline or not text:
            return 0
            
        try:
            # Truncate text to 512 tokens to prevent model overflow
            result = self.sentiment_pipeline(text[:512])[0]
            
            # Label mapping for cardiffnlp/twitter-roberta-base-sentiment
            mapping = {
                "LABEL_0": -1, # Negative
                "LABEL_1": 0,  # Neutral
                "LABEL_2": 1   # Positive
            }
            
            label = result.get('label')
            score = result.get('score', 0)
            
            return mapping.get(label, 0) * score
        except Exception as e:
            logging.error(f"Sentiment analysis processing error: {e}")
            return 0
