import time
import pandas as pd
import yfinance as yf
from curve_alpha.utils import safe_get

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
            if market_cap and fcf:
                fcf_yield = fcf / market_cap

            ev_sales = safe_get(info, "enterpriseToRevenue")
            ev_ebitda = safe_get(info, "enterpriseToEbitda")

            debt_to_equity = safe_get(info, "debtToEquity")
            if debt_to_equity is not None:
                debt_to_equity = debt_to_equity / 100.0

            rows.append({
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
                "short_percent_float": safe_get(info, "shortPercentOfFloat"),
                "held_percent_institutions": safe_get(info, "heldPercentInstitutions"),
                "held_percent_insiders": safe_get(info, "heldPercentInsiders"),
                "buyback_yield": None,
                "revenue": revenue,
                "ebitda": ebitda,
                "total_debt": total_debt,
                "total_cash": total_cash,
            })
            time.sleep(0.05)
        except Exception as e:
            rows.append({"ticker": t, "error": str(e)})
    return pd.DataFrame(rows)

def load_price_history(tickers, period="1y", interval="1d"):
    frames = []
    for t in tickers:
        try:
            px = yf.download(t, period=period, interval=interval, auto_adjust=True, progress=False)
            if px.empty:
                continue
            px = px.reset_index()
            date_col = "Date" if "Date" in px.columns else "Datetime"
            px = px[[date_col, "Close"]].rename(columns={date_col: "date", "Close": "close"})
            px["ticker"] = t
            frames.append(px[["ticker", "date", "close"]])
            time.sleep(0.05)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame(columns=["ticker", "date", "close"])
    return pd.concat(frames, ignore_index=True)
