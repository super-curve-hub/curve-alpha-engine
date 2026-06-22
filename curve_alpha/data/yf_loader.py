import time
import pandas as pd
import yfinance as yf

def load_fundamentals(tickers):
    rows = []

    for t in tickers:
        try:
            info = yf.Ticker(t).info

            rows.append({
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
                "short_percent_float": info.get("shortPercentOfFloat"),
                "held_percent_institutions": info.get("heldPercentInstitutions"),
                "held_percent_insiders": info.get("heldPercentInsiders"),
                "buyback_yield": None,
            })

        except Exception as e:
            print("FUNDAMENTAL ERROR:", t, e)

        time.sleep(0.05)

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
                group_by="column"
            )

            if px.empty:
                continue

            # MultiIndex対策
            if isinstance(px.columns, pd.MultiIndex):
                px.columns = px.columns.get_level_values(0)

            px = px.reset_index()

            if "Date" in px.columns:
                date_col = "Date"
            else:
                date_col = px.columns[0]

            px = px.rename(
                columns={
                    date_col: "date",
                    "Close": "close"
                }
            )

            if "close" not in px.columns:
                continue

            px["ticker"] = t

            frames.append(
                px[
                    [
                        "ticker",
                        "date",
                        "close"
                    ]
                ]
            )

        except Exception as e:

            print(
                "PRICE ERROR:",
                t,
                e
            )

        time.sleep(0.05)

    if len(frames) == 0:

        return pd.DataFrame(
            columns=[
                "ticker",
                "date",
                "close"
            ]
        )

    out = pd.concat(
        frames,
        ignore_index=True
    )

    out.columns = [
        str(c).lower()
        for c in out.columns
    ]

    return out
