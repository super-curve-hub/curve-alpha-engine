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

    for t in tickers:

        try:

            info = yf.Ticker(t).info

            market_cap = safe_get(info, "marketCap")
            fcf = safe_get(info, "freeCashflow")
            total_debt = safe_get(info, "totalDebt")
            total_cash = safe_get(info, "totalCash")
            revenue = safe_get(info, "totalRevenue")
            ebitda = safe_get(info, "ebitda")

            fcf_yield = None

            if (
                market_cap is not None
                and market_cap > 0
                and fcf is not None
            ):
                fcf_yield = fcf / market_cap

            ev_sales = safe_get(
                info,
                "enterpriseToRevenue"
            )

            ev_ebitda = safe_get(
                info,
                "enterpriseToEbitda"
            )

            debt_to_equity = safe_get(
                info,
                "debtToEquity"
            )

            if debt_to_equity is not None:
                debt_to_equity = debt_to_equity / 100.0

            rows.append(
                {
                    "ticker": t,
                    "market_cap": market_cap,
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
                    "ev_ebitda": ev_ebitda,
                    "ev_sales": ev_sales,
                    "fcf_yield": fcf_yield,
                    "debt_to_equity": debt_to_equity,
                    "beta": safe_get(info, "beta"),
                    "short_ratio": safe_get(info, "shortRatio"),
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
                    "revenue": revenue,
                    "ebitda": ebitda,
                    "total_debt": total_debt,
                    "total_cash": total_cash,
                }
            )

            time.sleep(0.05)

        except Exception as e:

            print(
                "FUNDAMENTAL ERROR:",
                t,
                str(e)
            )

            rows.append(
                {
                    "ticker": t,
                    "error": str(e),
                }
            )

    return pd.DataFrame(rows)


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
                threads=False,
            )

            if px.empty:
                continue

            # ---------------------------------
            # yfinance MultiIndex完全除去
            # ---------------------------------

            if isinstance(
                px.columns,
                pd.MultiIndex
            ):
                px.columns = (
                    px.columns
                    .get_level_values(0)
                )

            px = px.reset_index()

            date_col = (
                "Date"
                if "Date" in px.columns
                else px.columns[0]
            )

            if "Close" not in px.columns:

                print(
                    "Close column missing:",
                    t
                )

                continue

            tmp = pd.DataFrame()

            tmp["ticker"] = [t] * len(px)

            tmp["date"] = pd.to_datetime(
                px[date_col],
                errors="coerce"
            )

            tmp["close"] = pd.to_numeric(
                px["Close"],
                errors="coerce"
            )

            tmp = tmp.dropna(
                subset=[
                    "date",
                    "close",
                ]
            )

            frames.append(tmp)

            time.sleep(0.05)

        except Exception as e:

            print(
                "PRICE ERROR:",
                t,
                str(e)
            )

    if len(frames) == 0:

        return pd.DataFrame(
            columns=[
                "ticker",
                "date",
                "close",
            ]
        )

    out = pd.concat(
        frames,
        ignore_index=True,
    )

    # 強制フラット化
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


def load_all_data(
    universe,
    price_period="1y",
    price_interval="1d",
):

    tickers = (
        universe["ticker"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    fundamentals = load_fundamentals(
        tickers
    )

    prices = load_price_history(
        tickers,
        period=price_period,
        interval=price_interval,
    )

    return fundamentals, prices
