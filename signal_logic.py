class SignalLogic:
    @staticmethod
    def generate_signal(ticker, dfs, regime, sentiment):
        if not all(tf in dfs for tf in ['1h', '4h', '1d']):
            return None
            
        h1, h4, d1 = dfs['1h'], dfs['4h'], dfs['1d']

        def is_bullish(df):
            try:
                # pandas-ta naming: Span A = ISA_9, RSI = RSI_14
                span_a = df['ISA_9'].iloc[-1]
                rsi = df['RSI_14'].iloc[-1]
                close = df['close'].iloc[-1]
                return (close > span_a) and (rsi > 50)
            except KeyError:
                return False

        bullish_h1 = is_bullish(h1)
        bullish_h4 = is_bullish(h4)
        bullish_d1 = is_bullish(d1)

        if bullish_h1 and bullish_h4 and bullish_d1 and sentiment > 0:
            side = 'LONG'
        elif not bullish_h1 and not bullish_h4 and not bullish_d1 and sentiment < 0:
            side = 'SHORT'
        else:
            return None

        # Volatility & Regime logic
        try:
            upper = h1['BBU_20_2.0'].iloc[-1]
            lower = h1['BBL_20_2.0'].iloc[-1]
            volatility = (upper - lower) / h1['close'].iloc[-1]
        except KeyError:
            volatility = 0

        if volatility > 0.05 and regime == 'Ranging':
            trade_type = 'Scalping'
        elif regime == 'Trending':
            trade_type = 'Swing Trading'
        else:
            trade_type = 'Day Trading'

        # Confidence Calculation
        score = sum([bullish_h1, bullish_h4, bullish_d1, sentiment > 0])
        confidence = score / 4.0

        return {
            'ticker': ticker, 
            'side': side, 
            'type': trade_type, 
            'confidence': confidence
        }
