import pandas as pd

class RiskManagement:
    @staticmethod
    def calculate_sl_tp(df, side, entry_price):
        """Calculate SL and TP."""
        atr = ta.atr(df['high'], df['low'], df['close'], length=14).iloc[-1]
        if side == 'LONG':
            sl = df['low'].rolling(20).min().iloc[-1]  # Swing low
            tp = entry_price + 2 * (entry_price - sl)  # 1:2 RR
        else:
            sl = df['high'].rolling(20).max().iloc[-1]  # Swing high
            tp = entry_price - 2 * (sl - entry_price)
        return sl, tp

    @staticmethod
    def check_active_signals(db, current_prices):
        """Check if active signals hit TP/SL."""
        signals = db.get_active_signals()
        for signal in signals:
            signal_id, ticker, side, entry, sl, tp, _ = signal
            current_price = current_prices[ticker]
            if (side == 'LONG' and current_price >= tp) or (side == 'SHORT' and current_price <= tp):
                pnl = (current_price - entry) / entry * 100 if side == 'LONG' else (entry - current_price) / entry * 100
                db.remove_signal(signal_id)
                return f"TP Hit for {ticker}: +{pnl:.2f}%"
            elif (side == 'LONG' and current_price <= sl) or (side == 'SHORT' and current_price >= sl):
                pnl = (sl - entry) / entry * 100 if side == 'LONG' else (entry - sl) / entry * 100
                db.remove_signal(signal_id)
                return f"SL Hit for {ticker}: -{pnl:.2f}%"
        return None
