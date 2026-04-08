设计草案主要集中在如下三个方面：
1. **统一字段命名规范**
2. **统一引用路径规范**
3. **统一表达式子集规范**
所以我下面直接把这套 DSL 推进到 **spec 草案** 层面。

---

# 一、先明确：这套 DSL 的实现目标

这套 DSL 最终应该支持三件事：

## 1. 可配置

你改 YAML，不改 Python 主逻辑，也能调整规则。

## 2. 可执行

解析器可以按固定顺序运行：

* feature
* state
* pattern
* transition
* salience
* relation
* regime

## 3. 可审计

任意一天、任意一个结论，都能追溯到：

* 哪些字段
* 哪些规则
* 哪些命中项

所以你要设计的不是“写给人看的语法”，而是：

> **写给规则引擎解析、同时又便于人类维护的配置语言**

---

# 二、统一命名规范：先把名字管住

这是第一步。
建议你不要让字段名自由生长，不然三个月后会非常乱。

我建议命名分四类：

---

## 1. 原始字段命名：raw fields

统一小写，下划线，尽量短但明确。

### 单指数原始字段

```yaml
open
high
low
close
volume
amount
adv
decl
date
symbol
```

### 禁止混用

不要一会儿叫：

* `turnover`
* `amt`
* `成交额`

统一就叫：

```yaml
amount
```

如果以后要区分成交量单位、成交额单位，在 metadata 里处理，不在字段名里处理。

---

## 2. 特征字段命名：features

规则：

```text
<family>_<detail>_<window?>
```

例如：

### 收益

```yaml
ret_1d
ret_5d
ret_20d
ret_60d
```

### 均线

```yaml
ma_5
ma_10
ma_20
ma_60
ma_120
```

### 均线斜率

```yaml
ma_slope_20
ma_slope_60
```

### 距离/位置

```yaml
distance_to_ma20
distance_to_ma60
price_percentile_120d
price_percentile_250d
range_position_20d
```

### 量能

```yaml
amount_ma_20
amount_ratio_1_20
amount_ratio_5_20
amount_percentile_120d
volume_percentile_120d
```

### 广度

```yaml
breadth_ratio
breadth_diff
breadth_ratio_ma_5
breadth_ratio_ma_20
breadth_percentile_120d
```

### 波动

```yaml
true_range
atr_14
atr_pct_14
volatility_percentile_250d
```

---

## 3. 状态字段命名：states

状态字段统一以 `_state` 结尾。

```yaml
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

这样一眼就知道它是离散状态，不是连续值。

---

## 4. 标签字段命名：tags

所有标签类输出统一以 `_tags` 结尾，且为 list。

```yaml
pattern_tags
transition_tags
relation_tags
warning_tags
```

不要有时用单数、有时用复数，也不要混成字符串。

统一规则：

> **tags 一律是 string list**

---

# 三、状态值命名规范

状态值最好也统一成英文枚举，展示时再映射成中文。

因为：

* 代码里英文更稳
* YAML 条件判断更清楚
* 中文标签适合作为 narrative 层输出

---

## 1. 趋势状态

```yaml
up
down
range
transitional_up
transitional_down
```

---

## 2. 位置状态

```yaml
low
low_mid
mid
mid_high
high
```

---

## 3. 量能状态

```yaml
extreme_contraction
contraction
normal
expansion
extreme_expansion
```

---

## 4. 广度状态

```yaml
weak
neutral_weak
neutral
neutral_strong
strong
```

---

## 5. 波动状态

```yaml
low
medium
high
extreme
```

---

## 6. relation 状态

```yaml
left_strong
right_strong
neutral

left_confirmed
right_confirmed
left_unconfirmed
right_unconfirmed

left_persistent
right_persistent
left_recent_turn
right_recent_turn
mixed

widening_to_left
widening_to_right
narrowing_from_left
narrowing_from_right
stable
```

---

# 四、对象命名规范

你后面要同时支持：

* 单指数对象
* pair 对象
* market 对象

所以路径前缀要统一。

建议三层对象名：

```yaml
index.<index_id>
pair.<pair_id>
market
```

例如：

```yaml
index.hs300
index.cyb
index.csi1000

pair.hs300_vs_cyb
pair.sz50_vs_csi1000

market
```

---

## 指数 id 建议固定成短码

```yaml
sh_index
sz_index
sz50
hs300
csi500
csi1000
cyb
star
```

不要今天叫 `创业板`，明天叫 `gem`，后天叫 `cyb_index`。
固定一种。

---

# 五、统一引用路径规范

这是 DSL 最关键的一步。
因为所有 `when`、`formula` 最终都在引用字段。

我建议用**点路径**，规则如下：

---

## 1. 当前对象字段

如果规则运行上下文就是单指数对象，那么可以直接写：

```yaml
close
ret_20d
trend_state
pattern_tags
```

但为了长期清晰，我更建议即使在当前上下文也支持显式路径：

```yaml
self.close
self.ret_20d
self.trend_state
self.pattern_tags
```

推荐解析器同时支持：

* 简写：`close`
* 显式写法：`self.close`

---

## 2. 历史状态引用

统一用：

```yaml
prev.<field>
```

例如：

```yaml
prev.trend_state
prev.volume_state
prev.breadth_state
prev.close
```

如果以后要支持多期回看，再扩展成：

```yaml
lag( field, n )
```

但第一版先用 `prev.` 足够。

---

## 3. 单指数显式引用

在 regime 层、relation 层里，经常要跨对象引用，统一写：

```yaml
index.hs300.trend_state
index.cyb.volume_state
index.csi1000.breadth_state
```

---

## 4. pair 对象引用

统一写：

```yaml
pair.hs300_vs_cyb.leader_state
pair.sz50_vs_csi1000.confirmation_state
pair.hs300_vs_csi500.relation_tags
```

---

## 5. market 对象引用

统一写：

```yaml
market.relation_tags
market.top_positive
market.market_regime.label
```

不过严格来说，`market_regime` 就挂在 `market` 下即可。

---

# 六、推荐的上下文规则

不同 DSL 层允许的默认上下文不同。

---

## 1. feature/state/pattern/transition/salience 层

默认上下文是单指数对象：

```yaml
self
prev
```

允许引用：

* `self.xxx`
* `prev.xxx`

不建议在这一层直接引用别的指数。
否则层次会乱。

---

## 2. relation 层

默认上下文是 pair 对象：

```yaml
self
left
right
```

允许引用：

* `left.ret_20d`
* `right.breadth_ratio_ma_5`
* `self.leader_state`

这里不要直接写 `index.hs300.xxx`，除非你有特殊需求。
pair 内部优先用 `left/right`。

---

## 3. regime 层

默认上下文是 market：

允许引用：

* `index.xxx`
* `pair.xxx`
* `market.xxx`

这里才是全局聚合层。

---

# 七、表达式子集规范：必须限制语言能力

这是实现稳定性的关键。
不要让 `when` / `formula` 变成一个任意 Python 子集，不然：

* 安全性差
* 解析困难
* 调试困难
* 可移植性差

建议第一版限制为**小型声明式表达式语言**。

---

## 1. 值类型

只支持这几类：

* number
* boolean
* string
* list[string]

---

## 2. 比较操作符

只支持：

```yaml
==
!=
>
>=
<
<=
in
not in
```

---

## 3. 逻辑操作符

只支持：

```yaml
and
or
not
```

不支持位运算、不支持复杂 lambda。

---

## 4. 算术操作符

只支持：

```yaml
+
-
*
/
```

---

## 5. 允许的内置函数

### 数值函数

```yaml
abs(x)
max(a, b, ...)
min(a, b, ...)
round(x, n)
```

### 时间序列函数

```yaml
delay(x, n)
rolling_mean(x, n)
rolling_max(x, n, exclude_current=true|false)
rolling_min(x, n, exclude_current=true|false)
```

### 集合函数

```yaml
len(x)
contains(list, item)
```

### 逻辑辅助函数

```yaml
all_of(...)
any_of(...)
```

不过 `all_of/any_of` 第一版可以先不做。

---

# 八、布尔表达式规范

为了保证一致性，建议所有 `when` 都只返回 boolean。

例如：

```yaml
when: "trend_state == 'up' and position_state in ['mid', 'mid_high']"
```

而所有 `formula` 都返回 number / boolean / string，但最好不要返回复杂对象。

---

# 九、统一 schema：每一层允许的字段结构

下面我把各层的推荐 schema 压成规则。

---

## 1. Feature rule schema

```yaml
- id: <string>
  type: formula | rolling | percentile | boolean
  input: [<field_ref>, ...]
  formula: <expr>        # formula / boolean 类型必填
  window: <int>          # rolling / percentile 类型常用
  method: mean|max|min   # rolling 类型需要
  output: <field_name>
  tags: [<string>, ...]
```

---

## 2. State rule schema

```yaml
- id: <string>
  output: <state_field_name>
  cases:
    - when: <bool_expr>
      value: <enum_value>
    - when: <bool_expr>
      value: <enum_value>
  default: <enum_value>
```

---

## 3. Pattern rule schema

```yaml
- id: <string>
  group: <string>
  priority: <number>
  when: <bool_expr>
  add_tag: <string>
  add_context_tags: [<string>, ...]   # optional
```

---

## 4. Transition rule schema

```yaml
- id: <string>
  when: <bool_expr>
  add_tag: <string>
  priority: <number>    # optional
```

---

## 5. Salience rule schema

```yaml
- id: <string>
  group: <string>
  when: <bool_expr>
  score: <number>
  bucket: positive | negative | warning | transition | positive_or_negative | warning_or_transition
  polarity: positive | negative | context_dependent
  reason: <string>
```

---

## 6. Pair definition schema

```yaml
- id: <pair_id>
  left: <index_id>
  right: <index_id>
  tags: [<string>, ...]
```

---

## 7. Pair feature schema

与 feature 基本一致，只是 input 支持 `left.` 和 `right.` 引用。

---

## 8. Pair state schema

与 state 基本一致。

---

## 9. Relation tag schema

```yaml
- id: <string>
  pair: <pair_id>
  group: <string>
  priority: <number>
  when: <bool_expr>
  add_tag: <string>
```

---

## 10. Regime rule schema

```yaml
- id: <regime_id>
  label: <string>
  rules:
    - id: <string>
      when: <bool_expr>
      score: <number>
      evidence: <string>
```

---

# 十、执行顺序规范：必须写死

这个顺序不能交给配置自由决定。

固定为：

```yaml
pipeline:
  - load_raw
  - compute_features
  - derive_states
  - detect_patterns
  - detect_transitions
  - score_salience
  - compute_pair_features
  - derive_pair_states
  - detect_relation_tags
  - score_regimes
  - render_narrative
```

理由很简单：

* salience 依赖 pattern/transition
* relation 依赖单指数特征和状态
* regime 依赖 relation + 单指数结果
* LLM 只能最后用

---

# 十一、输出对象规范

建议每次运行统一产出三个层次的结果对象。

---

## 1. 单指数输出

```yaml
index:
  hs300:
    raw: {}
    features: {}
    states: {}
    pattern_tags: []
    transition_tags: []
    salience:
      total_score: 0
      positive_score: 0
      negative_score: 0
      warning_score: 0
      transition_score: 0
      matched_rules: []
```

---

## 2. pair 输出

```yaml
pair:
  hs300_vs_cyb:
    features: {}
    states: {}
    relation_tags: []
```

---

## 3. market 输出

```yaml
market:
  top_positive: []
  top_negative: []
  top_warning: []
  top_transition: []
  relation_tags: []
  market_regime:
    label: ""
    score: 0
    confidence: 0
    evidence: []
```

---

# 十二、错误处理规范

你这个系统一定要提前规定错误行为，否则 DSL 一复杂就会很痛苦。

---

## 1. 缺字段

如果 rule 引用了不存在字段：

* 默认报错并中止该层
* 日志记录 rule id 和缺失字段

不要静默忽略。

---

## 2. 除零

公式中除零统一用安全除法策略：

```text
a / (b + 1e-9)
```

或者内置 `safe_div(a, b)`。

---

## 3. 无法命中任何 case

state rule 如果没有命中任何 case：

* 使用 `default`
* 若无 default，报 schema error

---

## 4. 标签重复

`pattern_tags / transition_tags / relation_tags` 自动去重，保持 insertion order。

---

# 十三、版本规范

非常建议从现在开始就加版本号。

每个 DSL 文件顶部都加：

```yaml
version: "0.1"
dsl_type: features
```

例如：

```yaml
version: "0.1"
dsl_type: salience
```

这样以后升级 schema 不会乱。

---

# 十四、一个简化但完整的统一示例

我给你一个最小但统一的片段，你能直观看到风格。

```yaml
version: "0.1"
dsl_type: states

context:
  asset_type: index
  freq: daily
  market: CN_A

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
```

再看 relation 层：

```yaml
version: "0.1"
dsl_type: relation_tags

context:
  asset_type: index_pair
  freq: daily
  market: CN_A

relation_tags:
  - id: r_growth_over_core
    pair: hs300_vs_cyb
    group: style
    priority: 92
    when: "self.leader_state == 'right_strong' and self.confirmation_state == 'right_confirmed'"
    add_tag: 成长风格占优
```

再看 regime 层：

```yaml
version: "0.1"
dsl_type: regimes

context:
  asset_type: market
  freq: daily
  market: CN_A

regimes:
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
        evidence: 成长方向相对核心资产占优
```

---

# 十五、你现在真正拥有的 DSL 分层

到这里为止，你这套系统已经能正式定义为：

## 单对象层

* `features.dsl.yaml`
* `states.dsl.yaml`
* `patterns.dsl.yaml`
* `transitions.dsl.yaml`
* `salience.dsl.yaml`

## 关系层

* `pairs.dsl.yaml`
* `pair_features.dsl.yaml`
* `pair_states.dsl.yaml`
* `relation_tags.dsl.yaml`

## 聚合层

* `regimes.dsl.yaml`

## 渲染层

* `narrative_prompt.md` 或模板文件

---

# 十六、下一步最合理的推进方向

现在最有价值的已经不是继续扩概念，而是二选一：

## 方向 A：把这套 spec 进一步收敛成 **正式 BNF/EBNF 风格的表达式语法规范**

适合你想自己写 parser。

## 方向 B：直接进入 **parser/evaluator 设计**

也就是：

* 数据结构
* 依赖解析
* 执行器
* rule trace
* debug 输出

如果你是想真正落代码，我建议下一步直接做 **parser/evaluator 设计草案**，因为那一步会把现在这些 schema 变成真正可运行的骨架。
