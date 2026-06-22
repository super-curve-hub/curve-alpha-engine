from pathlib import Path
import yaml
from curve_alpha.data.loader import load_universe, load_all_data
from curve_alpha.ranking.engine import build_ranking
from curve_alpha.report.note import make_top20_markdown

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

with open(BASE / "config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

universe = load_universe(BASE / "universe_default.csv")
fundamentals, prices = load_all_data(
    universe,
    price_period=config.get("lookback", {}).get("price_period", "1y"),
    price_interval=config.get("lookback", {}).get("price_interval", "1d"),
)

print("\n=== UNIVERSE ===")
print(universe.head())
print(universe.columns)

print("\n=== FUNDAMENTALS ===")
print(fundamentals.head())
print(fundamentals.columns)

print("\n=== PRICES ===")
print(prices.head())
print(prices.columns)
ranking = build_ranking(universe, fundamentals, prices, weights=config["weights"])
ranking.to_csv(OUT / "curve_alpha_ranking.csv", index=False)

md = make_top20_markdown(ranking)
(OUT / "monthly_top20.md").write_text(md, encoding="utf-8")

print(ranking[["ticker", "curve_alpha_score", "rating"]].head(20).to_string(index=False))
print(f"Saved: {OUT / 'curve_alpha_ranking.csv'}")
print(f"Saved: {OUT / 'monthly_top20.md'}")
