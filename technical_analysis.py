import pandas_ta_classic as ta
import pandas as pd

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df):
        """Calculate all required indicators."""
        # Trend
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['ichimoku'] = ta.ichimoku(df['high'], df['low'], df['close'])
        df['aroon'] = ta.aroon(df['high'], df['low'], length=14)
        # Momentum
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['macd'] = ta.macd(df['close'])
        df['stoch'] = ta.stoch(df['high'], df['low'], df['close'])
        # Volume
        df['obv'] = ta.obv(df['close'], df['volume'])
        # Volatility
        df['bbands'] = ta.bbands(df['close'], length=20)
        # Advanced
        df['fib_levels'] = ta.fibonacci_retracement(df['high'], df['low'])
        # Support/Resistance (simple pivot-based)
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']
        return df
