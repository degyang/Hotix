好，我直接按你们现有 DSL 风格，往上补三层：

1. **Policy DSL v1**
2. **Conflict DSL v1**
3. **Context State Machine DSL v1**

目标不是推翻你现有这套，而是**无缝接在 `regimes → contexts` 后面**。
你们现有 DSL 已经把市场推断链路搭好了：`features → states → patterns / transitions → pair_states → relation_tags → regimes → contexts → salience`。       

下面这三层，就是把它补成真正的决策层。

---

# 一、Policy DSL v1

这个层负责把：

* `market_context`
* `market_regime`
* `relation_tags`
* `top_positive / top_negative / top_warning`
* 关键 index 状态

翻译成**具体策略权限**。

## 1.1 设计目标

你们现在 `contexts.yaml` 里已经有：

* `allowed_styles`
* `disallowed_styles`
* `risk_budget`

比如 `Cash` 对应“观察 / 复盘 / 等待”，禁止“主动进攻 / 高频试错 / 重仓出击”，并给出 10% 总仓、1 个仓位、单票 5%。

但这还是**风格级**。
Policy DSL 要把它下钻成 **setup 级**。

---

## 1.2 建议的输出对象

```yaml
policy_output:
  setup_permissions:
    breakout:
      status: forbidden
      size: none
    continuation_pullback:
      status: probe_only
      size: small
    low_level_repair:
      status: allowed
      size: small
    defensive_core_rotation:
      status: restricted
      size: small
    high_beta_chase:
      status: forbidden
      size: none

  execution_constraints:
    max_new_positions: 1
    intraday_addons: false
    require_confirmation: true

  vetoes:
    - no_clear_structure
    - warning_overhang
```

---

## 1.3 DSL 草案

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

  execution_constraints:
    max_new_positions: 1
    intraday_addons: false
    require_confirmation: true

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
      setup_permissions.high_beta_chase.status: restricted
      setup_permissions.high_beta_chase.size: small
      execution_constraints.max_new_positions: 3
      execution_constraints.intraday_addons: true
      execution_constraints.require_confirmation: false

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
      setup_permissions.high_beta_chase.status: forbidden
      execution_constraints.max_new_positions: 2
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true

  - id: pol_defense_base
    priority: 100
    when: "market.market_context.label == 'Defense'"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.continuation_pullback.status: restricted
      setup_permissions.continuation_pullback.size: small
      setup_permissions.low_level_repair.status: forbidden
      setup_permissions.defensive_core_rotation.status: allowed
      setup_permissions.defensive_core_rotation.size: small
      execution_constraints.max_new_positions: 1
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true

  - id: pol_cash_base
    priority: 100
    when: "market.market_context.label == 'Cash'"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.continuation_pullback.status: forbidden
      setup_permissions.low_level_repair.status: probe_only
      setup_permissions.low_level_repair.size: tiny
      setup_permissions.defensive_core_rotation.status: restricted
      setup_permissions.defensive_core_rotation.size: tiny
      setup_permissions.high_beta_chase.status: forbidden
      setup_permissions.reversal_catch.status: forbidden
      execution_constraints.max_new_positions: 1
      execution_constraints.intraday_addons: false
      execution_constraints.require_confirmation: true

  - id: pol_growth_confirmed_bonus
    priority: 90
    when: "'成长风格占优' in market.relation_tags and market.market_context.label in ['Offense', 'Caution']"
    set:
      setup_permissions.breakout.status: allowed
      setup_permissions.breakout.size: normal
      setup_permissions.continuation_pullback.status: allowed

  - id: pol_large_cap_defense_bias
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

  - id: pol_negative_override
    priority: 98
    when: "len(market.top_negative) > 0"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.reversal_catch.status: forbidden
      execution_constraints.intraday_addons: false

  - id: pol_no_structure_cash_cap
    priority: 99
    when: "len(market.relation_tags) == 0"
    set:
      setup_permissions.breakout.status: forbidden
      setup_permissions.high_beta_chase.status: forbidden
```

---

## 1.4 这层和现有 DSL 的关系

它直接复用你们现有：

* `contexts.yaml` 的 context label 和 risk_budget
* `relation_tags.yaml` 的结构标签
* `salience.yaml` 聚合出来的 `top_positive / top_negative / top_warning` 机制

所以这层不是新系统，而是你们现有 inference engine 的**执行翻译器**。

---

# 二、Conflict DSL v1

这个层负责显式回答：

> 为什么今天不是 Offense？
> 为什么 Cash 压过了 runner-up？
> 哪个信号被哪个信号覆盖了？

你们现在已经有 regimes/context 的 score 机制，但冲突还是隐式的。`contexts.yaml` 里是打分，`regimes.yaml` 也是打分。 
Conflict DSL 就是把“隐式裁决”显式化。

---

## 2.1 输出对象

```yaml
conflict_output:
  active_conflicts:
    - id: cf_positive_without_structure
      explain: 局部正向信号存在，但未形成结构主线
      winner: cash
      loser: offense

  decision_overrides:
    block_context_upgrade: true
    reduce_confidence: 0.15

  vetoes:
    - no_structure_confirmation
```

---

## 2.2 DSL 草案

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
      reduce_confidence: 0.10
      add_veto: no_structure_confirmation

  - id: cf_warning_over_positive
    priority: 100
    when: "len(market.top_positive) > 0 and len(market.top_warning) > 0"
    explain: 正向信号与预警并存，优先降低进攻强度
    effect:
      cap_context_to: caution
      reduce_confidence: 0.10
      add_veto: warning_overhang

  - id: cf_negative_over_breakout
    priority: 100
    when: "len(market.top_negative) > 0"
    explain: 存在显著负向信号，突破类交易不应获得权限
    effect:
      force_policy:
        setup_permissions.breakout.status: forbidden
      add_veto: negative_structure_pressure

  - id: cf_growth_unconfirmed
    priority: 90
    when: "'成长风格占优' not in market.relation_tags and index.399006.breadth_state in ['strong', 'neutral_strong']"
    explain: 成长端有修复迹象，但未获结构确认
    effect:
      force_policy:
        setup_permissions.high_beta_chase.status: forbidden
        setup_permissions.low_level_repair.status: probe_only
      reduce_confidence: 0.05

  - id: cf_core_strong_but_unconfirmed
    priority: 90
    when: "'权重大盘主导' not in market.relation_tags and index.000300.trend_state in ['up', 'transitional_up']"
    explain: 权重相对偏强，但不足以确认防守主导结构
    effect:
      cap_context_to: caution
      reduce_confidence: 0.05

  - id: cf_chaotic_market_override
    priority: 110
    when: "market.market_regime.label == '混沌市'"
    explain: 市场处于混沌状态，优先保留现金与等待权
    effect:
      force_context: cash
      block_context_upgrade: true
      add_veto: chaotic_market_override
```

---

## 2.3 这层为什么必要

因为你前面给我的实际运行结果里，已经出现了很典型的冲突：

* 多个指数 `breadth_state = strong`
* 但同时整体 `market_regime = 混沌市`
* 最终 `market_context = Cash`
* `runner_up = Offense`

这说明系统已经在做冲突裁决，只是还没把理由对象化。
Conflict DSL 的意义，就是把这种“判是判出来了，但为什么它赢”明确写出来。

---

# 三、Context State Machine DSL v1

这层负责让系统从“单日判定器”升级成“连续状态机”。

你们现在 `transitions.yaml` 已经有单资产级别的转移标签，比如“趋势转上 / 趋势转下 / 量能跳升 / 广度恶化”。
但还没有 market/context 级别的迁移规则。

---

## 3.1 输出对象

```yaml
context_transition_output:
  prev_context: Cash
  current_context: Caution
  transition_tag: 现金期尝试修复
  transition_reason:
    - 出现显著正向信号
    - relation_tags 开始形成
  persistence: false
```

---

## 3.2 DSL 草案

```yaml
version: "0.1"
dsl_type: context_transitions

context_transitions:
  - id: ctx_cash_to_caution
    when: "prev.market_context.label == 'Cash' and len(market.top_positive) > 0 and len(market.relation_tags) > 0"
    add_tag: 现金期尝试修复
    explain: 现金环境中开始出现可跟踪修复信号

  - id: ctx_caution_to_offense
    when: "prev.market_context.label == 'Caution' and market.market_regime.label == '成长进攻市' and '成长风格占优' in market.relation_tags and len(market.top_warning) == 0"
    add_tag: 进攻环境确认
    explain: 结构主线与进攻风格获得确认

  - id: ctx_offense_to_caution
    when: "prev.market_context.label == 'Offense' and len(market.top_warning) > 0"
    add_tag: 进攻降速
    explain: 进攻环境出现预警，应降频降仓

  - id: ctx_caution_to_cash
    when: "prev.market_context.label == 'Caution' and market.market_regime.label == '混沌市' and len(market.relation_tags) == 0"
    add_tag: 结构丢失退回现金
    explain: 市场主线消失，退出试错状态

  - id: ctx_defense_to_cash
    when: "prev.market_context.label == 'Defense' and len(market.top_negative) > 0 and len(market.relation_tags) == 0"
    add_tag: 防守失效退回现金
    explain: 防守主导结构失效，现金优先

  - id: ctx_cash_persistence
    when: "prev.market_context.label == 'Cash' and market.market_context.label == 'Cash'"
    add_tag: 现金期延续
    explain: 仍未出现足够的结构确认信号
```

---

## 3.3 可选：Regime State Machine

如果你后面想再细一步，也可以单独加一个 `regime_transitions.yaml`：

```yaml
version: "0.1"
dsl_type: regime_transitions

regime_transitions:
  - id: reg_chaotic_to_split
    when: "prev.market_regime.label == '混沌市' and market.market_regime.label == '结构分裂市'"
    add_tag: 混沌转向结构分裂

  - id: reg_split_to_growth
    when: "prev.market_regime.label == '结构分裂市' and market.market_regime.label == '成长进攻市'"
    add_tag: 成长主线成型
```

这个可以后放。

---

# 四、建议的执行顺序

基于你们现有 DSL，我建议 runtime 顺序扩成这样：

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

这里我建议把 `salience` 放在 `regimes/contexts` 之前，因为 `contexts.yaml` 里已经依赖 `market.top_positive / top_negative / top_warning`。

---

# 五、最终决策对象 v1

补完后，最终每日输出对象可以长这样：

```yaml
date: 2026-04-07

market_regime:
  label: 混沌市
  score: 2.0

market_context:
  label: Cash
  score: 5.0
  confidence: 0.71

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

  execution_constraints:
    max_new_positions: 1
    intraday_addons: false
    require_confirmation: true

conflicts:
  active_conflicts:
    - id: cf_positive_without_structure
      explain: 局部正向信号存在，但未形成结构主线
    - id: cf_chaotic_market_override
      explain: 市场处于混沌状态，优先保留现金与等待权

context_transition:
  prev: Caution
  current: Cash
  tag: 结构丢失退回现金

risk_budget:
  total_exposure: 0.10
  max_positions: 1
  max_single_name_weight: 0.05
```

---

# 六、你现在最值得优先落地的顺序

先不要三层一起上。

我建议：

先做 **Policy DSL v1**。
因为这层一出来，你系统就会从“上下文判定”变成“可执行策略权限”。

第二步再做 **Conflict DSL v1**。
因为它能把很多“结果对，但理由还不够透明”的问题补齐。

第三步做 **Context State Machine DSL v1**。
因为这一步是让系统从“日判定”升级成“连续状态机”。

---

# 七、我对这一步的结论

基于你们现有 DSL，我现在更确定一件事：

> 你们不是缺规则语言，
> 你们缺的是**规则语言的上层：policy、conflict、state transition**。

这三层一补上，你们的系统就不再只是“市场解释器”，而会变成：

> **有推断、有权限、有裁决、有连续状态迁移的决策引擎。**

下一步最合适的是，我直接继续把这三份 DSL 再往前推进成**你们现有风格的正式 YAML 文件版本**，并把字段命名、优先级、merge 规则一起定下来。
