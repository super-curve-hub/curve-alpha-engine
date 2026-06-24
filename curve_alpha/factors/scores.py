import numpy as np
import pandas as pd


def winsorize_series(s, lower=0.05, upper=0.95):
    """
    外れ値を上下分位で丸める。
    """
    s = pd.to_numeric(s, errors="coerce")

    if s.notna().sum() <= 1:
        return s

    lo = s.quantile(lower)
    hi = s.quantile(upper)

    return s.clip(lo, hi)


def percentile_score(s, higher_is_better=True):
    """
    クロスセクションで0〜100点化する。
    """
    s = pd.to_numeric(s, errors="coerce")

    if s.notna().sum() <= 1:
        return pd.Series(np.nan, index=s.index)

    pct = s.rank(pct=True) * 100

    if not higher_is_better:
        pct = 100 - pct

    return pct


def add_factor_scores(df):
    """
    quality / value / growth / leverage / squeeze の5スコアを追加する。
    """

    df = df.copy()

    numeric_cols = [
        "market_cap",
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "profit_margin",
        "revenue_growth",
        "earnings_growth",
        "pe",
        "forward_pe",
        "pb",
        "ev_ebitda",
        "ev_sales",
        "fcf_yield",
        "debt_to_equity",
        "beta",
        "short_ratio",
        "short_percent_float",
        "held_percent_institutions",
        "held_percent_insiders",
        "revenue",
        "ebitda",
        "total_debt",
        "total_cash",
        "net_debt",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "net_debt" in df.columns and "ebitda" in df.columns:
        df["net_debt_to_ebitda"] = np.where(
            (df["ebitda"].notna()) & (df["ebitda"] > 0),
            df["net_debt"] / df["ebitda"],
            np.nan,
        )
    else:
        df["net_debt_to_ebitda"] = np.nan

    if "total_cash" in df.columns and "total_debt" in df.columns:
        df["cash_to_debt"] = np.where(
            (df["total_debt"].notna()) & (df["total_debt"] > 0),
            df["total_cash"] / df["total_debt"],
            np.nan,
        )
    else:
        df["cash_to_debt"] = np.nan

    factor_input_cols = [
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "profit_margin",
        "revenue_growth",
        "earnings_growth",
        "pe",
        "forward_pe",
        "pb",
        "ev_ebitda",
        "ev_sales",
        "fcf_yield",
        "debt_to_equity",
        "net_debt_to_ebitda",
        "cash_to_debt",
        "beta",
        "short_ratio",
        "short_percent_float",
        "held_percent_institutions",
        "held_percent_insiders",
    ]

    for col in factor_input_cols:
        if col in df.columns:
            df[f"{col}_w"] = winsorize_series(df[col])

    quality_parts = []

    for col in [
        "roe_w",
        "roa_w",
        "gross_margin_w",
        "operating_margin_w",
        "profit_margin_w",
    ]:
        if col in df.columns:
            quality_parts.append(percentile_score(df[col], higher_is_better=True))

    df["quality_score"] = (
        pd.concat(quality_parts, axis=1).mean(axis=1)
        if quality_parts
        else np.nan
    )

    value_parts = []

    for col in [
        "pe_w",
        "forward_pe_w",
        "pb_w",
        "ev_ebitda_w",
        "ev_sales_w",
    ]:
        if col in df.columns:
            value_parts.append(percentile_score(df[col], higher_is_better=False))

    if "fcf_yield_w" in df.columns:
        value_parts.append(percentile_score(df["fcf_yield_w"], higher_is_better=True))

    df["value_score"] = (
        pd.concat(value_parts, axis=1).mean(axis=1)
        if value_parts
        else np.nan
    )

    growth_parts = []

    for col in [
        "revenue_growth_w",
        "earnings_growth_w",
    ]:
        if col in df.columns:
            growth_parts.append(percentile_score(df[col], higher_is_better=True))

    df["growth_score"] = (
        pd.concat(growth_parts, axis=1).mean(axis=1)
        if growth_parts
        else np.nan
    )

    leverage_parts = []

    for col in [
        "debt_to_equity_w",
        "net_debt_to_ebitda_w",
    ]:
        if col in df.columns:
            leverage_parts.append(percentile_score(df[col], higher_is_better=False))

    if "cash_to_debt_w" in df.columns:
        leverage_parts.append(percentile_score(df["cash_to_debt_w"], higher_is_better=True))

    df["leverage_score"] = (
        pd.concat(leverage_parts, axis=1).mean(axis=1)
        if leverage_parts
        else np.nan
    )

    squeeze_parts = []

    for col in [
        "short_ratio_w",
        "short_percent_float_w",
        "held_percent_institutions_w",
        "held_percent_insiders_w",
        "beta_w",
    ]:
        if col in df.columns:
            squeeze_parts.append(percentile_score(df[col], higher_is_better=True))

    df["squeeze_score"] = (
        pd.concat(squeeze_parts, axis=1).mean(axis=1)
        if squeeze_parts
        else np.nan
    )

    df["composite_score"] = (
        0.30 * df["quality_score"] +
        0.25 * df["value_score"] +
        0.20 * df["growth_score"] +
        0.15 * df["leverage_score"] +
        0.10 * df["squeeze_score"]
    )

    df["factor_regime"] = np.select(
        [
            (df["quality_score"] >= 70) & (df["value_score"] >= 70),
            (df["growth_score"] >= 75) & (df["quality_score"] >= 60),
            (df["value_score"] >= 75) & (df["quality_score"] < 50),
            (df["squeeze_score"] >= 80) & (df["short_percent_float"] > 0.05),
            (df["leverage_score"] < 30),
        ],
        [
            "Quality Value",
            "Quality Growth",
            "Deep Value / Possible Trap",
            "Squeeze Candidate",
            "Leveraged Balance Sheet",
        ],
        default="Neutral",
    )

    return df


def rank_factor_candidates(scored_df, top_n=30):
    """
    ファクター別に上位候補を抽出する。
    """

    df = scored_df.copy()

    output = {
        "quality_top": df.sort_values("quality_score", ascending=False).head(top_n),
        "value_top": df.sort_values("value_score", ascending=False).head(top_n),
        "growth_top": df.sort_values("growth_score", ascending=False).head(top_n),
        "low_leverage_top": df.sort_values("leverage_score", ascending=False).head(top_n),
        "squeeze_top": df.sort_values("squeeze_score", ascending=False).head(top_n),
        "composite_top": df.sort_values("composite_score", ascending=False).head(top_n),
    }

    return output