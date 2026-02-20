import pandas as pd
import logging

# Universal Import to prevent ModuleNotFoundError
try:
    import pandas_ta_classic as ta
except ImportError:
    try:
        import pandas_ta_openbb as ta
    except ImportError:
        import pandas_ta as ta

class TechnicalAnalysis:
    def __init__(self):
        logging.info("Technical Analysis Module Initialized")

    def calculate_indicators(self, df):
        try:
            # Ensure data is numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])

            # RSI
            df['rsi'] = ta.rsi(df['close'], length=14)
            
            # ADX
            adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
            df['adx'] = adx_df['ADX_14']
            
            # ATR for SL/TP
            df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            
            # EMA for Trend Detection
            df['ema_20'] = ta.ema(df['close'], length=20)
            df['ema_50'] = ta.ema(df['close'], length=50)
            
            return df
        except Exception as e:
            logging.error(f"Error calculating indicators: {e}")
            return None
