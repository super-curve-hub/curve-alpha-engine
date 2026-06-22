import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from curve_alpha.utils import percentile_score

def macro_beta_features(price: pd.DataFrame, macro_price: pd.DataFrame | None = None) -> pd.DataFrame:
    # MVP: 外部マクロ系列が無い場合は、低ボラ・高モメンタムをマクロ耐性の代替値にする。
    if price.empty:
        return pd.DataFrame(columns=["ticker", "macro_beta_proxy"])
    rows = []
    p = price.copy()
    p["date"] = pd.to_datetime(p["date"])
    for ticker, g in p.groupby("ticker"):
        close = g.sort_values("date")["close"].astype(float)
        r = close.pct_change().dropna()
        if len(r) < 20:
            rows.append({"ticker": ticker, "macro_beta_proxy": np.nan})
            continue
        macro_beta_proxy = -r.std() * np.sqrt(252)
        rows.append({"ticker": ticker, "macro_beta_proxy": macro_beta_proxy})
    return pd.DataFrame(rows)

def macro_score(df: pd.DataFrame) -> pd.Series:
    scores = []
    if "macro_beta_proxy" in df.columns:
        scores.append(percentile_score(df["macro_beta_proxy"], True))
    if "revenue_growth" in df.columns:
        scores.append(percentile_score(df["revenue_growth"], True))
    if "debt_to_equity" in df.columns:
        scores.append(percentile_score(df["debt_to_equity"], False))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
