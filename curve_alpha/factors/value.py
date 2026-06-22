import pandas as pd
from curve_alpha.utils import percentile_score

def value_score(df: pd.DataFrame) -> pd.Series:
    scores = []
    lower_better = ["pe", "forward_pe", "pb", "ev_ebitda", "ev_sales"]
    for c in lower_better:
        if c in df.columns:
            scores.append(percentile_score(df[c], False))
    if "fcf_yield" in df.columns:
        scores.append(percentile_score(df["fcf_yield"], True))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
