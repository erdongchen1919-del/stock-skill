import pandas as pd
import numpy as np

def compute_atr(df, window=14):
    # df columns: ['open','high','low','close']
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window).mean()
    return atr

def rank_by_momentum(price_df, lookback=20):
    # price_df: DataFrame columns = tickers, index = dates, values = close
    returns = price_df.pct_change(lookback)
    latest = returns.iloc[-1]
    ranks = latest.sort_values(ascending=False)
    return ranks

def generate_signals(price_history, ohlc_dict, cfg):
    lookback = cfg['strategy'].get('lookback_days', 20)
    top_n = cfg['strategy'].get('top_n', 10)
    ranks = rank_by_momentum(price_history, lookback)
    selected = list(ranks.index[:top_n])
    signals = {t: (1 if t in selected else 0) for t in price_history.columns}
    atrs = {}
    for t in selected:
        df = ohlc_dict.get(t)
        if df is not None and len(df) >= 14:
            atrs[t] = compute_atr(df).iloc[-1]
        else:
            atrs[t] = 0.0
    return signals, atrs
