import pandas as pd
import pandas_ta_classic as ta

class RiskManagement:
    @staticmethod
    def calculate_sl_tp(df, side, entry_price):
        # ATR for dynamic stop logic
        atr_series = ta.atr(df['high'], df['low'], df['close'], length=14)
        atr = atr_series.iloc[-1] if atr_series is not None else 0

        if side == 'LONG':
            sl = df['low'].rolling(20).min().iloc[-1]
            tp = entry_price + 2 * (entry_price - sl)
        else:
            sl = df['high'].rolling(20).max().iloc[-1]
            tp = entry_price - 2 * (sl - entry_price)
        
        return float(sl), float(tp)

    @staticmethod
    def check_active_signals(db, current_prices):
        signals = db.get_active_signals()
        for signal in signals:
            signal_id, ticker, side, entry, sl, tp, _ = signal
            if ticker not in current_prices:
                continue
                
            curr = current_prices[ticker]
            
            # TP Check
            if (side == 'LONG' and curr >= tp) or (side == 'SHORT' and curr <= tp):
                pnl = ((curr - entry) / entry * 100) if side == 'LONG' else ((entry - curr) / entry * 100)
                db.remove_signal(signal_id)
                return f"✅ TP Hit for {ticker}: +{pnl:.2f}%"
            
            # SL Check
            if (side == 'LONG' and curr <= sl) or (side == 'SHORT' and curr >= sl):
                pnl = ((sl - entry) / entry * 100) if side == 'LONG' else ((entry - sl) / entry * 100)
                db.remove_signal(signal_id)
                return f"❌ SL Hit for {ticker}: {pnl:.2f}%"
        return None
