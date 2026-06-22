import pandas as pd
from curve_alpha.factors.quality import quality_score
from curve_alpha.factors.value import value_score
from curve_alpha.factors.momentum import calc_momentum_features, momentum_score
from curve_alpha.factors.risk import risk_score
from curve_alpha.factors.flow import flow_score
from curve_alpha.factors.theme import theme_score
from curve_alpha.macro.beta import macro_beta_features, macro_score
from curve_alpha.utils import rating

DEFAULT_WEIGHTS = {
    "quality": 0.25,
    "value": 0.20,
    "momentum": 0.20,
    "risk": 0.10,
    "macro": 0.10,
    "flow": 0.05,
    "theme": 0.10,
}

def build_ranking(universe, fundamentals, prices, weights=None):

    print("UNIVERSE")
    print(universe.columns)

    print("FUNDAMENTALS")
    print(fundamentals.columns)

    weights = weights or DEFAULT_WEIGHTS

    df = universe.merge(fundamentals, on="ticker", how="left")
    print("MERGE1 OK")

    mom = calc_momentum_features(prices)

    print("MOM")
    print(mom.columns)

    df = df.merge(mom, on="ticker", how="left")
    print("MERGE2 OK")

    mb = macro_beta_features(prices)

    print("MB")
    print(mb.columns)

    df = df.merge(mb, on="ticker", how="left")
    print("MERGE3 OK")

    df["quality_score"] = quality_score(df)
    df["value_score"] = value_score(df)
    df["momentum_score"] = momentum_score(df)
    df["risk_score"] = risk_score(df)
    df["macro_score"] = macro_score(df)
    df["flow_score"] = flow_score(df)
    df["theme_score"] = theme_score(df)

    df["curve_alpha_score"] = (
        weights["quality"] * df["quality_score"] +
        weights["value"] * df["value_score"] +
        weights["momentum"] * df["momentum_score"] +
        weights["risk"] * df["risk_score"] +
        weights["macro"] * df["macro_score"] +
        weights["flow"] * df["flow_score"] +
        weights["theme"] * df["theme_score"]
    ).round(2)

    df["rating"] = df["curve_alpha_score"].apply(rating)

    cols = [
        "ticker", "name", "sector", "theme_tags",
        "curve_alpha_score", "rating",
        "quality_score", "value_score", "momentum_score",
        "risk_score", "macro_score", "flow_score", "theme_score",
        "market_cap", "pe", "forward_pe", "pb", "ev_ebitda", "ev_sales",
        "roe", "operating_margin", "revenue_growth", "fcf_yield",
        "ret_1m", "ret_3m", "ret_6m", "ret_12m", "vol_1y", "max_drawdown",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].sort_values("curve_alpha_score", ascending=False).reset_index(drop=True)
