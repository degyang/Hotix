---
parent: "[[10-Projects/Active/11.09 Hotix/Overview]]"
---

# Workflow - Hotix Stage II

## 分支与 PR 流程

### 分支命名

`<type>/<简短描述>`

| type | 用途 |
|------|------|
| `feat` | 新功能（新引擎、新 DSL、新 CLI 参数） |
| `fix` | Bug 修复 |
| `refactor` | 不改变行为的重构 |
| `docs` | 文档变更 |
| `chore` | 构建、CI、工具链变更 |

示例：`feat/universe-report-templates`、`fix/salience-nan`、`docs/stage2-summary`

### PR 流程

1. 从 `main` 创建分支或 worktree
2. 先写测试，再改实现
3. 本地通过全量检查：`pytest && ruff check . && ruff format --check .`
4. 推送分支并创建 PR
5. CI 通过后合并
6. 删除分支和 worktree

**PR 作用：**
- 强制 CI 检查，防止未测试代码合入 main
- 代码审查节点，确保报告语境和数据边界不被突破
- PR 描述记录 why，commit 记录 what

### Worktree 工作模式

Worktree 允许在同一个仓库的独立目录中同时开发多个分支，互不干扰。

```bash
# 创建 worktree
git worktree add ../Hotix-feat-xxx feat/xxx

# 在 worktree 中工作
cd ../Hotix-feat-xxx
# ... 开发、测试、提交 ...

# 推送并创建 PR
git push -u origin feat/xxx
gh pr create --title "feat: xxx" --body "..."

# 合并后清理
cd /Users/mac/Projects/Hotix
git worktree remove ../Hotix-feat-xxx
git branch -d feat/xxx
```

**Worktree 作用：**
- main 保持可用状态，随时可以运行 `hotix --latest`
- 多个功能并行开发时互不污染
- 避免频繁 stash/checkout 丢失工作状态

## TDD 驱动开发

### 基本循环

```
写失败测试 → 写最小实现 → 绿 → 重构 → 提交
```

每次循环控制在 5-15 分钟内，保持小步前进。

### 场景化 TDD 流程

#### 改报告模板

1. `tests/unit/test_report_templates.py` 加模板测试 → 红
2. 修改 `src/hotix/engine/report_templates.py` 或 `output_writer.py` → 绿
3. 同步更新 `tests/unit/test_output_writer.py` 和 `tests/integration/test_pipeline.py`

#### 改组合分析

1. `tests/unit/test_universe_engine.py` 写 topn 或 universe 行为测试 → 红
2. 修改 `src/hotix/engine/universe_engine.py` → 绿
3. 用真实数据路径验证 `tests/integration/test_pipeline.py`

#### 改 CLI 行为

1. `tests/integration/test_pipeline.py` 加 CLI 测试 → 红
2. 修改 `src/hotix/run_daily.py` → 绿
3. 同步更新 `docs/current/cli.md`、`docs/current/development.md`

### 提交前检查

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

三项全绿才允许创建 PR。

## CI

仓库配置了 GitHub Actions CI（`.github/workflows/ci.yml`），在 push 到 main 和 PR 时自动运行：

- `pytest`
- `ruff check .`
- `ruff format --check .`

---

Parent: [[10-Projects/Active/11.09 Hotix/Overview]]
