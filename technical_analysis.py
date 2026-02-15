import pandas as pd
import pandas_ta as ta

class TechnicalAnalysis:
    def __init__(self):
        pass

    def calculate_indicators(self, df):
        """
        Calculates a robust set of indicators for filtering and ML training.
        Maintains all previous features (EMA, RSI, ATR, ADX).
        """
        if df.empty or len(df) < 30:
            return df
        
        # Numeric conversion
        for col in ['high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])

        # Existing Indicators
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['adx'] = adx_df['ADX_14'] if adx_df is not None else 0

        # New ML Features
        # 1. Volume Relative to its 20-period average
        df['vol_sma'] = ta.sma(df['volume'], length=20)
        df['vol_ratio'] = df['volume'] / df['vol_sma']
        
        # 2. Price Change % (Momentum feature)
        df['pcnt_change'] = df['close'].pct_change(periods=5) * 100

        return df
