import akshare as ak
import pandas as pd


def get_daily(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    ts_code: '000001.SZ'
    start_date / end_date: '20180101'
    return: DataFrame with index=datetime, columns=open/high/low/close/volume
    """

    symbol = ts_code.split(".")[0]  # 000001.SZ -> 000001

    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"  # 前复权
    )

    if df.empty:
        raise ValueError(f"No data for {ts_code}")

    df.rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        },
        inplace=True,
    )

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    df = df.sort_index()

    return df[["open", "high", "low", "close", "volume"]]

def get_index_daily(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    symbol:
        'sh000300'  沪深300
        'sh000001'  上证指数
        'sz399905'  中证500
    """
    df = ak.stock_zh_index_daily(symbol=symbol)

    df.rename(
        columns={
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        },
        inplace=True,
    )

    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    return df.loc[start_date:end_date]