# 当前有效文档

> 这些文档描述 Hotix 的当前状态和使用方法

## 核心文档

| 文档 | 说明 | 最后更新 |
|------|------|---------|
| [architecture.md](architecture.md) | 系统架构、模块设计、pipeline 流程 | 2026-05-28 |
| [cli.md](cli.md) | 命令行选项、输出格式 | 2026-05-28 |
| [data.md](data.md) | CSV 格式、registry 配置 | 2026-05-28 |
| [development.md](development.md) | 测试、linting、变更流程 | 2026-05-28 |

## 部署文档

- [deployment/ecc/](deployment/ecc/) - ECC 环境部署指南

## 使用指南

### 对新手
1. 先看 [../Quickstart.md](../Quickstart.md)
2. 再看 [cli.md](cli.md) 了解命令选项
3. 查看 [data.md](data.md) 了解数据格式

### 对开发者
1. 先看 [architecture.md](architecture.md) 了解系统设计
2. 再看 [development.md](development.md) 了解开发流程
3. 参考 [../design/](../design/) 了解设计理念

### 对 Agent
- 快速定位：所有当前有效信息都在这个目录
- 状态明确：这些文档反映 `main` 分支的当前状态
- 优先级：如果文档与代码不一致，以代码为准

## 注意事项

⚠️ 这些文档应与 `main` 分支代码保持同步。如发现不一致，请提 issue。
