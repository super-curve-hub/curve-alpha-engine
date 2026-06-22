import pandas as pd
from curve_alpha.utils import percentile_score

def flow_score(df: pd.DataFrame) -> pd.Series:
    scores = []
    if "held_percent_institutions" in df.columns:
        scores.append(percentile_score(df["held_percent_institutions"], True))
    if "held_percent_insiders" in df.columns:
        scores.append(percentile_score(df["held_percent_insiders"], True))
    if "short_percent_float" in df.columns:
        scores.append(percentile_score(df["short_percent_float"], False))
    if "short_ratio" in df.columns:
        scores.append(percentile_score(df["short_ratio"], False))
    if "buyback_yield" in df.columns:
        scores.append(percentile_score(df["buyback_yield"], True))
    if not scores:
        return pd.Series(50, index=df.index)
    return pd.concat(scores, axis=1).mean(axis=1).clip(0, 100)
