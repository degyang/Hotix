# Hotix 快速入门 — Python + TDD + Multi-Agent

## 🚀 5 分钟快速开始

### 1. 验证部署

```bash
cd ~/Developments/Hotix

# 检查 ECC 组件
ls .claude/agents/    # 应看到 15 个代理文件
ls .claude/skills/    # 应看到 8+ 个技能目录
ls .claude/rules/     # 应看到 Python 规则文件
cat .claude/project-config.json  # 查看项目配置
```

### 2. 启动 Claude Code

```bash
# 在 Hotix 项目目录启动
claude .

# 或在任意目录指定项目路径
claude /Users/mac/Developments/Hotix
```

Claude Code 会自动加载 `.claude/` 目录中的配置。

---

## 🎯 第一个 TDD 任务

### 场景: 实现用户注册功能

#### 步骤 1: 启动 TDD 工作流

```
> /tdd
> 我需要一个用户注册 API 端点, 支持邮箱验证和密码哈希
```

**Claude 会自动:**
1. 激活 `tdd-guide` 代理
2. 调用 `python-reviewer` 确保符合 PEP 8
3. 使用 `security-reviewer` 检查密码安全
4. 遵循 TDD 循环: RED → GREEN → REFACTOR

#### 步骤 2: Claude 生成测试 (RED)

你会看到类似这样的测试文件:

```python
# tests/unit/test_registration.py
def test_user_can_register_with_valid_email():
    """用户能用有效邮箱注册."""
    result = register_user(email="user@example.com", password="secure123")
    assert result.success is True
    assert result.user.id is not None

def test_registration_fails_with_invalid_email():
    """无效邮箱注册应失败."""
    with pytest.raises(ValueError, match="invalid email"):
        register_user(email="not-an-email", password="123")
```

运行测试: `pytest tests/unit/test_registration.py`
预期: **RED** — 测试失败 (函数未实现)

#### 步骤 3: 实现代码 (GREEN)

Claude 会生成最小实现:

```python
# src/hotix/services/registration.py
def register_user(email: str, password: str) -> RegistrationResult:
    """注册新用户."""
    # 验证邮箱
    if "@" not in email:
        raise ValueError("invalid email")

    # 哈希密码
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # 创建用户
    user = User(email=email, password_hash=hashed.decode())
    return RegistrationResult(success=True, user=user)
```

再次运行测试: `pytest tests/unit/test_registration.py`
预期: **GREEN** — 所有测试通过

#### 步骤 4: 重构 (REFACTOR)

Claude 会:
- 提取验证逻辑到独立函数
- 添加类型提示
- 优化代码结构
- 确保覆盖率 >= 80%

---

## 🔄 Multi-Agent 协作示例

### 复杂任务: 设计支付系统

```
> /plan
> 设计一个支持 Stripe 和 PayPal 的支付系统
```

**工作流程:**

1. **planner** 代理激活 → 分解任务:
   ```
   子任务 1: 设计支付抽象层 (Payment Gateway Interface)
   子任务 2: 实现 Stripe 适配器
   子任务 3: 实现 PayPal 适配器
   子任务 4: 编写单元测试 (TDD)
   子任务 5: 集成测试
   子任务 6: 安全审计
   ```

2. **并行执行** (Claude 自动):
   - 线程 A: 编写 Stripe 适配器 + 测试
   - 线程 B: 编写 PayPal 适配器 + 测试
   - 线程 C: 设计支付模型 + 数据库迁移

3. **chief-of-staff** 协调:
   - 跟踪各子任务进度
   - 识别阻塞问题
   - 合并代码变更

4. **code-reviewer + security-reviewer** 并行审查:
   ```
   代码审查: ✅ 通过 (3 个建议)
   安全审查: ✅ 通过 (0 个高危问题)
   ```

5. **loop-operator** 监控长时间任务:
   - 每 30 秒检查进度
   - 检测停滞并提醒

---

## 📋 常用命令速查

| 命令 | 作用 | 激活代理 |
|------|------|---------|
| `/tdd` | 启动 TDD 工作流 | tdd-guide |
| `/plan` | 任务分解 | planner |
| `/code-review` | 代码审查 | code-reviewer |
| `/security-review` | 安全检查 | security-reviewer |
| `/architect` | 架构咨询 | architect |
| `/build-fix` | 修复构建错误 | build-error-resolver |
| `/quality-gate` | 运行质量门禁 | verification-loop |
| `/loop-start` | 启动循环监控 | loop-operator |
| `/sessions` | 查看会话列表 | — |
| `/save-session` | 保存当前会话 | — |

---

## 🛠️ 项目结构

```
Hotix/
├── .claude/                    # ECC 项目级配置 (可提交到 Git)
│   ├── agents/                 # 代理定义
│   ├── skills/                 # 工作流技能
│   ├── rules/                  # 编码规范
│   │   └── python/            # Python 规则 (PEP 8, typing...)
│   ├── commands/              #  slash 命令
│   ├── hooks.json             # 钩子配置
│   ├── mcp.json               # MCP 服务器
│   ├── AGENTS.md              # 代理使用指南
│   └── project-config.json    # 项目配置
├── src/hotix/                 # 源代码
│   ├── __init__.py
│   ├── models/               # 领域模型
│   ├── services/             # 业务逻辑
│   ├── api/                  # API 路由
│   └── db/                   # 数据库
├── tests/                     # 测试 (TDD 核心)
│   ├── conftest.py           # 全局 fixtures
│   ├── unit/                 # 单元测试 (60%)
│   ├── integration/          # 集成测试 (30%)
│   └── e2e/                  # 端到端测试 (10%)
├── pyproject.toml            # 项目配置 (uv/poetry)
├── pytest.ini                # pytest 配置
├── ruff.toml                 # lint 规则
├── .coveragerc               # coverage 配置
├── .ecc-config.json          # ECC 配置记录
├── CLAUDE.md                 # 项目级 Claude 配置
├── HOTIX-ECC-SETUP.md        # 完整部署文档
├── ECC-DEPLOY-REPORT.md      # 部署报告
└── scripts/
    └── setup-ecc.sh          # ECC 部署脚本
```

---

## ✅ TDD 检查清单

每个功能开发都遵循此流程:

### RED 阶段
- [ ] 编写失败的测试
- [ ] 运行 `pytest` 确认测试失败
- [ ] `git add` + `git commit -m "test: add reproducer for <feature>"`
- [ ] 创建 RED 阶段提交

### GREEN 阶段
- [ ] 编写最小实现
- [ ] 运行 `pytest` 确认测试通过
- [ ] `git commit -m "fix: implement <feature>"`
- [ ] 创建 GREEN 阶段提交

### REFACTOR 阶段
- [ ] 重构代码 (提取函数, 优化命名)
- [ ] 运行 `pytest --cov` 确认覆盖率 >= 80%
- [ ] 运行 `ruff check .` 确认无 lint 错误
- [ ] `git commit -m "refactor: clean up <feature>"`
- [ ] 创建 REFACTOR 阶段提交

### 最终验证
- [ ] 所有测试通过
- [ ] 覆盖率报告 >= 80%
- [ ] 代码审查通过 (`/code-review`)
- [ ] 安全检查通过 (`/security-review`)
- [ ] `git push`

---

## 🔒 质量门禁

### Pre-commit 钩子自动执行:

```
1. pytest --cov --cov-fail-under=80
2. ruff check .
3. black --check .
4. mypy hotix/ (可选)
5. 密钥扫描
```

**任何一项失败都会阻止提交。**

### 手动质量检查

```bash
# 完整测试套件
pytest                    # 运行所有测试
pytest -m unit           # 仅单元测试
pytest -m integration    # 仅集成测试

# 覆盖率报告
pytest --cov=hotix --cov-report=html
open htmlcov/index.html  # 查看详细覆盖率

# 代码质量
ruff check .             # lint 检查
black --check .          # 格式检查
mypy hotix/              # 类型检查

# 一次性全部运行
pre-commit run --all-files
```

---

## 🎭 Multi-Agent 激活规则

### 自动激活 (无需手动调用)

| 事件 | 激活代理 | 说明 |
|------|---------|------|
| 代码修改后 | `code-reviewer` | 每次 Write/Edit 后自动审查 |
| 检测到安全敏感代码 | `security-reviewer` | SQL, 认证, 密钥相关 |
| 复杂任务 (>5 个子任务) | `planner` | 自动建议分解任务 |
| 长时间运行的任务 | `loop-operator` | 监控进度, 检测停滞 |

### 手动激活

```bash
# 在 Claude 对话中直接输入:
/tdd                        # 启动 TDD 引导
/plan                       # 任务分解
/code-review src/hotix/api/users.py
/security-review src/hotix/auth/
/architect                  # 架构咨询
```

---

## 📊 代理能力矩阵

| 代理 | 专长 | 触发条件 | 输出 |
|------|------|---------|------|
| `python-reviewer` | PEP 8, typing, idioms | `.py` 文件修改 | 代码改进建议 |
| `tdd-guide` | TDD 流程引导 | `/tdd` 命令 | 测试用例 + 实现步骤 |
| `code-reviewer` | 代码质量, 可维护性 | 代码修改后 | CRITICAL/HIGH/MED 问题 |
| `security-reviewer` | SQLi, XSS, secrets | 安全相关代码 | 漏洞报告 + 修复建议 |
| `planner` | 任务分解, 依赖分析 | `/plan` 或复杂任务 | 任务图 + 时间估计 |
| `architect` | 系统设计, 扩展性 | `/architect` | 架构图 + 技术选型 |
| `chief-of-staff` | 多代理协调 | 多代理任务 | 进度跟踪 + 分配 |
| `loop-operator` | 任务监控 | 长时间任务 | 进度报告 + 停滞警告 |

---

## 🔧 常用开发命令

```bash
# 初始化开发环境
uv sync --all-extras        # 安装所有依赖 (dev + 主)
pre-commit install          # 安装 Git 钩子

# 日常开发
pytest                      # 运行所有测试
pytest tests/unit/         # 仅单元测试
pytest --cov=hotix         # 覆盖率报告
ruff check .               # lint 检查
black .                    # 自动格式化
mypy hotix/                # 类型检查

# 调试
python -m ipdb src/hotix/services/foo.py
python -c "from hotix.models.user import User; print(User())"

# 文档
mkdocs serve               # 启动文档服务器 (如有)
```

---

## 🐛 故障排除

### 问题: 代理未加载

```bash
# 检查 .claude 目录
ls -la .claude/agents/

# 重新部署
cd ~/Developments/Hotix
bash scripts/setup-ecc.sh

# 重启 Claude Code
# 完全退出后重新启动: claude .
```

### 问题: TDD 工作流不生效

```bash
# 验证 tdd-workflow skill 存在
ls .claude/skills/tdd-workflow/

# 检查 AGENTS.md
cat .claude/AGENTS.md | grep tdd

# 重新安装 workflow-quality 模块
npx ecc-universal install --add workflow-quality --target claude --local-dir .claude
```

### 问题: Python 规则未应用

```bash
# 验证 Python 规则
ls .claude/rules/python/

# 检查是否包含 python-coding-style.md
cat .claude/rules/python/python-coding-style.md | head -20
```

### 问题: 覆盖率检查失败

```bash
# 查看哪些文件未覆盖
pytest --cov=hotix --cov-report=term-missing

# 临时跳过 (不推荐)
pytest --no-cov

# 提升覆盖率: 添加缺失的测试用例
```

---

## 📚 进一步学习

| 资源 | 路径 |
|------|------|
| ECC 完整文档 | `~/Developments/everything-claude-code/README.md` |
| 代理目录 | `~/.claude/AGENTS.md` 或项目 `.claude/AGENTS.md` |
| TDD 技能详解 | `.claude/skills/tdd-workflow/SKILL.md` |
| Python 测试技能 | `.claude/skills/python-testing/SKILL.md` |
| Python 模式技能 | `.claude/skills/python-patterns/SKILL.md` |
| Python 规则集 | `.claude/rules/python/` |
| ECC 项目配置 | `HOTIX-ECC-SETUP.md` |
| 部署报告 | `ECC-DEPLOY-REPORT.md` |

---

## 🎯 下一步建议

1. **完成第一个 TDD 迭代**
   ```bash
   claude .
   > /tdd
   > 实现一个简单的计算器服务 (加减乘除)
   ```

2. **配置 CI/CD**
   ```yaml
   # .github/workflows/ci.yml
   - name: Run Tests
     run: pytest --cov=hotix --cov-fail-under=80
   ```

3. **添加框架特定技能** (如需)
   ```bash
   # Django
   bash scripts/setup-ecc.sh --add django-patterns
   # FastAPI
   # 使用 python-patterns 已覆盖
   ```

4. **团队共享配置**
   ```bash
   git add .claude/
   git commit -m "feat: add ECC project-level config"
   git push
   ```

---

**准备好了吗？开始第一个 TDD 任务: `claude .` → `/tdd` 🚀**
