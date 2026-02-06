import backtrader as bt
import matplotlib.pyplot as plt
from data.akshare_fetch import get_daily, get_index_daily
from strategies.ma_strategy import MaStrategy


def run(use_index_filter: bool):
    cerebro = bt.Cerebro()

    cerebro.addstrategy(
        MaStrategy,
        use_index_filter=use_index_filter,
    )

    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)

    # 个股
    stock_df = get_daily(
        ts_code="300750.SZ",    #宁德时代
        start_date="20180101",
        end_date="20240101",
    )
    stock_data = bt.feeds.PandasData(dataname=stock_df)
    cerebro.adddata(stock_data)

    # 指数（新浪）
    index_df = get_index_daily(
        symbol="sh000300",
        start_date="20180101",
        end_date="20240101",
    )
    index_data = bt.feeds.PandasData(dataname=index_df)
    cerebro.adddata(index_data)

    # 分析器
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(
        bt.analyzers.SharpeRatio,
        _name="sharpe",
        timeframe=bt.TimeFrame.Days,
        annualize=True,
    )


    result = cerebro.run()[0]

    return {
        "final_value": cerebro.broker.getvalue(),
        "max_drawdown": result.analyzers.dd.get_analysis()["max"]["drawdown"],
        "sharpe": result.analyzers.sharpe.get_analysis().get("sharperatio"),
    }


if __name__ == "__main__":
    r1 = run(use_index_filter=False)
    r2 = run(use_index_filter=True)

    print("❌ 无指数过滤")
    for k, v in r1.items():
        print(f"  {k}: {v}")

    print("\n✅ 有指数过滤")
    for k, v in r2.items():
        print(f"  {k}: {v}")

