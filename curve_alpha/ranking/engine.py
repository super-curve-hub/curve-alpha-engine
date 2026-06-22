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

    print("\n========== CURVE ALPHA DEBUG ==========")

    print("UNIVERSE:", universe.shape)
    print("FUNDAMENTALS:", fundamentals.shape)
    print("PRICES:", prices.shape)

    weights = weights or DEFAULT_WEIGHTS

    # ------------------------------------
    # Required Columns Check
    # ------------------------------------

    for name, df in {
        "universe": universe,
        "fundamentals": fundamentals,
        "prices": prices,
    }.items():

        if "ticker" not in df.columns:

            raise ValueError(
                f"{name} missing ticker column\n"
                f"columns={df.columns.tolist()}"
            )

    # ------------------------------------
    # Deduplicate
    # ------------------------------------

    universe = universe.drop_duplicates(
        subset=["ticker"]
    )

    fundamentals = fundamentals.drop_duplicates(
        subset=["ticker"]
    )

    # ------------------------------------
    # Base Merge
    # ------------------------------------

    df = universe.merge(
        fundamentals,
        on="ticker",
        how="left",
    )

    print("MERGE FUNDAMENTALS OK")

    # ------------------------------------
    # Momentum
    # ------------------------------------

    mom = calc_momentum_features(prices)

    if mom is None or len(mom) == 0:

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

    if "ticker" not in mom.columns:

        raise ValueError(
            f"Momentum output invalid:\n"
            f"{mom.columns.tolist()}"
        )

    mom = mom.drop_duplicates(
        subset=["ticker"]
    )

    df = df.merge(
        mom,
        on="ticker",
        how="left",
    )

    print("MERGE MOMENTUM OK")

    # ------------------------------------
    # Macro
    # ------------------------------------

    mb = macro_beta_features(prices)

    if mb is None or len(mb) == 0:

        mb = pd.DataFrame(
            columns=[
                "ticker",
                "macro_beta_proxy",
            ]
        )

    if "ticker" not in mb.columns:

        raise ValueError(
            f"Macro output invalid:\n"
            f"{mb.columns.tolist()}"
        )

    mb = mb.drop_duplicates(
        subset=["ticker"]
    )

    df = df.merge(
        mb,
        on="ticker",
        how="left",
    )

    print("MERGE MACRO OK")

    # ------------------------------------
    # Factor Scores
    # ------------------------------------

    df["quality_score"] = quality_score(df)
    df["value_score"] = value_score(df)
    df["momentum_score"] = momentum_score(df)
    df["risk_score"] = risk_score(df)
    df["macro_score"] = macro_score(df)
    df["flow_score"] = flow_score(df)
    df["theme_score"] = theme_score(df)

    score_cols = [
        "quality_score",
        "value_score",
        "momentum_score",
        "risk_score",
        "macro_score",
        "flow_score",
        "theme_score",
    ]

    df[score_cols] = df[score_cols].fillna(50)

    # ------------------------------------
    # Composite Score
    # ------------------------------------

    df["curve_alpha_score"] = (
        weights["quality"] * df["quality_score"]
        + weights["value"] * df["value_score"]
        + weights["momentum"] * df["momentum_score"]
        + weights["risk"] * df["risk_score"]
        + weights["macro"] * df["macro_score"]
        + weights["flow"] * df["flow_score"]
        + weights["theme"] * df["theme_score"]
    ).round(2)

    df["curve_alpha_score"] = (
        df["curve_alpha_score"]
        .fillna(50)
    )

    df["rating"] = (
        df["curve_alpha_score"]
        .apply(rating)
    )

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

    cols = [
        c
        for c in cols
        if c in df.columns
    ]

    out = (
        df[cols]
        .sort_values(
            "curve_alpha_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print(
        "\nRANKING COMPLETE:",
        len(out),
        "stocks"
    )

    return out
