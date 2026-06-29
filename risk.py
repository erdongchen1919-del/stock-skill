import math

def position_size(portfolio_value, price, atr, risk_per_trade=0.01, stop_atr_multiplier=3, max_position_pct=0.05):
    single_risk = portfolio_value * risk_per_trade
    stop_distance = atr * stop_atr_multiplier
    if stop_distance <= 0 or price <= 0:
        return 0
    qty = math.floor(single_risk / (stop_distance * price))
    max_qty_by_pct = math.floor((portfolio_value * max_position_pct) / price)
    qty = max(0, min(qty, max_qty_by_pct))
    return qty
