import numpy as np
import pandas as pd
from curve_alpha.utils import percentile_score

def calc_momentum_features(price: pd.DataFrame) -> pd.DataFrame:
    if price.empty:
        return pd.DataFrame(columns=["ticker", "ret_1m", "ret_3m", "ret_6m", "ret_12m", "dist_52w_high", "vol_1y", "max_drawdown"])
    p = price.copy()
    p["date"] = pd.to_datetime(p["date"])
    p = p.sort_values(["ticker", "date"])
    rows = []
    for ticker, g in p.groupby("ticker"):
        close = g["close"].astype(float).dropna()
        if len(close) < 2:
            continue
        def ret(n):
            return close.iloc[-1] / close.iloc[-n] - 1 if len(close) >= n else np.nan
        high = close.max()
        dist_high = close.iloc[-1] / high - 1 if high else np.nan
        rets = close.pct_change().dropna()
        vol = rets.std() * np.sqrt(252) if len(rets) > 2 else np.nan
        dd = close / close.cummax() - 1
        rows.append({
            "ticker": ticker,
            "ret_1m": ret(21),
            "ret_3m": ret(63),
            "ret_6m": ret(126),
            "ret_12m": ret(252),
            "dist_52w_high": dist_high,
            "vol_1y": vol,
            "max_drawdown": dd.min(),
        })
    return pd.DataFrame(rows)

def momentum_score(df: pd.DataFrame) -> pd.Series:
    scores = []
    for c in ["ret_1m", "ret_3m", "ret_6m", "ret_12m", "dist_52w_high"]:
        if c in df.columns:
            scores.append(percentile_score(df[c], True))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
