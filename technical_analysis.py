import pandas as pd
import pandas_ta as ta

class TechnicalAnalysis:
    def __init__(self):
        pass

    def calculate_indicators(self, df):
        """
        Calculates a robust set of indicators for high-quality filtering:
        EMA (Trend), RSI (Momentum), ATR (Volatility), and ADX (Strength).
        """
        if df.empty or len(df) < 30:
            return df
        
        # Numeric conversion
        for col in ['high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col])

        # 1. Trend: 20-period EMA
        df['ema_20'] = ta.ema(df['close'], length=20)
        
        # 2. Momentum: 14-period RSI
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        # 3. Volatility: 14-period ATR
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # 4. Strength: ADX (Directional Movement Index)
        # We use a custom call to access ADX components
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx_df is not None:
            df['adx'] = adx_df['ADX_14']
        else:
            df['adx'] = 0

        return df
