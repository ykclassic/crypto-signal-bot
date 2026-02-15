import logging
import pandas as pd

class AIRegimeDetector:
    def __init__(self):
        """
        Initializes the AI model using TensorFlow to avoid PyTorch dependencies.
        Falls back to rule-based sentiment if model loading fails.
        """
        self.sentiment_pipeline = None
        
        try:
            from transformers import pipeline
            import tensorflow as tf
            
            logging.info(f"Loading model with TensorFlow {tf.__version__}")
            
            # Use a TensorFlow-native model or one with better TF support
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="tf",
                truncation=True
            )
            logging.info("AIRegimeDetector: Successfully loaded sentiment model.")
            
        except ImportError as e:
            logging.error(f"Missing dependencies: {e}")
        except Exception as e:
            logging.error(f"Could not load AI model: {e}")
            logging.info("Falling back to technical-only regime detection.")
    
    def detect_regime(self, df):
        """
        Determines market regime based on price vs moving average.
        
        Args:
            df: DataFrame with 'close' column
            
        Returns:
            str: "BULLISH", "BEARISH", "RANGING", or "UNKNOWN"
        """
        if df is None or df.empty:
            logging.warning("Empty dataframe passed to detect_regime")
            return "UNKNOWN"
            
        if 'close' not in df.columns:
            logging.error("DataFrame missing 'close' column")
            return "UNKNOWN"
        
        try:
            # Need at least 20 periods for SMA calculation
            if len(df) < 20:
                logging.warning(f"Insufficient data: {len(df)} rows (need 20+)")
                return "UNKNOWN"
            
            last_close = df['close'].iloc[-1]
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            
            # Add threshold to avoid false signals in ranging markets
            threshold = 0.02  # 2% threshold
            diff_pct = (last_close - sma_20) / sma_20
            
            if diff_pct > threshold:
                return "BULLISH"
            elif diff_pct < -threshold:
                return "BEARISH"
            else:
                return "RANGING"
                
        except Exception as e:
            logging.error(f"Error in regime detection: {e}", exc_info=True)
            return "UNKNOWN"
    
    def get_sentiment(self, text):
        """
        Analyzes text sentiment using RoBERTa model.
        
        Args:
            text: String to analyze
            
        Returns:
            float: Sentiment score in range [-1, 1]
                  -1 = most negative, 0 = neutral, 1 = most positive
        """
        if not text or not isinstance(text, str):
            return 0.0
        
        if not self.sentiment_pipeline:
            logging.debug("Sentiment pipeline unavailable, returning neutral")
            return 0.0
        
        try:
            # Model handles truncation internally when truncation=True is set
            result = self.sentiment_pipeline(text)[0]
            
            # Cardiff NLP RoBERTa sentiment labels
            label_mapping = {
                "LABEL_0": -1.0,  # Negative
                "LABEL_1": 0.0,   # Neutral
                "LABEL_2": 1.0    # Positive
            }
            
            label = result.get('label', 'LABEL_1')
            confidence = result.get('score', 0.0)
            
            sentiment_value = label_mapping.get(label, 0.0)
            
            # Return weighted sentiment
            return sentiment_value * confidence
            
        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}", exc_info=True)
            return 0.0
