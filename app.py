import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import plotly.express as px

from curve_alpha.data.loader import load_all_data
from curve_alpha.ranking.engine import build_ranking
from curve_alpha.report.note import make_top20_markdown

st.set_page_config(page_title="Curve Alpha Engine", layout="wide")

BASE = Path(__file__).resolve().parent

st.title("Curve Alpha Engine v2")
st.caption("Quality / Value / Momentum / Risk / Macro / Flow / Theme 統合ランキング")

with open(BASE / "config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

uploaded = st.sidebar.file_uploader("Universe CSV", type=["csv"])
if uploaded:
    universe = pd.read_csv(uploaded)
else:
    universe = pd.read_csv(BASE / "universe_default.csv")

st.sidebar.write("銘柄数", len(universe))
run = st.sidebar.button("ランキング生成")

if run:
    with st.spinner("yfinanceからデータ取得中..."):
        fundamentals, prices = load_all_data(
            universe,
            price_period=config.get("lookback", {}).get("price_period", "1y"),
            price_interval=config.get("lookback", {}).get("price_interval", "1d"),
        )
        ranking = build_ranking(universe, fundamentals, prices, weights=config["weights"])

    st.subheader("Curve Alpha Ranking")
    st.dataframe(ranking, use_container_width=True)

    top = ranking.head(20)
    fig = px.bar(
        top.sort_values("curve_alpha_score"),
        x="curve_alpha_score",
        y="ticker",
        orientation="h",
        title="Top20 Curve Alpha Score",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Factor Map")
    factor_cols = [
        "quality_score",
        "value_score",
        "momentum_score",
        "risk_score",
        "macro_score",
        "flow_score",
        "theme_score",
    ]
    st.dataframe(ranking[["ticker"] + factor_cols].head(30), use_container_width=True)

    csv = ranking.to_csv(index=False).encode("utf-8-sig")
    st.download_button("CSVダウンロード", csv, "curve_alpha_ranking.csv", "text/csv")

    md = make_top20_markdown(ranking)
    st.download_button("note用Markdownダウンロード", md.encode("utf-8"), "monthly_top20.md", "text/markdown")

else:
    st.info("左のボタンからランキングを生成してください。")
    st.dataframe(universe, use_container_width=True)
