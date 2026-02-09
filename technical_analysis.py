import pandas_ta_classic as ta
import pandas as pd

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df):
        """Calculate all required indicators correctly handling multi-column outputs."""
        if df is None or df.empty:
            return df

        # 1. Simple Trend Indicators (Return single Series)
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        
        # 2. Indicators that return DataFrames (Multiple Columns)
        # Use join to merge the new columns into the main dataframe
        
        # MACD (returns MACD, Histogram, Signal)
        macd_df = ta.macd(df['close'])
        if macd_df is not None:
            df = df.join(macd_df)

        # Stochastic (returns k and d lines)
        stoch_df = ta.stoch(df['high'], df['low'], df['close'])
        if stoch_df is not None:
            df = df.join(stoch_df)

        # Aroon (returns Up, Down, and Osc)
        aroon_df = ta.aroon(df['high'], df['low'], length=14)
        if aroon_df is not None:
            df = df.join(aroon_df)

        # Bollinger Bands (returns Lower, Mid, Upper, Bandwidth, %B)
        bbands_df = ta.bbands(df['close'], length=20)
        if bbands_df is not None:
            df = df.join(bbands_df)

        # Ichimoku (returns two spans, base, conversion, and lagging)
        # Ichimoku returns a tuple of two DataFrames; we usually want the first one
        ichi_data = ta.ichimoku(df['high'], df['low'], df['close'])
        if ichi_data is not None:
            df = df.join(ichi_data[0])

        # 3. Momentum & Volume (Single Series)
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['obv'] = ta.obv(df['close'], df['volume'])
        
        # ADX (required for AI Regime detector)
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx_df is not None:
            df = df.join(adx_df)

        # 4. Manual Pivot Calculations
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']

        return df
