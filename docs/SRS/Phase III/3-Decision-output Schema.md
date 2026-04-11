那我继续往下，直接把这三层推进到**可正式落地的版本**：

1. **正式 YAML 文件草案**
2. **merge / override 语义**
3. **decision_output schema**
4. **最小实现顺序**

我会严格贴着你们现有 DSL 风格来写，不另造一套语言。你们当前 DSL 已经明确用了这些约定：

* `version`
* `dsl_type`
* 顶层对象数组
* `id / priority / when / output / set / add_tag / score / evidence`
* `cases + default`
* 基于 `self / prev / market / index` 的表达式上下文

所以后面的设计都沿这个范式延伸。

---

# 一、Policy DSL v1 正式文件草案

建议文件名：

```text
policies.yaml
```

建议内容：

```yaml
version: "0.1"
dsl_type: policies

defaults:
  setup_permissions:
    breakout:
      status: restricted
      size: small
    continuation_pullback:
      status: restricted
      size: small
    low_level_repair:
      status: restricted
      size: small
    defensive_core_rotation:
      status: restricted
      size: small
    high_beta_chase:
      status: forbidden
      size: none
    reversal_catch:
      status: forbidden
      size: none
    trend_follow:
      status: restricted
      size: small

  execution_constraints:
    max_new_positions: 1
    intraday_addons: false
    require_confirmation: true
    allow_gap_chase: false
    allow_average_up: false

  vetoes: []

policies:
  - id: pol_offense_base
    priority: 100
    when: "market.market_context.label == 'Offense'"
    set:
      setup_permissions.breakout.status: allowed
      setup_permissions.breakout.size: normal
      setup_permissions.continuation_pullback.status: allowed
      setup_permissions.continuation_pullback.size: normal
      setup_permissions.low_level_repair.status: probe_only
      setup_permissions.low_level_repair.size: small
      setup_permissions.defensive_core_rotation.status: restricted
      setup_permissions.defensive_core_rotation.size: small
      setup_permissions.high_beta_chase.status: restricted
      setup_permissions.high_beta_chase.size: small
      setup_permissions.trend_follow.status: allowed
      setup_permissions.trend_follow.size: normal
      execution_constraints.max_new_positions: 3
      execution_constraints.intraday_addons: true
      execution_constraints.require_confirmation: false
      execution_constraints.allow_gap_chase: true
      execution_constraints.allow_average_up: true

  - id: pol_caution_base
    priority: 100
    when: "market.market_context.label == 'Caution'"
    set:
      setup_permissions.breakout.status: restricted
      setup_permissions.breakout.size: small
      setup_permissions.continuation_pullback.status: allowed
      setup_permissions.continuation_pullback.size: small
      setup_permissions.low_level_repair.status: probe_only
      setup_permissions.low_level_repair.size: small
      setup_permissions.defensive_core_rotation.status: restricted
      setup_permissions.defensive_core_rotation.size: small
      setup_permissions.high_beta_chase.status: forbidden
      setup_permissions.reversal_catch.status: forbidden
      setup_permissions.trend_follow.status: restricted
      setup_permissions.trend_follow.size: small
      execution_constraints.max_new_positions: 2
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true
      execution_constraints.allow_gap_chase: false
      execution_constraints.allow_average_up: false

  - id: pol_defense_base
    priority: 100
    when: "market.market_context.label == 'Defense'"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.breakout.size: none
      setup_permissions.continuation_pullback.status: restricted
      setup_permissions.continuation_pullback.size: small
      setup_permissions.low_level_repair.status: forbidden
      setup_permissions.low_level_repair.size: none
      setup_permissions.defensive_core_rotation.status: allowed
      setup_permissions.defensive_core_rotation.size: small
      setup_permissions.high_beta_chase.status: forbidden
      setup_permissions.reversal_catch.status: forbidden
      setup_permissions.trend_follow.status: restricted
      setup_permissions.trend_follow.size: tiny
      execution_constraints.max_new_positions: 1
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true
      execution_constraints.allow_gap_chase: false
      execution_constraints.allow_average_up: false
      vetoes:
        - no_high_beta_expansion

  - id: pol_cash_base
    priority: 100
    when: "market.market_context.label == 'Cash'"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.breakout.size: none
      setup_permissions.continuation_pullback.status: forbidden
      setup_permissions.continuation_pullback.size: none
      setup_permissions.low_level_repair.status: probe_only
      setup_permissions.low_level_repair.size: tiny
      setup_permissions.defensive_core_rotation.status: restricted
      setup_permissions.defensive_core_rotation.size: tiny
      setup_permissions.high_beta_chase.status: forbidden
      setup_permissions.reversal_catch.status: forbidden
      setup_permissions.trend_follow.status: forbidden
      setup_permissions.trend_follow.size: none
      execution_constraints.max_new_positions: 1
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true
      execution_constraints.allow_gap_chase: false
      execution_constraints.allow_average_up: false
      vetoes:
        - chaotic_market_override

  - id: pol_growth_confirmed_bonus
    priority: 90
    when: "'成长风格占优' in market.relation_tags and market.market_context.label in ['Offense', 'Caution']"
    set:
      setup_permissions.breakout.status: allowed
      setup_permissions.breakout.size: normal
      setup_permissions.continuation_pullback.status: allowed
      setup_permissions.continuation_pullback.size: normal
      setup_permissions.trend_follow.status: allowed

  - id: pol_large_cap_defense_bonus
    priority: 90
    when: "'权重大盘主导' in market.relation_tags and market.market_context.label in ['Defense', 'Caution']"
    set:
      setup_permissions.defensive_core_rotation.status: allowed
      setup_permissions.defensive_core_rotation.size: normal
      setup_permissions.high_beta_chase.status: forbidden

  - id: pol_warning_cap
    priority: 95
    when: "len(market.top_warning) > 0"
    set:
      setup_permissions.breakout.status: restricted
      setup_permissions.breakout.size: small
      setup_permissions.high_beta_chase.status: forbidden
      execution_constraints.require_confirmation: true
      vetoes:
        - warning_overhang

  - id: pol_negative_override
    priority: 98
    when: "len(market.top_negative) > 0"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.breakout.size: none
      setup_permissions.reversal_catch.status: forbidden
      execution_constraints.intraday_addons: false
      vetoes:
        - negative_structure_pressure

  - id: pol_no_structure_override
    priority: 99
    when: "len(market.relation_tags) == 0"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.high_beta_chase.status: forbidden
      vetoes:
        - no_clear_structure

  - id: pol_transition_up_probe
    priority: 88
    when: "len(market.top_transition) > 0 and market.market_context.label in ['Cash', 'Caution']"
    set:
      setup_permissions.low_level_repair.status: probe_only
      setup_permissions.low_level_repair.size: tiny
```

---

# 二、Conflict DSL v1 正式文件草案

建议文件名：

```text
conflicts.yaml
```

这层的职责不是直接“算 context”，而是：

* 解释冲突
* 加 veto
* 限制升级
* 强制覆盖 policy 的部分字段
* 调整 confidence

建议内容：

```yaml
version: "0.1"
dsl_type: conflicts

conflicts:
  - id: cf_positive_without_structure
    priority: 100
    when: "len(market.top_positive) > 0 and len(market.relation_tags) == 0"
    explain: 局部正向信号存在，但未形成结构主线
    effect:
      winner_bias: cash
      loser_bias: offense
      block_context_upgrade: true
      confidence_delta: -0.10
      add_veto:
        - no_structure_confirmation

  - id: cf_warning_over_positive
    priority: 100
    when: "len(market.top_positive) > 0 and len(market.top_warning) > 0"
    explain: 正向信号与预警并存，优先降低进攻强度
    effect:
      cap_context_to: caution
      confidence_delta: -0.10
      add_veto:
        - warning_overhang

  - id: cf_negative_over_breakout
    priority: 100
    when: "len(market.top_negative) > 0"
    explain: 显著负向信号存在，突破类交易应被压制
    effect:
      force_policy:
        setup_permissions.breakout.status: forbidden
        setup_permissions.breakout.size: none
      add_veto:
        - negative_pressure_override

  - id: cf_chaotic_market_override
    priority: 110
    when: "market.market_regime.label == '混沌市'"
    explain: 市场处于混沌状态，现金优先于试错
    effect:
      force_context: cash
      block_context_upgrade: true
      confidence_delta: -0.05
      add_veto:
        - chaotic_market_override

  - id: cf_growth_unconfirmed
    priority: 90
    when: "'成长风格占优' not in market.relation_tags and index.399006.breadth_state in ['strong', 'neutral_strong']"
    explain: 成长端有修复迹象，但未获得结构确认
    effect:
      force_policy:
        setup_permissions.high_beta_chase.status: forbidden
        setup_permissions.low_level_repair.status: probe_only
      confidence_delta: -0.05

  - id: cf_core_unconfirmed
    priority: 90
    when: "'权重大盘主导' not in market.relation_tags and index.000300.trend_state in ['up', 'transitional_up']"
    explain: 权重偏强但未形成可依赖的防守主导
    effect:
      cap_context_to: caution
      confidence_delta: -0.05

  - id: cf_breadth_bounce_but_downtrend
    priority: 92
    when: "len(market.top_positive) > 0 and index.000300.trend_state == 'down' and index.399006.trend_state == 'down'"
    explain: 广度修复发生在整体下行背景中，优先视作修复而非主升
    effect:
      force_policy:
        setup_permissions.breakout.status: forbidden
        setup_permissions.low_level_repair.status: probe_only
      add_veto:
        - downtrend_background

  - id: cf_runner_up_offense_blocked
    priority: 85
    when: "market.market_context.runner_up == 'Offense' and len(market.relation_tags) == 0"
    explain: 存在进攻候选，但缺乏主线确认，不允许升级为进攻环境
    effect:
      block_context_upgrade: true
      confidence_delta: -0.05
```

---

# 三、Context State Machine DSL v1 正式文件草案

建议文件名：

```text
context_transitions.yaml
```

这层只处理 `prev.market_context → current.market_context` 的迁移语言，不和单资产 `transitions.yaml` 混在一起。你们现有 `transitions.yaml` 还是资产级状态转移，这样分层最清楚。

建议内容：

```yaml
version: "0.1"
dsl_type: context_transitions

context_transitions:
  - id: ctx_cash_to_caution
    priority: 100
    when: "prev.market_context.label == 'Cash' and self.market_context.label == 'Caution'"
    add_tag: 现金期尝试修复
    explain: 现金环境中开始出现可跟踪的修复信号

  - id: ctx_caution_to_offense
    priority: 100
    when: "prev.market_context.label == 'Caution' and self.market_context.label == 'Offense'"
    add_tag: 进攻环境确认
    explain: 市场完成从观察试错到进攻确认的迁移

  - id: ctx_offense_to_caution
    priority: 100
    when: "prev.market_context.label == 'Offense' and self.market_context.label == 'Caution'"
    add_tag: 进攻降速
    explain: 进攻环境中出现预警，进入降频与筛选阶段

  - id: ctx_caution_to_cash
    priority: 100
    when: "prev.market_context.label == 'Caution' and self.market_context.label == 'Cash'"
    add_tag: 结构丢失退回现金
    explain: 主线消失或信号失效，退出试错环境

  - id: ctx_defense_to_cash
    priority: 95
    when: "prev.market_context.label == 'Defense' and self.market_context.label == 'Cash'"
    add_tag: 防守失效退回现金
    explain: 防守主导不再成立，现金优先

  - id: ctx_cash_persistence
    priority: 80
    when: "prev.market_context.label == 'Cash' and self.market_context.label == 'Cash'"
    add_tag: 现金期延续
    explain: 仍未出现足够的结构确认信号

  - id: ctx_offense_persistence
    priority: 80
    when: "prev.market_context.label == 'Offense' and self.market_context.label == 'Offense'"
    add_tag: 进攻环境延续
    explain: 进攻主线仍然有效

  - id: ctx_defense_persistence
    priority: 80
    when: "prev.market_context.label == 'Defense' and self.market_context.label == 'Defense'"
    add_tag: 防守环境延续
    explain: 防守主导仍然成立
```

---

# 四、建议补一个 Decision Assembly DSL

这个不是必须，但很推荐。因为你们前面很多 DSL 都是在“推理”，最后最好有一个统一的输出拼装层。

建议文件名：

```text
decision_output.yaml
```

内容可以很轻，只定义要输出哪些块：

```yaml
version: "0.1"
dsl_type: decision_output

decision_output:
  include:
    - market_regime
    - market_context
    - policy
    - conflicts
    - context_transition
    - risk_budget
    - top_positive
    - top_negative
    - top_warning
    - top_transition

  derive:
    - id: final_risk_budget
      formula: "market.market_context.risk_budget"

    - id: final_confidence
      formula: "clip(market.market_context.confidence + conflicts.confidence_delta_sum, 0.0, 1.0)"
```

---

# 五、merge / override 语义

这个很关键。没有这个，DSL 虽然能写，但引擎会不稳定。

我建议你们定成下面这套，简单而够用。

## 5.1 执行顺序

```text
1. features
2. states
3. patterns
4. transitions
5. pair_features
6. pair_states
7. relation_tags
8. salience
9. regimes
10. contexts
11. policies
12. conflicts
13. context_transitions
14. decision_output assembly
```

这和你们现有 `contexts.yaml` 对 `market.top_positive / top_warning / relation_tags / market_regime` 的依赖关系一致。

---

## 5.2 priority 语义

统一规则：

* **priority 数值越大，越后覆盖**
* 同 priority 时，按文件内出现顺序覆盖
* 命中的所有规则都保留到 `trace.matched_rules`

这和你们现在很多规则体系是兼容的，改造成本最低。

---

## 5.3 set 的 merge 语义

### 标量字段

直接覆盖。

例如：

```yaml
setup_permissions.breakout.status: forbidden
```

后命中规则覆盖前命中规则。

### 列表字段

默认 append + 去重。

例如：

```yaml
vetoes:
  - warning_overhang
```

如果多个规则都加 veto，就合并去重。

### 对象字段

递归 merge。

例如：

```yaml
setup_permissions.breakout:
  status: restricted
  size: small
```

只改子字段，不重置整个对象。

---

## 5.4 status 的强弱序

对策略权限建议固定一个偏序，避免覆盖时语义紊乱：

```text
forbidden > restricted > probe_only > allowed
```

size 建议也固定：

```text
none < tiny < small < normal < large
```

当引擎遇到“两个命中规则都写 status”时，有两种方案：

### 简单方案

直接按 priority 覆盖。

### 更稳方案

先按 priority，若同 priority 冲突，则取更保守的一边。

我建议你们上 **更稳方案**，因为交易规则里保守覆盖通常更安全。

---

## 5.5 conflict effect 的语义

Conflict DSL 里我用了这些 effect 字段，建议语义固定：

* `force_context`: 直接把最终 context 改成某值
* `cap_context_to`: 设 context 上限，例如最多到 `Caution`
* `block_context_upgrade`: 不允许从更保守环境升级
* `force_policy`: 直接覆盖 policy 对象路径
* `confidence_delta`: 对最终 confidence 加减
* `add_veto`: 加入 veto 列表

### context 强弱顺序建议固定为：

```text
Cash < Defense < Caution < Offense
```

含义是风险开放程度从低到高。
`cap_context_to: caution` 的意思就是：最终 context 最激进也只能到 Caution，不能升到 Offense。

---

# 六、decision_output schema v1

建议你们最终 daily JSON 统一成这个结构，比现在更完整，但仍然兼容你们当前输出风格：

```yaml
date: 2026-04-07

market:
  market_regime:
    label: 混沌市
    score: 2.0
    confidence: 0.67
    evidence: []

  market_context:
    label: Cash
    score: 5.0
    confidence: 0.71
    allowed_styles: []
    disallowed_styles: []
    risk_budget:
      total_exposure: 0.10
      max_positions: 1
      max_single_name_weight: 0.05
    runner_up: Offense
    runner_up_score: 2.0

  policy:
    setup_permissions:
      breakout:
        status: forbidden
        size: none
      continuation_pullback:
        status: forbidden
        size: none
      low_level_repair:
        status: probe_only
        size: tiny
      defensive_core_rotation:
        status: restricted
        size: tiny
      high_beta_chase:
        status: forbidden
        size: none
      reversal_catch:
        status: forbidden
        size: none
      trend_follow:
        status: forbidden
        size: none

    execution_constraints:
      max_new_positions: 1
      intraday_addons: false
      require_confirmation: true
      allow_gap_chase: false
      allow_average_up: false

    vetoes:
      - chaotic_market_override
      - no_clear_structure

  conflicts:
    active:
      - id: cf_positive_without_structure
        explain: 局部正向信号存在，但未形成结构主线
      - id: cf_chaotic_market_override
        explain: 市场处于混沌状态，现金优先于试错
    confidence_delta_sum: -0.15
    block_context_upgrade: true

  context_transition:
    prev_label: Caution
    current_label: Cash
    tags:
      - 结构丢失退回现金

  highlights:
    top_positive: []
    top_negative: []
    top_warning: []
    top_transition: []

  trace:
    matched_policy_rules: []
    matched_conflict_rules: []
    matched_context_transition_rules: []
```

---

# 七、最小落地顺序

不要一次全做完。按这个顺序最稳。

## 第一步：先落 `policies.yaml`

这是收益最大的，因为一做完，你的系统就从“市场环境判断”升级成“具体 setup 权限系统”。

## 第二步：再落 `conflicts.yaml`

把现在隐式的“为什么 Cash 压过 Offense”显式化。

## 第三步：再落 `context_transitions.yaml`

把 daily snapshot 变成连续状态机。

## 第四步：最后补 `decision_output.yaml`

统一出口，方便 Obsidian、日志、回测、复盘一起接。

---

# 八、我对你们现有 DSL 的最终判断

看完你上传的这些规则后，我的判断比之前更强了：

> 你们真正缺的已经不是“市场理解能力”，
> 而是**把市场理解翻译成明确执行权限和状态迁移**。

你们现有 DSL 已经把：

* feature 计算
* state 离散化
* pattern 识别
* pair 对比
* relation 抽象
* regime/context 归纳

做得相当完整了。

后面这一步，核心不是加更多指标，而是**让已有判断长出牙齿**。

下一步最合适的是，我直接继续帮你把这四份 YAML 精修成**与你们现有字段命名完全一致的版本**，并顺带补一版 Python evaluator 的伪代码。
