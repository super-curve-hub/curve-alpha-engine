import sys
from pathlib import Path

# examples/ 配下から直接実行しても curve_alpha を import できるようにする
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from curve_alpha.data.yf_loader import load_fundamentals
from curve_alpha.factors.scores import add_factor_scores, rank_factor_candidates


def main():
    tickers = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA",
        "7203.T",
        "9984.T",
        "8035.T",
    ]

    print("=== Load fundamentals ===")
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
    ranked = rank_factor_candidates(scored, top_n=5)

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

    print("\nOK: equity factor screen finished")


if __name__ == "__main__":
    main()