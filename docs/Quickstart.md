# Hotix 快速使用指南

这份指南面向第一次接触 Hotix、希望在几分钟内跑出结果的使用者。

## 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

## 2. 运行单日市场摘要

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

你会看到一个简化后的市场结果，核心关注：

- `market.market_regime.label`：市场阶段标签
- `market.market_regime.score`：Regime 得分
- `market.market_regime.confidence`：置信度

## 3. 看完整数据

如果你想看所有指数、指数对、trace 和市场信息：

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --dump-json
```

这个输出适合：

- 排查 DSL 规则效果
- 观察 feature/state/tag 的实际产物
- 对照 golden fixture 做人工检查

## 4. 生成日报文件

把 JSON 和 Markdown 文件写到 `src/hotix/outputs/`：

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures --write-files
```

Markdown 日报内容包括：

- 市场状态
- 今日最亮信号 / 最暗信号 / 预警 / 切换
- 结构关系
- Regime 证据
- 指数状态概览

## 5. 使用调试模式

调试单指数：

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-index 000300
```

调试指数对：

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-pair 000300_vs_399006
```

调试市场级结果：

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-market
```

## 6. 运行测试

```bash
python3 -m pytest
```

默认测试只使用 `tests/fixtures` 中的确定性样例数据。标记为 `external` 的测试依赖本机外部行情目录，默认不运行。

## 7. 数据目录要求

CSV 文件需要提供这些标准字段：

```text
date, open, high, low, close, volume, amount, adv, decl
```

加载器也会把以下外部字段名标准化：

```text
datetime -> date
vol -> volume
up_count -> adv
down_count -> decl
```

每个在 `src/hotix/config/index_registry.yaml` 中注册的指数，都需要在 `--data-dir` 指向的目录里有对应 CSV 文件，文件名可以是指数 id 或配置中的 `symbol`。
