import yaml
import time
import schedule
import argparse
from strategy import generate_signals
from risk import position_size
from utils import load_universe_history, send_alert
from broker_simulator import SimulatorBroker
# from broker_tqsdk import TqSdkBroker  # for future real integration

cfg = yaml.safe_load(open('config.yaml'))

def job(run_once=False):
    print("策略周期执行，模式:", cfg['mode'])
    price_df, ohlc_dict = load_universe_history(cfg['universe'], period_days=cfg['strategy']['lookback_days'] + 5)
    if price_df is None or price_df.empty:
        print("未能加载数据，结束本次运行")
        return

    signals, atrs = generate_signals(price_df, ohlc_dict, cfg)
    # 选择 broker：simulator 或 实盘 adapter（根据 cfg）
    if cfg['broker'].get('provider', 'simulator') == 'simulator':
        broker = SimulatorBroker(initial_cash=cfg['broker'].get('sim_account_balance', 100000),
                                 price_series=price_df, ohlc_dict=ohlc_dict)
    else:
        # placeholder for real broker adapter
        # broker = TqSdkBroker(mode=cfg['mode'], sim_balance=cfg['broker'].get('sim_account_balance', 100000))
        broker = SimulatorBroker(initial_cash=cfg['broker'].get('sim_account_balance', 100000),
                                 price_series=price_df, ohlc_dict=ohlc_dict)

    portfolio_value = broker.get_account_value()
    orders = []
    for ticker, s in signals.items():
        if s == 1 and not broker.has_position(ticker):
            price = price_df[ticker].iloc[-1]
            atr = atrs.get(ticker, 0.0)
            qty = position_size(portfolio_value, price, atr,
                                cfg['risk']['risk_per_trade'],
                                cfg['risk']['stop_atr_multiplier'],
                                cfg['risk']['max_position_pct'])
            if qty > 0:
                order = broker.place_market_order(ticker, qty, side='BUY')
                orders.append(order)
                print(f"下单: {ticker} 买入 {qty} 股 at {price}")
    # 可在此实现卖出逻辑与动态止损追踪（示例 MVP 仅示范建仓）
    if cfg['alerts'].get('webhook'):
        send_alert("策略运行完成", {"orders": orders})
    # print current portfolio snapshot
    print("Portfolio snapshot:", broker.snapshot())

    # close broker resources if needed
    broker.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run job once and exit')
    args = parser.parse_args()
    if args.once:
        job(run_once=True)
    else:
        # schedule at market open by default
        schedule.every().day.at("09:30").do(job)
        print("启动调度，等待策略执行...")
        while True:
            schedule.run_pending()
            time.sleep(1)
