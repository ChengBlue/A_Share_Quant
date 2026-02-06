# A Share Quant

A 股量化回测项目：使用 [akshare](https://github.com/akfamily/akshare) 获取 A 股行情数据，基于 [Backtrader](https://www.backtrader.com/) 进行策略回测与对比。

## 功能概览

- **数据层**：通过 akshare 拉取个股日 K、指数日 K，统一为 OHLCV 格式，方便策略使用。
- **策略层**：实现均线金叉/死叉策略，支持「指数均线过滤」和「固定比例止损」，便于做多/空仓控制。
- **回测层**：一键对比「开启指数过滤」与「不开启」的收益、回撤、夏普等指标，便于评估择时过滤效果。

---

## 项目结构

```
a_share_quant/
├── data/
│   └── akshare_fetch.py   # 数据获取：个股日线、指数日线（统一字段与索引）
├── strategies/
│   └── ma_strategy.py     # 均线策略：金叉/死叉 + 指数过滤 + 固定止损
├── backtest/
│   └── run_backtest.py    # 回测入口：构建 Cerebro、加载数据与策略、运行并输出指标
├── config.py              # 全局配置（预留）
├── main.py                # 主入口（预留）
└── README.md
```

| 路径 | 说明 |
|------|------|
| `data/akshare_fetch.py` | 封装 akshare 调用，返回 `open/high/low/close/volume`、日期索引的 DataFrame，供回测与策略使用。 |
| `strategies/ma_strategy.py` | Backtrader 策略类：双均线 + 可选指数过滤 + 固定止损；需传入个股与指数两条数据。 |
| `backtest/run_backtest.py` | 默认用宁德时代 + 沪深300，分别跑「无指数过滤」和「有指数过滤」，打印最终资金、最大回撤、夏普。 |
| `config.py` / `main.py` | 当前为空，可用于后续统一配置与入口。 |

---

## 环境要求

- **Python**：3.8 及以上
- **依赖**：`akshare`、`pandas`、`backtrader`、`matplotlib`（backtrader 绘图可选）

---

## 安装

### 1. 克隆或进入项目目录

```bash
cd a_share_quant
```

### 2. 建议使用虚拟环境（可选）

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install akshare pandas backtrader matplotlib
```

若项目后续提供 `requirements.txt`，可使用：

```bash
pip install -r requirements.txt
```

### 4. 验证

在项目根目录执行：

```bash
python -c "from data.akshare_fetch import get_index_daily; print(get_index_daily('sh000300','20200101','20201231').shape)"
```

无报错并输出形状即表示环境正常。

---

## 数据模块说明（`data/akshare_fetch.py`）

所有接口返回的 DataFrame 均为 **日期为索引**，列名为英文：`open`、`high`、`low`、`close`、`volume`，便于与 Backtrader 的 `PandasData` 对接。

### 1. 个股日线：`get_daily(ts_code, start_date, end_date)`

| 参数 | 类型 | 说明 |
|------|------|------|
| `ts_code` | str | 股票代码，如 `000001.SZ`、`300750.SZ`、`600519.SH`（代码会自动去掉后缀给 akshare 使用） |
| `start_date` | str | 开始日期，格式 `YYYYMMDD`，如 `20180101` |
| `end_date`   | str | 结束日期，格式 `YYYYMMDD` |

- **数据说明**：日频、**前复权**（`adjust="qfq"`），来自 akshare 的 `stock_zh_a_hist`。
- **返回**：`pd.DataFrame`，索引 `date`（datetime），列 `open/high/low/close/volume`，按日期升序。
- **异常**：若区间内无数据会抛出 `ValueError`。

### 2. 指数日线：`get_index_daily(symbol, start_date, end_date)`

| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol`     | str | 指数代码，如 `sh000300`、`sh000001`、`sz399905` |
| `start_date` | str | 开始日期 `YYYYMMDD` |
| `end_date`   | str | 结束日期 `YYYYMMDD` |

- **数据说明**：指数日 K，接口为 `stock_zh_index_daily`，在函数内按 `start_date`～`end_date` 做切片。
- **返回**：同上，索引 + 五列 OHLCV。
- **常用指数**：
  - `sh000300`：沪深300  
  - `sh000001`：上证指数  
  - `sz399001`：深证成指  
  - `sz399905`：中证500  

---

## 策略说明（`strategies/ma_strategy.py`）

`MaStrategy` 为 Backtrader 的 `bt.Strategy` 子类，逻辑概览：

1. **均线**：对**第一条数据（个股）**计算快线 SMA(fast)、慢线 SMA(slow)，用 `CrossOver` 得到金叉/死叉。
2. **指数过滤（可选）**：对**第二条数据（指数）**计算 SMA(index_period)，仅当「指数收盘价 > 指数均线」时允许开仓。
3. **入场**：当前无持仓时，若出现金叉（快线上穿慢线），且满足指数过滤（若开启），则买入。
4. **出场**：  
   - 固定止损：当前收盘价低于买入价的 `(1 - stop_loss)` 则卖出；  
   - 或死叉（慢线上穿快线）则卖出。

### 策略参数（`params`）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fast` | int | 10 | 快线周期（日） |
| `slow` | int | 30 | 慢线周期（日） |
| `index_period` | int | 120 | 指数均线周期（日），仅当 `use_index_filter=True` 时生效 |
| `stop_loss` | float | 0.08 | 固定止损比例，如 0.08 表示 8% 止损 |
| `use_index_filter` | bool | True | 是否启用指数过滤（指数收盘 > 指数均线才允许交易） |

### 数据顺序要求

- `datas[0]`：**个股**（必须）
- `datas[1]`：**指数**（启用指数过滤时必须，且日期范围需覆盖个股）

在 `backtest/run_backtest.py` 中已按此顺序 `adddata`，自定义回测时保持一致即可。

### 调试输出

策略在 `stop()` 中会打印 `allow_trade_days` 与 `total_days`，便于确认指数过滤生效的天数比例。

---

## 回测模块说明（`backtest/run_backtest.py`）

### 运行方式

**必须在项目根目录**执行（保证 `data`、`strategies`、`backtest` 包可被导入）：

```bash
# 推荐：以模块方式运行
python -m backtest.run_backtest
```

或：

```bash
python backtest/run_backtest.py
```

### 默认配置

- **标的**：个股 300750.SZ（宁德时代），指数 sh000300（沪深300）
- **区间**：2018-01-01～2024-01-01
- **初始资金**：100000
- **佣金**：0.001（单边）
- **对比**：先跑 `use_index_filter=False`，再跑 `use_index_filter=True`，分别打印指标。

### 输出指标含义

| 指标 | 含义 |
|------|------|
| `final_value` | 回测结束时的账户总资产 |
| `max_drawdown` | 最大回撤（百分比，如 15.2 表示 15.2%） |
| `sharpe` | 年化夏普比率（日频年化），越大表示风险调整后收益越好 |

### 如何修改标的、区间或策略参数

在 `run_backtest.py` 中：

- 修改 `get_daily(ts_code="...", start_date="...", end_date="...")` 的个股与区间。
- 修改 `get_index_daily(symbol="...", start_date="...", end_date="...")` 的指数与区间。
- 在 `cerebro.addstrategy(MaStrategy, ...)` 中传入 `fast`、`slow`、`index_period`、`stop_loss`、`use_index_filter` 等参数。

例如只跑「有指数过滤」并改止损为 5%：

```python
result = run(use_index_filter=True)
# 或在 addstrategy 时传入: stop_loss=0.05
```

---

## 使用示例

### 1. 仅获取指数数据并查看

```python
from data.akshare_fetch import get_index_daily

df = get_index_daily("sh000300", "20180101", "20240101")
print(df.head())
print(df.columns)
```

### 2. 获取个股日线并检查列

```python
from data.akshare_fetch import get_daily

df = get_daily("300750.SZ", "20200101", "20201231")
print(df.tail())
assert list(df.columns) == ["open", "high", "low", "close", "volume"]
```

### 3. 在脚本中调用回测并拿到结果

```python
from backtest.run_backtest import run

r = run(use_index_filter=True)
print("最终资金:", r["final_value"])
print("最大回撤%:", r["max_drawdown"])
print("夏普:", r["sharpe"])
```

---

## 注意事项与常见问题

1. **运行目录**：所有涉及 `from data.xxx`、`from strategies.xxx`、`from backtest.xxx` 的脚本，都应在**项目根目录**下运行，否则会报模块找不到。
2. **网络**：akshare 需要联网拉取数据，若请求失败请检查网络与 akshare 接口是否变更。
3. **日期格式**：统一使用 `YYYYMMDD` 字符串，如 `20180101`。
4. **指数与个股区间**：指数数据的日期范围应至少覆盖个股回测区间，否则指数过滤在缺失日期上可能异常。
5. **输出无显示**：若在终端中运行脚本无打印，可尝试 `python -u backtest/run_backtest.py`（无缓冲），或确认无异常被静默捕获。

---

## 后续可扩展方向

- 在 `config.py` 中集中管理：标的列表、回测区间、佣金、初始资金、策略默认参数等。
- 在 `main.py` 中提供命令行参数，选择标的、区间、是否指数过滤等，再调用 `backtest.run_backtest.run()`。
- 增加更多 Backtrader 分析器（如年化收益、胜率、交易次数），或导出收益曲线、回撤曲线到文件。
- 数据层：增加本地缓存、增量更新，或支持 tushare 等其它数据源。
- 策略层：增加更多策略文件，或在同一回测中做多策略对比。

---

## 许可证

按项目需要自行选择。
