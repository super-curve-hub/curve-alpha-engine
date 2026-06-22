import numpy as np
import pandas as pd

def percentile_score(s: pd.Series, higher_is_better: bool = True) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    r = x.rank(pct=True)
    if not higher_is_better:
        r = 1 - r
    return (r * 100).fillna(50).clip(0, 100)

def safe_get(d: dict, key: str, default=None):
    try:
        v = d.get(key, default)
        return default if v is None else v
    except Exception:
        return default

def rating(score: float) -> str:
    if score >= 90:
        return "Strong Buy"
    if score >= 80:
        return "Buy"
    if score >= 70:
        return "Accumulate"
    if score >= 60:
        return "Neutral"
    if score >= 50:
        return "Reduce"
    return "Avoid"
