import pandas as pd

from curve_alpha.factors.quality import quality_score
from curve_alpha.factors.value import value_score
from curve_alpha.factors.momentum import (
    calc_momentum_features,
    momentum_score,
)
from curve_alpha.factors.risk import risk_score
from curve_alpha.factors.flow import flow_score
from curve_alpha.factors.theme import theme_score
from curve_alpha.macro.beta import (
    macro_beta_features,
    macro_score,
)
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


def build_ranking(
    universe: pd.DataFrame,
    fundamentals: pd.DataFrame,
    prices: pd.DataFrame,
    weights=None,
) -> pd.DataFrame:

    print("\n========== DEBUG ==========")

    print("UNIVERSE COLS")
    print(universe.columns.tolist())

    print("FUNDAMENTALS COLS")
    print(fundamentals.columns.tolist())

    print("PRICES COLS")
    print(prices.columns.tolist())

    if "ticker" not in universe.columns:
        raise ValueError(
            f"ticker missing in universe: {universe.columns.tolist()}"
        )

    if "ticker" not in fundamentals.columns:
        raise ValueError(
            f"ticker missing in fundamentals: {fundamentals.columns.tolist()}"
        )

    if "ticker" not in prices.columns:
        raise ValueError(
            f"ticker missing in prices: {prices.columns.tolist()}"
        )

    weights = weights or DEFAULT_WEIGHTS

    # --------------------------------------------------
    # Merge fundamentals
    # --------------------------------------------------

    df = universe.merge(
        fundamentals,
        on="ticker",
        how="left",
    )

    print("MERGE1 OK")

    # --------------------------------------------------
    # Momentum
    # --------------------------------------------------

    mom = calc_momentum_features(prices)

    if mom.empty:
        mom = pd.DataFrame(
            columns=[
                "ticker",
                "ret_1m",
                "ret_3m",
                "ret_6m",
                "ret_12m",
                "dist_52w_high",
                "vol_1y",
                "max_drawdown",
            ]
        )

    print("MOM COLS")
    print(mom.columns.tolist())

    if "ticker" not in mom.columns:
        raise ValueError(
            f"ticker missing in mom: {mom.columns.tolist()}"
        )

    df = df.merge(
        mom,
        on="ticker",
        how="left",
    )

    print("MERGE2 OK")

    # --------------------------------------------------
    # Macro
    # --------------------------------------------------

    mb = macro_beta_features(prices)

    if mb.empty:
        mb = pd.DataFrame(
            columns=[
                "ticker",
                "macro_beta_proxy",
            ]
        )

    print("MB COLS")
    print(mb.columns.tolist())

    if "ticker" not in mb.columns:
        raise ValueError(
            f"ticker missing in mb: {mb.columns.tolist()}"
        )

    df = df.merge(
        mb,
        on="ticker",
        how="left",
    )

    print("MERGE3 OK")

    # --------------------------------------------------
    # Factor Scores
    # --------------------------------------------------

    df["quality_score"] = quality_score(df)
    df["value_score"] = value_score(df)
    df["momentum_score"] = momentum_score(df)
    df["risk_score"] = risk_score(df)
    df["macro_score"] = macro_score(df)
    df["flow_score"] = flow_score(df)
    df["theme_score"] = theme_score(df)

    # --------------------------------------------------
    # Total Score
    # --------------------------------------------------

    df["curve_alpha_score"] = (
        weights["quality"] * df["quality_score"]
        + weights["value"] * df["value_score"]
        + weights["momentum"] * df["momentum_score"]
        + weights["risk"] * df["risk_score"]
        + weights["macro"] * df["macro_score"]
        + weights["flow"] * df["flow_score"]
        + weights["theme"] * df["theme_score"]
    ).round(2)

    df["rating"] = df["curve_alpha_score"].apply(rating)

    cols = [
        "ticker",
        "name",
        "sector",
        "theme_tags",
        "curve_alpha_score",
        "rating",
        "quality_score",
        "value_score",
        "momentum_score",
        "risk_score",
        "macro_score",
        "flow_score",
        "theme_score",
        "market_cap",
        "pe",
        "forward_pe",
        "pb",
        "ev_ebitda",
        "ev_sales",
        "roe",
        "operating_margin",
        "revenue_growth",
        "fcf_yield",
        "ret_1m",
        "ret_3m",
        "ret_6m",
        "ret_12m",
        "vol_1y",
        "max_drawdown",
    ]

    cols = [c for c in cols if c in df.columns]

    return (
        df[cols]
        .sort_values(
            "curve_alpha_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )
