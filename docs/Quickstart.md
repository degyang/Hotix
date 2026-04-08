# Hotix 快速使用指南

这份指南面向第一次接触 Hotix、希望在几分钟内跑出结果的使用者。

## 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r market_system/requirements.txt
```

## 2. 运行单日市场摘要

```bash
python3 -m market_system.run_daily --date 2026-04-05
```

你会看到一个简化后的市场结果，核心关注：

- `market.market_regime.label`：市场阶段标签
- `market.market_regime.score`：Regime 得分
- `market.market_regime.confidence`：置信度

## 3. 看完整数据

如果你想看所有指数、指数对、trace 和市场信息：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --dump-json
```

这个输出适合：

- 排查 DSL 规则效果
- 观察 feature/state/tag 的实际产物
- 对照 golden fixture 做人工检查

## 4. 生成日报文件

把 JSON 和 Markdown 文件直接写到 `market_system/outputs/`：

```bash
python3 -m market_system.run_daily --start 2026-04-04 --end 2026-04-05 --write-files
```

生成结果：

- `market_system/outputs/json/2026-04-04.json`
- `market_system/outputs/json/2026-04-05.json`
- `market_system/outputs/markdown/2026-04-04.md`
- `market_system/outputs/markdown/2026-04-05.md`

Markdown 日报示例内容包括：

- 市场状态
- 今日最亮信号 / 最暗信号 / 预警 / 切换
- 结构关系
- Regime 证据
- 指数状态概览

## 5. 使用调试模式

调试单指数：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-index hs300
```

调试指数对：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-pair hs300_vs_cyb
```

调试市场级结果：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-market
```

这些模式适合快速判断：

- 某个 feature 是否按预期计算
- state 是否落到了正确分支
- pair / regime 规则是否命中

## 6. 运行测试

```bash
python3 -m pytest market_system/tests -q
```

如果环境正常，当前仓库应通过全部测试。

## 7. 当前版本的一个重要限制

当前默认数据源是：

- `market_system/tests/fixtures/*.csv`

这意味着它更像“可运行的引擎原型 + 样例数据”，不是直接接生产行情目录的成品版本。若要切到真实数据，需要修改 `market_system/engine/pipeline.py` 中 `build_context()` 使用的数据目录。

## 8. 你最可能会用到的 4 条命令

安装依赖：

```bash
python3 -m pip install -r market_system/requirements.txt
```

看单日摘要：

```bash
python3 -m market_system.run_daily --date 2026-04-05
```

看完整 JSON：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --dump-json
```

跑测试：

```bash
python3 -m pytest market_system/tests -q
```
