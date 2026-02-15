import pandas_ta as ta
import pandas as pd

class TechnicalAnalysis:
    @staticmethod
    def calculate_indicators(df):
        if df is None or df.empty:
            return df

        # 1. EMAs and SMAs
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)

        # 2. Complex Indicators
        macd = ta.macd(df['close'])
        if macd is not None: df = pd.concat([df, macd], axis=1)

        stoch = ta.stoch(df['high'], df['low'], df['close'])
        if stoch is not None: df = pd.concat([df, stoch], axis=1)

        aroon = ta.aroon(df['high'], df['low'], length=14)
        if aroon is not None: df = pd.concat([df, aroon], axis=1)

        bbands = ta.bbands(df['close'], length=20)
        if bbands is not None: df = pd.concat([df, bbands], axis=1)

        # Ichimoku returns (Span A/B, etc)
        ichi, _ = ta.ichimoku(df['high'], df['low'], df['close'])
        if ichi is not None: df = pd.concat([df, ichi], axis=1)

        # 3. Momentum & Volume
        df['RSI_14'] = ta.rsi(df['close'], length=14)
        df['obv'] = ta.obv(df['close'], df['volume'])
        
        adx = ta.adx(df['high'], df['low'], df['close'], length=14)
        if adx is not None: df = pd.concat([df, adx], axis=1)

        # 4. Manual Pivots
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']

        return df
