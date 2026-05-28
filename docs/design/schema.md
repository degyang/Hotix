
文档会做四件事：
1. 把 `salience.dsl.yaml` 具体化
2. 把它和前面的 `feature/state/pattern/relation/regime` 串成统一 schema
3. 明确 salience 与 pair 的职责边界
4. 给你一版第一期可落地的最小实现方案

---

# 一、先明确：Salience Engine 到底输出什么

这层不要太泛。
我建议它最终只输出四个东西：

## 1. top_positive

当天最亮的正向信号

## 2. top_negative

当天最暗的负向信号

## 3. top_warning

当天最值得警惕的结构性预警

## 4. top_transition

当天最重要的状态切换

你后面的日报第一句、重点证据、甚至 LLM 输入，都应该主要来自这四类结果，而不是来自 pair 列表本身。

---

# 二、Salience DSL 的核心思路

Salience 不是“再造一套 pattern”，而是：

> 对已有 feature / state / pattern / transition 做显著性评分，然后排序

所以它依赖前面几层，而不是替代前面几层。

推荐顺序：

```text
features
-> states
-> patterns
-> transitions
-> salience
-> relations
-> regimes
```

我这里特意把 `transitions` 单独拎出来，因为“今天发生了切换”往往比“今天静态很强”更重要。

---

# 三、Salience DSL：统一结构

我建议单独一个文件：

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

salience:
  scoring_rules: []
  aggregation: {}
  buckets: {}
```

其中三部分最关键：

* `scoring_rules`：单条打分规则
* `aggregation`：如何把多条分数组合
* `buckets`：怎么归到 positive / negative / warning / transition

---

# 四、Salience Scoring Rule 的建议语法

每条 rule 建议长这样：

```yaml
- id: s_extreme_volume_expansion
  applies_to: [index]
  when: "volume_state == 'extreme_expansion'"
  score: 2.0
  bucket: positive_or_negative
  polarity: context_dependent
  reason: 极度放量具有高显著性
  weight: 1.0
```

字段解释：

* `id`: 唯一标识
* `applies_to`: 适用对象
* `when`: 命中条件
* `score`: 原始显著分
* `bucket`: 候选桶
* `polarity`: 正负性质
* `reason`: 解释文本
* `weight`: 可选权重

---

# 五、为什么要有 polarity

因为有些特征不是天然正向或负向，而是要结合上下文。

例如：

* 极度放量
  不一定是好事，也可能是高位分歧

所以 polarity 可以分成三类：

* `positive`
* `negative`
* `context_dependent`

如果是 `context_dependent`，就要再结合 pattern/state 去定最终归属。

---

# 六、Salience DSL 第一版规则设计

我建议先把显著性规则分成五组：

1. 极值类
2. 模式类
3. 背离类
4. 切换类
5. 共振类

---

## 6.1 极值类规则

### 极度放量

```yaml
- id: s_extreme_volume_expansion
  group: extreme
  when: "volume_state == 'extreme_expansion'"
  score: 1.6
  bucket: positive_or_negative
  polarity: context_dependent
  reason: 极度放量是高显著事件
```

### 极度缩量

```yaml
- id: s_extreme_volume_contraction
  group: extreme
  when: "volume_state == 'extreme_contraction'"
  score: 1.4
  bucket: warning_or_transition
  polarity: context_dependent
  reason: 极度缩量通常意味着观望或衰竭
```

### 广度极弱

```yaml
- id: s_extreme_breadth_weak
  group: extreme
  when: "breadth_state == 'weak'"
  score: 2.2
  bucket: negative
  polarity: negative
  reason: 广度极弱反映内部承接不足
```

### 广度极强

```yaml
- id: s_extreme_breadth_strong
  group: extreme
  when: "breadth_state == 'strong'"
  score: 2.0
  bucket: positive
  polarity: positive
  reason: 广度极强说明市场内部跟随良好
```

### 波动极端

```yaml
- id: s_extreme_volatility
  group: extreme
  when: "volatility_state == 'extreme'"
  score: 1.7
  bucket: warning
  polarity: context_dependent
  reason: 极端波动通常对应结构不稳定
```

---

## 6.2 模式类规则

### 中继放量突破

```yaml
- id: s_pattern_trend_breakout
  group: pattern
  when: "'中继放量突破' in pattern_tags"
  score: 2.6
  bucket: positive
  polarity: positive
  reason: 中继放量突破是高质量趋势强化信号
```

### 低位放量修复

```yaml
- id: s_pattern_low_repair
  group: pattern
  when: "'低位放量修复' in pattern_tags"
  score: 2.1
  bucket: positive
  polarity: positive
  reason: 低位放量修复反映修复意愿增强
```

### 高位放量分歧

```yaml
- id: s_pattern_high_divergence
  group: pattern
  when: "'高位放量分歧' in pattern_tags"
  score: 2.8
  bucket: warning
  polarity: negative
  reason: 高位放量分歧是高优先级预警信号
```

### 放量下跌

```yaml
- id: s_pattern_down_on_expansion
  group: pattern
  when: "'放量下跌' in pattern_tags"
  score: 2.5
  bucket: negative
  polarity: negative
  reason: 放量下跌意味着抛压主动释放
```

### 指数上行但跟随不足

```yaml
- id: s_pattern_up_breadth_weak
  group: divergence
  when: "'指数上行但跟随不足' in pattern_tags"
  score: 2.4
  bucket: warning
  polarity: negative
  reason: 指数走强但内部跟随不足，结构不健康
```

---

## 6.3 背离类规则

### 高位 + 弱广度

```yaml
- id: s_high_with_weak_breadth
  group: divergence
  when: "position_state == 'high' and breadth_state in ['weak', 'neutral_weak']"
  score: 2.3
  bucket: warning
  polarity: negative
  reason: 高位运行但广度不佳
```

### 上涨 + 缩量

```yaml
- id: s_up_on_contraction
  group: divergence
  when: "ret_5d > 0 and volume_state in ['contraction', 'extreme_contraction']"
  score: 1.7
  bucket: warning
  polarity: context_dependent
  reason: 上涨缺乏量能配合
```

### 下跌 + 弱广度 + 放量

```yaml
- id: s_down_breadth_volume_resonance
  group: divergence
  when: "ret_1d < 0 and breadth_state == 'weak' and volume_state in ['expansion', 'extreme_expansion']"
  score: 2.9
  bucket: negative
  polarity: negative
  reason: 下跌、弱广度与放量形成负向共振
```

---

## 6.4 切换类规则

这类特别重要。

### 趋势转上

```yaml
- id: s_transition_trend_to_up
  group: transition
  when: "prev.trend_state in ['range', 'transitional_up'] and trend_state == 'up'"
  score: 2.2
  bucket: transition
  polarity: positive
  reason: 趋势状态向上切换
```

### 趋势转下

```yaml
- id: s_transition_trend_to_down
  group: transition
  when: "prev.trend_state in ['range', 'transitional_down'] and trend_state == 'down'"
  score: 2.4
  bucket: transition
  polarity: negative
  reason: 趋势状态向下切换
```

### 量能跳升

```yaml
- id: s_transition_volume_jump
  group: transition
  when: "prev.volume_state in ['contraction', 'normal'] and volume_state == 'extreme_expansion'"
  score: 1.9
  bucket: transition
  polarity: context_dependent
  reason: 量能状态出现跃迁
```

### 广度恶化

```yaml
- id: s_transition_breadth_deterioration
  group: transition
  when: "prev.breadth_state in ['neutral', 'neutral_strong', 'strong'] and breadth_state in ['weak', 'neutral_weak']"
  score: 2.3
  bucket: transition
  polarity: negative
  reason: 广度状态明显恶化
```

---

## 6.5 共振类规则

共振信号通常比单独信号更值得写在第一句。

### 突破 + 广度强 + 放量

```yaml
- id: s_resonance_breakout
  group: resonance
  when: "'中继放量突破' in pattern_tags and breadth_state in ['neutral_strong', 'strong'] and volume_state in ['expansion', 'extreme_expansion']"
  score: 3.2
  bucket: positive
  polarity: positive
  reason: 趋势突破、广度和量能形成正向共振
```

### 高位 + 放量 + 弱广度

```yaml
- id: s_resonance_distribution_risk
  group: resonance
  when: "position_state == 'high' and volume_state == 'extreme_expansion' and breadth_state in ['weak', 'neutral_weak']"
  score: 3.4
  bucket: warning
  polarity: negative
  reason: 高位、放量与弱广度形成派发风险共振
```

---

# 七、Salience 的聚合方式

单条规则命中后只是碎片。
你要有聚合逻辑，把某个指数当天的多个命中信号合成“显著摘要”。

我建议输出结构长这样：

```yaml
salience_result:
  by_asset:
    cyb:
      total_score: 5.8
      positive_score: 4.9
      negative_score: 0.6
      warning_score: 0.3
      transition_score: 1.2
      matched_rules:
        - id: s_pattern_trend_breakout
          score: 2.6
          reason: 中继放量突破是高质量趋势强化信号
        - id: s_resonance_breakout
          score: 3.2
          reason: 趋势突破、广度和量能形成正向共振
```

然后系统再从这里提：

* `top_positive`
* `top_negative`
* `top_warning`
* `top_transition`

---

# 八、必须解决的一个问题：同一指数既亮又暗怎么办

这在 A 股很常见。
比如：

* 创业板上涨
* 但高位放量分歧
* 又有弱广度

所以不能简单只留一类标签。
你应该允许同一指数同时有：

* positive_score
* negative_score
* warning_score

最后再定义一个“主导显著性”：

```yaml
dominant_salience:
  bucket: warning
  score: 3.4
```

也就是说：

> 这个指数今天最值得被记住的，不一定是上涨，而可能是上涨中的风险特征。

这很重要。

---

# 九、Salience 与 Pair 的职责分工

你前面问得很对，所以这里要正式定下来。

## Salience 的职责

回答：

* 今天哪个指数最亮
* 今天哪个指数最暗
* 今天哪个异常最重要
* 今天哪个切换最值得关注

它输出的是 **对象级显著性**

---

## Pair / Relation 的职责

回答：

* 这个亮点属于哪种风格结构
* 它是否相对其他层占优
* 是否形成扩散
* 是孤立现象还是结构性变化

它输出的是 **关系级解释**

---

## 更直白一点

Salience 负责：

> “今天先看谁”

Relation 负责：

> “为什么看它，它意味着什么结构”

---

# 十、统一 schema：加上 Salience 后的结构

我把前面的所有层重新统一一下。

```yaml
version: "0.1"

pipeline:
  - features
  - states
  - patterns
  - transitions
  - salience
  - relations
  - regimes
  - narrative
```

---

## Layer 1: features

输出：

* `ret_1d`
* `ret_20d`
* `ma_20`
* `amount_ratio_1_20`
* `breadth_ratio`
* `atr_pct_14`
  等

---

## Layer 2: states

输出：

* `trend_state`
* `position_state`
* `volume_state`
* `breadth_state`
* `volatility_state`

---

## Layer 3: patterns

输出：

* `pattern_tags`

---

## Layer 4: transitions

输出：

* `transition_tags`

例如：

* 趋势转上
* 趋势转下
* 广度恶化
* 量能跳升

---

## Layer 5: salience

输出：

* `top_positive`
* `top_negative`
* `top_warning`
* `top_transition`

---

## Layer 6: relations

输出：

* `leader_state`
* `confirmation_state`
* `relation_tags`

---

## Layer 7: regimes

输出：

* `market_regime.label`
* `market_regime.score`
* `market_regime.confidence`
* `market_regime.evidence`

---

## Layer 8: narrative

LLM 只吃结构化结果，输出 Markdown / 日报。

---

# 十一、Transition DSL 也应该补出来

因为 salience 很依赖它。
建议单独一层，不要塞到 state 里。

结构可以很简单：

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

transitions:

  - id: t_trend_upshift
    when: "prev.trend_state in ['range', 'transitional_up'] and trend_state == 'up'"
    add_tag: 趋势转上

  - id: t_trend_downshift
    when: "prev.trend_state in ['range', 'transitional_down'] and trend_state == 'down'"
    add_tag: 趋势转下

  - id: t_volume_jump
    when: "prev.volume_state in ['contraction', 'normal'] and volume_state == 'extreme_expansion'"
    add_tag: 量能跳升

  - id: t_breadth_deterioration
    when: "prev.breadth_state in ['neutral', 'neutral_strong', 'strong'] and breadth_state in ['weak', 'neutral_weak']"
    add_tag: 广度恶化
```

这样 salience 可以直接消费 `transition_tags`。

---

# 十二、第一期你最值得做的，不是全量，而是“显著性最小集”

为了避免系统太大，我建议第一期 salience 只盯住下面这些：

## 正向

* 中继放量突破
* 低位放量修复
* 广度极强
* 趋势转上
* 突破共振

## 负向

* 放量下跌
* 广度极弱
* 趋势转下
* 下跌负向共振

## 预警

* 高位放量分歧
* 指数上行但跟随不足
* 高位+放量+弱广度
* 极度缩量

## 切换

* 趋势转上
* 趋势转下
* 量能跳升
* 广度恶化

这就已经足够支撑日报第一层观察。

---

# 十三、日报生成时的优先顺序也要改

你以后日报的组织顺序，不应该是：

1. 先讲 pair
2. 再讲 regime
3. 再补充亮点

而应该是：

## 一句话结论

由 `top salience + regime` 共同生成

## 第一段：今天最亮 / 最暗 / 最危险的信号

直接来自 salience

## 第二段：这些信号属于什么结构变化

来自 relation tags

## 第三段：归纳为哪种市场状态

来自 regime

这个顺序会更接近真正的交易观察流程。

---

# 十四、给你一个完整的输出样例

比如某天结构化结果可能长这样：

```yaml
top_positive:
  - asset: cyb
    score: 5.8
    reasons:
      - 中继放量突破
      - 趋势突破、广度和量能形成正向共振

top_negative:
  - asset: csi1000
    score: 4.9
    reasons:
      - 放量下跌
      - 下跌、弱广度与放量形成负向共振

top_warning:
  - asset: hs300
    score: 3.7
    reasons:
      - 指数上行但跟随不足

top_transition:
  - asset: star
    score: 2.2
    reasons:
      - 趋势状态向上切换

relation_tags:
  - 成长风格占优
  - 扩散不足

market_regime:
  label: 结构分裂市
  confidence: 0.68
  evidence:
    - 创业板方向显著走强
    - 中证1000出现放量下跌与广度恶化
    - 成长有亮点但中小盘整体扩散不足
```

那日报第一句就会非常自然：

> 今日市场最亮的特征出现在创业板的放量突破，但中证1000同步出现放量下跌与广度恶化，整体更像成长亮点与小票退潮并存的结构分裂环境。

这就比“沪深300 vs 创业板谁强”更像真正的市场洞察。

---

# 十五、最后定一个顶层原则

你可以把这句直接写进系统设计文档：

> **市场洞察的第一入口是显著性发现，关系比较用于结构归因，市场分类用于最终归纳。**

或者更工程化一点：

> **Salience-first, Relation-second, Regime-last.**

---

下一步最合理的是继续把这套东西再压实一层，直接做：
**统一字段命名规范 + 引用路径规范 + 表达式子集规范**，也就是把 DSL 从“思路”推进成“真正可实现的语言规格”。
