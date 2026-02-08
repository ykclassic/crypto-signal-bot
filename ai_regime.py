import tensorflow as tf
import numpy as np
import pandas as pd
from transformers import pipeline

class AIRegimeDetector:
    def __init__(self):
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
        self.lstm_model = self.build_lstm_model()
        self.load_model()

    def build_lstm_model(self):
        """Build LSTM model for next close prediction."""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(100, 5)),  # OHLCV
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def load_model(self):
        """Load pre-trained model if exists, else use heuristic."""
        try:
            self.lstm_model.load_weights('lstm_model.h5')
        except:
            self.use_heuristic = True

    def detect_regime(self, df):
        """Classify as Trending or Ranging using ADX."""
        adx = ta.adx(df['high'], df['low'], df['close'], length=14)
        return 'Trending' if adx.iloc[-1] > 25 else 'Ranging'

    def predict_next_close(self, df):
        """Predict next close using LSTM or heuristic."""
        if not self.use_heuristic:
            # Prepare data (last 100 candles, OHLCV)
            data = df[['open', 'high', 'low', 'close', 'volume']].tail(100).values
            data = np.reshape(data, (1, 100, 5))
            prediction = self.lstm_model.predict(data)[0][0]
            return prediction
        else:
            # Heuristic: Next close = current close + EMA trend
            ema_trend = df['ema_20'].iloc[-1] - df['ema_20'].iloc[-2]
            return df['close'].iloc[-1] + ema_trend

    def analyze_sentiment(self, text):
        """Sentiment score using Transformer."""
        result = self.sentiment_pipeline(text)[0]
        return 1 if result['label'] == 'LABEL_2' else -1 if result['label'] == 'LABEL_0' else 0
