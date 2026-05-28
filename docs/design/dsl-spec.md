
# 一、DSL 的设计原则

先定原则，不然后面会乱。

## 1. 先特征，后状态，最后模式

顺序必须固定：

```text
raw data -> features -> states -> patterns
```

不能反过来。
因为 pattern 一定是建立在 state 或 feature 之上的。

---

## 2. 状态必须离散，模式必须枚举

例如：

* `trend_state = up`
* `position_state = high`
* `volume_state = extreme_expansion`

而不是让 LLM说“感觉偏强”。

---

## 3. DSL 分三层文件

建议拆成三个 DSL 文件：

* `features.dsl.yaml`
* `states.dsl.yaml`
* `patterns.dsl.yaml`

这样层次最清楚。

---

## 4. 每条规则都要有唯一 id

因为以后你要：
* 调试
* 统计命中率
* 做回测
* 看哪条规则过宽

所以每条规则都必须有 `id`。

---

# 二、DSL 总体语法骨架

我建议用 **YAML 作为承载格式**，因为：
* 比 JSON 可读
* 比自定义语法好维护
* Python 解析方便
* 后面 Obsidian / 配置管理也顺手

DSL 的总体结构建议是：

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

features: []
states: []
patterns: []
```

当然实际会拆文件。

---

# 三、第 2 部分：Feature DSL

这一层只做一件事：

> **把原始数据算成标准字段**

这层不要有主观判断，只做计算。

---

## 3.1 Feature DSL 的基本结构

每个 feature 定义建议长这样：

```yaml
- id: ret_20d
  type: formula
  input: [close]
  formula: close / delay(close, 20) - 1
  output: ret_20d
  tags: [price, return]
```

字段说明：
* `id`: 规则唯一标识
* `type`: 特征类型
* `input`: 依赖字段
* `formula`: 计算表达式
* `output`: 输出字段名
* `tags`: 便于分类

---

## 3.2 我建议支持的 feature 类型

- A. formula：直接公式计算
- B. rolling：滚动窗口计算
- C. percentile：历史分位数
- D. compare：比较型特征
- E. boolean：布尔事件特征

---

## 3.3 Feature DSL 示例：价格类

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

features:

  - id: ret_1d
    type: formula
    input: [close]
    formula: close / delay(close, 1) - 1
    output: ret_1d
    tags: [price, return]

  - id: ret_5d
    type: formula
    input: [close]
    formula: close / delay(close, 5) - 1
    output: ret_5d
    tags: [price, return]

  - id: ret_20d
    type: formula
    input: [close]
    formula: close / delay(close, 20) - 1
    output: ret_20d
    tags: [price, return]

  - id: ma_20
    type: rolling
    input: [close]
    window: 20
    method: mean
    output: ma_20
    tags: [price, moving_average]

  - id: ma_60
    type: rolling
    input: [close]
    window: 60
    method: mean
    output: ma_60
    tags: [price, moving_average]

  - id: ma_slope_20
    type: formula
    input: [ma_20]
    formula: ma_20 / delay(ma_20, 5) - 1
    output: ma_slope_20
    tags: [price, slope]

  - id: distance_to_ma20
    type: formula
    input: [close, ma_20]
    formula: close / ma_20 - 1
    output: distance_to_ma20
    tags: [price, distance]

  - id: price_percentile_120d
    type: percentile
    input: [close]
    window: 120
    output: price_percentile_120d
    tags: [price, position]

  - id: breakout_20d
    type: boolean
    input: [close]
    formula: close > rolling_max(high, 20, exclude_current=true)
    output: breakout_20d
    tags: [price, breakout]

  - id: breakdown_20d
    type: boolean
    input: [close]
    formula: close < rolling_min(low, 20, exclude_current=true)
    output: breakdown_20d
    tags: [price, breakdown]
```

---

## 3.4 Feature DSL 示例：量能类

A 股里建议优先支持 `amount`，其次 `volume`。

```yaml
  - id: amount_ma_20
    type: rolling
    input: [amount]
    window: 20
    method: mean
    output: amount_ma_20
    tags: [liquidity, turnover]

  - id: amount_ratio_1_20
    type: formula
    input: [amount, amount_ma_20]
    formula: amount / amount_ma_20
    output: amount_ratio_1_20
    tags: [liquidity, turnover_ratio]

  - id: amount_ratio_5_20
    type: formula
    input: [amount]
    formula: rolling_mean(amount, 5) / rolling_mean(amount, 20)
    output: amount_ratio_5_20
    tags: [liquidity, turnover_ratio]

  - id: amount_percentile_120d
    type: percentile
    input: [amount]
    window: 120
    output: amount_percentile_120d
    tags: [liquidity, percentile]

  - id: volume_percentile_120d
    type: percentile
    input: [volume]
    window: 120
    output: volume_percentile_120d
    tags: [liquidity, percentile]
```

---

## 3.5 Feature DSL 示例：广度类

```yaml
  - id: breadth_ratio
    type: formula
    input: [adv, decl]
    formula: adv / (adv + decl + 1e-9)
    output: breadth_ratio
    tags: [breadth]

  - id: breadth_diff
    type: formula
    input: [adv, decl]
    formula: adv - decl
    output: breadth_diff
    tags: [breadth]

  - id: breadth_ratio_ma_5
    type: rolling
    input: [breadth_ratio]
    window: 5
    method: mean
    output: breadth_ratio_ma_5
    tags: [breadth, smooth]

  - id: breadth_ratio_ma_20
    type: rolling
    input: [breadth_ratio]
    window: 20
    method: mean
    output: breadth_ratio_ma_20
    tags: [breadth, smooth]

  - id: breadth_percentile_120d
    type: percentile
    input: [breadth_ratio]
    window: 120
    output: breadth_percentile_120d
    tags: [breadth, percentile]
```

---

## 3.6 Feature DSL 示例：波动类

```yaml
  - id: true_range
    type: formula
    input: [high, low, close]
    formula: max(high - low, abs(high - delay(close, 1)), abs(low - delay(close, 1)))
    output: true_range
    tags: [volatility]

  - id: atr_14
    type: rolling
    input: [true_range]
    window: 14
    method: mean
    output: atr_14
    tags: [volatility]

  - id: atr_pct_14
    type: formula
    input: [atr_14, close]
    formula: atr_14 / close
    output: atr_pct_14
    tags: [volatility]

  - id: volatility_percentile_250d
    type: percentile
    input: [atr_pct_14]
    window: 250
    output: volatility_percentile_250d
    tags: [volatility, percentile]
```

---

# 四、第 3 部分：State DSL

这一层的目标是：

> **把 feature 映射成稳定状态**

这是整个系统最关键的一层，因为后面的 pattern 都依赖这里。

---

## 4.1 State DSL 基本结构

每个 state 定义长这样：

```yaml
- id: trend_state
  source_type: derived_state
  output: trend_state
  cases:
    - when: "close > ma_20 and ma_20 > ma_60 and ma_slope_20 > 0"
      value: up
    - when: "close < ma_20 and ma_20 < ma_60 and ma_slope_20 < 0"
      value: down
  default: range
```

字段说明：

* `id`: 状态规则 id
* `source_type`: 固定写 `derived_state`
* `output`: 输出字段名
* `cases`: 条件分支
* `default`: 默认值

---

## 4.2 State DSL：趋势状态

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

states:

  - id: trend_state
    source_type: derived_state
    output: trend_state
    cases:
      - when: "close > ma_20 and ma_20 > ma_60 and ma_slope_20 > 0 and ma_slope_60 >= 0"
        value: up
      - when: "close < ma_20 and ma_20 < ma_60 and ma_slope_20 < 0 and ma_slope_60 <= 0"
        value: down
      - when: "abs(distance_to_ma20) <= 0.02 and abs(ma_slope_20) < 0.01"
        value: range
      - when: "close > ma_20 and ma_20 <= ma_60"
        value: transitional_up
      - when: "close < ma_20 and ma_20 >= ma_60"
        value: transitional_down
    default: range
```

这里我加了两个过渡态：

* `transitional_up`
* `transitional_down`

这在 A 股很有用，因为很多关键阶段不是纯 up/down。

---

## 4.3 State DSL：位置状态

```yaml
  - id: position_state
    source_type: derived_state
    output: position_state
    cases:
      - when: "price_percentile_120d <= 0.20"
        value: low
      - when: "price_percentile_120d <= 0.40"
        value: low_mid
      - when: "price_percentile_120d <= 0.60"
        value: mid
      - when: "price_percentile_120d <= 0.80"
        value: mid_high
      - when: "price_percentile_120d > 0.80"
        value: high
    default: mid
```

这个是最典型的桶化状态。

---

## 4.4 State DSL：量能状态

这里建议结合 `ratio + percentile`，不要只看一个值。

```yaml
  - id: volume_state
    source_type: derived_state
    output: volume_state
    cases:
      - when: "amount_ratio_1_20 <= 0.65 and amount_percentile_120d <= 0.15"
        value: extreme_contraction
      - when: "amount_ratio_1_20 <= 0.85"
        value: contraction
      - when: "amount_ratio_1_20 < 1.15"
        value: normal
      - when: "amount_ratio_1_20 < 1.50"
        value: expansion
      - when: "amount_ratio_1_20 >= 1.50 or amount_percentile_120d >= 0.90"
        value: extreme_expansion
    default: normal
```

---

## 4.5 State DSL：广度状态

```yaml
  - id: breadth_state
    source_type: derived_state
    output: breadth_state
    cases:
      - when: "breadth_ratio < 0.35"
        value: weak
      - when: "breadth_ratio < 0.45"
        value: neutral_weak
      - when: "breadth_ratio <= 0.55"
        value: neutral
      - when: "breadth_ratio <= 0.65"
        value: neutral_strong
      - when: "breadth_ratio > 0.65"
        value: strong
    default: neutral
```

---

## 4.6 State DSL：波动状态

```yaml
  - id: volatility_state
    source_type: derived_state
    output: volatility_state
    cases:
      - when: "volatility_percentile_250d <= 0.20"
        value: low
      - when: "volatility_percentile_250d <= 0.60"
        value: medium
      - when: "volatility_percentile_250d <= 0.85"
        value: high
      - when: "volatility_percentile_250d > 0.85"
        value: extreme
    default: medium
```

---

# 五、第 4 部分：Pattern DSL

这一层要做的是：

> **把 feature + state 组合成模式标签**

pattern 必须是离散枚举，不然没法统计。

---

## 5.1 Pattern DSL 基本结构

建议每条 pattern 长这样：

```yaml
- id: p_low_volume_repair
  output: pattern_tags
  priority: 50
  when: "position_state in ['low', 'low_mid'] and volume_state in ['expansion', 'extreme_expansion'] and ret_1d > 0 and breadth_state in ['neutral_strong', 'strong']"
  add_tag: 低位放量修复
```

字段说明：

* `id`: 模式 id
* `output`: 通常固定 `pattern_tags`
* `priority`: 优先级
* `when`: 条件表达式
* `add_tag`: 打上的标签

---

## 5.2 为什么要有 priority

因为很多 pattern 会同时命中。

例如某天可能同时满足：

* 放量上涨
* 中继突破
* 广度确认

你要决定：

* 全部保留
* 还是保留高优先级主标签

所以 DSL 里先留好 `priority`。

---

## 5.3 Pattern DSL 示例：低位放量修复

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

patterns:

  - id: p_low_volume_repair
    output: pattern_tags
    priority: 80
    when: "position_state in ['low', 'low_mid'] and volume_state in ['expansion', 'extreme_expansion'] and ret_1d > 0 and breadth_state in ['neutral_strong', 'strong']"
    add_tag: 低位放量修复
```

---

## 5.4 Pattern DSL 示例：中继放量突破

```yaml
  - id: p_mid_trend_breakout
    output: pattern_tags
    priority: 90
    when: "trend_state == 'up' and position_state in ['mid', 'mid_high'] and breakout_20d == true and volume_state in ['expansion', 'extreme_expansion']"
    add_tag: 中继放量突破
```

---

## 5.5 Pattern DSL 示例：高位放量分歧

```yaml
  - id: p_high_volume_divergence
    output: pattern_tags
    priority: 95
    when: "position_state == 'high' and volume_state == 'extreme_expansion' and ret_1d > -0.01 and ret_1d < 0.01"
    add_tag: 高位放量分歧
```

这个定义先保持克制，后面你可以再加：

* 上影线
* 收盘位置
* 长阴长阳
* intraday reversal

---

## 5.6 Pattern DSL 示例：缩量上涨

```yaml
  - id: p_up_on_contraction
    output: pattern_tags
    priority: 40
    when: "ret_5d > 0 and volume_state in ['contraction', 'extreme_contraction']"
    add_tag: 缩量上涨
```

---

## 5.7 Pattern DSL 示例：放量下跌

```yaml
  - id: p_down_on_expansion
    output: pattern_tags
    priority: 85
    when: "ret_1d < 0 and volume_state in ['expansion', 'extreme_expansion'] and breadth_state in ['weak', 'neutral_weak']"
    add_tag: 放量下跌
```

---

## 5.8 Pattern DSL 示例：缩量回踩

```yaml
  - id: p_pullback_on_contraction
    output: pattern_tags
    priority: 75
    when: "trend_state == 'up' and ret_1d < 0 and volume_state in ['contraction', 'extreme_contraction'] and close > ma_60"
    add_tag: 缩量回踩
```

---

## 5.9 Pattern DSL 示例：指数上行但跟随不足

```yaml
  - id: p_index_up_breadth_weak
    output: pattern_tags
    priority: 88
    when: "ret_1d > 0 and breadth_state in ['weak', 'neutral_weak']"
    add_tag: 指数上行但跟随不足
```

这个在 A 股很关键，因为它能识别“少数权重拉指数”。

---

# 六、把 DSL 再推进一步：支持组合模式

你后面一定会需要“主模式 + 次模式”的结构。
所以建议 pattern 支持两个字段：

* `add_tag`
* `add_context_tags`

例如：

```yaml
  - id: p_high_breakout_with_weak_breadth
    output: pattern_tags
    priority: 98
    when: "breakout_20d == true and position_state == 'high' and breadth_state in ['weak', 'neutral_weak']"
    add_tag: 高位突破但广度不足
    add_context_tags:
      - 警惕假突破
      - 结构不健康
```

这样后面 regime 或 LLM 可以直接调用这些 context tags。

---

# 七、建议给 DSL 增加一个“规则组”概念

因为你以后会有很多规则，所以建议加 `group`。

---

## 7.1 Feature group

```yaml
group: price
group: liquidity
group: breadth
group: volatility
```

## 7.2 State group

```yaml
group: trend
group: position
group: volume
group: breadth
group: volatility
```

## 7.3 Pattern group

```yaml
group: reversal
group: breakout
group: continuation
group: warning
group: divergence
```

---

## 7.4 示例

```yaml
  - id: p_high_volume_divergence
    group: warning
    output: pattern_tags
    priority: 95
    when: "position_state == 'high' and volume_state == 'extreme_expansion' and ret_1d > -0.01 and ret_1d < 0.01"
    add_tag: 高位放量分歧
```

这对后面做统计很有用。

---

# 八、建议给 DSL 增加“适用对象过滤器”

因为你未来不仅有指数，还会有：
* 行业板块
* 个股
* 周线对象

所以 DSL 最好支持 filter。

---

## 8.1 示例

```yaml
applies_to:
  asset_type: index
  freq: daily
```

或者更细：

```yaml
applies_to:
  asset_type: index
  index_family: [broad, large_cap, growth, small_cap]
```

这样以后你可以：
* 某些规则只给指数
* 某些规则只给创业板/科创板
* 某些规则只给中小盘指数

---

# 九、给你一版更完整的 DSL 汇总样例

下面我把三层放在一起，让你直观看到“从 feature 到 state 到 pattern”的链条。

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

features:
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
    formula: ma_20 / delay(ma_20, 5) - 1
    output: ma_slope_20

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
    formula: amount / amount_ma_20
    output: amount_ratio_1_20

  - id: amount_percentile_120d
    type: percentile
    input: [amount]
    window: 120
    output: amount_percentile_120d

  - id: breadth_ratio
    type: formula
    input: [adv, decl]
    formula: adv / (adv + decl + 1e-9)
    output: breadth_ratio

  - id: ret_1d
    type: formula
    input: [close]
    formula: close / delay(close, 1) - 1
    output: ret_1d

  - id: breakout_20d
    type: boolean
    input: [close, high]
    formula: close > rolling_max(high, 20, exclude_current=true)
    output: breakout_20d

states:
  - id: trend_state
    output: trend_state
    cases:
      - when: "close > ma_20 and ma_20 > ma_60 and ma_slope_20 > 0"
        value: up
      - when: "close < ma_20 and ma_20 < ma_60 and ma_slope_20 < 0"
        value: down
      - when: "close > ma_20 and ma_20 <= ma_60"
        value: transitional_up
      - when: "close < ma_20 and ma_20 >= ma_60"
        value: transitional_down
    default: range

  - id: position_state
    output: position_state
    cases:
      - when: "price_percentile_120d <= 0.20"
        value: low
      - when: "price_percentile_120d <= 0.40"
        value: low_mid
      - when: "price_percentile_120d <= 0.60"
        value: mid
      - when: "price_percentile_120d <= 0.80"
        value: mid_high
      - when: "price_percentile_120d > 0.80"
        value: high
    default: mid

  - id: volume_state
    output: volume_state
    cases:
      - when: "amount_ratio_1_20 <= 0.65 and amount_percentile_120d <= 0.15"
        value: extreme_contraction
      - when: "amount_ratio_1_20 <= 0.85"
        value: contraction
      - when: "amount_ratio_1_20 < 1.15"
        value: normal
      - when: "amount_ratio_1_20 < 1.50"
        value: expansion
      - when: "amount_ratio_1_20 >= 1.50 or amount_percentile_120d >= 0.90"
        value: extreme_expansion
    default: normal

  - id: breadth_state
    output: breadth_state
    cases:
      - when: "breadth_ratio < 0.35"
        value: weak
      - when: "breadth_ratio < 0.45"
        value: neutral_weak
      - when: "breadth_ratio <= 0.55"
        value: neutral
      - when: "breadth_ratio <= 0.65"
        value: neutral_strong
      - when: "breadth_ratio > 0.65"
        value: strong
    default: neutral

patterns:
  - id: p_low_volume_repair
    group: reversal
    priority: 80
    when: "position_state in ['low', 'low_mid'] and volume_state in ['expansion', 'extreme_expansion'] and ret_1d > 0 and breadth_state in ['neutral_strong', 'strong']"
    add_tag: 低位放量修复

  - id: p_mid_trend_breakout
    group: breakout
    priority: 90
    when: "trend_state == 'up' and position_state in ['mid', 'mid_high'] and breakout_20d == true and volume_state in ['expansion', 'extreme_expansion']"
    add_tag: 中继放量突破

  - id: p_high_volume_divergence
    group: warning
    priority: 95
    when: "position_state == 'high' and volume_state == 'extreme_expansion' and ret_1d > -0.01 and ret_1d < 0.01"
    add_tag: 高位放量分歧

  - id: p_index_up_breadth_weak
    group: divergence
    priority: 88
    when: "ret_1d > 0 and breadth_state in ['weak', 'neutral_weak']"
    add_tag: 指数上行但跟随不足
```

---

# 十、这套 DSL 还缺什么？还缺一个“表达式子集”规范

因为你后面要自己写 parser，所以表达式语言不能太随意。

我建议你一开始把 `when` 和 `formula` 限制在一个很小的子集里。

---

## 10.1 formula 支持的函数

建议只支持这些：
* `delay(x, n)`
* `rolling_mean(x, n)`
* `rolling_max(x, n, exclude_current=true/false)`
* `rolling_min(x, n, exclude_current=true/false)`
* `abs(x)`
* `max(a, b, c...)`
* `min(a, b, c...)`

---

## 10.2 when 支持的操作符

* `and`
* `or`
* `in`
* `==`
* `!=`
* `>`
* `>=`
* `<`
* `<=`

不要一开始就支持复杂嵌套函数，不然 parser 难度会上去。

---

# 十一、对你当前系统最实用的建议：先收敛成“第一版 DSL 子集”

不要一开始做得太大。
第一版就做下面这些，已经足够跑起来了。

---

## Feature DSL 第一版

只做 15~20 个字段：

### 价格
* `ret_1d`
* `ret_5d`
* `ret_20d`
* `ma_20`
* `ma_60`
* `ma_slope_20`
* `distance_to_ma20`
* `price_percentile_120d`
* `breakout_20d`

### 量能
* `amount_ma_20`
* `amount_ratio_1_20`
* `amount_percentile_120d`

### 广度
* `breadth_ratio`
* `breadth_diff`
* `breadth_ratio_ma_5`

### 波动
* `true_range`
* `atr_14`
* `atr_pct_14`
* `volatility_percentile_250d`

---

## State DSL 第一版

只做 5 个状态：
* `trend_state`
* `position_state`
* `volume_state`
* `breadth_state`
* `volatility_state`

---

## Pattern DSL 第一版

只做 10 个 pattern：
* 低位放量修复
* 中继放量突破
* 高位放量分歧
* 缩量上涨
* 放量下跌
* 缩量回踩
* 指数上行但跟随不足
* 低位极缩量
* 高位缩量横盘
* 放量破位

这样最好。

---

# 十二、最后给你一个工程上最关键的结论

你要的 DSL，本质上不是“给 LLM 看”的语言，而是：

> **给规则引擎看的可配置语义层**

所以它必须满足：
* **指标可计算**
* **状态可离散**
* **模式可复用**
* **标签可统计**
* **条件可回测**

换句话说，它不是 Prompt DSL，而是 **Trading Structure DSL**。