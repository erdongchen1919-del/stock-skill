"""
TqSdk Broker Adapter - STUB

提示：此文件为接入 TqSdk/TqSim 的示例骨架。TqSdk 的具体下单 API 需参考官方文档并在生产环境中用环境变量或 Vault 管理密钥/账户信息。
示例要点：
- paper: api = TqApi(TqSim())
- live: api = TqApi(...) 并提供实际账号/证书
- 下单示例（伪代码; 请按 tqsdk 文档调整参数）：
    order = api.insert_order(symbol="SHSE.600519", direction="BUY", offset="OPEN", volume=100, limit_price=None)
- 查询委托/回报使用 api.wait_update() 与 order 字段检查

请在真实使用前用官方文档验证 insert_order/TargetPosTask 的函数签名与参数。
"""
from tqsdk import TqApi, TqSim

class TqSdkBroker:
    def __init__(self, mode="paper", sim_balance=100000):
        self.mode = mode
        if mode == "paper":
            self.api = TqApi(TqSim())
            # TODO: 配置模拟账户初始资金（若需要）
        else:
            # TODO: 生产环境下初始化 api（可能需要用户凭据）
            self.api = TqApi()
        # 持仓/订单需要通过 api 查询

    def get_account_value(self):
        # TODO: 使用 tqsdk 查询账户净值并返回
        raise NotImplementedError("请在 broker_tqsdk.py 中实现 get_account_value")

    def place_market_order(self, symbol, qty, side='BUY'):
        # TODO: 使用 api.insert_order 下单并返回订单状态
        raise NotImplementedError("请在 broker_tqsdk.py 中实现 place_market_order")

    def close(self):
        try:
            self.api.close()
        except:
            pass
