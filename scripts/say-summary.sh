#!/bin/bash
###############################################################################
# Hotix ECC 部署总结语音播报 — 简洁版
# 特点: 分块播放, 每段简短, 避免听觉疲劳
###############################################################################

VOICE="Alex"
RATE=170

echo "🎤 开始播报 Hotix ECC 部署总结..."
echo ""

delayed_say() {
  local text="$1"
  local delay="${2:-0.3}"
  say -v "$VOICE" -r $RATE "$text"
  sleep "$delay"
}

# 1. 项目概况 (极简)
delayed_say "Hotix 项目部署完成。" 0.5
delayed_say "技术: Python, TDD, Multi-Agent。" 0.5
delayed_say "时间: 2026年4月10日。" 0.5

# 2. 核心组件 (分块, 每块 3-4 项)
delayed_say "共 15 个智能代理。" 0.5
delayed_say "Python 审查, 代码审查, 安全审查, TDD 引导。" 0.5
delayed_say "规划, 架构, 协调, 监控, 构建修复, 重构。" 0.5

delayed_say "8 个工作流技能。" 0.5
delayed_say "TDD 工作流, Python 测试, Python 模式, 项目入门。" 0.5
delayed_say "端到端测试, 质量门禁, 自主循环, 多代理协同。" 0.5

delayed_say "15 个快捷命令可用。" 0.5
delayed_say " slash TDD, slash plan, slash code-review, slash security。" 0.5
delayed_say " slash architect, build-fix, quality-gate, sessions 等。" 0.5

delayed_say "9 个规则文件。" 0.5
delayed_say "Python 规则 5 个, 通用规则 4 个。" 0.5

# 3. 部署特色 (要点式)
delayed_say "项目级部署, 配置在 dot claude 文件夹。" 0.5
delayed_say "可提交 Git, 团队共享。" 0.5
delayed_say "特色: Python 优先, TDD 强制, 多代理协同。" 0.5
delayed_say "质量门禁, MCP 集成。" 0.5

# 4. 开始使用
delayed_say "开始使用:" 0.5
delayed_say "cd Hotix, 运行 claude dot。" 0.5
delayed_say "输入 slash TDD, 开始开发。" 0.5

delayed_say "祝您开发愉快！" 1.0

echo ""
echo "✅ 语音播报完成！"
echo ""
echo "文档:"
echo "  START-HERE.md     — 部署总结"
echo "  QUICKSTART.md     — 5分钟快速入门"
echo ""
