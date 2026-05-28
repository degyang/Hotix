# Hotix Documentation

> Hotix 是一个市场结构识别引擎，描述当前市场结构，不做预测、回测或交易建议。

## 🚀 快速开始

**新用户？** 从这里开始：[Quickstart.md](Quickstart.md)（5分钟上手）

## 📚 文档导航

### 当前文档（Current）

使用这些文档了解和使用当前系统：

- [Architecture](current/architecture.md) - 系统架构和模块设计
- [CLI Reference](current/cli.md) - 命令行使用指南
- [Data Contract](current/data.md) - 数据格式和接口
- [Development](current/development.md) - 开发、测试、部署指南
- [Deployment](current/deployment/) - 部署文档

### 设计文档（Design）

理解系统的设计理念和架构决策：

- [Requirements](design/requirements.md) - 需求设计和系统目标
- [DSL Specification](design/dsl-spec.md) - DSL 语法和规范
- [Schema Design](design/schema.md) - 数据结构设计
- [Salience Design](design/salience.md) - 显著性评分设计

### 实施记录（Implementation）

#### Stage I（已完成 ✅）

第一阶段构建了核心市场结构识别能力：

- Phase I: 核心引擎（features, states, patterns, salience, pairs, regimes）
- Phase II: 市场上下文（contexts）
- Phase III: 策略许可（policies）

详见：[stage-1/](stage-1/)

#### Stage II（已完成 ✅）

第二阶段已完成通用市场分析与组合报告能力：

- ✅ Salience v2: 结构化显著性
- ✅ Universe Analysis: 组合分析
- ✅ Market Profile: 市场画像
- ✅ Report Templates: 按组合类型输出 Markdown

详见：[stage-2/](stage-2/)

### 历史归档（Archive）

历史设计文档和详细实施记录：[archive/](archive/)

## 📊 当前状态

**包名**: `hotix`  
**命令**: `hotix --date YYYY-MM-DD --data-dir path/`  
**测试**: 76 passed, 3 deselected  
**最后更新**: 2026-05-28

## 🎯 文档约定

- ✅ = 已完成并在生产使用
- 🚧 = 正在开发中
- 📋 = 规划中
- 🗄️ = 已归档（历史参考）

## 🤝 贡献指南

更新文档时：
1. 在文档顶部标注最后更新日期
2. 使用状态标识（✅ 🚧 📋 🗄️）
3. 保持与代码的一致性
4. 更新相关的 README.md 索引
