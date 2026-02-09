class SignalLogic:
    @staticmethod
    def generate_signal(ticker, dfs, regime, sentiment):
        """Generate signal based on consensus across timeframes with correct column mapping."""
        
        # Ensure dataframes exist for all timeframes
        if not all(tf in dfs for tf in ['1h', '4h', '1d']):
            return None
            
        h1, h4, d1 = dfs['1h'], dfs['4h'], dfs['1d']

        def is_bullish(df):
            try:
                # pandas-ta Ichimoku Span A is usually 'ISA_9'
                # RSI is 'RSI_14'
                # Check for standard column names produced by pandas-ta-classic
                span_a = df['ISA_9'].iloc[-1]
                rsi = df['RSI_14'].iloc[-1]
                close = df['close'].iloc[-1]
                
                return (close > span_a) and (rsi > 50)
            except KeyError:
                # Fallback if indicators failed to calculate
                return False

        bullish_h1 = is_bullish(h1)
        bullish_h4 = is_bullish(h4)
        bullish_d1 = is_bullish(d1)

        # Logic for Signal Side
        if bullish_h1 and bullish_h4 and bullish_d1 and sentiment > 0:
            side = 'LONG'
        elif not bullish_h1 and not bullish_h4 and not bullish_d1 and sentiment < 0:
            side = 'SHORT'
        else:
            return None

        # Trade type determination based on Volatility
        try:
            # Standard BB names: Upper = BBU_20_2.0, Lower = BBL_20_2.0
            upper_band = h1['BBU_20_2.0'].iloc[-1]
            lower_band = h1['BBL_20_2.0'].iloc[-1]
            current_close = h1['close'].iloc[-1]
            
            volatility = (upper_band - lower_band) / current_close
        except KeyError:
            volatility = 0

        if volatility > 0.05 and regime == 'Ranging':
            trade_type = 'Scalping'
        elif regime == 'Trending':
            trade_type = 'Swing Trading'
        else:
            trade_type = 'Day Trading'

        # Calculate Confidence Score
        # (Using a simple float calculation as requested)
        score = 0
        if bullish_h1: score += 1
        if bullish_h4: score += 1
        if bullish_d1: score += 1
        if sentiment > 0: score += 1
        
        confidence = score / 4.0

        return {
            'ticker': ticker, 
            'side': side, 
            'type': trade_type, 
            'confidence': confidence
        }
