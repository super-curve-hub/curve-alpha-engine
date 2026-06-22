import time
import pandas as pd
import yfinance as yf


def safe_get(data, key, default=None):
    try:
        value = data.get(key, default)

        if value is None:
            return default

        return value

    except Exception:
        return default


def load_fundamentals(tickers):

    rows = []

    for ticker in tickers:

        try:

            info = yf.Ticker(ticker).info

            market_cap = safe_get(
                info,
                "marketCap"
            )

            fcf = safe_get(
                info,
                "freeCashflow"
            )

            fcf_yield = None

            if (
                market_cap is not None
                and market_cap > 0
                and fcf is not None
            ):
                fcf_yield = (
                    fcf / market_cap
                )

            debt_to_equity = safe_get(
                info,
                "debtToEquity"
            )

            if debt_to_equity is not None:
                debt_to_equity = (
                    debt_to_equity / 100.0
                )

            rows.append(
                {
                    "ticker": ticker,

                    "market_cap": market_cap,

                    "roe": safe_get(
                        info,
                        "returnOnEquity"
                    ),

                    "roa": safe_get(
                        info,
                        "returnOnAssets"
                    ),

                    "gross_margin": safe_get(
                        info,
                        "grossMargins"
                    ),

                    "operating_margin": safe_get(
                        info,
                        "operatingMargins"
                    ),

                    "profit_margin": safe_get(
                        info,
                        "profitMargins"
                    ),

                    "revenue_growth": safe_get(
                        info,
                        "revenueGrowth"
                    ),

                    "earnings_growth": safe_get(
                        info,
                        "earningsGrowth"
                    ),

                    "pe": safe_get(
                        info,
                        "trailingPE"
                    ),

                    "forward_pe": safe_get(
                        info,
                        "forwardPE"
                    ),

                    "pb": safe_get(
                        info,
                        "priceToBook"
                    ),

                    "ev_ebitda": safe_get(
                        info,
                        "enterpriseToEbitda"
                    ),

                    "ev_sales": safe_get(
                        info,
                        "enterpriseToRevenue"
                    ),

                    "fcf_yield": fcf_yield,

                    "debt_to_equity": debt_to_equity,

                    "beta": safe_get(
                        info,
                        "beta"
                    ),

                    "short_ratio": safe_get(
                        info,
                        "shortRatio"
                    ),

                    "short_percent_float": safe_get(
                        info,
                        "shortPercentOfFloat"
                    ),

                    "held_percent_institutions": safe_get(
                        info,
                        "heldPercentInstitutions"
                    ),

                    "held_percent_insiders": safe_get(
                        info,
                        "heldPercentInsiders"
                    ),

                    "buyback_yield": None,

                    "revenue": safe_get(
                        info,
                        "totalRevenue"
                    ),

                    "ebitda": safe_get(
                        info,
                        "ebitda"
                    ),

                    "total_debt": safe_get(
                        info,
                        "totalDebt"
                    ),

                    "total_cash": safe_get(
                        info,
                        "totalCash"
                    ),
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
            if isinstance(
                px.columns,
                pd.MultiIndex
            ):
                px.columns = [
                    str(c[0])
                    for c in px.columns
                ]

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

                print(
                    "DATE COLUMN NOT FOUND:",
                    ticker
                )

                continue

            close_col = None

            for c in px.columns:

                if str(c).lower() == "close":

                    close_col = c
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

    out.columns = [
        str(c).lower()
        for c in out.columns
    ]

    return out[
        [
            "ticker",
            "date",
            "close",
        ]
    ]
