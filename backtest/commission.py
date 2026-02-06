import backtrader as bt


class ChinaStockCommission(bt.CommInfoBase):
    """
    A股交易成本模型：
    - 买入：佣金
    - 卖出：佣金 + 印花税
    """

    params = dict(
        commission=0.0003,   # 万3
        stamp_duty=0.001,    # 印花税 0.1%
        stocklike=True,
        commtype=bt.CommInfoBase.COMM_PERC,
    )

    def _getcommission(self, size, price, pseudoexec):
        commission = abs(size) * price * self.p.commission
        stamp = 0.0

        # 卖出才收印花税
        if size < 0:
            stamp = abs(size) * price * self.p.stamp_duty

        return commission + stamp
