import os
import requests
import logging

class AIRegimeDetector:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

    def get_sentiment(self, text):
        """Sends text to Hugging Face API instead of running it locally."""
        if not text: return 0
        try:
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": text[:512]})
            result = response.json()[0] # Returns list of results
            
            # Find the highest score
            # RoBERTa output: [{'label': 'LABEL_0', 'score': 0.99}, ...]
            top_result = max(result, key=lambda x: x['score'])
            mapping = {"LABEL_0": -1, "LABEL_1": 0, "LABEL_2": 1}
            return mapping.get(top_result['label'], 0) * top_result['score']
        except Exception as e:
            logging.error(f"API Sentiment failed: {e}")
            return 0

    def detect_regime(self, df):
        """Keeps logic technical to ensure it never fails."""
        if df is None or len(df) < 20: return "UNKNOWN"
        return "BULLISH" if df['close'].iloc[-1] > df['close'].rolling(20).mean().iloc[-1] else "BEARISH"
