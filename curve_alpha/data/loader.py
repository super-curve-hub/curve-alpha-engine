import time
import pandas as pd
import yfinance as yf


def load_price_history(
    tickers,
    period="1y",
    interval="1d"
):

    all_rows = []

    for ticker in tickers:

        try:

            px = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if px.empty:
                continue

            # yfinance MultiIndex対策
            if isinstance(px.columns, pd.MultiIndex):

                px.columns = [
                    str(col[0])
                    for col in px.columns
                ]

            px = px.reset_index()

            # Date列検出
            date_col = None

            for col in px.columns:

                if str(col).lower() in [
                    "date",
                    "datetime",
                ]:

                    date_col = col
                    break

            if date_col is None:

                print(
                    "DATE COLUMN NOT FOUND:",
                    ticker
                )

                continue

            # Close列検出
            close_col = None

            for col in px.columns:

                if str(col).lower() == "close":

                    close_col = col
                    break

            if close_col is None:

                print(
                    "CLOSE COLUMN NOT FOUND:",
                    ticker
                )

                continue

            tmp = pd.DataFrame()

            tmp["ticker"] = ticker

            tmp["date"] = pd.to_datetime(
                px[date_col],
                errors="coerce"
            )

            tmp["close"] = pd.to_numeric(
                px[close_col],
                errors="coerce"
            )

            tmp = tmp.dropna(
                subset=[
                    "ticker",
                    "date",
                    "close",
                ]
            )

            all_rows.append(tmp)

            time.sleep(0.05)

        except Exception as e:

            print(
                "PRICE ERROR:",
                ticker,
                str(e)
            )

    if len(all_rows) == 0:

        return pd.DataFrame(
            columns=[
                "ticker",
                "date",
                "close",
            ]
        )

    out = pd.concat(
        all_rows,
        ignore_index=True,
    )

    # 念のため列名統一
    out.columns = [
        str(col).lower()
        for col in out.columns
    ]

    return out[
        [
            "ticker",
            "date",
            "close",
        ]
    ]
