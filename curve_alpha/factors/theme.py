import pandas as pd

THEME_KEYWORDS = {
    "ai": 100,
    "semiconductor": 95,
    "datacenter": 92,
    "power": 88,
    "space": 86,
    "satellite": 84,
    "defense": 82,
    "cloud": 80,
    "network": 78,
    "copper": 76,
    "shipping": 72,
    "lng": 72,
    "robotics": 70,
}

def score_tags(tags):
    if not isinstance(tags, str) or not tags.strip():
        return 50
    parts = [x.strip().lower() for x in tags.split(";") if x.strip()]
    if not parts:
        return 50
    return sum(THEME_KEYWORDS.get(x, 50) for x in parts) / len(parts)

def theme_score(df: pd.DataFrame) -> pd.Series:
    if "theme_tags" not in df.columns:
        return pd.Series(50, index=df.index)
    return df["theme_tags"].apply(score_tags).clip(0, 100)
