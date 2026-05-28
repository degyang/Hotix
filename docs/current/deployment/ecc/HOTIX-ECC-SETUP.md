# Hotix 项目 — ECC 定制化部署指南

## 项目概况

- **项目名称**: Hotix
- **开发语言**: Python
- **开发方法**: Test-Driven Development (TDD)
- **协作模式**: Multi-Agent 协同
- **目标 IDE**: Claude Code
- **部署位置**: `~/.claude/`

---

## 定制化设计理念

基于您的需求（Python + TDD + Multi-Agent），ECC 将配置为：

### 1. Python 优先
- 语言规则: `rules/python/` (PEP 8, type hints, EAFP 模式)
- 模式技能: `skills/python-patterns/` (Pythonic  idioms, 数据结构, 并发)
- 测试技能: `skills/python-testing/` (pytest, fixtures, mocking, coverage)
- 审查代理: `agents/python-reviewer` (代码质量, 安全, 性能)

### 2. TDD 驱动
- 工作流技能: `skills/tdd-workflow/` (RED → GREEN → REFACTOR)
- 质量门禁: `workflow-quality` 模块 (80%+ coverage 要求)
- Git 钩子: 提交前自动运行测试, 验证覆盖率
- 阶段提交: RED 阶段 → GREEN 阶段 → Refactor 阶段, 每个阶段都有 commit evidence

### 3. Multi-Agent 编排
- 核心代理:
  - `planner` - 任务分解与规划
  - `code-reviewer` - 代码质量审查
  - `security-reviewer` - 安全检查
  - `tdd-guide` - TDD 流程引导
  - `architect` - 架构决策
- 代理间通信: 使用 `chief-of-staff` 进行任务分配
- 并行执行: 独立任务使用并行代理处理
- 循环监控: `loop-operator` 监控长时间运行的任务

---

## 安装计划

### 方案 A: 完整开发者配置（推荐）

```bash
cd /Users/mac/Developments/everything-claude-code

# 1. 生成 Hotix 项目的定制化安装计划
node scripts/install-plan.js \
  --profile developer \
  --add lang:python \
  --add capability:database \
  --add capability:security \
  --target claude \
  --output ~/Developments/Hotix/ecc-install-plan.json

# 2. 查看安装计划
cat ~/Developments/Hotix/ecc-install-plan.json

# 3. 执行安装
node scripts/install-apply.js \
  --plan ~/Developments/Hotix/ecc-install-plan.json \
  --target-dir ~/.claude

# 4. 验证安装
node scripts/list-installed.js --target claude --json
```

**安装内容**:
- Baseline: rules-core, agents-core, commands-core, hooks-runtime, platform-configs, workflow-quality
- Language: framework-language (包含 Python/Django 支持)
- Database: 数据库模式与迁移技能
- Security: 安全审查技能
- Orchestration: 多代理编排命令

---

### 方案 B: 最小核心 + 按需扩展

```bash
# 1. 先安装核心
node scripts/install-apply.js --profile core --target claude

# 2. 添加 Python 特定组件
node scripts/install-apply.js --add rules/python --target claude
node scripts/install-apply.js --add skills/python-patterns --target claude
node scripts/install-apply.js --add skills/python-testing --target claude
node scripts/install-apply.js --add skills/tdd-workflow --target claude

# 3. 添加核心代理
node scripts/install-apply.js \
  --add agents/planner \
  --add agents/code-reviewer \
  --add agents/security-reviewer \
  --add agents/tdd-guide \
  --add agents/architect \
  --target claude

# 4. 添加多代理编排能力
node scripts/install-apply.js \
  --add agents/chief-of-staff \
  --add agents/loop-operator \
  --add agents/harness-optimizer \
  --target claude
```

---

## 项目级配置

### CLAUDE.md（项目根目录）

在 `~/Developments/Hotix/CLAUDE.md` 中配置项目特定的规则：

```markdown
# Hotix 项目配置

## 开发栈
- 语言: Python 3.11+
- 测试: pytest + pytest-cov
- 覆盖率: 80% minimum
- 类型检查: mypy
- 代码质量: ruff (lint) + black (format)
- 依赖管理: uv 或 poetry

## TDD 工作流
1. 写测试 (RED) → 提交: `test: add reproducer for <feature>`
2. 实现代码 (GREEN) → 提交: `fix: <feature or bug>`
3. 重构 (REFACTOR) → 提交: `refactor: clean up <feature>`

## Multi-Agent 策略
- 复杂任务 → planner 分解为子任务
- 代码编写 → tdd-guide 引导 TDD
- 代码审查 → code-reviewer + security-reviewer 并行审查
- 架构决策 → architect 提供咨询
- 任务协调 → chief-of-staff 分配并跟踪进度

## 代理激活规则
- 自动激活: 代码修改后立即 code-reviewer
- 自动激活: 复杂任务开始时 planner
- 自动激活: 安全敏感代码 security-reviewer
- 手动调用: /tdd, /plan, /code-review, /security-review
```

---

### Git 钩子增强

在 Hotix 项目根目录创建 `.git/hooks/` 配置：

```bash
# pre-commit: 运行测试 + 覆盖率检查 + lint
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pytest with coverage..."
pytest --cov=hotix --cov-report=term-missing --cov-fail-under=80
if [ $? -ne 0 ]; then
  echo "❌ Tests failed or coverage < 80%"
  exit 1
fi

echo "Running ruff lint..."
ruff check .
if [ $? -ne 0 ]; then
  echo "❌ Lint failed"
  exit 1
fi

echo "✅ Pre-commit checks passed"
EOF
chmod +x .git/hooks/pre-commit
```

---

## 技能定制

### 增强的 Python Testing Skill

在 `~/.claude/skills/hotix-python-testing/SKILL.md` 创建项目特定的测试规范：

```markdown
---
name: hotix-python-testing
description: Hotix 项目专用的 Python 测试策略：pytest fixtures, factory-boy, testcontainers 集成, 覆盖率 80%+.
origin: custom
---

# Hotix Python Testing Standards

## 测试目录结构
```
tests/
├── conftest.py              # 全局 fixtures
├── unit/                    # 单元测试
│   ├── test_models.py
│   └── test_services.py
├── integration/             # 集成测试
│   ├── test_api.py
│   └── test_database.py
├── e2e/                    # 端到端测试
│   └── test_workflows.py
└── factories.py            # 测试数据工厂
```

## 核心原则
1. 每个测试都是独立的，无状态
2. 使用 fixtures 注入依赖
3. 单元测试 < 100ms, 集成测试 < 500ms
4. Mock 外部服务 (数据库, API, 文件系统)
5. 使用 parametrize 测试多组输入
```

---

## Multi-Agent 协作模式

### 任务分解流程

```
用户需求: "实现用户注册 API 端点"

1. planner → 分解任务:
   - 设计用户模型 (User model)
   - 设计注册请求/响应 DTO
   - 实现密码哈希逻辑
   - 编写单元测试 (TDD)
   - 实现 API 端点
   - 编写集成测试
   - 代码审查

2. tdd-guide → 引导 TDD 循环:
   - RED: 写失败的注册测试
   - GREEN: 实现最小注册逻辑
   - REFACTOR: 清理代码

3. code-reviewer → 审查代码质量
4. security-reviewer → 检查密码存储、输入验证
5. chief-of-staff → 协调任务进度
```

### 并行执行策略

```bash
# 独立任务可并行处理
# 示例: 同时审查代码 + 运行测试 + 安全检查
# 使用 /multi-execute 或 /multi-frontend
```

---

## 验证安装

```bash
# 1. 检查已安装组件
node ~/Developments/everything-claude-code/scripts/list-installed.js \
  --target claude \
  --json | jq '.installed | map(select(.family | contains("python") or contains("tdd")))'

# 2. 运行诊断
node ~/Developments/everything-claude-code/scripts/doctor.js \
  --target claude

# 3. 查看状态
node ~/Developments/everything-claude-code/scripts/status.js \
  --target claude
```

---

## 使用示例

### 在 Hotix 项目中使用 Claude Code

```bash
cd ~/Developments/Hotix

# 1. 启动 Claude Code（已自动加载 Hotix 配置）
claude .

# 2. 创建新功能 - TDD 模式
> /tdd
> 我需要一个用户注册 API 端点，支持邮箱验证

# Claude 会自动:
# - 激活 python-testing skill
# - 调用 tdd-guide agent
# - 生成测试用例
# - 实现代码
# - 运行测试验证

# 3. 代码审查
> /code-review
> 请审查 src/hotix/auth/service.py

# 4. 安全检查
> /security-review
> 检查用户密码存储逻辑

# 5. 架构咨询
> /plan
> 设计一个事件驱动的通知系统
```

---

## 维护与更新

### 更新 ECC 组件

```bash
cd ~/Developments/everything-claude-code

# 拉取最新版本
git pull origin main

# 重新运行安装计划（保留现有配置）
node scripts/install-apply.js \
  --plan ~/Developments/Hotix/ecc-install-plan.json \
  --target-dir ~/.claude \
  --dry-run  # 先预览变更

# 确认无误后执行
node scripts/install-apply.js \
  --plan ~/Developments/Hotix/ecc-install-plan.json \
  --target-dir ~/.claude
```

### 添加新技能

```bash
# 发现可用的 Python 相关技能
node scripts/catalog.js components --family language

# 添加到 Hotix
node scripts/install-apply.js \
  --add skills/django-patterns \
  --target claude
```

---

## 故障排除

### 问题: 代理未激活
```bash
# 检查 AGENTS.md 是否存在
ls ~/.claude/AGENTS.md

# 重新安装 agents-core
node scripts/install-apply.js --add agents-core --target claude
```

### 问题: TDD 技能不生效
```bash
# 验证 tdd-workflow skill 已安装
ls ~/.claude/skills/tdd-workflow/

# 重新安装 workflow-quality
node scripts/install-apply.js --add workflow-quality --target claude
```

### 问题: Python 规则未应用
```bash
# 检查 Python 规则文件
ls ~/.claude/rules/python/

# 重新安装 framework-language 模块
node scripts/install-apply.js --add framework-language --target claude
```

---

## 下一步

1. ✅ 运行安装脚本（见下方）
2. ✅ 在 Hotix 项目根目录创建 `CLAUDE.md`
3. ✅ 配置 Git 钩子
4. ✅ 初始化 pytest + coverage 配置
5. ✅ 开始第一个 TDD 迭代

---

## 快速开始命令

```bash
# 一键部署（方案 A）
cd ~/Developments/everything-claude-code
chmod +x scripts/install-apply.js scripts/install-plan.js

# 生成计划
node scripts/install-plan.js \
  --profile developer \
  --add lang:python \
  --add capability:database \
  --add capability:security \
  --target claude \
  --output ~/Developments/Hotix/ecc-plan.json

# 执行安装
node scripts/install-apply.js \
  --plan ~/Developments/Hotix/ecc-plan.json \
  --target-dir ~/.claude

# 验证
node scripts/list-installed.js --target claude | grep -E "(python|tdd|agent)"
```

---

**准备就绪后, 在 Hotix 目录运行 `claude .` 开始开发！**
