import pandas as pd
from curve_alpha.utils import percentile_score

def quality_score(df: pd.DataFrame) -> pd.Series:
    cols_high = [
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "profit_margin",
        "revenue_growth",
        "earnings_growth",
        "fcf_yield",
    ]
    scores = []
    for c in cols_high:
        if c in df.columns:
            scores.append(percentile_score(df[c], True))
    if "debt_to_equity" in df.columns:
        scores.append(percentile_score(df["debt_to_equity"], False))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
