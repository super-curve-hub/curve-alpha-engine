import pandas as pd
import yfinance as yf


def load_fundamentals(tickers):
    return pd.DataFrame(
        {
            "ticker": tickers
        }
    )


def load_price_history(
    tickers,
    period="1y",
    interval="1d"
):

    ticker = tickers[0]

    px = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    print("STEP1")
    print(type(px.columns))
    print(px.columns)

    if isinstance(px.columns, pd.MultiIndex):
        px.columns = px.columns.get_level_values(0)

    print("STEP2")
    print(type(px.columns))
    print(px.columns)

    px = px.reset_index()

    out = pd.DataFrame(
        {
            "ticker": [ticker] * len(px),
            "date": px["Date"].values,
            "close": px["Close"].values,
        }
    )

    print("STEP3")
    print(type(out.columns))
    print(out.columns)

    print("STEP4")
    print(out.head())

    return out
