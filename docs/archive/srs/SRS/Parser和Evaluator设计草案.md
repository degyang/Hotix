那就直接进入 **parser / evaluator 设计草案**。

这一步的目标不是再谈理念，而是回答：

> 这套 DSL 在程序里到底怎么跑起来？

我下面按工程实现顺序来拆：

1. 运行时对象模型
2. parser 该做什么
3. evaluator 该做什么
4. 依赖与执行顺序
5. trace / debug / 审计
6. 第一版最小实现建议

---

# 一、先定运行时对象模型

你的 DSL 最终不是直接“生成一句话”，而是持续填充一棵运行时状态树。

我建议统一成这 3 类对象：

## 1. IndexRuntime

单指数运行时对象。

```python
{
  "id": "hs300",
  "meta": {...},
  "raw": {...},
  "features": {...},
  "states": {...},
  "pattern_tags": [],
  "transition_tags": [],
  "salience": {...},
  "trace": {...}
}
```

---

## 2. PairRuntime

指数对运行时对象。

```python
{
  "id": "hs300_vs_cyb",
  "left": "hs300",
  "right": "cyb",
  "features": {...},
  "states": {...},
  "relation_tags": [],
  "trace": {...}
}
```

---

## 3. MarketRuntime

市场级运行时对象。

```python
{
  "relation_tags": [],
  "top_positive": [],
  "top_negative": [],
  "top_warning": [],
  "top_transition": [],
  "market_regime": {...},
  "trace": {...}
}
```

---

# 二、整个引擎的核心思想：不是“解释 YAML”，而是“执行 rule graph”

你不要把它实现成一堆 if/else 硬拼，而是实现成：

> **配置加载 → schema 校验 → rule 编译 → 分层执行 → trace 输出**

也就是 5 个步骤。

---

## Step 1. Loader

读取 YAML 文件，得到原始配置 dict。

## Step 2. Validator

校验 schema：

* 必填字段是否存在
* output 名是否合法
* expression 是否可解析
* 引用字段是否符合层级规则

## Step 3. Compiler

把 DSL 编译成内部 Rule 对象。

## Step 4. Evaluator

按 pipeline 顺序执行，填充 runtime。

## Step 5. Trace / Reporter

输出命中规则、计算值、异常、最终结果。

---

# 三、内部 Rule 对象应该长什么样

不要在执行时反复处理 YAML 原文。
应该先编译成内部对象。

我建议至少有这几类 dataclass。

---

## 1. FeatureRule

```python
@dataclass
class FeatureRule:
    id: str
    rule_type: str
    inputs: list[str]
    formula: str | None
    window: int | None
    method: str | None
    output: str
    tags: list[str]
```

---

## 2. StateRule

```python
@dataclass
class StateCase:
    when: str
    value: str

@dataclass
class StateRule:
    id: str
    output: str
    cases: list[StateCase]
    default: str
```

---

## 3. TagRule

Pattern / Transition / RelationTag 其实都可以抽象成一种。

```python
@dataclass
class TagRule:
    id: str
    group: str | None
    when: str
    add_tag: str
    priority: float | None
    pair: str | None = None
```

---

## 4. SalienceRule

```python
@dataclass
class SalienceRule:
    id: str
    group: str
    when: str
    score: float
    bucket: str
    polarity: str
    reason: str
```

---

## 5. RegimeRule / RegimeDefinition

```python
@dataclass
class RegimeScoringRule:
    id: str
    when: str
    score: float
    evidence: str

@dataclass
class RegimeDefinition:
    id: str
    label: str
    rules: list[RegimeScoringRule]
```

---

# 四、Parser 的职责到底是什么

Parser 不是 evaluator。
它只做三件事：

## 1. 读取并转成内部 rule 对象

把 YAML 转成上面的 dataclass。

## 2. 做静态校验

例如：

* `output` 是否以 `_state` 结尾
* `pattern_tags` 是否是 list 目标
* `pair` 是否引用了真实存在的 pair id
* `when` / `formula` 中有没有非法 token

## 3. 抽取依赖

比如从表达式里抽出：

* `self.ma_20`
* `prev.trend_state`
* `left.ret_20d`
* `index.cyb.trend_state`

这样 evaluator 才知道某条规则依赖什么。

---

# 五、表达式处理：建议做“小型 AST”，不要直接 eval

这是最关键的工程建议。

不要直接 Python `eval()`。
原因很简单：

* 不安全
* 不可控
* 错误信息差
* 未来很难限制语言子集

你应该做：

> tokenizer → parser → AST → safe evaluator

---

## 1. Tokenizer

把表达式拆成 token：

```text
self.close > self.ma_20 and self.ma_20 > self.ma_60
```

拆成：

* IDENT(self.close)
* OP(>)
* IDENT(self.ma_20)
* OP(and)
* IDENT(self.ma_20)
* OP(>)
* IDENT(self.ma_60)

---

## 2. Parser

生成 AST，例如：

```python
And(
  Compare(Ref("self.close"), ">", Ref("self.ma_20")),
  Compare(Ref("self.ma_20"), ">", Ref("self.ma_60"))
)
```

---

## 3. Safe Evaluator

给定 context，把 AST 计算成结果。

---

# 六、引用解析器怎么设计

你前面已经定了引用规范，所以现在要落实现。

我建议做一个统一的 `Resolver`。

---

## 1. Resolver 输入

* 当前 layer
* 当前 runtime object
* 全局 runtime store
* ref path，例如 `self.ma_20`

## 2. Resolver 输出

* 对应值
* 或抛出 MissingReferenceError

---

## 3. Resolver 的规则

### 在单指数层

支持：

* `self.xxx`
* `prev.xxx`

### 在 pair 层

支持：

* `self.xxx`
* `left.xxx`
* `right.xxx`

其中 `left.xxx` 实际上去 `IndexRuntime[left_id]` 查。

### 在 regime 层

支持：

* `index.xxx.yyy`
* `pair.xxx.yyy`
* `market.xxx`

---

# 七、依赖管理：哪些 rule 先算，哪些后算

这是实现里最容易踩坑的地方。

## 1. 层级顺序必须固定

你已经定了 pipeline，这很好。

## 2. 每一层内部还要做拓扑排序

因为 feature 之间也可能互相依赖。

例如：

* `amount_ma_20` 依赖 `amount`
* `amount_ratio_1_20` 依赖 `amount_ma_20`

所以 feature 不是按文件顺序死跑，而应该：

> 先构建依赖图，再拓扑排序执行

---

## 3. State / Pattern 通常不需要复杂图

因为 state 一般只依赖 feature 和已有 state。
第一版可以约定：

* states 不允许互相循环依赖
* patterns 不产生新 feature
* salience 不反向修改 states

这样整个系统是单向流。

---

# 八、建议的执行器架构

我建议拆成 4 个执行器，而不是一个大类。

---

## 1. IndexLayerEvaluator

处理：

* features
* states
* patterns
* transitions
* salience

输入：某个指数的历史 dataframe + 对应 runtime
输出：更新后的 IndexRuntime

---

## 2. PairLayerEvaluator

处理：

* pair_features
* pair_states
* relation_tags

输入：两个 IndexRuntime + PairRuntime
输出：更新后的 PairRuntime

---

## 3. MarketLayerEvaluator

处理：

* 汇总 relation_tags
* 汇总 salience top lists
* 计算 regime

输入：all IndexRuntime + all PairRuntime
输出：MarketRuntime

---

## 4. NarrativeRenderer

只处理最终结构化结果，生成 Markdown / JSON summary。
不参与判断。

---

# 九、时间维度怎么处理

你这个系统是日频，所以 evaluator 最好是“逐日推进”的，而不是只算单天快照。

我建议运行模式是：

## 模式 A：历史回放

按日期从旧到新逐天运行。
这样 `prev` 才有稳定含义。

## 模式 B：增量运行

每天只跑最新一天，但需要读取前一天快照。

---

## 每天运行时建议的最小状态

每个 index 在 `date=t` 运行时，至少拿到：

* 当天 raw row
* 到当天为止的 feature 缓冲区
* 前一天 states/tags/salience

这样就能算：

* rolling 指标
* prev 状态
* transition
* salience

---

# 十、Trace 设计：这是系统可信度的关键

交易系统里，如果你不知道“为什么得到这个结论”，那它迟早会失控。

所以每一层都必须带 trace。

---

## 1. Feature trace

记录：

* 规则 id
* 输入值
* 输出值

例如：

```python
trace["features"]["amount_ratio_1_20"] = {
  "rule_id": "amount_ratio_1_20",
  "inputs": {"amount": 5230000000, "amount_ma_20": 4100000000},
  "output": 1.2756
}
```

---

## 2. State trace

记录：

* 哪个 case 命中
* 命中了哪条 when
* 输出什么状态

```python
trace["states"]["trend_state"] = {
  "rule_id": "trend_state",
  "matched_case": 0,
  "when": "self.close > self.ma_20 and self.ma_20 > self.ma_60 and self.ma_slope_20 > 0",
  "value": "up"
}
```

---

## 3. Tag trace

记录：

* 哪些 tag rule 命中
* priority 是多少

```python
trace["patterns"].append({
  "rule_id": "p_mid_trend_breakout",
  "tag": "中继放量突破",
  "priority": 90
})
```

---

## 4. Salience trace

记录：

* 哪条规则贡献了多少分
* 落入哪个 bucket

```python
trace["salience"].append({
  "rule_id": "s_resonance_breakout",
  "score": 3.2,
  "bucket": "positive",
  "reason": "趋势突破、广度和量能形成正向共振"
})
```

---

## 5. Regime trace

记录：

* 每个 regime 命中了哪些 scoring rules
* 总分多少
* 最终为什么胜出

```python
trace["regimes"]["growth_attack"] = {
  "score": 8,
  "matched_rules": [
    {"id": "rr_gro_01", "score": 2, "evidence": "创业板进入进攻结构"},
    {"id": "rr_gro_03", "score": 3, "evidence": "成长方向相对核心资产占优"}
  ]
}
```

这个 trace 非常重要。以后你调规则时，主要就是看它。

---

# 十一、Debug 模式应该输出什么

我建议你直接预留两种模式。

## 1. normal mode

只输出最终结果。

## 2. explain mode

输出每层 trace，便于复盘。

比如你输入：

```bash
python run_daily.py --date 2026-04-05 --explain hs300
```

输出：

* hs300 的 feature 结果
* state 命中
* pattern 命中
* salience 计分
* 它在 pair / regime 中贡献了什么

这会非常有用。

---

# 十二、一个合理的代码目录

我建议目录直接这样建：

```text
market_system/
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
│  ├─ tokenizer.py
│  ├─ ast_nodes.py
│  ├─ expr_parser.py
│  ├─ resolver.py
│  ├─ feature_evaluator.py
│  ├─ state_evaluator.py
│  ├─ tag_evaluator.py
│  ├─ salience_evaluator.py
│  ├─ pair_evaluator.py
│  ├─ regime_evaluator.py
│  ├─ pipeline.py
│  └─ trace.py
│
├─ runtime/
│  ├─ snapshots/
│  └─ logs/
│
├─ outputs/
│  ├─ json/
│  ├─ markdown/
│  └─ obsidian/
│
└─ run_daily.py
```

---

# 十三、第一版千万不要一口气做完全部 AST 特性

第一版最容易失败的地方，就是 parser 做得太大。

你应该刻意做小。

---

## 第一版表达式只支持这些就够了

### 原子

* number
* string
* field ref

### 运算

* `+ - * /`
* `> >= < <= == !=`
* `and or not`
* `in`

### 函数

* `abs`
* `max`
* `min`
* `len`

rolling 计算不要放进 state/pattern evaluator 的表达式里，
而应尽量在 feature 层先算成字段。

也就是说：

> **复杂时间序列逻辑留在 feature 层，后面层只消费结果字段。**

这会让整个实现大幅稳定。

---

# 十四、第一版的最小闭环应该是什么

你不要一开始就上 8 个指数全部规则全开。
最好先跑通一个最小闭环。

我建议：

## 对象

* 先只做 3 个指数：`hs300`, `cyb`, `csi1000`
* 先只做 2 个 pair：`hs300_vs_cyb`, `hs300_vs_csi1000`

## features

只做 12~15 个核心字段

## states

只做：

* trend_state
* position_state
* volume_state
* breadth_state

## patterns

只做 6 个

* 中继放量突破
* 低位放量修复
* 高位放量分歧
* 放量下跌
* 缩量回踩
* 指数上行但跟随不足

## transitions

只做 4 个

* 趋势转上
* 趋势转下
* 量能跳升
* 广度恶化

## salience

只做 top_positive / top_negative / top_warning

## relation_tags

只做：

* 成长风格占优
* 权重大盘主导
* 小票情绪回暖
* 扩散不足

## regimes

只做：

* 权重防守市
* 成长进攻市
* 结构分裂市
* 混沌市

这已经足够出第一版日报了。

---

# 十五、推荐的开发顺序

这个顺序最稳。

## Phase 1：只做 feature + state

目标：单指数状态能稳定输出。

## Phase 2：加 pattern + transition

目标：能给出单指数结构标签。

## Phase 3：加 salience

目标：能回答“今天先看谁”。

## Phase 4：加 pair + relation

目标：能做结构归因。

## Phase 5：加 regime

目标：能做市场总分类。

## Phase 6：加 narrative

目标：把结构化结果转成日报。

这个顺序的好处是：
前一层错了，马上能看出来，不会所有东西一起糊掉。

---

# 十六、最后给你一个最关键的实现原则

这句可以直接当工程守则：

> **每一层只消费上一层的稳定输出，不跨层偷取原始复杂逻辑。**

具体就是：

* pattern 不直接做 rolling 计算
* salience 不重新解释原始 K 线
* relation 不重新定义单指数状态
* regime 不直接读取太多原始 feature 阈值

这样层次才稳。

---

下一步最合适的是我直接给你一版 **Python 数据结构与 evaluator 骨架代码**，包括：

* `RuntimeStore`
* `Resolver`
* `RuleEvaluator`
* `StateEvaluator`
* `TagEvaluator`
* `RegimeEvaluator`

这样你就可以真正开始写第一版引擎。
