import pandas as pd
import yfinance as yf


def load_fundamentals(tickers):
    return pd.DataFrame(
        columns=[
            "ticker"
        ]
    )


def load_price_history(
    tickers,
    period="1y",
    interval="1d"
):

    print("NEW YF_LOADER LOADED")

    out = pd.DataFrame(
        {
            "ticker": ["NVDA"],
            "date": ["2025-01-01"],
            "close": [100.0],
        }
    )

    return out
