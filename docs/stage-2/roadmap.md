---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Roadmap - Hotix Stage II

## 当前阶段结论

Stage II 的目标已经完成：Hotix 现在是一个通用市场分析引擎，能够针对不同组合类型输出一致但语境不同的 Markdown 报告。

当前 pipeline 重点链路：

```text
features → states → patterns → transitions → pair_features → pair_states →
relation_tags → salience → universes → market_profile → markdown_report
```

测试：76 passed, 3 deselected

---

## 已完成能力

1. **Salience v2** - 结构化显著性对象
2. **Universe Analysis** - 组合级别分析和截面 TOPN
3. **Market Profile** - 市场画像与关键结论汇总
4. **Report Templates** - 按组合类型输出专用语境
5. **Asset Registry** - 从 HotDX 配置加载指数/板块名称

---

## 当前边界

Hotix 当前只做：

- 市场结构识别
- 组合级别分析
- 组合类型化报告渲染

Hotix 当前不做：

- 预测
- 回测
- 仓位建议
- 交易执行
- 反馈校准闭环

---

## 阶段原则

1. **先保证分析语境准确** - 指数、ETF、个股、板块的报告要使用各自术语。
2. **先保证结果可读** - 报告中尽量显示真实名称，不只显示代码。
3. **先保证行为稳定** - 宽基指数和行业指数的 TOPN 规则要随样本量变化。
4. **每次变更都走 TDD** - 先加测试，再改实现。

---

## 后续建议

如果后续继续扩展，优先级建议如下：

1. 增加 ETF 和个股的真实数据源
2. 增加更完整的资产名称配置路径
3. 再考虑任何形式的验证、校准或反馈引擎
