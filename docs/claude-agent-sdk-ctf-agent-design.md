# CTF Agent 方案索引

更新时间：2026-03-28

这套方案分成两个阶段，不再放在同一份长文里混写。

## 第一阶段

直接使用 `Claude Code` 打题，不先写 Python 宿主程序。

文档：

- [phase1-claude-code-ctf-workflow.md](/home/yhh/ctfagent/docs/phase1-claude-code-ctf-workflow.md)
- [phase1-cc-first-development-strategy.md](/home/yhh/ctfagent/docs/phase1-cc-first-development-strategy.md)

适用目标：

- 先验证 Claude Code 能否配合你的工具、攻略、目录结构打题
- 先验证哪些能力应该沉淀成 `Skills`
- 先验证哪些工具值得做成 `MCP`

这一阶段的核心特点：

- 直接聊天驱动
- 人在回路中
- 重点是验证工作流，而不是全自动

## 第二阶段

在第一阶段跑顺之后，再使用 `Claude Agent SDK` 做 Python 自动化。

文档：

- [phase2-agent-sdk-python-automation.md](/home/yhh/ctfagent/docs/phase2-agent-sdk-python-automation.md)

适用目标：

- 程序化调度 challenge
- 保存 state、日志、工件
- 支持批量跑题、自动提交、评测与回放

这一阶段的核心特点：

- Python 宿主程序
- `Claude Agent SDK` 作为运行时
- 更强的状态管理、权限控制和自动化能力

## 相关资料

- 官方摘要：[`agent-sdk-official-notes.md`](/home/yhh/ctfagent/docs/agent-sdk-official-notes.md)
- challenge 结构与平台边界：[`challenge-package-and-platform-interface.md`](/home/yhh/ctfagent/docs/challenge-package-and-platform-interface.md)

## 命名约定

后续统一使用：

- `Claude Code`
- `Claude Agent SDK`

不再把现行方案写成 `Claude Code SDK`。
