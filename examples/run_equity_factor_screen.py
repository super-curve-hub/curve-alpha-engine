import sys
from pathlib import Path

import pandas as pd

# examples/ 配下から直接実行しても curve_alpha を import できるようにする
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from curve_alpha.data.yf_loader import load_fundamentals
from curve_alpha.factors.scores import add_factor_scores, rank_factor_candidates


def load_universe(csv_path):
    """
    universe_default.csv から銘柄リストを読み込む。

    対応列:
    - ticker
    - symbol
    - code
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Universe file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    candidate_cols = ["ticker", "symbol", "code"]
    ticker_col = None

    for col in candidate_cols:
        if col in df.columns:
            ticker_col = col
            break

    if ticker_col is None:
        raise ValueError(
            f"Universe CSV must contain one of columns: {candidate_cols}. "
            f"Current columns: {list(df.columns)}"
        )

    tickers = (
        df[ticker_col]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if not tickers:
        raise ValueError(f"No tickers found in {csv_path}")

    return tickers


def save_output(scored, output_dir):
    """
    総合スコア順の実務用ランキングだけをCSV保存する。

    保存先:
    output/equity_factor_screen.csv

    保存対象:
    - スコア列
    - 主要ファンダメンタルズ列
    - 需給・レバレッジ列

    保存しないもの:
    - *_w などのwinsorize済み中間列
    - net_debt_to_ebitda などの内部計算補助列
    - cash_to_debt などの内部計算補助列
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "equity_factor_screen.csv"

    output_cols = [
        # ranking
        "ticker",
        "composite_score",
        "factor_regime",
        "quality_score",
        "value_score",
        "growth_score",
        "leverage_score",
        "squeeze_score",

        # size
        "market_cap",

        # quality
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "profit_margin",

        # growth
        "revenue_growth",
        "earnings_growth",

        # value
        "pe",
        "forward_pe",
        "pb",
        "ev_ebitda",
        "ev_sales",
        "fcf_yield",

        # leverage / balance sheet
        "debt_to_equity",
        "total_debt",
        "total_cash",
        "net_debt",

        # flow / squeeze
        "short_ratio",
        "short_percent_float",
        "held_percent_institutions",
        "held_percent_insiders",
        "beta",

        # status
        "error",
    ]

    existing_cols = [c for c in output_cols if c in scored.columns]

    result = (
        scored[existing_cols]
        .sort_values("composite_score", ascending=False)
        .reset_index(drop=True)
    )

    result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def main():
    universe_path = ROOT_DIR / "universe_default.csv"
    output_dir = ROOT_DIR / "output"

    print("=== Load universe ===")
    tickers = load_universe(universe_path)

    print(f"Universe file: {universe_path}")
    print(f"Number of tickers: {len(tickers)}")
    print(f"First tickers: {tickers[:10]}")

    print("\n=== Load fundamentals ===")
    fund = load_fundamentals(tickers)

    show_fund_cols = [
        "ticker",
        "market_cap",
        "roe",
        "roa",
        "pe",
        "forward_pe",
        "pb",
        "ev_ebitda",
        "ev_sales",
        "fcf_yield",
        "debt_to_equity",
        "total_debt",
        "total_cash",
        "net_debt",
        "error",
    ]

    existing_fund_cols = [c for c in show_fund_cols if c in fund.columns]

    print("\n--- Fundamentals ---")
    print(fund[existing_fund_cols].to_string(index=False))

    print("\n=== Add factor scores ===")
    scored = add_factor_scores(fund)

    score_cols = [
        "ticker",
        "quality_score",
        "value_score",
        "growth_score",
        "leverage_score",
        "squeeze_score",
        "composite_score",
        "factor_regime",
    ]

    print("\n--- Composite Ranking ---")
    composite_ranking = (
        scored[score_cols]
        .sort_values("composite_score", ascending=False)
    )
    print(composite_ranking.to_string(index=False))

    print("\n=== Rank candidates ===")
    ranked = rank_factor_candidates(scored, top_n=10)

    sections = [
        ("Quality Top", "quality_top"),
        ("Value Top", "value_top"),
        ("Growth Top", "growth_top"),
        ("Low Leverage Top", "low_leverage_top"),
        ("Squeeze Top", "squeeze_top"),
        ("Composite Top", "composite_top"),
    ]

    for title, key in sections:
        print(f"\n--- {title} ---")
        print(ranked[key][score_cols].to_string(index=False))

    print("\n=== Save output ===")
    output_path = save_output(scored, output_dir)
    print(f"saved: {output_path}")

    print("\nOK: equity factor screen finished")


if __name__ == "__main__":
    main()