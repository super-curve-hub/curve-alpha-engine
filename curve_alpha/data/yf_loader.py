import time

import pandas as pd
import yfinance as yf

from curve_alpha.utils import safe_get


def _is_valid_number(x):
    """
    None / NaN を除外する簡易チェック。
    0 や負値は有効値として扱う。
    """
    return x is not None and pd.notna(x)


def load_fundamentals(tickers, sleep_sec=0.2):
    """
    yfinance からファンダメンタルズ情報を取得する。

    Parameters
    ----------
    tickers : list[str]
        例: ["AAPL", "MSFT", "7203.T"]
    sleep_sec : float
        銘柄ごとの待機秒数。429回避用。

    Returns
    -------
    pd.DataFrame
        銘柄別ファンダメンタルズ。

    Notes
    -----
    net_debt = total_debt - total_cash
    error は正常取得時 None、失敗時は例外メッセージ。
    """

    rows = []

    for t in tickers:
        try:
            info = yf.Ticker(t).info or {}

            market_cap = safe_get(info, "marketCap")
            fcf = safe_get(info, "freeCashflow")
            total_debt = safe_get(info, "totalDebt")
            total_cash = safe_get(info, "totalCash")
            revenue = safe_get(info, "totalRevenue")
            ebitda = safe_get(info, "ebitda")

            # FCF Yield
            # fcf が負でも有効。market_cap が 0 / None の場合だけ除外。
            fcf_yield = None
            if (
                _is_valid_number(market_cap)
                and _is_valid_number(fcf)
                and market_cap != 0
            ):
                fcf_yield = fcf / market_cap

            # yfinance の debtToEquity は % 表示のことが多いため 100 で割る。
            debt_to_equity = safe_get(info, "debtToEquity")
            if _is_valid_number(debt_to_equity):
                debt_to_equity = debt_to_equity / 100.0

            # Net Debt
            net_debt = None
            if _is_valid_number(total_debt) and _is_valid_number(total_cash):
                net_debt = total_debt - total_cash

            rows.append({
                "ticker": t,
                "market_cap": market_cap,

                # quality
                "roe": safe_get(info, "returnOnEquity"),
                "roa": safe_get(info, "returnOnAssets"),
                "gross_margin": safe_get(info, "grossMargins"),
                "operating_margin": safe_get(info, "operatingMargins"),
                "profit_margin": safe_get(info, "profitMargins"),

                # growth
                "revenue_growth": safe_get(info, "revenueGrowth"),
                "earnings_growth": safe_get(info, "earningsGrowth"),

                # value
                "pe": safe_get(info, "trailingPE"),
                "forward_pe": safe_get(info, "forwardPE"),
                "pb": safe_get(info, "priceToBook"),
                "ev_ebitda": safe_get(info, "enterpriseToEbitda"),
                "ev_sales": safe_get(info, "enterpriseToRevenue"),
                "fcf_yield": fcf_yield,

                # leverage / risk
                "debt_to_equity": debt_to_equity,
                "beta": safe_get(info, "beta"),

                # flow / squeeze
                "short_ratio": safe_get(info, "shortRatio"),
                "short_percent_float": safe_get(info, "shortPercentOfFloat"),
                "held_percent_institutions": safe_get(info, "heldPercentInstitutions"),
                "held_percent_insiders": safe_get(info, "heldPercentInsiders"),

                # capital return
                "buyback_yield": None,

                # raw financials
                "revenue": revenue,
                "ebitda": ebitda,
                "total_debt": total_debt,
                "total_cash": total_cash,
                "net_debt": net_debt,

                # status
                "error": None,
            })

        except Exception as e:
            rows.append({
                "ticker": t,
                "market_cap": None,

                # quality
                "roe": None,
                "roa": None,
                "gross_margin": None,
                "operating_margin": None,
                "profit_margin": None,

                # growth
                "revenue_growth": None,
                "earnings_growth": None,

                # value
                "pe": None,
                "forward_pe": None,
                "pb": None,
                "ev_ebitda": None,
                "ev_sales": None,
                "fcf_yield": None,

                # leverage / risk
                "debt_to_equity": None,
                "beta": None,

                # flow / squeeze
                "short_ratio": None,
                "short_percent_float": None,
                "held_percent_institutions": None,
                "held_percent_insiders": None,

                # capital return
                "buyback_yield": None,

                # raw financials
                "revenue": None,
                "ebitda": None,
                "total_debt": None,
                "total_cash": None,
                "net_debt": None,

                # status
                "error": str(e),
            })

        time.sleep(sleep_sec)

    return pd.DataFrame(rows)


def load_price_history(tickers, period="1y", interval="1d", sleep_sec=0.2):
    """
    yfinance から株価履歴を取得し、必ず縦持ち形式で返す。

    Returns
    -------
    pd.DataFrame
        columns = ["ticker", "date", "close"]

    Example
    -------
    ticker   date         close
    AAPL     2026-06-18   195.00
    MSFT     2026-06-18   480.00
    7203.T   2026-06-18   2793.50
    """

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

            if px is None or px.empty:
                print(f"[WARN] empty price data: {t}")
                continue

            # -----------------------------------------
            # Close列を安全に取り出す
            # yfinance は環境・版によって MultiIndex を返すことがある
            # -----------------------------------------
            if isinstance(px.columns, pd.MultiIndex):
                # 例: ("Close", "AAPL") が存在する場合
                if ("Close", t) in px.columns:
                    close = px[("Close", t)]

                # 例: 1階層目に Close があり、その下に ticker がある場合
                elif "Close" in px.columns.get_level_values(0):
                    close_block = px["Close"]

                    if isinstance(close_block, pd.DataFrame):
                        if t in close_block.columns:
                            close = close_block[t]
                        else:
                            close = close_block.iloc[:, 0]
                    else:
                        close = close_block

                # 例: 2階層目に Close がある特殊ケース
                elif "Close" in px.columns.get_level_values(-1):
                    close_block = px.xs("Close", axis=1, level=-1)

                    if isinstance(close_block, pd.DataFrame):
                        close = close_block.iloc[:, 0]
                    else:
                        close = close_block

                else:
                    print(f"[WARN] Close column not found: {t}")
                    continue

            else:
                if "Close" not in px.columns:
                    print(f"[WARN] Close column not found: {t}")
                    continue

                close = px["Close"]

            # -----------------------------------------
            # 縦持ち DataFrame に変換
            # -----------------------------------------
            out = close.to_frame(name="close").reset_index()

            date_col = "Date" if "Date" in out.columns else "Datetime"
            out = out.rename(columns={date_col: "date"})

            out["ticker"] = t
            out["date"] = pd.to_datetime(out["date"])
            out["close"] = pd.to_numeric(out["close"], errors="coerce")

            out = out.dropna(subset=["date", "close"])
            out = out[["ticker", "date", "close"]]

            frames.append(out)

        except Exception as e:
            print(f"[WARN] failed to load price history: {t} / {e}")
            continue

        time.sleep(sleep_sec)

    if not frames:
        return pd.DataFrame(columns=["ticker", "date", "close"])

    result = pd.concat(frames, ignore_index=True)

    # 念のため最終的に列構造を保証
    result = result[["ticker", "date", "close"]]
    result = result.sort_values(["ticker", "date"]).reset_index(drop=True)

    return result