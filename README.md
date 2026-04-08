# Hotix

Hotix 是一个基于规则和 DSL 的市场结构分析引擎原型，当前聚焦 Phase I 能力：

- 3 个指数：`hs300`、`cyb`、`csi1000`
- 2 个指数对：`hs300_vs_cyb`、`hs300_vs_csi1000`
- 输出市场状态、结构关系、Regime 判断、调试信息
- 支持 JSON 输出、Markdown 输出、单指数/指数对调试

当前仓库已经在 macOS + Python 3.12 下验证可运行。

## 项目结构

```text
Hotix/
├─ market_system/
│  ├─ config/                 # 指数注册表
│  ├─ dsl/                    # 规则 DSL
│  ├─ engine/                 # 核心引擎
│  ├─ outputs/                # 运行生成的 JSON / Markdown
│  ├─ tests/
│  │  ├─ fixtures/            # 当前默认示例数据
│  │  ├─ integration/
│  │  ├─ golden/
│  │  └─ unit/
│  ├─ requirements.txt
│  └─ run_daily.py            # CLI 入口
└─ docs/
```

## 环境要求

- macOS、Linux 或 Windows
- Python 3.12+
- `pip`

## 安装依赖

建议使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r market_system/requirements.txt
```

## 快速运行

运行某一天的市场摘要：

```bash
python3 -m market_system.run_daily --date 2026-04-05
```

示例输出：

```json
{
  "date": "2026-04-05",
  "market": {
    "date": "2026-04-05",
    "relation_tags": [],
    "top_positive": [],
    "top_negative": [],
    "top_warning": [],
    "top_transition": [],
    "market_regime": {
      "label": "混沌市",
      "score": 4.0,
      "confidence": 0.8
    }
  }
}
```

输出完整 JSON：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --dump-json
```

写出 JSON 和 Markdown 文件：

```bash
python3 -m market_system.run_daily --start 2026-04-04 --end 2026-04-05 --write-files
```

输出文件位于：

- `market_system/outputs/json/`
- `market_system/outputs/markdown/`

## 调试命令

查看单个指数的完整调试载荷：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-index hs300
```

查看某个指数对的调试载荷：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-pair hs300_vs_cyb
```

查看市场级调试信息：

```bash
python3 -m market_system.run_daily --date 2026-04-05 --debug-market
```

## 测试

运行全部测试：

```bash
python3 -m pytest market_system/tests -q
```

当前已验证结果：

```text
33 passed
```

## 数据说明

当前 CLI 默认通过 `build_context("market_system")` 加载：

- `market_system/config/index_registry.yaml`
- `market_system/dsl/*.yaml`
- `market_system/tests/fixtures/*.csv`

也就是说，仓库当前默认跑的是测试夹具数据，而不是独立的生产数据目录。如果你要接入真实日线数据，至少需要：

1. 准备与夹具相同字段结构的 CSV。
2. 调整 `market_system/engine/pipeline.py` 中 `build_context()` 的数据目录来源。
3. 保持注册表中的指数 id 与 CSV 文件名一致。

CSV 当前要求的列为：

```text
date, open, high, low, close, volume, amount, adv, decl
```

## 常见命令

安装依赖：

```bash
python3 -m pip install -r market_system/requirements.txt
```

单日运行：

```bash
python3 -m market_system.run_daily --date 2026-04-05
```

区间运行并写文件：

```bash
python3 -m market_system.run_daily --start 2026-04-04 --end 2026-04-05 --write-files
```

运行测试：

```bash
python3 -m pytest market_system/tests -q
```

## 延伸阅读

- 快速使用指南：[`docs/Quickstart.md`](docs/Quickstart.md)
- 设计文档：[`docs/superpowers/specs/2026-04-06-hotix-phase1-engine-design.md`](docs/superpowers/specs/2026-04-06-hotix-phase1-engine-design.md)
# Hotix
