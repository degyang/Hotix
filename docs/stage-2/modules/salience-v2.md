---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Salience v2 Core 需求规格

## 1. 定位

Salience v2 Core 是 Hotix 下一阶段的第一块核心能力。

它不负责预测，不负责回测，不负责给交易建议。它只负责一件事：

```text
把市场中已经发生的结构信号，转化为可排序、可解释、可追溯的显著性对象。
```

当前 Hotix 已能识别 features、states、patterns、transitions，但这些输出仍偏“信号列表”。Salience v2 Core 要解决的问题是：

```text
哪些信号最重要？
为什么重要？
属于哪个市场维度？
影响方向是什么？
证据来自哪里？
是否只是观察项，还是明确风险/正向/背离？
```

它是后续 Universe Analysis 和 Market Profile 的基础。

## 2. 核心目标

Salience v2 Core 的核心不是“多几个标签”，而是要建立一套横截面显著性机制：

```text
在一个给定组合样本中，对价格、量能、波动等多个维度分别排序，
输出每个维度最显著的正向 TOPN 和负向 TOPN。
```

也就是说，Salience 必须优先回答：

```text
今天谁涨得最显著？
今天谁跌得最显著？
今天谁放量最显著？
今天谁缩量最显著？
今天谁波动扩张最显著？
今天谁波动收缩最显著？
```

这里的 TOPN 是横截面概念，必须基于一个组合样本计算。样本可以是当前 8 个核心指数，后续也可以是行业指数、ETF 组合或股票池。

Salience v2 Core 完成后，每个资产的 salience 必须从简单 bucket：

```json
{
  "negative": {
    "score": 2.2,
    "reasons": ["广度极弱"]
  }
}
```

升级为结构化 items：

```json
{
  "items": [
    {
      "id": "sal_breadth_weak_000300",
      "date": "2026-05-27",
      "scope": "asset",
      "asset_id": "000300",
      "universe_id": null,
      "dimension": "breadth",
      "category": "negative",
      "polarity": "negative",
      "severity": "high",
      "score": 2.2,
      "confidence": "medium",
      "freshness": "new",
      "reason": "广度极弱",
      "evidence": {
        "breadth_ratio": 0.31,
        "breadth_state": "weak"
      },
      "tags": ["participation_risk"],
      "confirmation": {}
    }
  ]
}
```

同时必须保留旧 bucket 输出：

```json
{
  "negative": {
    "score": 2.2,
    "reasons": ["广度极弱"]
  }
}
```

这是兼容性要求，PR 1 不允许破坏旧报告、旧 golden、旧 market salience 汇总。

## 2.1 横截面 TOPN 是硬需求

Salience v2 Core 必须支持以下指标族的 TOPN 排名。

### 2.1.1 价格涨跌 price

关注指标：

```text
ret_1d
ret_5d
ret_20d
```

正向 TOPN：

```text
收益最高的 N 个资产
```

负向 TOPN：

```text
收益最低的 N 个资产
```

典型输出：

```json
{
  "metric": "ret_1d",
  "dimension": "price",
  "positive_topn": [
    {"asset_id": "399006", "value": 0.024, "rank": 1}
  ],
  "negative_topn": [
    {"asset_id": "000852", "value": -0.018, "rank": 1}
  ]
}
```

### 2.1.2 量能 volume

关注指标：

```text
amount_ratio_1_20
amount_ratio_5_20
amount_percentile_120d
```

量能的正负不能只按数值大小机械判断。量能必须结合价格方向解释：

```text
放量上涨 -> 正向量价确认
放量下跌 -> 负向风险确认
缩量上涨 -> 预警或观察
缩量下跌 -> 负向延续或抛压减弱，第一版归为 observation
```

PR 1 的最小实现：

```text
volume_expansion_topn: amount_ratio 最高的 N 个资产
volume_contraction_topn: amount_ratio 最低的 N 个资产
```

同时为每个 top item 附带 `ret_1d`，让后续报告能判断是放量上涨还是放量下跌。

### 2.1.3 波动 volatility

关注指标：

```text
atr_pct_14
volatility_percentile_250d
true_range / close
```

正向/负向解释：

```text
波动扩张本身不是正向，也不是负向；
它是风险显著性。
```

因此第一版输出：

```text
volatility_expansion_topn: 波动最高/扩张最明显的 N 个资产
volatility_contraction_topn: 波动最低/压缩最明显的 N 个资产
```

category 使用：

```text
warning
observation
```

不强行归类为 positive/negative。

### 2.1.4 广度 breadth

关注指标：

```text
breadth_ratio
breadth_diff
breadth_ratio_ma_5
```

正向 TOPN：

```text
广度最强的 N 个资产
```

负向 TOPN：

```text
广度最弱的 N 个资产
```

广度是市场健康度最重要的维度之一，应在 Universe 和 Market Profile 中优先展示。

### 2.1.5 位置 position

关注指标：

```text
price_percentile_120d
distance_to_ma20
```

输出：

```text
highest_position_topn: 位置最高的 N 个资产
lowest_position_topn: 位置最低的 N 个资产
```

解释：

```text
高位不是天然正向，低位也不是天然负向；
位置 topN 用于解释风险收益位置和拥挤程度。
```

## 2.2 TOPN 输出契约

Salience v2 Core 必须提供一个通用横截面输出结构：

```json
{
  "cross_section": {
    "price": {
      "ret_1d": {
        "positive_topn": [],
        "negative_topn": []
      }
    },
    "volume": {
      "amount_ratio_1_20": {
        "expansion_topn": [],
        "contraction_topn": []
      }
    },
    "volatility": {
      "volatility_percentile_250d": {
        "expansion_topn": [],
        "contraction_topn": []
      }
    },
    "breadth": {
      "breadth_ratio": {
        "positive_topn": [],
        "negative_topn": []
      }
    },
    "position": {
      "price_percentile_120d": {
        "highest_topn": [],
        "lowest_topn": []
      }
    }
  }
}
```

每个 top item 至少包含：

```text
asset_id
rank
value
dimension
metric
direction
date
related_values
reason
```

示例：

```json
{
  "asset_id": "399006",
  "rank": 1,
  "value": 0.024,
  "dimension": "price",
  "metric": "ret_1d",
  "direction": "positive",
  "date": "2026-05-27",
  "related_values": {
    "amount_ratio_1_20": 1.46,
    "breadth_ratio": 0.61
  },
  "reason": "日涨幅位列组合第 1"
}
```

## 2.3 TOPN 与 SalienceItem 的关系

横截面 TOPN 也应生成 `SalienceItem`，但它的来源不是单资产 rule，而是 cross-section ranking。

建议字段：

```text
scope: asset
dimension: price / volume / volatility / breadth / position
category: positive / negative / warning / observation
polarity: positive / negative / neutral / mixed
tags:
  - cross_section_topn
  - price_leader
```

item id 示例：

```text
rank_ret_1d_positive_399006
rank_ret_1d_negative_000852
rank_amount_ratio_1_20_expansion_000680
```

这样报告既可以展示结构化 `cross_section`，也可以把 TOPN 显著项混入统一 salience item 流。

## 3. 不做什么

Salience v2 Core 明确不做：

- 不做 Universe 汇总。
- 不做 Market Profile。
- 不做 pair 重构。
- 不做预测。
- 不做回测。
- 不做反馈校准。
- 不做交易 setup。
- 不做持仓/仓位/执行。
- 不改变当前 CLI 语义。

PR 1 只做 asset-level structured salience 与通用 cross-section TOPN 计算能力。PR 2 再把 TOPN 按 `universes.yaml` 接入具体组合。

## 4. 输入

Salience v2 Core 的输入仍然是当前 `IndexRuntime`：

```python
IndexRuntime(
    id="000300",
    date="2026-05-27",
    raw={...},
    features={...},
    states={...},
    pattern_tags=[...],
    transition_tags=[...],
    salience={...},
    trace={...},
)
```

可用证据来源：

```text
raw
features
states
pattern_tags
transition_tags
```

第一版不读取 pair、market、universe。

## 5. 输出

`runtime.salience` 必须包含：

```text
items
positive
negative
warning
transition
```

其中：

```text
items       新结构化显著性对象列表
positive    旧兼容 bucket
negative    旧兼容 bucket
warning     旧兼容 bucket
transition  旧兼容 bucket
```

bucket 结构保持：

```json
{
  "score": 2.2,
  "reasons": ["广度极弱"]
}
```

items 与 bucket 的关系：

- 每条命中的 salience rule 必须生成一个 item。
- 如果 rule 有 `bucket`，则同步累加到旧 bucket。
- item 是主输出，bucket 是兼容输出。

## 6. SalienceItem 字段规范

### 6.1 必填字段

| 字段 | 类型 | 示例 | 说明 |
|---|---|---|---|
| id | str | sal_breadth_weak_000300 | item 唯一 ID，建议 rule_id + asset_id |
| date | str | 2026-05-27 | 交易日期 |
| scope | str | asset | PR 1 固定为 asset |
| asset_id | str | 000300 | 指数/资产 ID |
| universe_id | str/null | null | PR 1 固定为 null |
| dimension | str | breadth | 分析维度 |
| category | str | negative | 显著性分类 |
| polarity | str | negative | 方向性 |
| severity | str | high | 严重程度 |
| score | float | 2.2 | 显著性分数 |
| confidence | str | medium | 证据充分度 |
| freshness | str | new | 新鲜度 |
| reason | str | 广度极弱 | 人类可读解释 |
| evidence | dict | {"breadth_ratio": 0.31} | 原始证据 |
| tags | list[str] | ["participation_risk"] | 机器可读标签 |
| confirmation | dict | {} | 多维确认信息 |

### 6.2 字段取值

`scope`：

```text
asset
```

PR 1 只允许 `asset`。

`dimension`：

```text
trend
position
volume
breadth
volatility
structure
anomaly
```

`category`：

```text
positive
negative
warning
transition
divergence
observation
```

`polarity`：

```text
positive
negative
neutral
mixed
```

`severity`：

```text
low
medium
high
critical
```

`confidence`：

```text
low
medium
high
```

注意：这里的 confidence 是“证据充分度”，不是预测置信度。

`freshness`：

```text
new
persistent
fading
unknown
```

PR 1 可以先用 `unknown` 作为默认值；如果 rule 配置了 freshness，则使用配置值。真正的 persistent/fading 需要更完整的跨日逻辑，可留到后续。

## 7. Salience DSL v2 需求

`src/hotix/dsl/salience.yaml` 每条规则必须支持以下字段：

```yaml
- id: s_extreme_breadth_weak
  dimension: breadth
  category: negative
  polarity: negative
  severity: high
  confidence: medium
  freshness: unknown
  group: extreme
  when: "self.breadth_state == 'weak'"
  score: 2.2
  bucket: negative
  reason: 广度极弱
  evidence_fields:
    - breadth_ratio
    - breadth_state
  tags:
    - participation_risk
```

### 7.1 必填字段

```text
id
dimension
category
polarity
severity
confidence
when
score
bucket
reason
```

### 7.2 可选字段

```text
freshness
group
evidence_fields
tags
confirmation_fields
```

### 7.3 兼容字段

当前已有字段必须继续支持：

```text
group
when
score
bucket
polarity
reason
```

如果已有规则中 `polarity` 已存在，沿用它，但必须与新字段语义一致。

## 8. Validator 需求

`validate_all_dsl()` 必须校验：

- `salience.yaml` 存在 `scoring_rules`。
- 每条 rule 有唯一 `id`。
- 每条 rule 有必填字段。
- `dimension` 在允许集合中。
- `category` 在允许集合中。
- `polarity` 在允许集合中。
- `severity` 在允许集合中。
- `confidence` 在允许集合中。
- `bucket` 在旧 bucket 集合中：

```text
positive
negative
warning
transition
```

- `when` 表达式可编译。
- `score` 可转换为 float。
- `evidence_fields` 如果存在，必须是 list。
- `tags` 如果存在，必须是 list。

错误信息必须可定位到 rule id，例如：

```text
salience rule missing dimension: s_extreme_breadth_weak
salience rule invalid category: s_extreme_breadth_weak
```

## 9. Evidence 解析需求

Salience engine 必须能从 runtime 中解析 evidence field。

解析顺序：

```text
raw
features
states
special fields
```

special fields：

```text
pattern_tags
transition_tags
```

例如：

```yaml
evidence_fields:
  - breadth_ratio
  - breadth_state
  - pattern_tags
```

输出：

```json
{
  "breadth_ratio": 0.31,
  "breadth_state": "weak",
  "pattern_tags": ["指数上行但跟随不足"]
}
```

如果 evidence field 缺失：

- 不应让整个 pipeline 崩溃。
- 应在 evidence 中跳过该字段。
- 可在 trace 中记录 missing evidence。

第一版可以只跳过缺失字段，后续再增强 trace。

## 10. Scoring 需求

PR 1 不做复杂动态评分，只保留当前规则分：

```text
item.score = float(rule["score"])
```

不在 PR 1 实现：

```text
intensity_score
scope_score
confirmation_score
freshness_score
rarity_score
conflict_penalty
```

这些属于 Salience v2 后续增强，不进入 Core。

但字段设计必须为后续保留空间。

## 11. Bucket 兼容需求

旧 bucket 必须继续工作。

如果命中规则：

```yaml
bucket: negative
score: 2.2
reason: 广度极弱
```

则输出：

```json
"negative": {
  "score": 2.2,
  "reasons": ["广度极弱"]
}
```

多个规则命中同一 bucket：

- score 累加。
- reasons 追加。
- reasons 不强制去重，保持当前行为即可；如当前已有去重行为则保持。

## 12. Trace 需求

`runtime.trace["salience"]` 应继续保留当前信息，并新增 structured item trace。

最低要求：

```json
{
  "salience": {
    "matched_rules": [
      {
        "rule_id": "s_extreme_breadth_weak",
        "item_id": "s_extreme_breadth_weak_000300",
        "dimension": "breadth",
        "category": "negative",
        "score": 2.2,
        "bucket": "negative"
      }
    ]
  }
}
```

如果当前 trace 结构不同，PR 1 应尽量向后兼容，不要无理由删除旧 trace 字段。

## 13. 真实数据 TDD 需求

必须新增或修改 external 测试，使用：

```text
~/data/index/daily
```

测试要求：

- 构建 context 成功。
- 使用 latest common date，不硬编码日期。
- 至少一个指数产生 `salience.items`。
- item 包含核心字段：

```text
dimension
category
polarity
severity
score
reason
evidence
```

示例：

```python
@pytest.mark.external
def test_real_data_latest_produces_structured_salience_items():
    ctx = build_context(PACKAGE_ROOT, data_dir=Path("~/data/index/daily").expanduser())
    payload = run_single_date(ctx, latest_available_date(ctx))

    all_items = [
        item
        for runtime in payload["indices"].values()
        for item in runtime["salience"].get("items", [])
    ]

    assert all_items
    assert {"dimension", "category", "polarity", "severity", "score", "reason", "evidence"} <= set(all_items[0])
```

## 14. Fixture / Golden 需求

PR 1 必须更新：

```text
tests/fixtures/expected_daily_2026-04-03.json
```

新增字段：

```text
indices.*.salience.items
```

旧字段保持：

```text
market.top_positive
market.top_negative
market.top_warning
market.top_transition
```

Golden 的意义是锁住结构，不是评价市场观点。

## 15. 文档需求

PR 1 至少更新：

```text
docs/Architecture.md
docs/Development.md
```

必须写清：

- Salience v2 是结构化显著性。
- confidence 是证据充分度，不是预测置信度。
- Hotix 当前不做预测和交易建议。
- 旧 bucket 仍保留兼容。

## 16. 测试清单

PR 1 必须通过：

```bash
.venv/bin/python -m pytest tests/unit/test_salience_v2.py -v
.venv/bin/python -m pytest tests/unit/test_salience_engine.py -v
.venv/bin/python -m pytest tests/unit/test_validator.py -v
.venv/bin/python -m pytest tests/integration/test_external_real_data.py -m external -v
.venv/bin/python -m pytest
.venv/bin/python -m pytest -m external
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

## 17. 完成定义

Salience v2 Core 完成时，必须满足：

- 每条命中的 salience rule 都生成 structured item。
- 每个 item 有 dimension/category/polarity/severity/evidence/reason。
- 旧 bucket 输出不破坏。
- validator 能拒绝 schema 不完整的 salience rule。
- 真实数据 latest 日能跑出 structured salience items。
- Golden 已更新。
- 文档已更新。
- 不引入预测、回测、交易建议。

## 18. 评审问题清单

PR 评审时必须逐项回答：

- 是否保留了旧 bucket 兼容？
- 是否所有 rule 都有 dimension/category/polarity/severity？
- confidence 是否没有被写成预测置信度？
- evidence 是否来自 runtime 已有字段？
- external 测试是否使用动态 latest common date？
- 报告或文档是否出现预测/买卖建议语言？
- 是否避免了 Universe/Market Profile 的提前实现？

---

Parent: [[10-Projects/Active/11.09 Hotix/Overview]]
