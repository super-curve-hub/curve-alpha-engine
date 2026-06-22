import pandas as pd
from pathlib import Path
from curve_alpha.data.yf_loader import load_fundamentals, load_price_history

def load_universe(path="universe_default.csv"):
    return pd.read_csv(path)

def load_all_data(universe, price_period="1y", price_interval="1d"):
    tickers = universe["ticker"].dropna().astype(str).unique().tolist()
    fundamentals = load_fundamentals(tickers)
    prices = load_price_history(tickers, period=price_period, interval=price_interval)
    return fundamentals, prices
