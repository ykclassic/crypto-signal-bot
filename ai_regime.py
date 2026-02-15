import os
import requests
import logging
import time

class AIRegimeDetector:
    def __init__(self):
        # Using the standard RoBERTa sentiment model via API
        self.api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

    def get_sentiment(self, text):
        """Sends text to Hugging Face API with a built-in 'Wake Up' check."""
        if not text:
            return 0
            
        payload = {"inputs": text[:512], "options": {"wait_for_model": True}}
        
        try:
            for attempt in range(3):  # Try 3 times if the model is loading
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
                result = response.json()

                # Handle model loading (503 error)
                if isinstance(result, dict) and "estimated_time" in result:
                    wait_time = result.get("estimated_time", 20)
                    logging.info(f"AI Model is warming up... waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                # Success: result is a nested list [[{'label':..., 'score':...}]]
                sentiment_data = result[0]
                top_result = max(sentiment_data, key=lambda x: x['score'])
                
                # LABEL_0: Negative, LABEL_1: Neutral, LABEL_2: Positive
                mapping = {"LABEL_0": -1, "LABEL_1": 0, "LABEL_2": 1}
                return mapping.get(top_result['label'], 0) * top_result['score']
                
        except Exception as e:
            logging.error(f"API Sentiment failed: {e}")
            return 0
        return 0

    def detect_regime(self, df):
        """Standard technical regime detection."""
        # Safety: Need at least 20 periods for a 20-period moving average
        if df is None or len(df) < 20:
            logging.warning("Insufficient data for regime detection.")
            return "UNKNOWN"
            
        # Calculate 20-period Simple Moving Average
        sma20 = df['close'].rolling(window=20).mean()
        current_price = df['close'].iloc[-1]
        current_sma = sma20.iloc[-1]
        
        return "BULLISH" if current_price > current_sma else "BEARISH"
