import os
import logging
# Force TensorFlow backend before importing transformers
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["USE_TF"] = "1"
os.environ["USE_TORCH"] = "0"

from transformers import pipeline

class AIRegimeDetector:
    def __init__(self):
        self.sentiment_pipeline = None
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="tf"
            )
        except Exception as e:
            logging.error(f"AI Model fallback activated: {e}")

    def detect_regime(self, df):
        # High-performance technical regime detection
        if df is None or len(df) < 50: return "RANGING"
        
        ema_fast = df['close'].ewm(span=20).mean().iloc[-1]
        ema_slow = df['close'].ewm(span=50).mean().iloc[-1]
        
        if ema_fast > ema_slow: return "BULLISH"
        return "BEARISH"
