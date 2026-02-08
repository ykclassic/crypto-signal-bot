class SignalLogic:
    @staticmethod
    def generate_signal(ticker, dfs, regime, sentiment):
        """Generate signal based on consensus across timeframes."""
        h1, h4, d1 = dfs['1h'], dfs['4h'], dfs['1d']
        
        # Check bullish consensus
        bullish_h1 = (h1['close'].iloc[-1] > h1['ichimoku'].iloc[-1]['senkou_span_a']) and (h1['rsi'].iloc[-1] > 50)
        bullish_h4 = (h4['close'].iloc[-1] > h4['ichimoku'].iloc[-1]['senkou_span_a']) and (h4['rsi'].iloc[-1] > 50)
        bullish_d1 = (d1['close'].iloc[-1] > d1['ichimoku'].iloc[-1]['senkou_span_a']) and (d1['rsi'].iloc[-1] > 50)
        
        if bullish_h1 and bullish_h4 and bullish_d1 and sentiment > 0:
            side = 'LONG'
        elif not bullish_h1 and not bullish_h4 and not bullish_d1 and sentiment < 0:
            side = 'SHORT'
        else:
            return None
        
        # Trade type
        volatility = (h1['bbands'].iloc[-1]['BBU'] - h1['bbands'].iloc[-1]['BBL']) / h1['close'].iloc[-1]
        if volatility > 0.05 and regime == 'Ranging':
            trade_type = 'Scalping'
        elif regime == 'Trending':
            trade_type = 'Swing Trading'
        else:
            trade_type = 'Day Trading'
        
        confidence = (1 if bullish_h1 else 0) + (1 if bullish_h4 else 0) + (1 if bullish_d1 else 0) + (1 if sentiment > 0 else 0)
        return {'ticker': ticker, 'side': side, 'type': trade_type, 'confidence': confidence / 4}
