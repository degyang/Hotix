---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Feedback Loop Design - Hotix

> 这是 Stage II 早期对反馈回路、验证与校准的设计记录。当前 Hotix 已收敛为通用市场分析与组合报告引擎，该设计仅作为历史参考保留。

## 1. 核心问题：描述性系统的判据困境

Hotix 是一个**描述性系统**：它描述"今天市场结构如何"，不是预测"明天市场怎么走"。

系统每天输出 `context = Cash`、`regime = 混沌市`、`breakout = forbidden`。这些标签描述的是当前的结构状态，不是对未来的断言。

**这带来一个根本问题：你怎么知道今天的描述是"对"的？**

预测系统的反馈很直接——预测涨，实际涨了就是对了。但描述系统没有这种判据。系统输出 `context = Cash`，你无法在当天验证这个标签是否"正确"，因为 Cash 描述的是"当前结构不支持进攻"，这个判断是否成立，当天市场不会给你答案。

更关键的是——**描述性系统的输出本身就是基于输入数据的统计结果**。系统从指数 CSV 中算出 features、states、tags、regime、context，每一步都是确定性的统计变换。从这个角度看，输出永远是"对的"——它忠实地反映了规则对数据的映射。

那问题到底在哪？

**问题不在"对不对"，而在"有没有用"。**

如果系统输出的标签和真实市场状态之间没有有意义的对应关系，那么标签只是命名，不是认知。具体来说：

1. 如果 Offense 日和 Cash 日的后续市场表现没有差异，标签就没有区分度，规则设定的阈值没有把真正不同的环境分开。
2. 如果 pipeline 前面说"所有指数都在跌"，后面却输出 regime = "成长进攻市"，标签就和前置证据矛盾，规则链存在逻辑漏洞。
3. 如果某个指数收盘价差 0.1% 就导致 context 从 Offense 翻到 Cash，标签就不稳定，规则阈值落在了噪声区。

这三个问题——**无区分度、不自洽、不稳定**——就是反馈的三层判据。

---

## 2. 反馈不是"验证输出正确性"，而是"验证输出有效性"

### 2.1 正确性 vs 有效性

| | 正确性 | 有效性 |
|---|--------|--------|
| 问的是 | 输出是否忠实反映了规则对数据的映射？ | 规则本身是否捕捉到了有意义的市场结构差异？ |
| 判据 | 确定性系统天然满足 | 需要外部证据 |
| 检查方式 | 单元测试、golden test | 一致性检查、区分度验证、稳定性检验 |

Hotix 的单元测试和 golden test 已经保证了正确性——给定的输入、给定的规则，输出一定是那个输出。

有效性是更高一层的问题：**规则本身是否值得存在？** 这才是反馈回路要回答的。

### 2.2 为什么统计描述本身不是反馈

如果 Validation Engine 只是输出"过去 250 天里，Cash 出现 180 天，Offense 出现 12 天"，这只是一个统计描述，不是反馈。

**反馈需要判据。** 没有判据，统计数字只是数字，你不知道 180:12 是"太多"还是"正好"。

判据从哪来？不是从系统内部来——系统内部只有规则和数据的映射，没有"应该怎样"的标准。判据只能从三个外部来源获取：

1. **逻辑一致性** — 来自系统内部各阶段的相互校验
2. **后续市场表现** — 来自现实世界对标签的事后验证
3. **对扰动的响应** — 来自"如果输入稍微不同，输出会怎样"的反事实检验

以下内容仅保留历史参考，不再代表当前阶段目标。

---

## 3. 第一层判据：内部一致性

### 3.1 原理

pipeline 是一条链式推断：features → states → patterns → transitions → pairs → relation_tags → salience → regimes → contexts → policies。

链条的每一层都依赖前一层的输出。如果某一层的结论和它所依赖的前置证据矛盾，说明规则链存在逻辑问题。

**关键点：一致性检查不需要外部数据，只需要检查 pipeline 内部各阶段输出之间是否自洽。**

### 3.2 具体检查项

| 检查项 | 不一致的信号 | 说明什么 |
|--------|------------|---------|
| regime 是"成长进攻市"但所有指数 trend_state = "down" | 评分规则可能被某个权重过大的指标主导 | regime scoring 的权重分配可能不合理 |
| relation_tags 为空但 top_positive 非空 | salience 和 relation_tags 的触发逻辑断裂 | pair 判定和 salience 判定可能基于不同维度的特征，没有桥接 |
| context = Offense 但 policy 中 breakout = forbidden | policy 规则和 context 规则的 when 条件覆盖了不同子集 | 两个 DSL 之间存在隐式冲突 |
| 前一天 Offense，第二天直接 Cash，中间没有经过 Caution | 规则对单日噪声过于敏感 | 转移路径不应该跨级跳跃 |

### 3.3 实现方式

```python
@dataclass
class Inconsistency:
    date: str
    check_id: str
    description: str
    evidence: dict
    suggested_fix: str | None

def consistency_check(payloads: list[dict]) -> list[Inconsistency]:
    """逐条检查每个 payload 内部和相邻 payload 之间的逻辑矛盾。"""
```

---

## 4. 第二层判据：区分度验证

### 4.1 原理

Hotix 的四个 context 标签（Offense / Caution / Defense / Cash）代表不同的市场环境。如果这些标签是有意义的，那么不同标签下的后续市场表现应该有统计上的显著差异。

**如果 Offense 日和 Cash 日的后续收益分布没有显著差异，说明标签没有区分度——规则设定的阈值没有把真正不同的市场环境分开。**

### 4.2 具体做法

```python
def compute_outcome_alignment(
    payloads: list[dict],
    return_data: pd.DataFrame,
    horizon: int = 5,
) -> pd.DataFrame:
    ...
```

### 4.3 区分度判据

**判据：相邻标签的后续收益分布应该有统计上的显著差异。**

### 4.4 数据来源

区分度验证不需要新的数据管道。当前 CSV 指数日线本身就可以提供后续收益。

---

## 5. 第三层判据：稳定性检验

### 5.1 原理

如果输入数据有一点点变化，系统的结论会不会翻转？

### 5.2 两种实现

#### 参数扫描法

```python
def sensitivity_analysis(...):
    ...
```

#### 数据噪声法

```python
def robustness_check(...):
    ...
```

---

## 6. 结论

这份设计记录保留的价值在于说明：为什么 Hotix 后来没有继续走反馈回路路线，而是先收敛到通用市场分析与组合报告。

---

Parent: [[10-Projects/Active/11.09 Hotix/Overview]]
