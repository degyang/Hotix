问题的引出：
> 市场结构识别，到底应该以
> **“预先定义好的 pair 关系”** 为主，
> 还是先从全市场里找出 **“今天最亮 / 最暗 / 最异常的特征”** 再展开？

我的判断是：
> **第一性原则上，应该先找“最亮/最暗的结构特征”，再用 pair 去解释和验证。**
> 而不是反过来，把 pair 当成唯一入口。

因为 pair 比较解决的是 **“谁相对谁更强”**，但它不一定能第一时间回答：
* 今天市场最显著的变化是什么
* 最值得注意的异常在哪里
* 哪个层级正在主导市场情绪
* 哪个信号最值得被提到日报第一句

所以如果你的目标是“洞察”，而不是“机械对比”，那系统最好是：

```text
先找显著特征
-> 再做结构归因
-> 再用 pair 验证
-> 最后归纳 regime
```

而不是：

```text
先做一堆 pair
-> 再硬凑结论
```

---

# 一、pair 的价值是什么，局限又是什么

先说清楚 pair 不是没用，而是它在系统里应该扮演**第二层角色**。

---

## pair 的价值

pair 最擅长的是回答这类问题：

* 大票是否强于小票
* 成长是否强于核心资产
* 中盘是否跟随
* 科创是否强于创业板
* 风格优势是否持续

也就是：

> **pair 擅长“关系判断”**

---

## pair 的局限

但 pair 不擅长回答：

* 今天最异常的是什么
* 是量能异常最突出，还是广度异常最突出
* 是权重抱团更显著，还是小票崩塌更显著
* 是某个指数突破最值得注意，还是某个指数高位放量分歧更值得警惕

因为 pair 是**预设视角**。
它会让你总是从“我提前定义好的几组比较”出发。

问题在于，市场每天最重要的东西，未必恰好落在你那几组 pair 上。

---

# 二、所以更好的架构是：先“特征发现”，再“关系解释”

我建议你把系统改成双阶段：

---

## Stage A：显著特征发现层

先回答：

> 今天市场里，最显著、最异常、最值得优先关注的信号是什么？

这里找的不是“pair 胜负”，而是：

* 哪个指数的趋势最强
* 哪个指数的量能最异常
* 哪个指数的广度最差
* 哪个模式标签优先级最高
* 哪个变化相对过去几天最突兀

这一步产出的应该是：

* **top bullish features**
* **top bearish features**
* **top anomalies**
* **top structural warnings**

---

## Stage B：结构关系解释层

然后再问：

> 这些最显著的特征，意味着什么结构变化？

这时候 pair 才上场，用来解释：

* 为什么是这个指数最亮
* 它相对谁更强
* 这种强是孤立的，还是被确认的
* 是扩散还是割裂

也就是说：

> **pair 不是入口，而是解释器**

这会比“先 pair 后结论”稳很多。

---

# 三、“最亮/最暗”到底是什么

你这个提法很好，但必须工具化，不然又会变成 LLM 自由发挥。

我建议把“最亮/最暗”定义成：

> **相对于自身历史分布、以及相对于同层对象，最显著偏离常态的状态或模式**

也就是两个维度：

---

## 1. 绝对显著性

某指数本身的状态有多异常

例如：

* `amount_percentile_120d = 0.97`
* `breadth_ratio = 0.22`
* `ret_20d = 近120日高分位`
* 命中 `高位放量分歧`

这说明它自身很突出。

---

## 2. 相对显著性

它相对其他指数有多突出

例如：

* 创业板的量能扩张明显强于其他指数
* 中证1000的广度恶化最明显
* 上证50在所有核心指数里最稳

这说明它在“横向比较”里突出。

---

# 四、所以你应该加一层：Salience DSL / Highlight Engine

这层正好放在 Pattern 和 Relation 之间，或者并行于 Relation。

系统顺序就变成：

```text
raw
-> features
-> states
-> patterns
-> salience
-> relations
-> regimes
```

这里的 `salience` 就是“最亮/最暗特征提取层”。

---

# 五、Salience Engine 要提取什么

我建议先提四类：

---

## 1. strongest_positive_signals

今天最亮的正向特征

例如：

* 创业板：中继放量突破
* 科创板：前沿科技偏好增强
* 中证1000：量能从极缩转扩张

---

## 2. strongest_negative_signals

今天最暗的负向特征

例如：

* 中证1000：放量下跌 + 广度弱
* 创业板：高位放量分歧
* 沪深300：指数上行但跟随不足

---

## 3. strongest_anomalies

今天最异常的特征

例如：

* 上证50量能极度放大，但 breadth 没同步改善
* 沪深300创新高，但广度处于弱区
* 中证500缩量横盘，但中证1000放量破位

---

## 4. strongest_transition_signals

今天最值得注意的“状态切换”信号

例如：

* 创业板从 `transitional_up -> up`
* 中证1000从 `range -> transitional_down`
* 科创板从 `normal volume -> extreme_expansion`

这类信息很值钱，因为它常常比静态强弱更重要。

---

# 六、怎么把“最亮/最暗”工具化

关键是做一个 **salience score（显著性评分）**。

不是让 LLM 觉得哪个亮，而是代码打分。

---

## 6.1 单指标显著性

例如每个 feature/state/pattern 都有基础分。

### 数值型显著性

用分位数或 z-score：

* `amount_percentile_120d > 0.9` → 高显著
* `breadth_ratio < 0.3` → 高显著
* `volatility_percentile_250d > 0.9` → 高显著

### 状态型显著性

给离散状态赋权：

* `extreme_expansion` > `expansion`
* `high` + `warning pattern` > 一般 pattern
* `weak breadth` + `positive return` = 背离加权

---

## 6.2 Pattern 显著性

Pattern 天然适合带分数。

例如：

```yaml
patterns:
  - id: p_high_volume_divergence
    priority: 95
    salience_weight: 1.4
```

那当天命中后：

```text
pattern_salience = priority * salience_weight
```

---

## 6.3 变化显著性

比静态状态更重要的是“变化”。

例如：

* 今天量能从 `contraction -> extreme_expansion`
* 今天 trend 从 `range -> transitional_up`
* breadth 从 `neutral -> weak`

你可以为“状态跃迁”单独打分。

比如：

```yaml
transitions:
  - from: contraction
    to: extreme_expansion
    score: 2.0
```

---

# 七、最合理的系统结构：不是二选一，而是“主从关系”

你的问题不是“pair 对不对”，而是“pair 应该排在什么位置”。

我的答案是：

> **显著特征发现是主，pair 关系解释是从。**

也就是：

---

## 主线：先找亮点 / 暗点

这是洞察入口。

问的是：

* 今天什么最突出
* 今天什么最危险
* 今天什么最反常
* 今天哪里发生了切换

---

## 从线：再用 pair 做结构归因

这是解释层。

问的是：

* 这个亮点属于哪种风格主导
* 它有没有扩散
* 它是不是孤立现象
* 它相对其他层级是否占优

---

# 八、举个例子，你就能看到两者差异

假设今天结果是：

* 上证50小涨
* 沪深300小涨
* 创业板涨幅一般
* 中证1000大跌
* 中证1000 breadth 极弱
* 中证1000放量破位

如果你先从 pair 入手，你可能得到：

* 上证50相对中证1000占优
* 沪深300相对中证1000占优
* 权重大盘主导

这没错，但**不够锋利**。

因为今天真正最值得写进第一句的可能是：

> **小盘风险偏好显著坍塌，中证1000出现放量破位并伴随广度恶化。**

然后再补一句：

> 这种坍塌使得权重相对优势进一步强化，市场呈现明显的防守化结构。

看到了吗？

* 第一层是“最亮/最暗特征”
* 第二层才是“pair 结构解释”

这才更像人类交易员的观察顺序。

---

# 九、所以 DSL 上应该怎么改

我建议你新增一层：

## `salience.dsl.yaml`

它负责三件事：

### 1. 定义哪些特征可参与显著性排序

例如：

* ret_1d, ret_5d, ret_20d
* amount_ratio_1_20
* amount_percentile_120d
* breadth_ratio
* volatility_percentile_250d
* pattern priority

### 2. 定义显著性评分规则

例如：

* 极值分位数加分
* 状态跃迁加分
* warning pattern 加分
* 多个负面特征共振再加分

### 3. 输出 top highlights

例如：

* top_positive
* top_negative
* top_warning
* top_transition

---

# 十、Salience DSL 可以长这样

```yaml
version: "0.1"

context:
  asset_type: index
  freq: daily
  market: CN_A

salience_rules:

  - id: s_extreme_volume_expansion
    when: "volume_state == 'extreme_expansion'"
    score: 2.0
    bucket: positive_or_negative
    reason: 极度放量具有高显著性

  - id: s_extreme_breadth_weak
    when: "breadth_state == 'weak'"
    score: 2.2
    bucket: negative
    reason: 广度极弱代表市场内部承接不足

  - id: s_high_warning_pattern
    when: "'高位放量分歧' in pattern_tags"
    score: 2.5
    bucket: warning
    reason: 高位分歧是高优先级预警信号

  - id: s_breakout_with_confirmation
    when: "'中继放量突破' in pattern_tags and breadth_state in ['neutral_strong', 'strong']"
    score: 2.3
    bucket: positive
    reason: 放量突破且广度确认是高质量正向信号

  - id: s_transition_to_up
    when: "prev.trend_state in ['range', 'transitional_up'] and trend_state == 'up'"
    score: 1.8
    bucket: transition
    reason: 趋势状态向上切换
```

最后输出：

```yaml
salience_output:
  top_positive:
    - asset: cyb
      score: 4.6
      reasons:
        - 中继放量突破
        - 广度确认
    - asset: star
      score: 3.8
      reasons:
        - 前沿科技偏好增强

  top_negative:
    - asset: csi1000
      score: 5.1
      reasons:
        - 放量破位
        - 广度极弱
```

---

# 十一、我的明确建议

所以我会这样定结论：

## 不是放弃 pair

而是降级它的角色。

---

## 最优顺序应当是：

### 第一步：显著性发现

先找今天最值得被优先描述的东西。

### 第二步：关系解释

用 pair 说明它属于什么结构变化。

### 第三步：regime 归纳

把这些变化汇总成市场状态。

---

# 十二、最后给你一句适合写进系统设计文档的话

> **市场洞察的入口应优先是“显著特征发现”，而不是固定 pair 比较；pair 比较主要用于对显著特征进行结构归因、扩散验证与风格解释。**

这句话基本就是你这个分歧点的最终定稿。

下一步我建议直接做两件具体事之一：
要么我帮你把 `salience.dsl.yaml` 完整写出来；要么我帮你把整个执行链改成 `features -> states -> patterns -> salience -> relations -> regimes` 的统一 schema。
