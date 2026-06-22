import numpy as np
import pandas as pd

from curve_alpha.utils import percentile_score


def calc_momentum_features(
    price: pd.DataFrame
) -> pd.DataFrame:

    expected_cols = [
        "ticker",
        "ret_1m",
        "ret_3m",
        "ret_6m",
        "ret_12m",
        "dist_52w_high",
        "vol_1y",
        "max_drawdown",
    ]

    if price is None:
        return pd.DataFrame(columns=expected_cols)

    if len(price) == 0:
        return pd.DataFrame(columns=expected_cols)

    if "ticker" not in price.columns:
        print(
            "[MOMENTUM] ticker column missing:",
            price.columns.tolist()
        )
        return pd.DataFrame(columns=expected_cols)

    if "date" not in price.columns:
        print(
            "[MOMENTUM] date column missing:",
            price.columns.tolist()
        )
        return pd.DataFrame(columns=expected_cols)

    if "close" not in price.columns:
        print(
            "[MOMENTUM] close column missing:",
            price.columns.tolist()
        )
        return pd.DataFrame(columns=expected_cols)

    p = price.copy()

    p["date"] = pd.to_datetime(
        p["date"],
        errors="coerce"
    )

    p["close"] = pd.to_numeric(
        p["close"],
        errors="coerce"
    )

    p = p.dropna(
        subset=[
            "ticker",
            "date",
            "close"
        ]
    )

    if len(p) == 0:
        return pd.DataFrame(columns=expected_cols)

    p = p.sort_values(
        [
            "ticker",
            "date"
        ]
    )

    rows = []

    for ticker, g in p.groupby("ticker"):

        g = g.sort_values("date")

        close = g["close"].astype(float)

        if len(close) < 2:
            continue

        def calc_return(days):

            if len(close) <= days:
                return np.nan

            try:
                return (
                    close.iloc[-1]
                    /
                    close.iloc[-(days + 1)]
                    - 1
                )
            except Exception:
                return np.nan

        ret_1m = calc_return(21)
        ret_3m = calc_return(63)
        ret_6m = calc_return(126)
        ret_12m = calc_return(252)

        try:
            high_52w = close.max()

            dist_52w_high = (
                close.iloc[-1]
                /
                high_52w
                - 1
            )

        except Exception:

            dist_52w_high = np.nan

        returns = close.pct_change().dropna()

        try:

            vol_1y = (
                returns.std()
                *
                np.sqrt(252)
            )

        except Exception:

            vol_1y = np.nan

        try:

            drawdown = (
                close
                /
                close.cummax()
                - 1
            )

            max_drawdown = drawdown.min()

        except Exception:

            max_drawdown = np.nan

        rows.append(
            {
                "ticker": ticker,
                "ret_1m": ret_1m,
                "ret_3m": ret_3m,
                "ret_6m": ret_6m,
                "ret_12m": ret_12m,
                "dist_52w_high": dist_52w_high,
                "vol_1y": vol_1y,
                "max_drawdown": max_drawdown,
            }
        )

    if len(rows) == 0:

        return pd.DataFrame(
            columns=expected_cols
        )

    out = pd.DataFrame(rows)

    return out


def momentum_score(
    df: pd.DataFrame
) -> pd.Series:

    score_parts = []

    factors = [
        "ret_1m",
        "ret_3m",
        "ret_6m",
        "ret_12m",
        "dist_52w_high",
    ]

    for factor in factors:

        if factor in df.columns:

            score_parts.append(
                percentile_score(
                    df[factor],
                    higher_is_better=True
                )
            )

    if len(score_parts) == 0:

        return pd.Series(
            50,
            index=df.index
        )

    return (
        pd.concat(
            score_parts,
            axis=1
        )
        .mean(axis=1)
        .clip(0, 100)
    )
