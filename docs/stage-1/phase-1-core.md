
Hotix是市场分析引擎，设计方案如下所述。
* 系统目标
* 系统边界
* 目录结构
* 数据结构
* DSL 文件定义
* 执行流程
* 每个模块职责
* 开发顺序
* 每一步产出
* 调试方法
* 第一版最小可用范围

---

# 一、项目目标

构建一个面向中国 A 股核心指数的**市场结构识别引擎**，输入为指数 OHLCV、成交额、成分股上涨/下跌家数，输出为：
1. 单指数特征与状态
2. 单指数模式标签
3. 单指数显著性结论
4. 指数间结构关系标签
5. 市场总体结构分类
6. 面向人工复盘的结构化日报输入

---

# 二、第一版范围

第一版不要做满 8 个指数，先做最小闭环。

## 2.1 指数范围

先做 3 个指数：
* 沪深300：`hs300`
* 创业板指：`cyb`
* 中证1000：`csi1000`

## 2.2 pair 范围

先做 2 对：
* `hs300_vs_cyb`
* `hs300_vs_csi1000`

## 2.3 输出目标

第一版每天输出：
* 3 个指数的状态
* 每个指数的 pattern tags
* 每个指数的 salience 结果
* 2 个 pair 的 relation tags
* 1 个 market regime
* 1 份 JSON
* 1 份 Markdown

---

# 三、技术边界

## 3.1 规则引擎负责
* 数据读取
* 指标计算
* 状态离散化
* pattern 打标
* transition 打标
* salience 评分
* pair 比较
* relation tags
* regime 分类

## 3.2 LLM 不参与第一版判断

第一版不要接 LLM。
先把**结构化判断引擎**跑通。

等 JSON 和 Markdown 稳定后，再接 LLM 做语言润色。

---

# 四、项目目录结构

直接按下面创建：

```text
market_system/
├─ data/
│  ├─ raw/
│  │  ├─ hs300.csv
│  │  ├─ cyb.csv
│  │  └─ csi1000.csv
│  ├─ processed/
│  └─ snapshots/
│
├─ dsl/
│  ├─ features.yaml
│  ├─ states.yaml
│  ├─ patterns.yaml
│  ├─ transitions.yaml
│  ├─ salience.yaml
│  ├─ pairs.yaml
│  ├─ pair_features.yaml
│  ├─ pair_states.yaml
│  ├─ relation_tags.yaml
│  └─ regimes.yaml
│
├─ engine/
│  ├─ models.py
│  ├─ loader.py
│  ├─ validator.py
│  ├─ resolver.py
│  ├─ expression.py
│  ├─ feature_engine.py
│  ├─ state_engine.py
│  ├─ tag_engine.py
│  ├─ salience_engine.py
│  ├─ pair_engine.py
│  ├─ regime_engine.py
│  ├─ pipeline.py
│  └─ trace.py
│
├─ outputs/
│  ├─ json/
│  └─ markdown/
│
├─ config/
│  └─ index_registry.yaml
│
├─ run_daily.py
└─ requirements.txt
```

---

# 五、输入数据标准

每个指数原始表必须至少有以下字段：

```text
date
open
high
low
close
volume
amount
adv
decl
```

要求：

1. `date` 为交易日
2. `amount` 为成交额
3. `adv` / `decl` 为该指数成分股当日上涨 / 下跌家数
4. 每个指数单独一张表
5. 全部按日期升序
6. 缺失值先在数据预处理阶段处理，不要在规则层临时补

---

# 六、核心运行时对象

系统内部只维护三类对象。

## 6.1 单指数对象 `IndexRuntime`

```python
{
  "id": "hs300",
  "date": "2026-04-05",
  "raw": {},
  "features": {},
  "states": {},
  "pattern_tags": [],
  "transition_tags": [],
  "salience": {
    "total_score": 0.0,
    "positive_score": 0.0,
    "negative_score": 0.0,
    "warning_score": 0.0,
    "transition_score": 0.0,
    "matched_rules": []
  },
  "trace": {}
}
```

## 6.2 pair 对象 `PairRuntime`

```python
{
  "id": "hs300_vs_cyb",
  "date": "2026-04-05",
  "left": "hs300",
  "right": "cyb",
  "features": {},
  "states": {},
  "relation_tags": [],
  "trace": {}
}
```

## 6.3 market 对象 `MarketRuntime`

```python
{
  "date": "2026-04-05",
  "top_positive": [],
  "top_negative": [],
  "top_warning": [],
  "top_transition": [],
  "relation_tags": [],
  "market_regime": {
    "label": "",
    "score": 0.0,
    "confidence": 0.0,
    "evidence": []
  },
  "trace": {}
}
```

---

# 七、字段命名规范

必须从第一天就固定。

## 7.1 原始字段

```text
open high low close volume amount adv decl
```

## 7.2 feature 字段

```text
ret_1d ret_5d ret_20d
ma_20 ma_60
ma_slope_20
distance_to_ma20
price_percentile_120d
amount_ma_20
amount_ratio_1_20
amount_ratio_5_20
amount_percentile_120d
breadth_ratio
breadth_diff
breadth_ratio_ma_5
atr_14
atr_pct_14
volatility_percentile_250d
breakout_20d
breakdown_20d
```

## 7.3 state 字段

统一 `_state` 结尾：

```text
trend_state
position_state
volume_state
breadth_state
volatility_state
leader_state
confirmation_state
spread_state
leadership_persistence_state
```

## 7.4 tag 字段

统一 list：

```text
pattern_tags
transition_tags
relation_tags
```

---

# 八、第一版 DSL 文件内容

下面是第一版必须写的配置文件。

---

## 8.1 `config/index_registry.yaml`

```yaml
indices:
  hs300:
    name: 沪深300
    role: core_benchmark
    layer: core

  cyb:
    name: 创业板指
    role: growth_risk_appetite
    layer: growth

  csi1000:
    name: 中证1000
    role: small_cap_sentiment
    layer: sentiment
```

---

## 8.2 `dsl/features.yaml`

第一版只放这些 feature：

```yaml
version: "0.1"
dsl_type: features

features:
  - id: ret_1d
    type: formula
    input: [close]
    formula: "close / delay(close, 1) - 1"
    output: ret_1d

  - id: ret_5d
    type: formula
    input: [close]
    formula: "close / delay(close, 5) - 1"
    output: ret_5d

  - id: ret_20d
    type: formula
    input: [close]
    formula: "close / delay(close, 20) - 1"
    output: ret_20d

  - id: ma_20
    type: rolling
    input: [close]
    window: 20
    method: mean
    output: ma_20

  - id: ma_60
    type: rolling
    input: [close]
    window: 60
    method: mean
    output: ma_60

  - id: ma_slope_20
    type: formula
    input: [ma_20]
    formula: "ma_20 / delay(ma_20, 5) - 1"
    output: ma_slope_20

  - id: distance_to_ma20
    type: formula
    input: [close, ma_20]
    formula: "close / ma_20 - 1"
    output: distance_to_ma20

  - id: price_percentile_120d
    type: percentile
    input: [close]
    window: 120
    output: price_percentile_120d

  - id: amount_ma_20
    type: rolling
    input: [amount]
    window: 20
    method: mean
    output: amount_ma_20

  - id: amount_ratio_1_20
    type: formula
    input: [amount, amount_ma_20]
    formula: "amount / amount_ma_20"
    output: amount_ratio_1_20

  - id: amount_ratio_5_20
    type: formula
    input: [amount]
    formula: "rolling_mean(amount, 5) / rolling_mean(amount, 20)"
    output: amount_ratio_5_20

  - id: amount_percentile_120d
    type: percentile
    input: [amount]
    window: 120
    output: amount_percentile_120d

  - id: breadth_ratio
    type: formula
    input: [adv, decl]
    formula: "adv / (adv + decl + 1e-9)"
    output: breadth_ratio

  - id: breadth_diff
    type: formula
    input: [adv, decl]
    formula: "adv - decl"
    output: breadth_diff

  - id: breadth_ratio_ma_5
    type: rolling
    input: [breadth_ratio]
    window: 5
    method: mean
    output: breadth_ratio_ma_5

  - id: true_range
    type: formula
    input: [high, low, close]
    formula: "max(high - low, abs(high - delay(close, 1)), abs(low - delay(close, 1)))"
    output: true_range

  - id: atr_14
    type: rolling
    input: [true_range]
    window: 14
    method: mean
    output: atr_14

  - id: atr_pct_14
    type: formula
    input: [atr_14, close]
    formula: "atr_14 / close"
    output: atr_pct_14

  - id: volatility_percentile_250d
    type: percentile
    input: [atr_pct_14]
    window: 250
    output: volatility_percentile_250d

  - id: breakout_20d
    type: boolean
    input: [close, high]
    formula: "close > rolling_max(high, 20, exclude_current=true)"
    output: breakout_20d

  - id: breakdown_20d
    type: boolean
    input: [close, low]
    formula: "close < rolling_min(low, 20, exclude_current=true)"
    output: breakdown_20d
```

---

## 8.3 `dsl/states.yaml`

```yaml
version: "0.1"
dsl_type: states

states:
  - id: trend_state
    output: trend_state
    cases:
      - when: "self.close > self.ma_20 and self.ma_20 > self.ma_60 and self.ma_slope_20 > 0"
        value: up
      - when: "self.close < self.ma_20 and self.ma_20 < self.ma_60 and self.ma_slope_20 < 0"
        value: down
      - when: "self.close > self.ma_20 and self.ma_20 <= self.ma_60"
        value: transitional_up
      - when: "self.close < self.ma_20 and self.ma_20 >= self.ma_60"
        value: transitional_down
    default: range

  - id: position_state
    output: position_state
    cases:
      - when: "self.price_percentile_120d <= 0.20"
        value: low
      - when: "self.price_percentile_120d <= 0.40"
        value: low_mid
      - when: "self.price_percentile_120d <= 0.60"
        value: mid
      - when: "self.price_percentile_120d <= 0.80"
        value: mid_high
    default: high

  - id: volume_state
    output: volume_state
    cases:
      - when: "self.amount_ratio_1_20 <= 0.65 and self.amount_percentile_120d <= 0.15"
        value: extreme_contraction
      - when: "self.amount_ratio_1_20 <= 0.85"
        value: contraction
      - when: "self.amount_ratio_1_20 < 1.15"
        value: normal
      - when: "self.amount_ratio_1_20 < 1.50"
        value: expansion
    default: extreme_expansion

  - id: breadth_state
    output: breadth_state
    cases:
      - when: "self.breadth_ratio < 0.35"
        value: weak
      - when: "self.breadth_ratio < 0.45"
        value: neutral_weak
      - when: "self.breadth_ratio <= 0.55"
        value: neutral
      - when: "self.breadth_ratio <= 0.65"
        value: neutral_strong
    default: strong

  - id: volatility_state
    output: volatility_state
    cases:
      - when: "self.volatility_percentile_250d <= 0.20"
        value: low
      - when: "self.volatility_percentile_250d <= 0.60"
        value: medium
      - when: "self.volatility_percentile_250d <= 0.85"
        value: high
    default: extreme
```

---

## 8.4 `dsl/patterns.yaml`

第一版先做 6 个：

```yaml
version: "0.1"
dsl_type: patterns

patterns:
  - id: p_low_volume_repair
    group: reversal
    priority: 80
    when: "self.position_state in ['low', 'low_mid'] and self.volume_state in ['expansion', 'extreme_expansion'] and self.ret_1d > 0 and self.breadth_state in ['neutral_strong', 'strong']"
    add_tag: 低位放量修复

  - id: p_mid_trend_breakout
    group: breakout
    priority: 90
    when: "self.trend_state == 'up' and self.position_state in ['mid', 'mid_high'] and self.breakout_20d == true and self.volume_state in ['expansion', 'extreme_expansion']"
    add_tag: 中继放量突破

  - id: p_high_volume_divergence
    group: warning
    priority: 95
    when: "self.position_state == 'high' and self.volume_state == 'extreme_expansion' and self.ret_1d > -0.01 and self.ret_1d < 0.01"
    add_tag: 高位放量分歧

  - id: p_down_on_expansion
    group: breakdown
    priority: 85
    when: "self.ret_1d < 0 and self.volume_state in ['expansion', 'extreme_expansion'] and self.breadth_state in ['weak', 'neutral_weak']"
    add_tag: 放量下跌

  - id: p_pullback_on_contraction
    group: continuation
    priority: 75
    when: "self.trend_state == 'up' and self.ret_1d < 0 and self.volume_state in ['contraction', 'extreme_contraction'] and self.close > self.ma_60"
    add_tag: 缩量回踩

  - id: p_index_up_breadth_weak
    group: divergence
    priority: 88
    when: "self.ret_1d > 0 and self.breadth_state in ['weak', 'neutral_weak']"
    add_tag: 指数上行但跟随不足
```

---

## 8.5 `dsl/transitions.yaml`

```yaml
version: "0.1"
dsl_type: transitions

transitions:
  - id: t_trend_upshift
    when: "prev.trend_state in ['range', 'transitional_up'] and self.trend_state == 'up'"
    add_tag: 趋势转上

  - id: t_trend_downshift
    when: "prev.trend_state in ['range', 'transitional_down'] and self.trend_state == 'down'"
    add_tag: 趋势转下

  - id: t_volume_jump
    when: "prev.volume_state in ['contraction', 'normal'] and self.volume_state == 'extreme_expansion'"
    add_tag: 量能跳升

  - id: t_breadth_deterioration
    when: "prev.breadth_state in ['neutral', 'neutral_strong', 'strong'] and self.breadth_state in ['weak', 'neutral_weak']"
    add_tag: 广度恶化
```

---

## 8.6 `dsl/salience.yaml`

```yaml
version: "0.1"
dsl_type: salience

salience:
  scoring_rules:
    - id: s_pattern_trend_breakout
      group: pattern
      when: "'中继放量突破' in self.pattern_tags"
      score: 2.6
      bucket: positive
      polarity: positive
      reason: 中继放量突破

    - id: s_pattern_low_repair
      group: pattern
      when: "'低位放量修复' in self.pattern_tags"
      score: 2.1
      bucket: positive
      polarity: positive
      reason: 低位放量修复

    - id: s_pattern_high_divergence
      group: pattern
      when: "'高位放量分歧' in self.pattern_tags"
      score: 2.8
      bucket: warning
      polarity: negative
      reason: 高位放量分歧

    - id: s_pattern_down_on_expansion
      group: pattern
      when: "'放量下跌' in self.pattern_tags"
      score: 2.5
      bucket: negative
      polarity: negative
      reason: 放量下跌

    - id: s_pattern_up_breadth_weak
      group: divergence
      when: "'指数上行但跟随不足' in self.pattern_tags"
      score: 2.4
      bucket: warning
      polarity: negative
      reason: 指数上行但跟随不足

    - id: s_extreme_breadth_weak
      group: extreme
      when: "self.breadth_state == 'weak'"
      score: 2.2
      bucket: negative
      polarity: negative
      reason: 广度极弱

    - id: s_extreme_breadth_strong
      group: extreme
      when: "self.breadth_state == 'strong'"
      score: 2.0
      bucket: positive
      polarity: positive
      reason: 广度极强

    - id: s_transition_trend_to_up
      group: transition
      when: "'趋势转上' in self.transition_tags"
      score: 2.2
      bucket: transition
      polarity: positive
      reason: 趋势转上

    - id: s_transition_trend_to_down
      group: transition
      when: "'趋势转下' in self.transition_tags"
      score: 2.4
      bucket: transition
      polarity: negative
      reason: 趋势转下
```

---

## 8.7 `dsl/pairs.yaml`

```yaml
version: "0.1"
dsl_type: pairs

pairs:
  - id: hs300_vs_cyb
    left: hs300
    right: cyb
    tags: [core_vs_growth]

  - id: hs300_vs_csi1000
    left: hs300
    right: csi1000
    tags: [core_vs_small]
```

---

## 8.8 `dsl/pair_features.yaml`

```yaml
version: "0.1"
dsl_type: pair_features

pair_features:
  - id: rs_ret_5d
    type: formula
    input: [left.ret_5d, right.ret_5d]
    formula: "left.ret_5d - right.ret_5d"
    output: rs_ret_5d

  - id: rs_ret_20d
    type: formula
    input: [left.ret_20d, right.ret_20d]
    formula: "left.ret_20d - right.ret_20d"
    output: rs_ret_20d

  - id: rs_amount_spread
    type: formula
    input: [left.amount_ratio_5_20, right.amount_ratio_5_20]
    formula: "left.amount_ratio_5_20 - right.amount_ratio_5_20"
    output: rs_amount_spread

  - id: rs_breadth_spread
    type: formula
    input: [left.breadth_ratio_ma_5, right.breadth_ratio_ma_5]
    formula: "left.breadth_ratio_ma_5 - right.breadth_ratio_ma_5"
    output: rs_breadth_spread
```

---

## 8.9 `dsl/pair_states.yaml`

```yaml
version: "0.1"
dsl_type: pair_states

pair_states:
  - id: leader_state
    output: leader_state
    cases:
      - when: "self.rs_ret_20d >= 0.03"
        value: left_strong
      - when: "self.rs_ret_20d <= -0.03"
        value: right_strong
    default: neutral

  - id: leadership_persistence_state
    output: leadership_persistence_state
    cases:
      - when: "self.rs_ret_5d > 0 and self.rs_ret_20d > 0"
        value: left_persistent
      - when: "self.rs_ret_5d < 0 and self.rs_ret_20d < 0"
        value: right_persistent
      - when: "self.rs_ret_5d > 0 and self.rs_ret_20d <= 0"
        value: left_recent_turn
      - when: "self.rs_ret_5d < 0 and self.rs_ret_20d >= 0"
        value: right_recent_turn
    default: mixed

  - id: confirmation_state
    output: confirmation_state
    cases:
      - when: "self.leader_state == 'left_strong' and self.rs_amount_spread > 0 and self.rs_breadth_spread > 0"
        value: left_confirmed
      - when: "self.leader_state == 'right_strong' and self.rs_amount_spread < 0 and self.rs_breadth_spread < 0"
        value: right_confirmed
      - when: "self.leader_state == 'left_strong'"
        value: left_unconfirmed
      - when: "self.leader_state == 'right_strong'"
        value: right_unconfirmed
    default: neutral
```

---

## 8.10 `dsl/relation_tags.yaml`

```yaml
version: "0.1"
dsl_type: relation_tags

relation_tags:
  - id: r_growth_over_core
    pair: hs300_vs_cyb
    group: style
    priority: 92
    when: "self.leader_state == 'right_strong' and self.confirmation_state == 'right_confirmed'"
    add_tag: 成长风格占优

  - id: r_large_cap_dominant
    pair: hs300_vs_csi1000
    group: structure
    priority: 90
    when: "self.leader_state == 'left_strong' and self.confirmation_state == 'left_confirmed'"
    add_tag: 权重大盘主导

  - id: r_small_cap_rebound
    pair: hs300_vs_csi1000
    group: sentiment
    priority: 88
    when: "self.leader_state == 'right_strong' and self.confirmation_state == 'right_confirmed'"
    add_tag: 小票情绪回暖
```

---

## 8.11 `dsl/regimes.yaml`

第一版只做 4 类：

```yaml
version: "0.1"
dsl_type: regimes

regimes:
  - id: defensive_large_cap
    label: 权重防守市
    rules:
      - id: rr_def_01
        when: "index.hs300.trend_state in ['up', 'transitional_up']"
        score: 2
        evidence: 沪深300维持强势

      - id: rr_def_02
        when: "'权重大盘主导' in market.relation_tags"
        score: 3
        evidence: 权重大盘主导

      - id: rr_def_03
        when: "index.cyb.trend_state in ['down', 'range', 'transitional_down']"
        score: 1
        evidence: 创业板未形成进攻

      - id: rr_def_04
        when: "index.csi1000.breadth_state in ['weak', 'neutral_weak']"
        score: 1
        evidence: 小盘赚钱效应弱

  - id: growth_attack
    label: 成长进攻市
    rules:
      - id: rr_gro_01
        when: "index.cyb.trend_state in ['up', 'transitional_up']"
        score: 2
        evidence: 创业板进入进攻结构

      - id: rr_gro_02
        when: "'成长风格占优' in market.relation_tags"
        score: 3
        evidence: 成长风格占优

      - id: rr_gro_03
        when: "index.csi1000.trend_state in ['up', 'transitional_up', 'range'] and index.csi1000.breadth_state in ['neutral_strong', 'strong']"
        score: 1
        evidence: 小盘提供辅助跟随

  - id: split_structure
    label: 结构分裂市
    rules:
      - id: rr_spl_01
        when: "'成长风格占优' in market.relation_tags and index.csi1000.breadth_state in ['weak', 'neutral_weak']"
        score: 2
        evidence: 成长有表现但小盘承接差

      - id: rr_spl_02
        when: "'权重大盘主导' in market.relation_tags and index.cyb.trend_state in ['down', 'transitional_down']"
        score: 3
        evidence: 权重强而成长弱

  - id: chaotic_market
    label: 混沌市
    rules:
      - id: rr_cha_01
        when: "index.hs300.trend_state == 'range' and index.cyb.trend_state == 'range' and index.csi1000.trend_state == 'range'"
        score: 2
        evidence: 三大方向均缺乏清晰方向

      - id: rr_cha_02
        when: "len(market.relation_tags) == 0"
        score: 2
        evidence: 未形成明确结构主线
```

---

# 九、执行流程

固定执行顺序，不允许乱。

## 9.1 单指数层

对每个指数逐日执行：

1. 读取当日 raw
2. 计算 features
3. 推导 states
4. 识别 pattern tags
5. 识别 transition tags
6. 计算 salience

## 9.2 pair 层

对每个 pair 在同一天执行：

1. 读取 left index runtime
2. 读取 right index runtime
3. 计算 pair features
4. 推导 pair states
5. 识别 relation tags

## 9.3 market 层

在同一天执行：

1. 汇总全部 index salience
2. 生成 top_positive / top_negative / top_warning / top_transition
3. 汇总全部 pair relation tags
4. 跑 regime scoring
5. 选择最高分 regime
6. 输出结果

---

# 十、代码模块职责

---

## 10.1 `loader.py`

负责：

* 加载全部 YAML
* 加载指数原始数据
* 加载 index registry

输出：

* DSL dict
* DataFrame dict

---

## 10.2 `validator.py`

负责：

* 校验 YAML 结构
* 校验字段是否齐全
* 校验 expression 里引用是否合法
* 校验 pair 是否引用真实 index id
* 校验 output 名称是否合法

第一版这里做硬校验，出错直接停。

---

## 10.3 `resolver.py`

负责：

* 解析 `self.xxx`
* 解析 `prev.xxx`
* 解析 `left.xxx`
* 解析 `right.xxx`
* 解析 `index.xxx.yyy`
* 解析 `market.xxx`

这是表达式执行的统一入口。

---

## 10.4 `expression.py`

负责：

* 执行公式
* 执行布尔表达式
* 支持受限函数集

第一版可以先不用自己写完整 AST，直接做**白名单安全表达式执行器**，但必须：

* 禁止任意 Python builtins
* 只开放允许的变量和函数

允许函数建议只保留：

* `abs`
* `max`
* `min`
* `len`

feature 层里的 `delay` / `rolling_mean` / `rolling_max` / `rolling_min` 直接在 `feature_engine.py` 内部实现，不放到通用布尔表达式里。

---

## 10.5 `feature_engine.py`

负责：

* 根据 `features.yaml` 顺序或依赖顺序计算 feature
* 写入 `runtime["features"]`
* 记录 trace

第一版不要做复杂依赖图。
直接保证 `features.yaml` 中按依赖顺序写好即可。

---

## 10.6 `state_engine.py`

负责：

* 读取 `states.yaml`
* 遍历每条 state rule
* 自上而下匹配 case
* 命中第一条后写入 state
* 若无命中则写 default

---

## 10.7 `tag_engine.py`

负责三类 tag：

* pattern
* transition
* relation

逻辑统一：

1. 逐条读取 rule
2. `when == true` 则 append tag
3. 最后去重保序

---

## 10.8 `salience_engine.py`

负责：

1. 逐条评分 rule
2. 命中后记分
3. 写入：

   * total_score
   * positive_score
   * negative_score
   * warning_score
   * transition_score
4. 记录 matched_rules

然后由 market 层统一排序。

---

## 10.9 `pair_engine.py`

负责：

1. 根据 `pairs.yaml` 创建 pair runtime
2. 计算 pair features
3. 计算 pair states
4. 识别 relation tags

---

## 10.10 `regime_engine.py`

负责：

1. 遍历每个 regime
2. 累加命中规则得分
3. 收集 evidence
4. 输出各 regime score
5. 取最高分
6. 计算 confidence

confidence 第一版用简单归一化：

```text
最高分 / 所有 regime 分数和
```

---

## 10.11 `pipeline.py`

负责总调度：

1. 加载配置
2. 加载数据
3. 按日期循环
4. 每日执行 index -> pair -> market
5. 写出 JSON / Markdown

---

## 10.12 `trace.py`

负责 trace 结构统一格式化。
第一版不用太复杂，但必须把以下内容记下来：

* feature 输入与输出
* state 命中 case
* tag 命中规则
* salience 命中规则和分数
* regime 命中规则与证据

---

# 十一、每日输出文件

每天输出两份。

## 11.1 JSON

路径：

```text
outputs/json/YYYY-MM-DD.json
```

内容包含：

* all index runtimes
* all pair runtimes
* market runtime

## 11.2 Markdown

路径：

```text
outputs/markdown/YYYY-MM-DD.md
```

格式先固定为模板生成，不接 LLM。

建议格式：

```markdown
# 市场结构日报 - YYYY-MM-DD

## 市场状态
- Regime: 成长进攻市
- Confidence: 0.67

## 今日最亮信号
- 创业板指：中继放量突破；趋势转上

## 今日最暗信号
- 中证1000：放量下跌；广度极弱

## 今日预警
- 沪深300：指数上行但跟随不足

## 结构关系
- 成长风格占优
- 小票未明显跟随

## Regime 证据
- 创业板进入进攻结构
- 成长风格占优
- 小盘提供辅助跟随不足
```

---

# 十二、具体落地步骤

下面是按实际开发顺序写的执行清单。

---

## Step 1：初始化项目目录

你要做的事：

1. 创建 `market_system/`
2. 按上面目录创建子目录
3. 准备 `requirements.txt`

建议依赖：

```text
pandas
pyyaml
pyarrow
numpy
```

完成标志：

* 项目目录完整
* 能运行一个空的 `run_daily.py`

---

## Step 2：准备原始数据

你要做的事：

1. 把 3 个指数数据整理成统一格式
2. 保存到 `data/raw/*.parquet`
3. 每张表字段统一成：

   * `date open high low close volume amount adv decl`

检查项：

* 日期无重复
* 日期升序
* 无空字段名
* amount 非空
* adv / decl 非空

完成标志：

* 3 张 parquet 文件可被 pandas 正常读取

---

## Step 3：写 `index_registry.yaml`

你要做的事：

1. 把 3 个指数注册进去
2. 固定 id
3. 后面一律用 id，不再混中文名

完成标志：

* `loader.py` 能读取 registry

---

## Step 4：写 10 个 DSL 文件

不要边写代码边想 DSL，先把 DSL 文件写完。

顺序：

1. `features.yaml`
2. `states.yaml`
3. `patterns.yaml`
4. `transitions.yaml`
5. `salience.yaml`
6. `pairs.yaml`
7. `pair_features.yaml`
8. `pair_states.yaml`
9. `relation_tags.yaml`
10. `regimes.yaml`

完成标志：

* 全部 YAML 能被正常加载
* 基础 schema 人工检查无错

---

## Step 5：实现 `loader.py`

功能：

1. 读取所有 DSL 文件
2. 读取 raw 数据
3. 返回 dict

接口建议：

```python
dsl = load_all_dsl("dsl/")
data = load_all_data("data/raw/")
registry = load_registry("config/index_registry.yaml")
```

完成标志：

* 在 `run_daily.py` 中能 print 出各 DSL rule 数量和各指数行数

---

## Step 6：实现 `validator.py`

第一版最少做这些校验：

1. 每条 rule 必须有 `id`
2. `states.yaml` 每条必须有 `output/cases/default`
3. `patterns.yaml` 每条必须有 `when/add_tag`
4. `pairs.yaml` 引用的指数必须存在
5. `regimes.yaml` 每个 regime 必须有 `label/rules`
6. rule id 不可重复

完成标志：

* 配置错误时能报清晰错误
* 正确配置时通过

---

## Step 7：实现 `models.py`

定义三类 runtime 数据结构。
第一版直接用 dataclass 或普通 dict 都可以。

建议优先 dataclass。

完成标志：

* 能创建空的 IndexRuntime / PairRuntime / MarketRuntime

---

## Step 8：实现 `resolver.py`

分三层实现：

### 8.1 单指数层

支持：

* `self.xxx`
* `prev.xxx`

### 8.2 pair 层

支持：

* `self.xxx`
* `left.xxx`
* `right.xxx`

### 8.3 regime 层

支持：

* `index.hs300.trend_state`
* `market.relation_tags`

完成标志：

* 给定 mock runtime，路径解析都能拿到正确值

---

## Step 9：实现 `expression.py`

第一版直接做一个**安全 eval 封装**，不要过度设计。

要求：

1. 只暴露白名单变量
2. 只暴露白名单函数：`abs max min len`
3. 禁止 builtins
4. 错误时抛出带 rule id 的异常

完成标志：

* 能正确执行 state/pattern/regime 的 `when`

---

## Step 10：实现 `feature_engine.py`

顺序执行 `features.yaml`。

建议：

1. 当前日上下文只拿到该指数截至当日的 dataframe slice
2. rolling / percentile 在这里直接算
3. formula 结果写入 `runtime.features`

完成标志：

* 给定某日数据，能输出完整 feature 字典

---

## Step 11：实现 `state_engine.py`

逻辑固定：

1. 遍历 state rules
2. 顺序匹配 case
3. 命中第一条即返回
4. 无命中则 default

完成标志：

* 某一天 3 个指数都能输出 5 个 state

---

## Step 12：实现 `tag_engine.py`

先支持：

* pattern
* transition

完成标志：

* 某一天能输出 `pattern_tags` 和 `transition_tags`

---

## Step 13：实现 `salience_engine.py`

逻辑：

1. 遍历 salience rules
2. 命中则打分
3. 按 bucket 累积分数
4. 记录 matched_rules

完成标志：

* 某一天某个指数能输出 salience 结构

---

## Step 14：实现 `pair_engine.py`

先做：

1. pair feature
2. pair state
3. relation tags

完成标志：

* 某一天 2 个 pair 都能跑出结果

---

## Step 15：实现 `regime_engine.py`

逻辑：

1. 先汇总 market.relation_tags
2. 遍历 regime rules
3. 累计得分
4. 选择最高分
5. 计算 confidence
6. 输出 evidence

完成标志：

* 每日能得到一个 regime label

---

## Step 16：实现 `pipeline.py`

每日总流程：

1. 日期循环
2. 为每个指数生成当日 runtime
3. 运行：

   * feature
   * state
   * pattern
   * transition
   * salience
4. 为每个 pair 运行：

   * pair feature
   * pair state
   * relation tags
5. 汇总 market
6. regime scoring
7. 输出文件

完成标志：

* 给定一段历史数据，能逐日跑通

---

## Step 17：实现 `run_daily.py`

建议支持两个参数：

```bash
python run_daily.py --date 2026-04-05
python run_daily.py --start 2026-01-01 --end 2026-04-05
```

完成标志：

* 能跑单日
* 能跑区间

---

## Step 18：实现 JSON 输出

输出全部结构化结果。
这是最重要的机器可读产物。

完成标志：

* 每日一个 JSON 文件
* JSON 字段结构固定

---

## Step 19：实现 Markdown 输出

不要接 LLM，先模板化。

完成标志：

* 每日一个 Markdown 文件
* 内容来自 JSON，不靠人工拼

---

## Step 20：加 explain/debug 模式

建议命令：

```bash
python run_daily.py --date 2026-04-05 --explain hs300
```

输出：

* hs300 的 features
* states
* pattern hits
* transition hits
* salience hits
* pair 关系贡献
* regime 贡献

完成标志：

* 任意一天任一对象都可追溯

---

# 十三、开发优先级

不要并行乱做，按这个顺序：

## 第一周

做完：

* 目录
* 原始数据
* DSL 文件
* loader
* validator
* models

## 第二周

做完：

* resolver
* expression
* feature_engine
* state_engine

## 第三周

做完：

* tag_engine
* salience_engine
* pair_engine

## 第四周

做完：

* regime_engine
* pipeline
* JSON/Markdown 输出
* explain 模式

---

# 十四、验收标准

第一版验收只看这 6 条。

## 14.1 数据层

3 个指数原始数据能稳定读取

## 14.2 单指数层

每天都能输出：

* features
* states
* pattern_tags
* transition_tags
* salience

## 14.3 pair 层

每天都能输出 2 个 pair 的：

* features
* states
* relation_tags

## 14.4 market 层

每天都能输出：

* top_positive
* top_negative
* top_warning
* market_regime

## 14.5 结果层

每天都生成：

* JSON
* Markdown

## 14.6 可解释性

任意结论都能追溯到 rule id 和命中原因

---

# 十五、第一版不要做的事

这些先不要碰：

1. 不要先接 LLM
2. 不要先做 8 个指数全量
3. 不要先做复杂 AST 解析器
4. 不要先做行业板块
5. 不要先做回测框架
6. 不要先做 Web UI
7. 不要先优化成高度通用引擎

第一版的目标只有一个：

> **把“3 指数 + 2 pair + 4 regime”的规则引擎完整跑通，并能稳定输出每日结构化结果。**

---

# 十六、你现在立刻可以开始的具体动作

按顺序做，不要跳。

## 今天先做

1. 建目录
2. 整理 3 个指数 parquet
3. 写 `index_registry.yaml`
4. 写 10 个 DSL 文件初稿

## 然后做

5. 写 `loader.py`
6. 写 `validator.py`
7. 写 `models.py`

## 再然后

8. 跑 feature/state
9. 跑 pattern/transition/salience
10. 跑 pair/relation/regime
11. 输出 JSON/Markdown

---

如果你下一步要，我建议最直接的是我继续给你：**第一版 Python 代码骨架**，按上面目录直接把 `models.py / loader.py / validator.py / pipeline.py` 这些基础文件先搭起来。
