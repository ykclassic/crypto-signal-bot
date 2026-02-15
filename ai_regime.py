import logging
import pandas as pd
from transformers import pipeline

class AIRegimeDetector:
    def __init__(self):
        try:
            # Explicitly set framework to "tf" (TensorFlow) to avoid torch NameError
            # The cardiffnlp model supports both PT and TF weights
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="tf" 
            )
            logging.info("AI Regime Detector initialized with TensorFlow.")
        except Exception as e:
            logging.error(f"Failed to load AI model: {e}. Sentiment analysis will be disabled.")
            self.sentiment_pipeline = None

    def detect_regime(self, df):
        """
        Determines market regime (Bullish, Bearish, Sideways).
        """
        if df is None or df.empty:
            return "Unknown"
            
        # Example logic: Using the last close vs a simple moving average
        # In a real setup, this would use your ML model logic
        last_close = df['close'].iloc[-1]
        sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
        
        if last_close > sma_20:
            return "Trending Bullish"
        elif last_close < sma_20:
            return "Trending Bearish"
        return "Ranging"

    def analyze_sentiment(self, text):
        """Safe sentiment analysis wrapper."""
        if not self.sentiment_pipeline:
            return 0
        try:
            result = self.sentiment_pipeline(text[:512]) # Truncate for RoBERTa limits
            # RoBERTa output: LABEL_0 (Neg), LABEL_1 (Neu), LABEL_2 (Pos)
            label = result[0]['label']
            score = result[0]['score']
            
            if label == 'LABEL_2': return score
            if label == 'LABEL_0': return -score
            return 0
        except Exception as e:
            logging.error(f"Sentiment pipe error: {e}")
            return 0
