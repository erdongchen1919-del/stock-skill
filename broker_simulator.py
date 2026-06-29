"""
本地模拟 Broker（可立即运行，无需券商 API）

实现要点：
- 保存现金与持仓（字典）
- place_market_order：按当前可得 price_series 的最新价进行成交
- has_position/check positions/get_account_value/snapshot
"""
import pandas as pd
import copy
import datetime

class SimulatorBroker:
    def __init__(self, initial_cash=100000, price_series=None, ohlc_dict=None):
        self.cash = float(initial_cash)
        self.positions = {}  # ticker -> {'qty': int, 'avg_price': float}
        self.price_series = price_series  # DataFrame closes
        self.ohlc_dict = ohlc_dict or {}
        self.trade_log = []

    def get_account_value(self):
        # 现金 + 持仓市值（按最新价）
        market_value = 0.0
        if self.price_series is None or self.price_series.empty:
            return self.cash
        latest = self.price_series.iloc[-1]
        for t, pos in self.positions.items():
            price = latest.get(t)
            if price is not None and not pd.isna(price):
                market_value += pos['qty'] * float(price)
        return self.cash + market_value

    def has_position(self, ticker):
        return ticker in self.positions and self.positions[ticker]['qty'] > 0

    def place_market_order(self, symbol, qty, side='BUY'):
        # 执行：用最新可用价格（close）成交
        if self.price_series is None or self.price_series.empty:
            raise RuntimeError("Price series not available for execution")
        latest_price = float(self.price_series[symbol].iloc[-1])
        cost = latest_price * qty
        if side.upper() == 'BUY':
            if cost > self.cash:
                # 部分成交策略：此处简单返回失败
                return {"symbol": symbol, "qty": 0, "side": side, "status": "rejected_insufficient_cash"}
            # 执行成交
            self.cash -= cost
            if symbol in self.positions:
                prev = self.positions[symbol]
                new_qty = prev['qty'] + qty
                new_avg = (prev['avg_price'] * prev['qty'] + latest_price * qty) / new_qty
                self.positions[symbol] = {'qty': new_qty, 'avg_price': new_avg}
            else:
                self.positions[symbol] = {'qty': qty, 'avg_price': latest_price}
            order = {"symbol": symbol, "qty": qty, "side": side, "price": latest_price, "status": "filled", "timestamp": datetime.datetime.now().isoformat()}
            self.trade_log.append(order)
            return order
        elif side.upper() == 'SELL':
            if symbol not in self.positions or self.positions[symbol]['qty'] < qty:
                return {"symbol": symbol, "qty": 0, "side": side, "status": "rejected_insufficient_qty"}
            latest = self.positions[symbol]
            self.positions[symbol]['qty'] -= qty
            proceeds = latest_price * qty
            self.cash += proceeds
            order = {"symbol": symbol, "qty": qty, "side": side, "price": latest_price, "status": "filled", "timestamp": datetime.datetime.now().isoformat()}
            self.trade_log.append(order)
            return order
        else:
            return {"symbol": symbol, "qty": 0, "side": side, "status": "invalid_side"}

    def snapshot(self):
        return {"cash": self.cash, "positions": self.positions, "trade_count": len(self.trade_log), "market_value": self.get_account_value()}

    def close(self):
        # nothing to close for local simulator
        pass
