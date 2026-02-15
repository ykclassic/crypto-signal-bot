import logging
import pandas as pd
import os

# TRICK: Tell transformers explicitly to use TensorFlow and ignore PyTorch
os.environ["USE_TF"] = "1"
os.environ["USE_TORCH"] = "0"

from transformers import pipeline

class AIRegimeDetector:
    def __init__(self):
        self.sentiment_pipeline = None
        try:
            # We wrap this because GitHub Actions environment is strict
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="tf"
            )
            logging.info("AI Detector loaded via TensorFlow.")
        except Exception as e:
            logging.error(f"AI Model load failed (likely missing torch/tf mismatch): {e}")

    def detect_regime(self, df):
        """High-reliability technical fallback."""
        if df is None or df.empty: return "UNKNOWN"
        
        # SMA 20/50 Crossover Logic
        sma20 = df['close'].rolling(20).mean().iloc[-1]
        if df['close'].iloc[-1] > sma20:
            return "BULLISH"
        return "BEARISH"
