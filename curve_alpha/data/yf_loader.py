import time
import pandas as pd
import yfinance as yf


def load_fundamentals(tickers):

    rows = []

    for t in tickers:

        try:

            info = yf.Ticker(t).info

            rows.append(
                {
                    "ticker": t,
                    "market_cap": info.get("marketCap"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                    "gross_margin": info.get("grossMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "profit_margin": info.get("profitMargins"),
                    "revenue_growth": info.get("revenueGrowth"),
                    "earnings_growth": info.get("earningsGrowth"),
                    "pe": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "pb": info.get("priceToBook"),
                    "ev_ebitda": info.get("enterpriseToEbitda"),
                    "ev_sales": info.get("enterpriseToRevenue"),
                    "fcf_yield": None,
                    "debt_to_equity": info.get("debtToEquity"),
                    "beta": info.get("beta"),
                    "short_ratio": info.get("shortRatio"),
                    "short_percent_float": info.get(
                        "shortPercentOfFloat"
                    ),
                    "held_percent_institutions": info.get(
                        "heldPercentInstitutions"
                    ),
                    "held_percent_insiders": info.get(
                        "heldPercentInsiders"
                    ),
                    "buyback_yield": None,
                }
            )

        except Exception as e:

            print(
                "FUNDAMENTAL ERROR:",
                t,
                str(e)
            )

        time.sleep(0.05)

    return pd.DataFrame(rows)


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

            # -------------------------
            # MultiIndex対策
            # -------------------------

            if isinstance(
                px.columns,
                pd.MultiIndex
            ):

                px.columns = (
                    px.columns
                    .get_level_values(0)
                )

            px = px.reset_index()

            date_col = None

            for c in px.columns:

                if str(c).lower() in [
                    "date",
                    "datetime",
                ]:

                    date_col = c
                    break

            if date_col is None:

                date_col = px.columns[0]

            close_col = None

            for c in px.columns:

                if str(c).lower() == "close":

                    close_col = c
                    break

            if close_col is None:

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

            tmp = tmp.dropna()

            all_rows.append(tmp)

        except Exception as e:

            print(
                "PRICE ERROR:",
                ticker,
                str(e)
            )

        time.sleep(0.05)

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
        ignore_index=True
    )

    out.columns = [
        str(x).lower()
        for x in out.columns
    ]

    return out
