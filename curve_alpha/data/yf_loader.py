import time
import pandas as pd
import yfinance as yf


def safe_get(data, key, default=None):
    try:
        return data.get(key, default)
    except Exception:
        return default


def load_fundamentals(tickers):

    rows = []

    for ticker in tickers:

        try:

            info = yf.Ticker(ticker).info

            rows.append(
                {
                    "ticker": ticker,
                    "market_cap": safe_get(info, "marketCap"),
                    "roe": safe_get(info, "returnOnEquity"),
                    "roa": safe_get(info, "returnOnAssets"),
                    "gross_margin": safe_get(info, "grossMargins"),
                    "operating_margin": safe_get(info, "operatingMargins"),
                    "profit_margin": safe_get(info, "profitMargins"),
                    "revenue_growth": safe_get(info, "revenueGrowth"),
                    "earnings_growth": safe_get(info, "earningsGrowth"),
                    "pe": safe_get(info, "trailingPE"),
                    "forward_pe": safe_get(info, "forwardPE"),
                    "pb": safe_get(info, "priceToBook"),
                    "ev_ebitda": safe_get(info, "enterpriseToEbitda"),
                    "ev_sales": safe_get(info, "enterpriseToRevenue"),
                    "debt_to_equity": safe_get(info, "debtToEquity"),
                    "beta": safe_get(info, "beta"),
                    "short_ratio": safe_get(info, "shortRatio"),
                    "short_percent_float": safe_get(info, "shortPercentOfFloat"),
                    "held_percent_institutions": safe_get(info, "heldPercentInstitutions"),
                    "held_percent_insiders": safe_get(info, "heldPercentInsiders"),
                }
            )

        except Exception as e:

            print(
                "FUNDAMENTAL ERROR:",
                ticker,
                str(e)
            )

        time.sleep(0.05)

    return pd.DataFrame(rows)


def load_price_history(
    tickers,
    period="1y",
    interval="1d"
):

    rows = []

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

            px = px.reset_index()

            date_series = px.iloc[:, 0]

            # MultiIndex対応
            if isinstance(px.columns, pd.MultiIndex):

                if "Close" not in px.columns.get_level_values(0):
                    continue

                close_series = px["Close"].iloc[:, 0]

            else:

                if "Close" not in px.columns:
                    continue

                close_series = px["Close"]

            tmp = pd.DataFrame(
                {
                    "ticker": [ticker] * len(px),
                    "date": pd.to_datetime(
                        date_series,
                        errors="coerce"
                    ),
                    "close": pd.to_numeric(
                        close_series,
                        errors="coerce"
                    ),
                }
            )

            tmp = tmp.dropna(
                subset=[
                    "date",
                    "close",
                ]
            )

            rows.append(tmp)

            time.sleep(0.05)

        except Exception as e:

            print(
                "PRICE ERROR:",
                ticker,
                str(e)
            )

    if len(rows) == 0:

        return pd.DataFrame(
            columns=[
                "ticker",
                "date",
                "close",
            ]
        )

    out = pd.concat(
        rows,
        ignore_index=True,
    )

    # ここで完全に作り直す
    out = pd.DataFrame(
        {
            "ticker": out["ticker"].astype(str).values,
            "date": pd.to_datetime(
                out["date"]
            ).values,
            "close": pd.to_numeric(
                out["close"],
                errors="coerce"
            ).values,
        }
    )

    return out
