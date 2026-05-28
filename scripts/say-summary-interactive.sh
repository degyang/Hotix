#!/bin/bash
###############################################################################
# Hotix ECC 部署总结 — 交互式语音播报 (简洁版)
# 可选择语言, 每段内容经过精简
###############################################################################

VOICE="Alex"
RATE=170

delayed_say() {
  local text="$1"
  local delay="${2:-0.3}"
  say -v "$VOICE" -r $RATE "$text"
  sleep "$delay"
}

speak_english_short() {
  echo "🎤 英文播报 (简洁版)..."

  delayed_say "Hotix project ECC deployment complete." 0.5
  delayed_say "Tech stack: Python, TDD, Multi-Agent." 0.5
  delayed_say "Date: April 10th, 2026." 0.5

  delayed_say "15 agents installed." 0.5
  delayed_say "Python reviewer, code reviewer, security, TDD guide." 0.5
  delayed_say "Planner, architect, chief of staff, loop operator." 0.5
  delayed_say "Build resolver, refactor, docs, performance, database, E2E." 0.5

  delayed_say "8 workflow skills." 0.5
  delayed_say "TDD workflow, Python testing, Python patterns, onboarding." 0.5
  delayed_say "E2E testing, quality gates, autonomous loops, agentic engineering." 0.5

  delayed_say "15 commands available." 0.5
  delayed_say " slash TDD, plan, code-review, security, architect." 0.5
  delayed_say " build-fix, quality-gate, sessions, checkpoint, and more." 0.5

  delayed_say "9 rule files." 0.5
  delayed_say "5 Python rules, 4 common rules." 0.5

  delayed_say "Project-local deployment in dot claude folder." 0.5
  delayed_say "Git committable for team sharing." 0.5
  delayed_say "Features: Python first, TDD enforced, multi-agent, quality gates." 0.5

  delayed_say "To start: cd Hotix, run claude dot, then slash TDD." 0.5
  delayed_say "Happy coding!" 1.0

  echo "✅ 英文播报完成！"
}

speak_chinese_short() {
  echo "🎤 中文播报 (简洁版)..."

  if ! say -v "Ting-Ting" "测试" 2>/dev/null; then
    echo "⚠️  中文语音未安装, 回退到英文..."
    echo ""
    speak_english_short
    return
  fi

  say -v "Ting-Ting" -r 150 "Hotix 项目 ECC 部署完成。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "技术栈: Python, TDD, Multi-Agent。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "日期: 2026年4月10日。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "已安装 15 个智能代理。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "包括: Python 审查, 代码审查, 安全, TDD 引导。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "规划, 架构, 协调, 监控, 构建修复, 重构。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "8 个工作流技能。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "TDD, Python 测试, Python 模式, 项目入门。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "端到端, 质量门禁, 自主循环, 多代理协同。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "15 个快捷命令。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 " slash TDD, plan, code-review, security, architect。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "9 个规则文件。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "项目级部署, 配置在 dot claude 文件夹。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "可提交 Git 共享。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "特色: Python 优先, TDD 强制, 多代理协同, 质量门禁。"
  sleep 0.5

  say -v "Ting-Ting" -r 150 "开始使用: 进入 Hotix, 运行 claude dot, 输入 slash TDD。"
  sleep 0.5
  say -v "Ting-Ting" -r 150 "祝您开发愉快！"
  sleep 1.0

  echo "✅ 中文播报完成！"
}

# 交互菜单
show_menu() {
  clear
  cat << 'MENU'
╔═══════════════════════════════════════════════════════════╗
║   Hotix ECC 部署总结 — 语音播报 (简洁版)                ║
╚═══════════════════════════════════════════════════════════╝

  1. 英文播报 (简洁) — 推荐
  2. 中文播报 (简洁) — 需中文语音包
  0. 退出

MENU
}

# 主循环
while true; do
  show_menu
  read -p "请选择 (0-2): " choice

  case $choice in
    1)
      speak_english_short
      read -p "按 Enter 继续..."
      ;;
    2)
      speak_chinese_short
      read -p "按 Enter 继续..."
      ;;
    0)
      echo "👋 再见！"
      exit 0
      ;;
    *)
      echo "❌ 无效选择"
      sleep 1
      ;;
  esac
done
