import pandas as pd
import pandas_ta as ta

class TechnicalAnalysis:
    def __init__(self):
        pass

    def calculate_indicators(self, df):
        """
        Calculates RSI, EMA, and ATR for the given DataFrame.
        Maintains all previous technical features.
        """
        if df.empty:
            return df
        
        # Ensure numeric data
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])

        # RSI - 14 period
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        # EMA - 20 period
        df['ema_20'] = ta.ema(df['close'], length=20)
        
        # ATR - 14 period (Standard for volatility measurement)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        return df
