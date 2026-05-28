第二阶段不要急着扩很多新对象，正确落地方式是：

> **在第一阶段“3 指数 + 2 pair + 4 regime”稳定运行之后，把系统从“单日结构识别器”升级成“可校准、可扩展、可用于交易约束的市场上下文引擎”。**

如果第一阶段的核心是“看懂市场”，
那第二阶段的核心就是：
1. **把范围从 3 个指数扩到完整核心指数面板**
2. **把输出从“观察结论”升级为“交易约束”**
3. **把规则从静态可跑，升级为可验证、可校准、可追踪**
4. **为第三阶段接行业板块、策略、执行做接口准备**

下面我直接按落地来讲，不讲空话。

---

# 一、第二阶段的目标

第二阶段的正式目标建议写成：

## 目标 A：扩展指数面板

从第一阶段的：

* hs300
* cyb
* csi1000

扩展到完整核心面板，例如：

* sh_index
* sz_index
* sz50
* hs300
* csi500
* csi1000
* cyb
* star

---

## 目标 B：形成稳定的市场上下文输出

不仅输出：

* top_positive
* top_negative
* regime

还要输出：

* 当前市场允许什么交易
* 当前市场不允许什么交易
* 当前风险预算建议是什么

也就是你之前说的那类：

* Offense
* Caution
* Defense
* Cash

但第二阶段先不要直接做完整交易系统，而是先做**Context Layer**。

---

## 目标 C：建立规则验证与校准机制

第一阶段只是“跑通”，第二阶段必须开始做：

* 历史回放
* regime 分布统计
* tag 命中统计
* 错判样本复盘
* 阈值修订流程

---

# 二、第二阶段不要做什么

先把边界说清楚。

第二阶段**不要**直接做：

* 个股级 signal engine
* 仓位 sizing engine
* 实盘自动下单
* 复杂 UI 平台
* LLM 主导判断
* 过度泛化成通用量化平台

第二阶段只做一件事：

> **把“市场结构识别”升级成“市场上下文引擎”。**

---

# 三、第二阶段的系统结构

第一阶段你已经有：

```text
raw
-> features
-> states
-> patterns
-> transitions
-> salience
-> relations
-> regimes
```

第二阶段在它上面加 3 层：

```text
raw
-> features
-> states
-> patterns
-> transitions
-> salience
-> relations
-> regimes
-> context
-> validation
-> reporting
```

新增的三层分别是：

## 1. context layer

把 regime 翻译成交易约束

## 2. validation layer

回放、统计、校准

## 3. reporting layer

更稳定的日报/周报/调试输出

---

# 四、第二阶段的核心模块

建议拆成 6 个具体模块。

---

## 模块 1：完整指数面板扩容

### 要做什么

把 index registry 从 3 个扩到 8 个。

### 具体新增对象

* `sh_index`
* `sz_index`
* `sz50`
* `hs300`
* `csi500`
* `csi1000`
* `cyb`
* `star`

### 新增 pair

不要全排列，先加关键 pair：

#### 核心 vs 成长

* `hs300_vs_cyb`
* `hs300_vs_star`

#### 核心 vs 扩散

* `hs300_vs_csi500`
* `hs300_vs_csi1000`

#### 大小盘

* `sz50_vs_csi1000`

#### 成长内部

* `cyb_vs_star`

#### 扩散内部

* `csi500_vs_csi1000`

### 落地方式

只需要改：

* `config/index_registry.yaml`
* `dsl/pairs.yaml`

然后把 raw parquet 补齐。

### 验收标准

* 8 个指数全部能跑单日
* 新增 pair 全部能产出 relation tags

---

## 模块 2：Context Engine

这是第二阶段最关键的模块。

### 要解决的问题

把“市场 regime”转成“交易环境约束”。

第一阶段输出的是：

* 结构结论

第二阶段要多输出：

* 行为结论

---

### Context 输出建议

先固定成这几个字段：

```yaml
market_context:
  label: Offense | Caution | Defense | Cash
  score: 0-10
  allowed_styles: []
  disallowed_styles: []
  risk_budget:
    total_exposure: 0.xx
    max_positions: n
    max_single_name_weight: 0.xx
  evidence: []
  vetoes: []
```

---

### 先不要复杂，第一版 Context 只做四档

#### Offense

环境偏进攻，允许高弹性、趋势跟随

#### Caution

允许交易，但只做最强方向，频率降下来

#### Defense

以防守为主，主要保护资本

#### Cash

停止主动进攻，只观察与复盘

---

### Context 规则从哪里来

直接消费：

* regime
* salience
* relation_tags
* 部分单指数状态

也就是：

> **Context 不重新发明判断，只消费前面层的稳定输出。**

---

### 具体规则示例

#### Offense

```yaml
if:
  regime == 成长进攻市
  and top_positive not empty
  and top_negative weak
then:
  label: Offense
  allowed_styles: [趋势跟随, 成长进攻, 高弹性试错]
  disallowed_styles: [逆势抄底]
  risk_budget:
    total_exposure: 0.8
    max_positions: 6
    max_single_name_weight: 0.2
```

#### Defense

```yaml
if:
  regime == 权重防守市
  or top_negative strong
  or 小票情绪显著退潮
then:
  label: Defense
  allowed_styles: [低频, 核心资产, 轻仓]
  disallowed_styles: [高弹性追涨, 高频试错]
```

#### Cash

```yaml
if:
  regime == 混沌市
  and top_warning strong
  and relation_tags empty_or_conflicted
then:
  label: Cash
```

---

### 落地文件

新增：

* `dsl/contexts.yaml`
* `engine/context_engine.py`

---

## 模块 3：Validation Engine

第二阶段必须开始做验证，不然规则会越来越玄。

### 要做什么

对历史区间做批量回放，然后统计：

* 各 regime 出现频率
* 各 relation tag 出现频率
* 各 salience tag 命中频率
* regime 切换序列
* 哪些日子最容易出现“结构分裂”
* 哪些阈值导致大量“混沌市”

---

### 最低限度要做的统计

#### 1. regime 分布

```yaml
growth_attack: 18%
defensive_large_cap: 24%
split_structure: 31%
chaotic_market: 27%
```

#### 2. tag 分布

统计：

* 成长风格占优
* 权重大盘主导
* 扩散不足
* 小票情绪回暖

#### 3. 上下文分布

统计：

* Offense
* Caution
* Defense
* Cash

#### 4. 转移矩阵

例如：

* 昨天 Defense，今天 Offense 的概率
* 昨天 Growth Attack，今天 Split 的概率

---

### 落地文件

新增：

* `engine/validation_engine.py`
* `outputs/stats/`

输出：

* `regime_distribution.csv`
* `context_distribution.csv`
* `transition_matrix.csv`

---

## 模块 4：Calibration Workflow

这个不是单个文件，而是一套固定修规则流程。

### 为什么要有

第二阶段开始，你不能再“凭感觉”改规则。
必须形成流程：

1. 找错判日
2. 看 trace
3. 定位是哪一层错
4. 修阈值或修规则
5. 重新回放
6. 对比前后分布变化

---

### 具体落地动作

#### 每周一次校准

看：

* regime 分布是否失衡
* 是否某个 regime 过多
* 是否过多天被归到 chaotic
* 是否某些 tag 几乎永远不命中

#### 每次只改一类东西

例如：

* 只改 breadth_state 阈值
* 或只改 growth_attack 的 scoring rule
* 不要一次大改所有规则

#### 每次改完必须回放最近 1-2 年

输出前后对比。

---

### 具体文件建议

新增：

* `config/calibration_notes.md`
* `outputs/stats/calibration_runs/`

每次校准记录：

* 改了什么
* 为什么改
* 前后结果差异

---

## 模块 5：稳定日报 / 周报层

第一阶段有 markdown 日报，但比较粗。

第二阶段要稳定成两个输出：

### 日报

继续保留，但加：

* context
* risk budget
* allowed / disallowed styles

### 周报

新增周报，不重新跑一套逻辑，而是聚合日结果。

周报内容建议：

* 本周 regime 变化序列
* 本周 context 序列
* 本周最常见正向/负向信号
* 本周最重要结构转折日
* 下周的初始观察重点

---

### 落地文件

新增：

* `engine/reporting_engine.py`
* `outputs/weekly_markdown/`

---

## 模块 6：接口层，为第三阶段做准备

第二阶段末尾要留接口，不要临时拼。

### 第三阶段要接什么

将来你要接：

* 行业板块
* setup
* 个股候选池
* execution constraint

所以第二阶段要把 market context 结果输出成机器可用接口。

建议新增一个稳定文件：

```text
outputs/context/YYYY-MM-DD_context.json
```

内容只保留最关键字段：

```yaml
date:
context_label:
regime:
top_positive:
top_negative:
relation_tags:
allowed_styles:
disallowed_styles:
risk_budget:
vetoes:
```

这样以后第三阶段的策略模块，直接读这个文件就行。

---

# 五、第二阶段的落地顺序

不要同时做 6 个模块。
按下面顺序最稳。

---

## Phase 2.1：扩面板，不改逻辑

先做：

1. 补全 8 个指数 raw 数据
2. 更新 `index_registry.yaml`
3. 更新 `pairs.yaml`
4. 跑通 8 指数 + 核心 pair

### 验收

* 单日能完整跑
* 区间回放能跑
* JSON / Markdown 都正常

---

## Phase 2.2：加 Context Engine

新增：

* `dsl/contexts.yaml`
* `engine/context_engine.py`

先输出：

* label
* allowed_styles
* disallowed_styles
* risk_budget

### 验收

* 每日 JSON 中有 `market_context`
* Markdown 中多一节“交易环境与约束”

---

## Phase 2.3：加 Validation Engine

新增：

* `engine/validation_engine.py`

实现：

* 区间批量回放后的分布统计
* 转移矩阵
* 简单 CSV 输出

### 验收

* 能对 1 年历史跑出 regime/context 分布
* 能看出是否分类严重失衡

---

## Phase 2.4：加 Calibration Workflow

不是大写代码，而是把流程定下来。

### 要做的事

* 加一个 `scripts/backtest_stats.py` 或类似命令
* 每次改规则后跑全样本统计
* 输出前后 diff

### 验收

* 能明确回答“这次改阈值后，哪些 regime 增多了，哪些减少了”

---

## Phase 2.5：加周报

实现周报聚合，不加新判断层。

### 验收

* 一周能自动生成 1 份 weekly markdown

---

# 六、第二阶段要新增的文件

我直接给你文件清单。

```text
dsl/
├─ contexts.yaml

engine/
├─ context_engine.py
├─ validation_engine.py
├─ reporting_engine.py

outputs/
├─ context/
├─ stats/
├─ weekly_markdown/
```

如果你想把校准脚本单独放出来，也可以加：

```text
scripts/
├─ run_validation.py
├─ compare_calibration_runs.py
```

---

# 七、第二阶段的 DSL 怎么设计

新增 `contexts.yaml` 即可，先保持简单。

## `dsl/contexts.yaml` 初稿结构

```yaml
version: "0.1"
dsl_type: contexts

contexts:
  - id: offense
    label: Offense
    rules:
      - id: ctx_off_01
        when: "market.market_regime.label == '成长进攻市'"
        score: 3
        evidence: 成长进攻市成立

      - id: ctx_off_02
        when: "len(market.top_positive) > 0"
        score: 1
        evidence: 存在显著正向信号

      - id: ctx_off_03
        when: "'成长风格占优' in market.relation_tags"
        score: 2
        evidence: 成长结构占优

    allowed_styles:
      - 趋势跟随
      - 高弹性进攻
    disallowed_styles:
      - 逆势抄底
    risk_budget:
      total_exposure: 0.8
      max_positions: 6
      max_single_name_weight: 0.2
```

其余：

* `caution`
* `defense`
* `cash`

同样写法。

---

# 八、第二阶段的代码新增顺序

按代码实现来说，最稳顺序是：

## 1. 扩 index / pair 配置

不改引擎

## 2. 写 `context_engine.py`

只消费 market runtime

## 3. 改 `pipeline.py`

让它在 regime 后面再跑 context

## 4. 改 `output_writer.py`

把 context 加进 JSON/Markdown

## 5. 写 `validation_engine.py`

读区间结果做统计

## 6. 写 `reporting_engine.py`

生成 weekly

---

# 九、第二阶段的验收标准

第二阶段完成，不看代码量，只看这几个结果。

## 1. 8 指数核心面板跑通

## 2. 每日有 market_context

## 3. 每日输出 allowed/disallowed/risk_budget

## 4. 能对一年历史做 regime/context 分布统计

## 5. 能输出 regime/context 转移矩阵

## 6. 能生成 weekly markdown

## 7. 有明确校准流程，不再凭感觉改规则

---

# 十、我对第二阶段的直接建议

如果按实际项目推进，我建议你这样安排：

### 先做“第二阶段上半段”

也就是：

* 扩 8 指数
* 加 context
* 改日报输出

这部分最快见效。

### 再做“第二阶段下半段”

也就是：

* validation
* calibration
* weekly

这部分决定系统后面会不会失控。

---

# 十一、下一步怎么继续最合适

下一步最适合直接进入**第二阶段的具体代码设计**，不要再泛谈。

最自然的顺序是：

1. 我先给你 `dsl/contexts.yaml` 第一版
2. 再给你 `engine/context_engine.py`
3. 再告诉你怎么把它接进 `pipeline.py` 和 `output_writer.py`

这样你就能先把第二阶段最核心的“市场上下文引擎”落进去。
