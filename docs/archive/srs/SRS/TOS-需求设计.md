该项目分成五层：
1. **对象层**：你到底在分析什么
2. **特征层**：每个对象提取哪些字段
3. **规则层**：哪些判断由程序做
4. **解释层**：哪些交给 LLM
5. **输出层**：最终怎么落到日报 / 面板 / 后续策略接口

---

# 一、先把对象定义清楚：你这个系统的最小分析单元是什么

你的第一阶段对象不是“整个市场”，而是两类对象：
## A. 单个指数对象

例如：
* 上证指数
* 深证成指
* 创业板指
* 科创 50 / 科创板指
* 上证 50
* 沪深 300
* 中证 500
* 中证 1000
每个指数对象都要单独跑一遍状态引擎。

---

## B. 指数对对象
也就是“结构关系对象”，例如：
* 上证 50 vs 中证 1000
* 沪深 300 vs 创业板指
* 创业板指 vs 科创板指
* 沪深 300 vs 中证 500
* 中证 500 vs 中证 1000

这类对象不是看绝对走势，而是看：
* 谁更强
* 风格是否扩散
* 市场是大票主导还是小票主导
* 成长是否强于核心资产

所以：
> **单指数对象负责“本身状态”，指数对对象负责“结构关系”**

这两个对象都必须工具化。

---

# 二、模块总图：建议拆成 8 个具体模块

这是最实用的拆法。

---

## 模块 1：Index Registry（指数注册表）

这是静态配置层，长期复用。

### 作用
给每个指数定义“角色”，后面规则引擎要依赖它。

### 由谁完成
纯人工配置 + YAML/JSON 文件，**必须工具化存档**

### 示例
```yaml
indices:
  sh_index:
    name: 上证指数
    role: broad_shanghai
    family: core_broad
    style_bias: value_defensive
    layer: core

  sz_index:
    name: 深证成指
    role: broad_shenzhen
    family: growth_broad
    style_bias: growth
    layer: growth

  sz50:
    name: 上证50
    role: mega_cap_anchor
    family: large_cap
    style_bias: value_defensive
    layer: core

  hs300:
    name: 沪深300
    role: core_benchmark
    family: large_mid_core
    style_bias: balanced
    layer: core

  csi500:
    name: 中证500
    role: mid_cap_diffusion
    family: mid_cap
    style_bias: cyclic_growth_mix
    layer: diffusion

  csi1000:
    name: 中证1000
    role: small_cap_sentiment
    family: small_cap
    style_bias: high_beta
    layer: sentiment

  cyb:
    name: 创业板指
    role: growth_risk_appetite
    family: growth
    style_bias: growth_high_beta
    layer: growth

  star:
    name: 科创板指
    role: frontier_tech_risk
    family: tech_high_beta
    style_bias: frontier_growth
    layer: growth
```

### 这一步能否交给 LLM

不能。
LLM可以帮你起草，但最终必须人工定稿。

---

## 模块 2：Feature Engine（特征计算引擎）

这是底层计算核心。

### 作用
把原始 OHLCV + breadth 转成标准特征。

### 输入

每个指数：
* open
* high
* low
* close
* volume
* amount（最好有成交额）
* advancers
* decliners

### 输出字段建议

---

### 2.1 价格特征

```yaml
ret_1d
ret_5d
ret_20d
ret_60d
ma_5
ma_10
ma_20
ma_60
ma_120
ma_slope_20
ma_slope_60
distance_to_ma20
distance_to_ma60
price_percentile_120d
price_percentile_250d
range_position_20d
breakout_20d
breakdown_20d
```

---

### 2.2 量能特征

```yaml
vol_ma_5
vol_ma_20
vol_ratio_1_20      # 当日量 / 20日均量
vol_ratio_5_20      # 5日均量 / 20日均量
amount_ma_20
amount_ratio_1_20
amount_percentile_120d
amount_percentile_250d
volume_percentile_120d
```

如果你有成交额，**优先成交额**，因为 A 股指数分析里成交额通常比原始 volume 更稳。

---

### 2.3 波动特征

```yaml
true_range
atr_14
atr_pct_14
realized_vol_20
realized_vol_60
volatility_percentile_250d
```

---

### 2.4 广度特征

```yaml
adv
decl
breadth_ratio           # adv / (adv + decl)
breadth_diff            # adv - decl
breadth_thrust_5d       # 5日广度均值或合计
breadth_thrust_20d
breadth_ratio_ma_5
breadth_ratio_ma_20
breadth_diff_zscore_20
breadth_percentile_120d
```

---

### 2.5 相对强弱特征

这个不是在单指数模块算，而是在 pair 模块算，但可预留：

```yaml
relative_strength_vs_hs300
relative_strength_vs_sz50
relative_strength_vs_csi1000
```

### 这一步能否交给 LLM

完全不能。
必须纯代码。

---

## 模块 3：State Engine（状态离散化引擎）

这是你系统的第一个关键“脚手架层”。

### 作用

把连续数值变成离散状态标签。
因为后面所有模式判断、市场分类，都基于这些标签，而不是原始数字。

---

## 3.1 单指数趋势状态

例如：

```yaml
trend_state:
  - up
  - down
  - range
  - transitional
```

### 可规则化示例

```yaml
if:
  close > ma20 > ma60
  ma20_slope > 0
  ma60_slope >= 0
then:
  trend_state: up
```

```yaml
if:
  close < ma20 < ma60
  ma20_slope < 0
then:
  trend_state: down
```

否则：

* range
* transitional

---

## 3.2 位置状态

```yaml
position_state:
  - low
  - low_mid
  - mid
  - mid_high
  - high
```

### 可规则化依据

基于：

* `price_percentile_120d`
* `price_percentile_250d`

例如：

```yaml
if price_percentile_120d <= 0.2 -> low
if 0.2 < percentile <= 0.4 -> low_mid
if 0.4 < percentile <= 0.6 -> mid
if 0.6 < percentile <= 0.8 -> mid_high
if percentile > 0.8 -> high
```

---

## 3.3 量能状态

这个你非常重视，必须认真定义。

```yaml
volume_state:
  - extreme_contraction
  - contraction
  - normal
  - expansion
  - extreme_expansion
```

### 可规则化依据

优先使用 `amount_ratio_1_20` + `amount_percentile_120d`

例如：

```yaml
if amount_ratio_1_20 <= 0.65 -> extreme_contraction
if 0.65 < amount_ratio_1_20 <= 0.85 -> contraction
if 0.85 < amount_ratio_1_20 < 1.15 -> normal
if 1.15 <= amount_ratio_1_20 < 1.5 -> expansion
if amount_ratio_1_20 >= 1.5 -> extreme_expansion
```

再配合 percentile 做增强判断，避免简单阈值失真。

---

## 3.4 广度状态

```yaml
breadth_state:
  - weak
  - neutral_weak
  - neutral
  - neutral_strong
  - strong
```

例如：

```yaml
if breadth_ratio < 0.35 -> weak
if 0.35 <= breadth_ratio < 0.45 -> neutral_weak
if 0.45 <= breadth_ratio <= 0.55 -> neutral
if 0.55 < breadth_ratio <= 0.65 -> neutral_strong
if breadth_ratio > 0.65 -> strong
```

你也可以对 5 日均值再做一层平滑状态。

---

## 3.5 波动状态

```yaml
volatility_state:
  - low
  - medium
  - high
  - extreme
```

根据：

* `atr_pct_14`
* `volatility_percentile_250d`

---

### 这一步能否交给 LLM

不行。
这一步一旦漂，后面全漂。

---

## 模块 4：Pattern Engine（模式识别引擎）

这是第二个关键脚手架层。

### 作用

将多个状态组合成“市场语义模式”。

你前面一直说“量能对应位置极敏感”，这个就体现在这里。

---

## 4.1 单指数模式标签

建议先做最常用的十几个，不要一开始做太多。

### 示例模式 1：低位放量修复

```yaml
if:
  position_state in [low, low_mid]
  volume_state in [expansion, extreme_expansion]
  ret_1d > 0
  breadth_state in [neutral_strong, strong]
then:
  add_tag: 低位放量修复
```

---

### 示例模式 2：中继放量突破

```yaml
if:
  trend_state == up
  position_state in [mid, mid_high]
  breakout_20d == true
  volume_state in [expansion, extreme_expansion]
then:
  add_tag: 中继放量突破
```

---

### 示例模式 3：高位放量分歧

```yaml
if:
  position_state == high
  volume_state == extreme_expansion
  ret_1d between [-0.5%, 1%]
  range_position_20d high
then:
  add_tag: 高位放量分歧
```

---

### 示例模式 4：缩量上涨

```yaml
if:
  ret_5d > 0
  volume_state in [contraction, extreme_contraction]
then:
  add_tag: 缩量上涨
```

---

### 示例模式 5：放量下跌

```yaml
if:
  ret_1d < 0
  volume_state in [expansion, extreme_expansion]
  breadth_state in [weak, neutral_weak]
then:
  add_tag: 放量下跌
```

---

### 示例模式 6：缩量回踩

```yaml
if:
  trend_state == up
  ret_1d < 0
  volume_state in [contraction, extreme_contraction]
  close > ma60
then:
  add_tag: 缩量回踩
```

---

### 示例模式 7：指数涨但广度弱

```yaml
if:
  ret_1d > 0
  breadth_state in [weak, neutral_weak]
then:
  add_tag: 指数上行但跟随不足
```

---

## 4.2 模式标签为什么必须工具化

因为“放量突破”和“高位放量分歧”这类概念，是交易系统的语义基础。
如果今天 LLM说这是突破，明天说这是分歧，系统就没法累计统计、回测、验证。

所以：

> **pattern tags 必须是稳定、可复盘、可回测的枚举值**

---

## 模块 5：Relation Engine（跨指数关系引擎）

这是第三个核心脚手架层，也是你这个系统真正体现“8 个指数不是孤立对象”的地方。

---

## 5.1 先定义关键配对

不要一开始全配对，先抓核心。

### 大小盘

* 上证 50 vs 中证 1000
* 沪深 300 vs 中证 1000

### 核心 vs 扩散

* 沪深 300 vs 中证 500
* 沪深 300 vs 中证 1000

### 成长 vs 核心

* 创业板指 vs 沪深 300
* 科创板指 vs 沪深 300

### 高弹性成长内部

* 科创板指 vs 创业板指

### 中小盘扩散链

* 中证 500 vs 中证 1000

---

## 5.2 配对输出什么

每对指数至少输出这几个字段：

```yaml
pair: cyb_vs_hs300
rs_5d
rs_20d
rs_trend
leader
spread_state
confirmation_state
```

---

### 具体解释

#### rs_5d / rs_20d

相对收益差，例如：

* 创业板近 20 日收益 - 沪深 300 近 20 日收益

#### rs_trend

相对强弱趋势：

* strengthening
* weakening
* flat

#### leader

谁在领先：

* cyb
* hs300
* neutral

#### spread_state

优势是否扩大：

* widening
* narrowing
* stable

#### confirmation_state

是否得到量能/广度确认：

* confirmed
* unconfirmed
* diverging

---

## 5.3 重要结构关系标签

在 pair engine 上直接打结构标签。

### 例子 1：权重主导

```yaml
if:
  sz50 stronger than csi1000 on 20d
  sz50 trend_state in [up, transitional_up]
  csi1000 trend_state in [down, range]
then:
  add_relation_tag: 权重主导
```

### 例子 2：成长进攻

```yaml
if:
  cyb stronger than hs300
  star stronger than hs300
  csi1000 not weak
then:
  add_relation_tag: 成长进攻扩散
```

### 例子 3：扩散不足

```yaml
if:
  hs300 up
  csi500 weak_or_neutral
  csi1000 weak
then:
  add_relation_tag: 扩散不足
```

### 例子 4：小票情绪回暖

```yaml
if:
  csi1000 stronger than hs300
  csi1000 volume_state in [expansion, extreme_expansion]
then:
  add_relation_tag: 小票情绪回暖
```

---

## 模块 6：Market Regime Engine（市场结构分类引擎）

这是总分类器。

### 作用

根据单指数状态 + 关系标签，生成市场结构结论。

这一步必须由规则主导，不能由 LLM自由定义。

---

## 6.1 建议的市场结构枚举

先不要太多，6 类够了。

```yaml
market_regime:
  - 权重防守市
  - 核心均衡市
  - 成长进攻市
  - 小票情绪市
  - 结构分裂市
  - 混沌市
```

---

## 6.2 规则示例

### 权重防守市

```yaml
if:
  sz50 strong
  hs300 strong_or_neutral_strong
  cyb weak_or_neutral_weak
  star weak
  csi1000 weak
then:
  regime: 权重防守市
```

---

### 核心均衡市

```yaml
if:
  hs300 strong
  sz50 neutral_strong
  cyb neutral
  csi500 neutral_strong
  csi1000 neutral
then:
  regime: 核心均衡市
```

---

### 成长进攻市

```yaml
if:
  cyb strong
  star strong_or_neutral_strong
  hs300 neutral_or_neutral_strong
  csi500 confirmed
  csi1000 neutral_strong_or_strong
then:
  regime: 成长进攻市
```

---

### 小票情绪市

```yaml
if:
  csi1000 strong
  csi500 strong
  sz50 weak
  hs300 neutral_or_weak
then:
  regime: 小票情绪市
```

---

### 结构分裂市

```yaml
if:
  core strong
  growth weak
  small_cap weak
  or
  core weak
  growth strong
  but diffusion absent
then:
  regime: 结构分裂市
```

---

### 混沌市

```yaml
if:
  majority neutral
  leadership unstable
  relation tags conflict
then:
  regime: 混沌市
```

---

## 6.3 输出的不只是分类，还要有置信度

这个也最好工具化。

### 一个简单方法

按规则命中项数打分：

```yaml
regime_score:
  权重防守市: 0.78
  成长进攻市: 0.22
```

最后取最高者。

这样比硬判定更稳。

---

## 模块 7：Narrative Layer（解释层 / LLM 层）

到这里才轮到 LLM。

它的输入不应该是原始 K 线，而应该是前面模块的结构化输出。

---

## 7.1 LLM 的输入建议

给它这些就够了：

```yaml
date: 2026-04-05

single_index_states:
  hs300:
    trend_state: up
    position_state: mid_high
    volume_state: expansion
    breadth_state: neutral_strong
    pattern_tags: [中继放量突破]

  csi1000:
    trend_state: range
    position_state: low_mid
    volume_state: contraction
    breadth_state: weak
    pattern_tags: [弱修复]

relation_tags:
  - 权重主导
  - 扩散不足
  - 成长未形成共振

market_regime:
  label: 权重防守市
  confidence: 0.78

risk_flags:
  - 沪深300处于中高位
  - 中证1000广度弱
```

---

## 7.2 LLM 负责输出什么

它只负责：

* 一句话市场结论
* 三条证据归纳
* 风格判断
* 交易含义
* 风险提示
* Markdown 日报整理

---

## 7.3 LLM 不负责什么

它不负责：

* 判定是否放量
* 判定是否高位
* 判定是否突破
* 判定市场 regime
* 自创标签

这是边界。

---

## 模块 8：Output Layer（归档与接口层）

这是工作流层。

### 作用

把规则结果和解释结果输出到你后续系统能复用的格式里。

---

## 8.1 建议输出三份文件

### A. machine_state.json

给程序和回测用

### B. market_summary.md

给人看

### C. obsidian_note.md

给你 Obsidian 使用，带 YAML frontmatter

---

## 8.2 Obsidian 输出示例

```markdown
---
date: 2026-04-05
market_regime: 权重防守市
confidence: 0.78
relation_tags:
  - 权重主导
  - 扩散不足
risk_flags:
  - 中证1000广度弱
---

# 市场结构日报

## 一句话结论
今日市场仍由权重核心资产主导，成长与小盘未形成有效跟随，整体仍偏防守环境。

## 关键证据
- 上证50与沪深300维持相对强势，显示核心权重仍是指数稳定器。
- 创业板与科创方向未形成同步强化，成长进攻链条尚未建立。
- 中证1000缩量且广度偏弱，说明小票层面的赚钱效应不足。

## 交易含义
当前更适合低频、顺核心资产主线的交易，不适合过度激进地在高弹性方向连续试错。

## 风险提示
若后续权重继续上行但500/1000仍不跟随，则需警惕指数稳定而交易体感偏差的环境延续。
```

---

# 三、把“哪些工具化，哪些 LLM 化”做成最终分工表

这是你最关心的，我直接压成表述。

---

## 必须工具化的部分

这些都是“判断骨架”。

### 1. 数据标准化

* 对齐交易日
* 缺失值处理
* 字段统一
* 指数元数据管理

### 2. 指标计算

* 收益率
* 均线
* 分位数
* 量比/额比
* 波动率
* 广度指标

### 3. 状态离散化

* 趋势状态
* 位置状态
* 量能状态
* 广度状态
* 波动状态

### 4. 模式标签识别

* 放量突破
* 高位分歧
* 缩量回踩
* 放量下跌
* 指数涨但广度弱
  等

### 5. 跨指数关系

* 大票 vs 小票
* 成长 vs 核心
* 扩散确认 / 不足
* 风格主导权

### 6. 市场分类

* 权重防守市
* 成长进攻市
* 结构分裂市
  等

### 7. 置信度计算

* 命中规则数
* 得分归一化
* regime 排名

---

## 适合 LLM 的部分

这些是“表达层”和“轻解释层”。

### 1. 中文日报生成

### 2. 证据归纳排序

### 3. 风格含义解释

### 4. 风险提示措辞优化

### 5. Obsidian / Discord 可读化输出

### 6. 面向人的总结，不面向机器的判断

---

## 不建议交给 LLM 的部分

这是底线。

### 1. 自由判定市场状态

### 2. 自由定义放量缩量

### 3. 自由解释高低位

### 4. 自由判断谁领先谁落后

### 5. 自由创造结构标签

---

# 四、建议的实际工程目录

你既然强调脚手架，那目录结构也应该一开始就稳。

```text
market_system/
├─ config/
│  ├─ index_registry.yaml
│  ├─ thresholds.yaml
│  ├─ pattern_rules.yaml
│  ├─ relation_rules.yaml
│  └─ regime_rules.yaml
│
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ snapshots/
│
├─ engine/
│  ├─ feature_engine.py
│  ├─ state_engine.py
│  ├─ pattern_engine.py
│  ├─ relation_engine.py
│  ├─ regime_engine.py
│  └─ exporter.py
│
├─ llm/
│  ├─ prompt_market_summary.md
│  └─ render_summary.py
│
├─ outputs/
│  ├─ json/
│  ├─ markdown/
│  └─ obsidian/
│
└─ run_daily.py
```

---

# 五、再往前一步：建议你先做“低自由度版本”，不要一上来追求完美

你的第一版最好是：

## 单指数状态只做 5 类

* trend_state
* position_state
* volume_state
* breadth_state
* volatility_state

## 单指数 pattern 只做 10~15 个

## 跨指数关系只做 5~8 对

## 市场 regime 只做 6 类

因为第一版最重要的不是“全”，而是：

> **输出稳定、定义一致、能连续运行、能复盘修订**

---

# 六、你当前应该马上进入的实施顺序

这是最实操的一段。

## Phase 1：静态定义

先写这 4 个配置文件：

1. `index_registry.yaml`
2. `thresholds.yaml`
3. `pattern_rules.yaml`
4. `regime_rules.yaml`

---

## Phase 2：确定性引擎

实现：

1. `feature_engine.py`
2. `state_engine.py`
3. `pattern_engine.py`
4. `relation_engine.py`
5. `regime_engine.py`

这一步完成后，即使没有 LLM，你都应该已经能输出结构化判断。

---

## Phase 3：LLM 渲染

只做：

* 把 JSON 转成 Markdown
* 保证语言统一
* 不允许它改动结论枚举

---

## Phase 4：持续校准

每天复盘时，不是让 LLM“重新思考”，而是去检查：

* 哪个阈值不合理
* 哪个模式定义太宽/太窄
* 哪个 regime 规则容易误判

也就是：

> **调规则，不调文风；调骨架，不调表述**

---

# 七、最后给你一个适合写进顶层文档的分工定义

你可以直接把这段作为系统原则：

## 系统分工原则

* **规则引擎负责判定**：数据处理、指标计算、状态离散化、模式识别、结构关系判断、市场分类。
* **LLM 负责解释**：将规则引擎输出转写为自然语言摘要、风险提示与日报内容。
* **任何影响交易分类的一阶判断，不得由 LLM 自由生成。**
* **LLM 的输入必须是结构化状态，而不是原始市场数据。**

---

下一步最合适的不是继续抽象，而是我直接帮你把第一版配置文件骨架写出来：
`index_registry.yaml + thresholds.yaml + pattern_rules.yaml + regime_rules.yaml` 的可落地初稿。
