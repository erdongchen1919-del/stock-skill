import akshare as ak
import pandas as pd
import datetime
import requests
import time

def try_fetch_akshare(ticker):
    """
    尝试多种符号格式获取 A 股日线（ak.stock_zh_a_daily）
    支持： "600519" / "600519.SH" / "600519.SS" / "000001.SZ"
    返回 DataFrame 或 None
    """
    candidates = [ticker]
    if "." in ticker:
        code, suffix = ticker.split(".", 1)
        # akshare 使用 sh/sz 前缀形式
        if suffix.upper() in ("SH", "SS"):
            candidates.append("sh" + code)
        if suffix.upper() == "SZ":
            candidates.append("sz" + code)
        candidates.append(code)
    else:
        # try as plain code, and with sh/sz prefixes
        candidates.append("sh" + ticker)
        candidates.append("sz" + ticker)
    for sym in candidates:
        try:
            df = ak.stock_zh_a_daily(symbol=sym)
            if df is not None and not df.empty:
                # ensure columns open/high/low/close exist and lowercase
                df = df.rename(columns={c: c.lower() for c in df.columns})
                # akshare index may be timestamps in string
                df.index = pd.to_datetime(df.index)
                # ensure column names
                if set(['open','high','low','close']).issubset(set(df.columns)):
                    return df[['open','high','low','close']].rename(columns=str.lower)
                # else try to find close/open columns with different names
        except Exception as e:
            # small delay to avoid throttling
            time.sleep(0.5)
            continue
    return None

def load_universe_history(tickers, period_days=60):
    """
    返回：
    - closes: DataFrame columns=tickers (按日期索引，最近日期在最后)
    - ohlc_dict: {ticker: DataFrame with columns ['open','high','low','close']}
    注：为提高健壮性，若 akshare 报错或未找到数据，可把数据预先放到 data/<ticker>.csv 并在此处加载。
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=period_days)
    closes = {}
    ohlc = {}
    for t in tickers:
        df = try_fetch_akshare(t)
        if df is None or df.empty:
            print(f"警告：未能通过 akshare 拉取 {t} 的数据。请确认代码或手动提供 data/{t}.csv")
            continue
        # 截取最后 period_days 条记录
        df_slice = df.loc[df.index >= pd.to_datetime(start)]
        if df_slice.empty:
            df_slice = df.tail(period_days)
        closes[t] = df_slice['close']
        ohlc[t] = df_slice[['open','high','low','close']].rename(columns=str.lower)
    if not closes:
        return None, {}
    closes_df = pd.DataFrame(closes)
    return closes_df, ohlc

def send_alert(title, payload, webhook_url=None):
    """
    简易 webhook 触发：POST JSON 到 webhook_url。
    webhook_url 可为钉钉/企业微信/Slack 的接入地址（需自行配置）。
    """
    url = webhook_url
    if url is None:
        return False
    try:
        content = {"title": title, "payload": payload}
        r = requests.post(url, json=content, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print("send_alert 异常：", e)
        return False
