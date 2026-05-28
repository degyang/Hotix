---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Report Templates

## 目标

为不同组合类型提供对应的 Markdown 语境，让同一套分析内核可以服务于指数、ETF、个股、板块和混合样本。

## 已实现内容

- 根据 `universe.type` 选择模板
- `index_panel` 兼容归一为 `index`
- sector 报告使用“板块结构日报 / 板块轮动分析 / 板块状态概览”
- 非 index 报告会把部分文案按组合类型进行语境替换
- 报告名称通过 HotDX 配置读取并展示中文名称

## 相关实现

- `src/hotix/engine/report_templates.py`
- `src/hotix/engine/output_writer.py`
- `src/hotix/engine/asset_registry.py`

## 结果

stage-2 的报告模板层已经完成，当前可直接支持真实的指数和行业指数数据输出更可读的 Markdown 报告。

---

Parent: [[10-Projects/Active/11.09 Hotix/Overview]]
