"""
简单回测脚本（基于历史日线，按策略生成信号并用 SimulatorBroker 模拟成交）
使用示例：python backtest.py
"""
import yaml
from utils import load_universe_history
from strategy import generate_signals
from broker_simulator import SimulatorBroker
from risk import position_size

def simple_backtest(cfg):
    closes, ohlc = load_universe_history(cfg['universe'], period_days=365*2)
    if closes is None:
        print("未能加载历史数据")
        return
    # 逐日模拟：每个调仓日计算信号并按规则下单（示意）
    broker = SimulatorBroker(initial_cash=cfg['broker'].get('sim_account_balance', 100000),
                             price_series=closes, ohlc_dict=ohlc)
    history = []
    dates = closes.index
    # 从 warmup 天开始
    warmup = cfg['strategy'].get('lookback_days', 20) + 5
    for i in range(warmup, len(dates)):
        slice_closes = closes.iloc[:i+1]
        slice_ohlc = {t: (ohlc[t].iloc[:i+1] if t in ohlc else None) for t in cfg['universe']}
        signals, atrs = generate_signals(slice_closes, slice_ohlc, cfg)
        portfolio_value = broker.get_account_value()
        for t, s in signals.items():
            if s == 1 and not broker.has_position(t):
                price = slice_closes[t].iloc[-1]
                atr = atrs.get(t, 0.0)
                qty = position_size(portfolio_value, price, atr,
                                    cfg['risk']['risk_per_trade'],
                                    cfg['risk']['stop_atr_multiplier'],
                                    cfg['risk']['max_position_pct'])
                if qty > 0:
                    order = broker.place_market_order(t, qty, side='BUY')
                    history.append((dates[i], order))
        # 简化：不实现卖出/止损追踪（用户可扩展）
    return broker, history

if __name__ == '__main__':
    cfg = yaml.safe_load(open('config.yaml'))
    broker, history = simple_backtest(cfg)
    print("回测结束，组合快照：", broker.snapshot())
    print("成交记录示例：", broker.trade_log[:10])
