项目：炒股-skill (MVP)

功能（MVP）
- 选股：20 日动量排名（Top N）
- 风控：基于 ATR 的止损距离、单笔风险与仓位上限
- 执行：本地模拟器（模拟市价成交、持仓与现金）
- 数据：使用 akshare 拉取 A 股日线（如需替换数据源可改 utils.py）
- 监控：运行日志 + 可配置 webhook（钉钉/企业微信/Slack）

快速开始
1. 创建虚拟环境并安装依赖：
   pip install -r requirements.txt

2. 编辑 config.yaml（调整 universe、回测区间、策略参数）

3. 运行一次性模拟/回测（快速验证）：
   python main.py --once

4. 运行为定时任务（每天 09:30 执行策略）：
   python main.py

切换到真实券商
- 目前默认使用本地模拟器 broker_simulator.py；若要接入 TqSdk/TqSim，请参考 broker_tqsdk.py stub 并按注释补充真实接入细节与密钥管理（密钥请用环境变量或 Vault，不要直接放到代码或聊天）。
