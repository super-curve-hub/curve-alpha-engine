import time
import pandas as pd
import yfinance as yf

def load_price_history(
    tickers,
    period="1y",
    interval="1d"
):
    frames = []

    for t in tickers:

        try:

            px = yf.download(
                t,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                group_by="column",
            )

            if px.empty:
                continue

            if isinstance(px.columns, pd.MultiIndex):
                px.columns = px.columns.get_level_values(0)

            px = px.reset_index()

            date_col = (
                "Date"
                if "Date" in px.columns
                else px.columns[0]
            )

            px = px.rename(
                columns={
                    date_col: "date",
                    "Close": "close",
                }
            )

            px["ticker"] = t

            frames.append(
                px[
                    [
                        "ticker",
                        "date",
                        "close",
                    ]
                ]
            )

            time.sleep(0.05)

        except Exception as e:
            print("PRICE ERROR", t, e)

    if not frames:

        return pd.DataFrame(
            columns=[
                "ticker",
                "date",
                "close",
            ]
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )
