import backtrader as bt


class MaStrategy(bt.Strategy):
    params = dict(
        fast=10,
        slow=30,
        index_period=120,   # 指数均线周期
        stop_loss=0.08,     # 8% 固定止损
        use_index_filter=True,     
    )

    def __init__(self):
        self.allow_trade_days = 0
        self.total_days = 0

        # 个股均线
        self.ma_fast = bt.indicators.SMA(self.datas[0].close, period=self.p.fast)
        self.ma_slow = bt.indicators.SMA(self.datas[0].close, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.ma_fast, self.ma_slow)

        # 指数均线（第二条 data）
        self.index_ma = bt.indicators.SMA(
            self.datas[1].close, period=self.p.index_period
        )

        self.buy_price = None



    def next(self):
        # 默认允许交易
        allow_trade = True

        # 如果开启指数过滤，才使用指数条件
        if self.p.use_index_filter:
            allow_trade = self.datas[1].close[0] > self.index_ma[0]

        # ===== 调试计数 =====
        self.total_days += 1
        if allow_trade:
            self.allow_trade_days += 1

        # ===== 后面逻辑不变 =====
        if not self.position:
            if allow_trade and self.crossover > 0:
                self.buy()
                self.buy_price = self.data.close[0]
        else:
            if self.data.close[0] < self.buy_price * (1 - self.p.stop_loss):
                self.sell()
                self.buy_price = None
            elif self.crossover < 0:
                self.sell()
                self.buy_price = None
                
    def stop(self):
        print(
            f"[DEBUG] allow_trade_days: {self.allow_trade_days}, "
            f"total_days: {self.total_days}"
        )
