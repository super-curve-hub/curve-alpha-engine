import pandas as pd
from curve_alpha.utils import percentile_score

def risk_score(df: pd.DataFrame) -> pd.Series:
    scores = []
    lower_better = ["beta", "vol_1y", "debt_to_equity", "short_percent_float"]
    for c in lower_better:
        if c in df.columns:
            scores.append(percentile_score(df[c], False))
    if "max_drawdown" in df.columns:
        scores.append(percentile_score(df["max_drawdown"], True))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
