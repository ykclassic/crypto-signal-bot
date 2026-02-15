import logging
import pandas as pd

class AIRegimeDetector:
    def __init__(self):
        """
        Initializes the AI model. Falls back to technical-only analysis if unavailable.
        """
        self.sentiment_pipeline = None
        
        try:
            # Check for PyTorch first
            try:
                import torch
                logging.info(f"PyTorch {torch.__version__} detected")
            except ImportError:
                logging.warning("PyTorch not available - sentiment analysis disabled")
                return
            
            # Try loading the model
            from transformers import pipeline
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment",
                framework="pt"  # Use PyTorch since it's available
            )
            logging.info("AIRegimeDetector: Successfully loaded sentiment model.")
            
        except Exception as e:
            logging.warning(f"AIRegimeDetector: Could not load AI model: {e}")
            logging.info("Continuing with technical analysis only.")
    
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
            # Need at least 20 periods for SMA
            if len(df) < 20:
                logging.warning(f"Insufficient data for regime: {len(df)} rows (need 20+)")
                return "UNKNOWN"
            
            last_close = df['close'].iloc[-1]
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            
            # Check for NaN
            if pd.isna(last_close) or pd.isna(sma_20):
                logging.warning("NaN values in regime calculation")
                return "UNKNOWN"
            
            # 2% threshold to avoid noise
            threshold = 0.02
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
        Analyzes text sentiment. Returns 0 if model unavailable.
        
        Args:
            text: String to analyze
            
        Returns:
            float: Sentiment score in range [-1, 1]
        """
        if not text or not isinstance(text, str):
            return 0.0
        
        if not self.sentiment_pipeline:
            logging.debug("Sentiment pipeline unavailable, returning neutral")
            return 0.0
        
        try:
            result = self.sentiment_pipeline(text, truncation=True, max_length=512)[0]
            
            # Cardiff NLP RoBERTa sentiment labels
            label_mapping = {
                "LABEL_0": -1.0,  # Negative
                "LABEL_1": 0.0,   # Neutral
                "LABEL_2": 1.0    # Positive
            }
            
            label = result.get('label', 'LABEL_1')
            confidence = result.get('score', 0.0)
            
            sentiment_value = label_mapping.get(label, 0.0)
            return sentiment_value * confidence
            
        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}", exc_info=True)
            return 0.0
