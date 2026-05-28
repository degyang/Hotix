#!/bin/bash
###############################################################################
# Hotix 项目本地 ECC 部署脚本
# 作用: 将 Everything Claude Code 组件安装到项目目录 (.claude/)
# 特点: 项目级配置, 可版本控制, 团队共享
###############################################################################

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 路径配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ECC_REPO="${ECC_REPO:-$HOME/Developments/everything-claude-code}"
TARGET_DIR="$PROJECT_ROOT/.claude"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Hotix 项目级 ECC 部署 — 本地 .claude 配置              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}项目目录: ${PROJECT_ROOT}${NC}"
echo -e "${CYAN}目标目录: ${TARGET_DIR}${NC}"
echo -e "${CYAN}ECC 仓库: ${ECC_REPO}${NC}"
echo ""

# 检查 ECC 仓库
if [ ! -d "$ECC_REPO" ]; then
  echo -e "${RED}❌ 未找到 ECC 仓库: $ECC_REPO${NC}"
  echo -e "${YELLOW}请设置 ECC_REPO 环境变量或克隆仓库:${NC}"
  echo "   git clone https://github.com/affaan-m/everything-claude-code $ECC_REPO"
  exit 1
fi

# 创建目标目录结构
echo -e "${YELLOW}📁 步骤 1/7: 创建 .claude 目录结构${NC}"
mkdir -p "$TARGET_DIR"/{skills,agents,rules,commands,hooks,contexts,mcp-configs}

# 复制/符号链接核心配置文件
echo -e "${YELLOW}📋 步骤 2/7: 部署配置文件${NC}"

# 项目级配置
cp "$PROJECT_ROOT/.ecc-config.json" "$TARGET_DIR/project-config.json" 2>/dev/null || true

# 创建项目级 AGENTS.md
cat > "$TARGET_DIR/AGENTS.md" << 'AGENTS_EOF'
# Hotix 项目代理配置

## 自动激活代理

### 编码阶段
- **code-reviewer**: 每次代码修改后自动激活, 审查代码质量
- **security-reviewer**: 检测到安全敏感代码时自动激活

### 任务阶段
- **planner**: 复杂任务开始时自动激活, 分解为子任务
- **tdd-guide**: 测试驱动开发引导
- **architect**: 架构决策咨询

### 协调阶段
- **chief-of-staff**: 多代理任务协调
- **loop-operator**: 长时间任务监控

## 手动调用

| 命令 | 代理 | 用途 |
|-------|------|------|
| `/tdd` | tdd-guide | 启动 TDD 工作流 |
| `/plan` | planner | 任务分解 |
| `/code-review` | code-reviewer | 代码审查 |
| `/security-review` | security-reviewer | 安全检查 |
| `/architect` | architect | 架构咨询 |
| `/build-fix` | build-error-resolver | 修复构建错误 |

## Python 特定代理

- **python-reviewer**: Python 代码审查专家 (PEP 8, typing, idioms)
- **tdd-guide**: TDD 流程引导 (RED → GREEN → REFACTOR)
- **security-reviewer**: 安全漏洞检测 (SQLi, XSS, secrets)

## 并行执行策略

独立任务使用并行执行:
- 代码审查 + 测试运行 + 安全检查 可同时进行
- 使用 `/multi-execute` 或 `/multi-frontend`

AGENTS_EOF
echo -e "${GREEN}✓ AGENTS.md 已部署${NC}"

# 步骤 3: 复制技能 (从 ECC 仓库)
echo -e "${YELLOW}🎯 步骤 3/7: 部署技能 (Skills)${NC}"

# 核心工作流技能
ESSENTIAL_SKILLS=(
  "tdd-workflow"
  "python-testing"
  "python-patterns"
  "codebase-onboarding"
  "e2e-testing"
  "verification-loop"
  "autonomous-loops"
  "agentic-engineering"
)

for skill in "${ESSENTIAL_SKILLS[@]}"; do
  SRC="$ECC_REPO/skills/$skill"
  DEST="$TARGET_DIR/skills/$skill"

  if [ -d "$SRC" ]; then
    mkdir -p "$DEST"
    # 复制所有 .md 文件
    find "$SRC" -name "*.md" -exec cp {} "$DEST" \; 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} skills/$skill"
  else
    echo -e "  ${YELLOW}⚠️  $skill 未找到 (跳过)${NC}"
  fi
done

# 额外 Python 技能 (可选)
OPTIONAL_SKILLS=(
  "django-patterns"
  "django-tdd"
  "django-security"
  "postgres-patterns"
  "docker-patterns"
)

echo ""
echo -e "${CYAN}可选技能 (如需则安装):${NC}"
for skill in "${OPTIONAL_SKILLS[@]}"; do
  if [ -d "$ECC_REPO/skills/$skill" ]; then
    echo -e "  ${YELLOW}○${NC} $skill (运行 --add skills/$skill 安装)"
  fi
done

# 步骤 4: 复制代理 (Agents)
echo ""
echo -e "${YELLOW}🤖 步骤 4/7: 部署代理 (Agents)${NC}"

CORE_AGENTS=(
  "python-reviewer"
  "code-reviewer"
  "security-reviewer"
  "tdd-guide"
  "planner"
  "architect"
  "refactor-cleaner"
  "docs-lookup"
  "build-error-resolver"
  "chief-of-staff"
  "loop-operator"
  "harness-optimizer"
  "performance-optimizer"
  "database-reviewer"
  "e2e-runner"
)

for agent in "${CORE_AGENTS[@]}"; do
  SRC="$ECC_REPO/agents/$agent.md"
  DEST="$TARGET_DIR/agents/$agent.md"

  if [ -f "$SRC" ]; then
    cp "$SRC" "$DEST"
    echo -e "  ${GREEN}✓${NC} agents/$agent.md"
  else
    echo -e "  ${YELLOW}⚠️  $agent.md 未找到${NC}"
  fi
done

# 步骤 5: 复制规则 (Rules)
echo ""
echo -e "${YELLOW}📜 步骤 5/7: 部署规则 (Rules)${NC}"

# Python 规则
if [ -d "$ECC_REPO/rules/python" ]; then
  cp -r "$ECC_REPO/rules/python"/* "$TARGET_DIR/rules/" 2>/dev/null || true
  echo -e "  ${GREEN}✓${NC} rules/python/ (PEP 8, patterns, security, testing, hooks)"
fi

# 通用规则
COMMON_RULES=(
  "common-coding-style"
  "common-security"
  "common-testing"
  "common-git-workflow"
  "common-agents"
  "common-patterns"
  "common-hooks"
  "common-development-workflow"
)

for rule in "${COMMON_RULES[@]}"; do
  SRC="$ECC_REPO/rules/common/$rule.md"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$TARGET_DIR/rules/"
    echo -e "  ${GREEN}✓${NC} rules/$rule.md"
  fi
done

# 步骤 6: 复制命令 (Commands)
echo ""
echo -e "${YELLOW}⌨️  步骤 6/7: 部署命令 (Commands)${NC}"

ESSENTIAL_COMMANDS=(
  "tdd"
  "plan"
  "code-review"
  "build-fix"
  "quality-gate"
  "loop-start"
  "loop-status"
  "sessions"
  "save-session"
  "resume-session"
  "checkpoint"
  "prompt-optimize"
  "skill-create"
  "catalog"
)

for cmd in "${ESSENTIAL_COMMANDS[@]}"; do
  SRC="$ECC_REPO/commands/$cmd.md"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$TARGET_DIR/commands/"
    echo -e "  ${GREEN}✓${NC} /$cmd"
  fi
done

# 步骤 7: 复制钩子 (Hooks) 配置
echo ""
echo -e "${YELLOW}🔗 步骤 7/7: 部署钩子配置 (Hooks)${NC}"

# 复制 hooks.json 核心配置
if [ -f "$ECC_REPO/hooks/hooks.json" ]; then
  # 精简 hooks.json — 只保留 Python/TDD 相关
  cat > "$TARGET_DIR/hooks.json" << 'HOOKS_EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "npx block-no-verify@1.1.2"
          }
        ],
        "description": "Block git hook-bypass flag",
        "id": "pre:bash:block-no-verify"
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/run-with-flags.js\" \"pre:bash:commit-quality\" \"scripts/hooks/pre-bash-commit-quality.js\" \"strict\""
          }
        ],
        "description": "Pre-commit quality check",
        "id": "pre:bash:commit-quality"
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/run-with-flags.js\" \"pre:compact\" \"scripts/hooks/pre-compact.js\" \"standard,strict\""
          }
        ],
        "description": "Save state before compaction",
        "id": "pre:compact"
      }
    ]
  }
}
HOOKS_EOF
  echo -e "  ${GREEN}✓${NC} hooks.json (精简版)"
fi

# 复制辅助脚本
if [ -d "$ECC_REPO/scripts/hooks" ]; then
  mkdir -p "$TARGET_DIR/scripts/hooks"
  # 只复制必要的钩子脚本
  for script in run-with-flags.js pre-compact.js suggest-compact.js; do
    if [ -f "$ECC_REPO/scripts/hooks/$script" ]; then
      cp "$ECC_REPO/scripts/hooks/$script" "$TARGET_DIR/scripts/hooks/"
      echo -e "  ${GREEN}✓${NC} scripts/hooks/$script"
    fi
  done
fi

# 步骤 8: 创建 MCP 配置
echo ""
echo -e "${YELLOW}🔌 步骤 8/7: 部署 MCP 服务器配置${NC}"

cat > "$TARGET_DIR/mcp.json" << 'MCP_EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github@2025.4.8"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@2.1.4"]
    },
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory@2026.1.26"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@0.0.69", "--extension"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking@2025.12.18"]
    }
  }
}
MCP_EOF
echo -e "  ${GREEN}✓${NC} mcp.json (Context7, GitHub, Playwright, etc.)"

# 步骤 9: 生成验证报告
echo ""
echo -e "${YELLOW}📊 步骤 9/9: 生成部署报告${NC}"

cat > "$PROJECT_ROOT/ECC-DEPLOY-REPORT.md" << 'REPORT_EOF'
# Hotix ECC 部署报告

## 部署信息
- **日期**: $(date '+%Y-%m-%d %H:%M:%S')
- **项目**: Hotix
- **部署模式**: 项目级本地部署
- **安装位置**: `.claude/` (项目根目录)
- **ECC 版本**: 1.10.0

## 已安装组件

### 规则 (Rules)
✅ **Core Rules** (rules/common/)
- common-coding-style.md
- common-security.md
- common-testing.md
- common-git-workflow.md
- common-agents.md
- common-patterns.md
- common-hooks.md
- common-development-workflow.md

✅ **Python Rules** (rules/python/)
- python-coding-style.md
- python-patterns.md
- python-security.md
- python-testing.md
- python-hooks.md

### 代理 (Agents)
✅ **Core Agents** (12 agents)
| Agent | 用途 |
|-------|------|
| python-reviewer | Python 代码审查 |
| code-reviewer | 通用代码审查 |
| security-reviewer | 安全漏洞检测 |
| tdd-guide | TDD 流程引导 |
| planner | 任务分解 |
| architect | 架构设计 |
| refactor-cleaner | 代码清理 |
| docs-lookup | 文档查询 |
| build-error-resolver | 构建错误修复 |
| chief-of-staff | 多代理协调 |
| loop-operator | 任务监控 |
| harness-optimizer | 配置优化 |

### 技能 (Skills)
✅ **Workflow Skills**
- tdd-workflow/ — 测试驱动开发完整流程
- codebase-onboarding/ — 项目入门指导
- e2e-testing/ — 端到端测试策略
- verification-loop/ — 验证循环
- autonomous-loops/ — 自主循环
- agentic-engineering/ — 代理工程

✅ **Python Skills**
- python-patterns/ — Pythonic 惯用法
- python-testing/ — pytest 测试策略
- (可选) django-patterns/, django-tdd/, django-security/

### 命令 (Commands)
✅ **Essential Commands** (14 commands)
- `/tdd` — TDD 工作流
- `/plan` — 任务规划
- `/code-review` — 代码审查
- `/build-fix` — 修复构建错误
- `/quality-gate` — 质量门禁
- `/loop-start` — 启动循环监控
- `/sessions` — 会话管理
- 等等...

### 钩子 (Hooks)
✅ **PreToolUse**
- block-no-verify — 阻止 `--no-verify` 绕过
- commit-quality — 提交前质量检查

✅ **PreCompact**
- pre-compact — 压缩前状态保存

## 配置文件

| 文件 | 路径 | 说明 |
|------|------|------|
| project-config.json | .claude/ | 项目级 ECC 配置 |
| AGENTS.md | .claude/ | 代理使用指南 |
| hooks.json | .claude/ | 钩子配置 |
| mcp.json | .claude/ | MCP 服务器 |
| pyproject.toml | 项目根目录 | Python 项目配置 |
| pytest.ini | 项目根目录 | pytest 配置 |
| ruff.toml | 项目根目录 | lint 配置 |
| .coveragerc | 项目根目录 | coverage 配置 |

## TDD 配置

```yaml
coverage_target: 80%
test_runner: pytest
commit_checkpoints: true  # RED → GREEN → REFACTOR 分阶段提交
```

## Multi-Agent 配置

```yaml
orchestrator: chief-of-staff
parallel_execution: true
auto_review: true
loop_monitoring: loop-operator
```

## 使用验证

```bash
# 1. 检查安装
find .claude -type f | wc -l  # 应显示已安装文件数

# 2. 启动 Claude Code
claude .

# 3. 验证代理加载
# Claude 应该显示已加载: python-reviewer, tdd-guide 等

# 4. 运行第一个 TDD 任务
> /tdd
> 我需要一个用户注册功能
```

## 维护

### 更新 ECC
```bash
cd ~/Developments/everything-claude-code
git pull origin main

# 重新运行部署脚本
./scripts/setup-ecc.sh --update
```

### 添加新技能
```bash
# 手动添加
cp -r ~/Developments/everything-claude-code/skills/new-skill .claude/skills/

# 或使用 ECC CLI
npx ecc-universal install --add skills/new-skill --target claude --local-dir .claude
```

### 移除项目级配置
```bash
rm -rf .claude
# 恢复全局安装
npx ecc-universal install --profile developer --target claude
```

## 团队协作

此 `.claude/` 目录可以:
- ✅ 提交到 Git (建议添加到 .gitignore 的例外)
- ✅ 团队共享配置
- ✅ 版本控制配置变更

添加到 `.gitignore`:
```
# 保留 .claude 配置但忽略运行时数据
.claude/session-data/
.claude/state.db
```

---

**部署完成！** 开始使用 `claude .` 进行开发吧 🚀
REPORT_EOF

echo ""
echo -e "${GREEN}✅ Hotix ECC 部署完成！${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}已安装组件摘要:${NC}"
echo -e "  • 12 个核心代理 (Python 审查, TDD, 安全, 架构...)"
echo -e "  • 8+ 个工作流技能 (TDD, 测试, Python 模式)"
echo -e "  • 14 个常用命令 (/tdd, /plan, /code-review...)"
echo -e "  • Python 规则集 (PEP 8, typing, security, testing)"
echo -e "  • MCP 服务器配置 (Context7, GitHub, Playwright...)"
echo -e "  • Git 钩子增强 (pre-commit 质量门禁)"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📚 文档:${NC}"
echo "   • $PROJECT_ROOT/HOTIX-ECC-SETUP.md — 完整部署文档"
echo "   • $PROJECT_ROOT/ECC-DEPLOY-REPORT.md — 部署报告"
echo ""
echo -e "${GREEN}🚀 下一步:${NC}"
echo "   1. cd $PROJECT_ROOT"
echo "   2. claude .                    # 启动 Claude Code"
echo "   3. /tdd                         # 开始 TDD 工作流"
echo "   4. 尝试: '实现用户注册 API'"
echo ""
echo -e "${YELLOW}💡 提示: 项目级 .claude/ 目录可提交到 Git 供团队共享${NC}"
echo ""
