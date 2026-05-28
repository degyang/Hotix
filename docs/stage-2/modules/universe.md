---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Universe 分析与市场画像规划

## 1. 为什么用 Universe 替代 pair 作为主轴

pair 适合比较两个对象，Universe 适合分析一组对象。市场分析的第一任务不是比较 A 和 B 谁强，而是理解一组资产内部发生了什么。

例如对宽基指数 universe，核心问题是：

```text
是不是普涨？
是不是少数权重拉动？
是不是成长强、防守弱？
是不是所有成员都在恶化？
```

这些问题无法仅靠 pair 解决。pair 是关系分析的一个工具，Universe 才是通用市场分析的基本单位。

## 2. Universe 定义

Universe 是一组带有共同分析语义的资产集合。

```yaml
universes:
  - id: broad_indices
    name: 宽基指数
    type: index_panel
    role: market_core
    members:
      - "000001"
      - "399001"
      - "000300"
      - "000905"
      - "000852"
      - "399006"

  - id: growth_proxy
    name: 成长代理
    type: theme_panel
    role: risk_appetite
    members:
      - "399006"
      - "000680"

  - id: user_watchlist
    name: 用户观察池
    type: custom
    role: watchlist
    members_from: "watchlist.csv"
```

Universe 的意义不只是成员列表，还包括 `role`。同一组资产如果承担不同角色，分析解释也不同。

## 3. Universe 分析输出

每个 Universe 输出一个 `UniverseProfile`：

```yaml
id: broad_indices
name: 宽基指数
date: "2026-04-03"
profile_label: weak_breadth_defensive
dominant_dimensions:
  - breadth
  - structure
state:
  trend_distribution:
    up: 1
    range: 2
    down: 3
  breadth_distribution:
    weak: 5
    neutral_weak: 1
  volume_distribution:
    expansion: 4
    normal: 2
participation:
  label: poor
  adv_ratio_median: 0.33
concentration:
  label: high
  top_positive_share: 0.72
salience:
  top_positive: []
  top_negative: [...]
  top_warning: [...]
  top_divergence: [...]
summary:
  - "宽基指数内部广度偏弱，负向显著性具有组合级范围。"
  - "上涨资产贡献集中，未形成健康扩散。"
```

## 4. Universe 分析维度

### 4.1 内部状态分布

统计成员状态：

```text
trend_state 分布
position_state 分布
volume_state 分布
breadth_state 分布
volatility_state 分布
```

目的：判断组合内部是否一致。

### 4.2 参与度 participation

衡量上涨/修复是否有足够成员参与：

```text
上涨成员比例
强广度成员比例
负向 salience 成员比例
正向 salience 成员比例
```

典型标签：

```text
broad_participation
narrow_participation
poor_participation
cap_weighted_only
```

### 4.3 集中度 concentration

判断结构是否被少数资产驱动：

```text
top positive salience share
top negative salience share
return contribution concentration
```

典型标签：

```text
high_concentration
balanced_contribution
single_asset_dominance
```

### 4.4 扩散度 diffusion

判断强势/弱势是否扩散：

```text
正向 salience 成员数量是否增加
负向 salience 成员数量是否增加
transition 成员是否集中出现
```

注意：这里不做预测，只描述当前扩散状态。

典型标签：

```text
positive_diffusion
negative_diffusion
no_diffusion
mixed_diffusion
```

### 4.5 分化 divergence

判断组合内部是否撕裂：

```text
一部分资产强趋势，一部分资产弱趋势
价格上涨但广度不足
成交放大但价格不跟随
防守资产强，进攻资产弱
```

典型标签：

```text
price_breadth_divergence
volume_price_divergence
style_divergence
internal_split
```

## 5. Market Profile

Market Profile 是多个 UniverseProfile 的汇总，不是简单平均。

它回答：

```text
市场主导结构是什么？
主导维度是什么？
风险集中在哪里？
有没有确认或冲突？
哪些 universe 是当前关键观察对象？
```

输出示例：

```yaml
market_profile:
  date: "2026-04-03"
  primary_label: defensive_split
  dominant_dimensions:
    - breadth
    - structure
  condition:
    trend: unclear
    breadth: weak
    volume: risk_confirming
    volatility: elevated
    structure: split
  key_points:
    - "广度是今日主导负向维度。"
    - "价格修复缺乏内部参与确认。"
    - "进攻方向未形成组合级扩散。"
  top_salience:
    negative: [...]
    warning: [...]
    divergence: [...]
  universe_rank:
    most_constructive:
      - defensive_assets
    most_fragile:
      - small_cap
      - growth_proxy
```

## 6. Market Profile 标签体系

第一版建议使用描述性标签，不使用交易性标签。

```text
healthy_expansion        健康扩散
narrow_strength          窄幅强势
defensive_split          防守分化
breadth_collapse         广度塌陷
repair_unconfirmed       修复未确认
risk_expansion           风险扩散
range_mixed              震荡混合
no_clear_structure       无清晰结构
```

标签只描述当前市场，不暗示未来。

## 7. Pipeline 规划

新主链路：

```text
load data
-> build asset runtimes
-> compute asset features/states/tags
-> compute asset salience
-> build universe profiles
-> compute universe salience
-> build market profile
-> render analysis report
```

现有 pair/regime/context/policy 可暂时保留，但新开发不围绕它们继续扩展。

## 8. 报告结构

日报应按分析师阅读顺序组织：

```text
# 市场结构日报

## 一句话画像
当前市场处于防守分化状态，广度弱是主导矛盾。

## 今日主导维度
- breadth: 高
- structure: 中高
- volume: 中

## 关键结论
1. 宽基指数内部广度偏弱，负向显著性范围广。
2. 成长方向存在局部价格修复，但内部参与不足。
3. 当前市场无清晰进攻主线。

## Universe 分析
### 宽基指数
...
### 成长代理
...
### 用户观察池
...

## Salience 明细
positive / negative / warning / divergence / transition

## 证据链
```

## 9. 验收标准

Universe Analysis 完成后：

- 可以配置多个 universe。
- 每个 universe 能输出状态分布、参与度、集中度、扩散度、分化信号。
- Market Profile 能从多个 universe 汇总主导市场画像。
- 报告中可以清楚说明“为什么今天是这个画像”。
- 不依赖 pair，也不输出预测和交易建议。

---

Parent: [[10-Projects/Active/11.09 Hotix/Overview]]
