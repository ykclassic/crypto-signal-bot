import pandas_ta as ta
import pandas as pd

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df):
        """Calculate all required indicators."""
        # Ensure df has enough data
        if len(df) < 50:  # Minimum for most indicators
            raise ValueError("Insufficient data for indicators")
        
        # Trend
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        
        # Ichimoku (returns DataFrame; join it)
        ichimoku_df = ta.ichimoku(df['high'], df['low'], df['close'])
        df = df.join(ichimoku_df, how='left')  # Adds columns like ISA_9, ISB_26, etc.
        
        df['aroon'] = ta.aroon(df['high'], df['low'], length=14)
        
        # Momentum
        df['rsi'] = ta.rsi(df['close'], length=14)
        macd_df = ta.macd(df['close'])
        df = df.join(macd_df, how='left')  # Adds MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        
        df['stoch'] = ta.stoch(df['high'], df['low'], df['close'])
        
        # Volume
        df['obv'] = ta.obv(df['close'], df['volume'])
        
        # Volatility
        bbands_df = ta.bbands(df['close'], length=20)
        df = df.join(bbands_df, how='left')  # Adds BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, BBB_20_2.0, BBPercent_20_2.0
        
        # Advanced
        fib_df = ta.fibonacci_retracement(df['high'], df['low'])
        df = df.join(fib_df, how='left')  # Adds fib levels if applicable
        
        # Support/Resistance (simple pivot-based)
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']
        
        # Drop NaNs to avoid length issues
        df.dropna(inplace=True)
        
        return df
