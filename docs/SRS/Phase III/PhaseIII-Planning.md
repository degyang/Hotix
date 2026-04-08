# Phase III 功能规划

## 当前实现状态总结

### 已完成模块

#### Phase I - 核心引擎
- ✅ 8个核心指数面板（上证指数、深证成指、上证50、沪深300、中证500、创业板指、中证1000、科创综指）
- ✅ Feature Engine（特征计算引擎）
- ✅ State Engine（状态离散化引擎）
- ✅ Pattern Engine（模式识别引擎）
- ✅ Transition Engine（状态切换识别）
- ✅ Salience Engine（显著性评分引擎）
- ✅ Pair Engine（指数对比较引擎）
- ✅ Regime Engine（市场结构分类引擎）
- ✅ 完整的 DSL 系统（features/states/patterns/transitions/salience/pairs/regimes）
- ✅ 基础的 JSON/Markdown 输出

#### Phase II - 市场上下文引擎
- ✅ Context Engine（交易环境约束引擎）
- ✅ 四档交易环境分类（Offense/Caution/Defense/Cash）
- ✅ 交易约束输出（allowed_styles/disallowed_styles/risk_budget）
- ✅ Context 证据追踪

### 系统架构特点

系统遵循"规则引擎主导判断，LLM 负责解释"的设计原则：
- 所有判断逻辑由规则引擎完成
- 结果完全可追溯、可复盘
- LLM 仅用于语言润色（尚未实现）

---

## Phase III 功能规划

### 规划原则

1. **稳定性优先**：在扩展新功能前，先确保现有系统稳定可靠
2. **可验证性**：所有新功能必须可验证、可校准
3. **渐进式扩展**：不追求一次性完美，而是逐步迭代
4. **保持边界**：明确每个模块的职责，避免功能混乱

---

## 功能模块详细规划

### 模块 1：Validation & Calibration Engine（验证与校准引擎）

**优先级：🔴 高（立即开始）**

#### 目标
建立规则验证与校准机制，防止规则系统失控，确保判断质量的长期稳定性。

#### 核心问题
- 如何知道规则是否合理？
- 如何发现规则失效？
- 如何系统化地修订规则？
- 如何评估规则修改的影响？

#### 具体功能

##### 1.1 历史回放统计
```yaml
功能：
  - 对历史区间批量回放
  - 统计各 regime 出现频率
  - 统计各 context 出现频率
  - 统计各 tag 命中频率
  - 识别异常分布（如某个 regime 占比过高）

输出：
  - regime_distribution.csv
  - context_distribution.csv
  - tag_frequency.csv
  - anomaly_report.md
```

##### 1.2 转移矩阵分析
```yaml
功能：
  - 计算 regime 转移概率矩阵
  - 计算 context 转移概率矩阵
  - 识别常见转移路径
  - 识别异常转移（如从 Offense 直接到 Cash）

输出：
  - regime_transition_matrix.csv
  - context_transition_matrix.csv
  - transition_patterns.json
```

##### 1.3 规则命中分析
```yaml
功能：
  - 统计每条规则的命中率
  - 识别从不命中的规则（可能需要删除）
  - 识别总是命中的规则（可能阈值过宽）
  - 分析规则之间的相关性

输出：
  - rule_hit_stats.csv
  - unused_rules.txt
  - always_hit_rules.txt
```

##### 1.4 错判样本复盘
```yaml
功能：
  - 标记明显错判的日期
  - 追踪错判原因（哪个规则、哪个阈值）
  - 生成详细的 trace 报告
  - 建议修订方向

输出：
  - misjudgment_cases.json
  - trace_reports/YYYY-MM-DD.md
```

##### 1.5 阈值修订流程
```yaml
功能：
  - 记录每次规则修改
  - 对比修改前后的分布变化
  - 生成修改影响报告
  - 维护修改历史

输出：
  - calibration_notes.md
  - calibration_runs/run_YYYYMMDD_HHMMSS/
    - before_stats.json
    - after_stats.json
    - diff_report.md
```

#### 落地文件
```text
engine/
  validation_engine.py

scripts/
  run_validation.py
  compare_calibration_runs.py

outputs/
  stats/
    regime_distribution.csv
    context_distribution.csv
    tag_frequency.csv
    regime_transition_matrix.csv
    context_transition_matrix.csv
    rule_hit_stats.csv
  calibration_runs/
  misjudgment_cases/

config/
  calibration_notes.md
```

#### 验收标准
- [ ] 能对任意历史区间生成分布统计
- [ ] 能输出 regime/context 转移矩阵
- [ ] 能识别从不命中的规则
- [ ] 能对比规则修改前后的影响
- [ ] 有明确的校准流程文档

---

### 模块 2：Weekly Reporting（周报系统）

**优先级：🟡 中（近期规划）**

#### 目标
聚合日度结果，提供周度视角的市场结构分析，帮助识别中期趋势和结构变化。

#### 核心问题
- 本周市场结构如何演变？
- 哪些信号持续出现？
- 哪天是关键转折点？
- 下周应该关注什么？

#### 具体功能

##### 2.1 周度聚合
```yaml
功能：
  - 聚合一周的日度结果
  - 统计本周 regime/context 序列
  - 识别主导 regime/context
  - 计算稳定性指标

输出：
  - weekly_summary.json
```

##### 2.2 信号频率分析
```yaml
功能：
  - 统计本周最常见的正向信号
  - 统计本周最常见的负向信号
  - 统计本周最常见的预警信号
  - 识别持续性信号 vs 一次性信号

输出：
  - weekly_signal_frequency.json
```

##### 2.3 转折点识别
```yaml
功能：
  - 识别 regime 切换日
  - 识别 context 切换日
  - 识别显著性突变日
  - 评估转折点的重要性

输出：
  - weekly_turning_points.json
```

##### 2.4 下周展望
```yaml
功能：
  - 基于本周结束状态
  - 基于转移概率
  - 给出下周初始观察重点
  - 给出需要警惕的风险点

输出：
  - weekly_outlook.md
```

##### 2.5 周报生成
```yaml
功能：
  - 自动生成周报 Markdown
  - 包含本周回顾、关键转折、下周展望
  - 不依赖 LLM，纯模板化

输出：
  - weekly_reports/YYYY-WW.md
```

#### 落地文件
```text
engine/
  reporting_engine.py

outputs/
  weekly_markdown/
    YYYY-WW.md
  weekly_json/
    YYYY-WW.json
```

#### 验收标准
- [ ] 能自动生成周报
- [ ] 周报包含本周 regime/context 序列
- [ ] 周报包含关键转折点
- [ ] 周报包含下周观察重点
- [ ] 周报格式稳定、可读

---

### 模块 3：Debug & Trace Enhancement（调试增强）

**优先级：🟡 中（近期规划）**

#### 目标
提升系统可解释性，让用户能够快速理解任何一个判断是如何得出的。

#### 核心问题
- 为什么今天是这个 regime？
- 为什么某个指数显著性高？
- 如果某个阈值改变会怎样？
- 哪些规则对最终结果影响最大？

#### 具体功能

##### 3.1 增强的 Explain 模式
```yaml
功能：
  - 对任意日期、任意对象生成详细解释
  - 显示所有中间计算结果
  - 显示所有规则命中情况
  - 显示依赖链路

命令：
  python run_daily.py --date 2026-04-05 --explain hs300
  python run_daily.py --date 2026-04-05 --explain-regime
  python run_daily.py --date 2026-04-05 --explain-context
```

##### 3.2 规则命中可视化
```yaml
功能：
  - 生成规则命中热力图
  - 显示哪些规则经常一起命中
  - 显示规则之间的依赖关系
  - 识别冗余规则

输出：
  - rule_heatmap.html
  - rule_dependency_graph.json
```

##### 3.3 阈值敏感性分析
```yaml
功能：
  - 对某个阈值进行扫描
  - 显示不同阈值下的结果分布
  - 帮助找到最优阈值
  - 识别敏感阈值 vs 稳定阈值

命令：
  python scripts/threshold_sensitivity.py \
    --rule volume_state \
    --param amount_ratio_threshold \
    --range 0.6-1.0 \
    --step 0.05
```

##### 3.4 反事实分析
```yaml
功能：
  - "如果某个规则不存在，结果会怎样？"
  - "如果某个阈值改变，结果会怎样？"
  - 评估单个规则的影响力
  - 识别关键规则

命令：
  python scripts/counterfactual.py \
    --date 2026-04-05 \
    --remove-rule p_high_volume_divergence
```

#### 落地文件
```text
scripts/
  explain_detail.py
  threshold_sensitivity.py
  counterfactual.py
  rule_visualization.py

outputs/
  debug/
    explain_reports/
    sensitivity_analysis/
    counterfactual_results/
```

#### 验收标准
- [ ] explain 模式能显示完整计算链路
- [ ] 能对任意阈值做敏感性分析
- [ ] 能做反事实分析
- [ ] 能生成规则依赖图

---

### 模块 4：行业板块层（Phase III 准备）

**优先级：🟢 中低（中期规划）**

#### 目标
从指数层面扩展到行业板块层面，识别行业轮动和行业相对强弱。

#### 核心问题
- 哪些行业在领涨？
- 哪些行业在领跌？
- 行业轮动是否健康？
- 行业表现与指数结构是否一致？

#### 具体功能

##### 4.1 行业数据接入
```yaml
功能：
  - 定义行业分类体系（如申万一级）
  - 接入行业指数数据
  - 标准化行业数据格式
  - 建立行业 registry

文件：
  config/sector_registry.yaml
  data/raw/sectors/
```

##### 4.2 行业特征计算
```yaml
功能：
  - 复用 feature engine
  - 计算行业级别的 features/states
  - 不需要重新发明，直接套用指数层逻辑

输出：
  - 行业级别的 features/states
```

##### 4.3 行业相对强弱
```yaml
功能：
  - 行业 vs 指数的相对强弱
  - 行业 vs 行业的相对强弱
  - 识别领涨/领跌行业
  - 识别行业轮动模式

输出：
  - sector_relative_strength.json
  - sector_rotation_tags
```

##### 4.4 行业与指数关联
```yaml
功能：
  - 行业表现是否与指数结构一致
  - 例如：成长进攻市，科技行业是否领涨
  - 识别结构与行业的背离

输出：
  - sector_index_alignment.json
```

#### 落地文件
```text
config/
  sector_registry.yaml

dsl/
  sector_features.yaml
  sector_states.yaml
  sector_patterns.yaml

engine/
  sector_engine.py

outputs/
  sectors/
```

#### 验收标准
- [ ] 能接入行业数据
- [ ] 能计算行业特征和状态
- [ ] 能识别领涨/领跌行业
- [ ] 能分析行业与指数的一致性

---

### 模块 5：Setup & Signal Layer（交易信号层）

**优先级：🟢 中低（中期规划）**

#### 目标
从市场结构识别到具体交易机会，将 market context 转化为可执行的交易信号。

#### 核心问题
- 当前环境下，什么样的 setup 是允许的？
- 哪些个股符合当前的 setup 定义？
- 信号质量如何评分？
- 如何与 market context 的约束匹配？

#### 具体功能

##### 5.1 Setup 定义
```yaml
功能：
  - 定义各类 setup（如趋势跟随、突破、反转）
  - 每个 setup 有明确的触发条件
  - 每个 setup 有适用的 market context
  - 每个 setup 有风险收益特征

文件：
  dsl/setups.yaml
```

##### 5.2 Setup 识别
```yaml
功能：
  - 在个股池中识别符合 setup 的标的
  - 评估 setup 质量
  - 检查是否符合当前 market context 约束

输出：
  - setup_candidates.json
```

##### 5.3 信号质量评分
```yaml
功能：
  - 基于历史表现评估 setup 质量
  - 基于当前市场环境调整评分
  - 考虑 setup 与 context 的匹配度

输出：
  - signal_scores.json
```

##### 5.4 候选池筛选
```yaml
功能：
  - 根据 market context 的 risk_budget
  - 筛选最优候选
  - 考虑分散度和相关性
  - 输出最终候选池

输出：
  - candidate_pool.json
```

#### 落地文件
```text
dsl/
  setups.yaml

engine/
  setup_engine.py
  signal_engine.py

outputs/
  signals/
    daily_setups.json
    candidate_pool.json
```

#### 验收标准
- [ ] 能定义和识别 setup
- [ ] 能评估信号质量
- [ ] 能根据 context 筛选候选
- [ ] 输出符合 risk_budget 约束

---

### 模块 6：LLM Narrative Layer（叙事层）

**优先级：🔵 低（长期规划）**

#### 目标
将结构化结果转化为自然语言洞察，提升可读性和传播性。

#### 核心问题
- 如何用自然语言描述市场结构？
- 如何归纳证据？
- 如何优化风险提示措辞？
- 如何保持语言风格一致？

#### 具体功能

##### 6.1 日报自动生成
```yaml
功能：
  - 基于结构化结果生成日报
  - 一句话市场结论
  - 三条关键证据
  - 风格判断
  - 交易含义
  - 风险提示

输入：
  - daily JSON output

输出：
  - narrative_daily.md
```

##### 6.2 证据归纳与排序
```yaml
功能：
  - 从多条证据中提取最重要的
  - 按重要性排序
  - 合并相似证据
  - 避免冗余

输出：
  - 精炼的证据列表
```

##### 6.3 风险提示优化
```yaml
功能：
  - 将技术性的 warning tags 转化为易懂的风险提示
  - 根据严重程度调整措辞
  - 保持专业但不过度技术化

输出：
  - 优化后的风险提示文本
```

##### 6.4 多语言支持
```yaml
功能：
  - 支持中英文输出
  - 保持术语一致性
  - 适应不同受众

输出：
  - 中英文日报
```

#### 落地文件
```text
engine/
  narrative_engine.py

prompts/
  daily_summary_prompt.md
  evidence_ranking_prompt.md
  risk_warning_prompt.md

outputs/
  narrative/
    daily/
    weekly/
```

#### 验收标准
- [ ] 能生成自然语言日报
- [ ] 语言风格稳定
- [ ] 不改变结构化判断
- [ ] 支持中英文

---

### 模块 7：Performance Tracking（表现追踪）

**优先级：🔵 低（长期规划）**

#### 目标
评估系统判断质量，识别改进方向，形成自我优化能力。

#### 核心问题
- Regime 预测准确吗？
- Context 切换是否有前瞻性？
- 哪些信号最有效？
- 系统在哪些情况下容易出错？

#### 具体功能

##### 7.1 Regime 预测准确率
```yaml
功能：
  - 评估 regime 分类的稳定性
  - 计算 regime 持续时间
  - 识别频繁切换的时期（可能是误判）
  - 评估 regime 与后续市场表现的一致性

输出：
  - regime_accuracy_report.json
```

##### 7.2 Context 前瞻性评估
```yaml
功能：
  - 评估 context 切换的时机
  - 是否提前识别风险？
  - 是否及时捕捉机会？
  - 计算 context 与后续收益的相关性

输出：
  - context_foresight_report.json
```

##### 7.3 信号有效性回测
```yaml
功能：
  - 对各类 pattern/transition 做有效性回测
  - 计算信号出现后的平均表现
  - 识别高质量信号 vs 低质量信号
  - 建议保留/删除/修改哪些规则

输出：
  - signal_effectiveness_report.json
```

##### 7.4 系统改进建议
```yaml
功能：
  - 基于表现追踪结果
  - 自动生成改进建议
  - 识别系统弱点
  - 建议下一步优化方向

输出：
  - improvement_suggestions.md
```

#### 落地文件
```text
engine/
  performance_engine.py

scripts/
  backtest_signals.py
  evaluate_regime_accuracy.py

outputs/
  performance/
    regime_accuracy/
    context_foresight/
    signal_effectiveness/
```

#### 验收标准
- [ ] 能评估 regime 准确率
- [ ] 能评估 context 前瞻性
- [ ] 能回测信号有效性
- [ ] 能生成改进建议

---

## 实施顺序建议

### 第一阶段（立即开始）
**目标：建立验证与校准能力**

1. **Validation Engine**
   - 历史回放统计
   - 转移矩阵分析
   - 规则命中分析
   - 预计时间：2-3周

### 第二阶段（近期规划，1-2个月内）
**目标：提升日常使用体验**

2. **Weekly Reporting**
   - 周度聚合
   - 周报生成
   - 预计时间：1-2周

3. **Debug Enhancement**
   - 增强 explain 模式
   - 阈值敏感性分析
   - 预计时间：2周

### 第三阶段（中期规划，3-6个月内）
**目标：扩展分析维度**

4. **行业板块层**
   - 行业数据接入
   - 行业相对强弱
   - 预计时间：3-4周

5. **Setup & Signal Layer**
   - Setup 定义与识别
   - 信号质量评分
   - 预计时间：4-6周

### 第四阶段（长期规划，6个月以上）
**目标：提升可读性和自我优化能力**

6. **LLM Narrative Layer**
   - 日报自动生成
   - 证据归纳
   - 预计时间：2-3周

7. **Performance Tracking**
   - 准确率评估
   - 有效性回测
   - 预计时间：3-4周

---

## 关键原则

### 1. 稳定性优先
在扩展新功能前，先确保现有系统稳定可靠。Validation Engine 是第一优先级。

### 2. 渐进式迭代
不追求一次性完美，每个模块先做最小可用版本，然后根据实际使用反馈迭代。

### 3. 保持边界清晰
- 规则引擎负责判断
- LLM 负责解释
- 不混淆职责

### 4. 可验证性
所有新功能必须可验证、可追溯、可复盘。

### 5. 文档先行
每个新模块开始前，先写设计文档，明确目标、功能、验收标准。

---

## 风险与挑战

### 技术风险
1. **数据质量**：行业数据、个股数据的质量和完整性
2. **性能问题**：随着数据量增加，计算性能可能成为瓶颈
3. **规则复杂度**：规则越多，维护成本越高

### 应对措施
1. 建立数据质量检查机制
2. 优化计算逻辑，考虑增量计算
3. 定期清理冗余规则，保持系统简洁

### 业务风险
1. **过度拟合**：规则过度优化历史数据，失去泛化能力
2. **判断失效**：市场环境变化导致规则失效
3. **依赖性**：过度依赖系统判断，忽视人工判断

### 应对措施
1. 通过 Validation Engine 持续监控规则表现
2. 定期校准，及时调整
3. 系统作为辅助工具，不替代人工判断

---

## 成功标准

Phase III 完成后，系统应该达到：

### 功能完整性
- ✅ 从指数到行业到个股的完整分析链路
- ✅ 从市场结构到交易信号的完整转化
- ✅ 从判断到解释的完整输出

### 可靠性
- ✅ 有完善的验证与校准机制
- ✅ 判断质量可追踪、可评估
- ✅ 系统表现可持续改进

### 可用性
- ✅ 日报、周报自动生成
- ✅ 调试工具完善
- ✅ 文档齐全

### 可扩展性
- ✅ 新增规则流程清晰
- ✅ 新增对象类型容易
- ✅ 系统架构稳定

---

## 下一步行动

### 立即行动（本周）
1. 创建 `engine/validation_engine.py` 骨架
2. 实现基础的历史回放统计功能
3. 输出第一版 regime/context 分布报告

### 近期行动（本月）
1. 完善 Validation Engine 全部功能
2. 建立校准流程文档
3. 对最近一年数据做全面验证

### 中期行动（下季度）
1. 实现 Weekly Reporting
2. 增强 Debug 工具
3. 开始规划行业板块层

---

## 附录：参考文档

- Phase I Design: `docs/SRS/Phase I/Phase-I-Design.md`
- Phase II Requirements: `docs/SRS/Phase II/PhaseII-1Requiement.md`
- Phase II Core: `docs/SRS/Phase II/PhaseII-2Core.md`
- DSL Design: `docs/SRS/TOS-Trading Engine DSL.md`
- Parser Design: `docs/SRS/Parser和Evaluator设计草案.md`

---

**文档版本：** v1.0  
**创建日期：** 2026-04-08  
**最后更新：** 2026-04-08  
**负责人：** System Architect
