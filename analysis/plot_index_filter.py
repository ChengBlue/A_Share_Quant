import matplotlib.pyplot as plt
import pandas as pd
from data.akshare_fetch import get_index_daily


def plot_index_filter():
        
    df = get_index_daily(
        symbol="sh000300",
        start_date="20180101",
        end_date="20240101",
    )


    # 120 日均线
    df["ma120"] = df["close"].rolling(120).mean()

    # 是否允许交易
    df["allow_trade"] = df["close"] > df["ma120"]

    plt.figure(figsize=(14, 7))

    # 指数
    plt.plot(df.index, df["close"], label="HS300 Close")

    # 均线
    plt.plot(df.index, df["ma120"], label="MA120")

    # 灰色阴影：不允许交易区间
    plt.fill_between(
        df.index,
        df["close"].min(),
        df["close"].max(),
        where=~df["allow_trade"],
        alpha=0.2,
        label="No Trade Zone",
    )

    plt.title("HS300 Trend Filter (Close > MA120)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # 画一个子图：交易许可
    plt.figure(figsize=(14, 2))
    plt.plot(df.index, df["allow_trade"].astype(int))
    plt.yticks([0, 1], ["No Trade", "Allow"])
    plt.title("Trade Permission Signal")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    plot_index_filter()
