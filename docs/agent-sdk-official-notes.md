# Claude Agent SDK 官方文档摘要

更新时间：2026-03-28

用途：

- 作为本地速查笔记
- 记录官方文档中和本项目最相关的 SDK 能力
- 避免后续继续误写成 `Claude Code SDK`

说明：

- 本文档是官方资料的摘要和索引，不是原文镜像
- 需要看完整细节时，直接打开对应官方链接
- 名称统一使用 `Claude Agent SDK`

## 1. Overview

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/overview

关键点：

- `Claude Agent SDK` 是正式名称，原 `Claude Code SDK` 已迁移为这个名字
- 它把 Claude Code 的核心能力以库的方式开放出来
- 官方描述的能力包括：
  - 内置工具
  - agent loop
  - context management
  - hooks
  - subagents
  - MCP
  - permissions
  - sessions
- 可用语言是 Python 和 TypeScript

对本项目的意义：

- 我们应该把它当作“CTF agent 运行时”
- 不要再把“Claude Code SDK”当成一个单独、现行的产品名来设计

## 2. Quickstart

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/quickstart

关键点：

- Python 包名：`claude-agent-sdk`
- TypeScript 包名：`@anthropic-ai/claude-agent-sdk`
- 基本使用模式是调用 `query(...)`，并传入 `ClaudeAgentOptions`
- 工具访问通过 `allowed_tools` 或 `allowedTools` 显式声明

对本项目的意义：

- 首版宿主程序可以直接围绕 `query(...)` 建一层 orchestration
- 先只开放最少工具，逐步增加 CTF 专用能力

## 3. Migration Guide

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/migration-guide

关键点：

- 官方文档已经按 `Claude Agent SDK` 重新组织
- 如果看到旧资料里提到 `Claude Code SDK`，在今天应视为旧名称

对本项目的意义：

- 后续仓库内文档、代码注释、README、设计稿统一写 `Claude Agent SDK`
- 如果要兼容旧资料，最多只在“术语说明”里提一次旧名

## 4. MCP

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/mcp
- https://code.claude.com/docs/en/mcp

关键点：

- SDK 支持连接 MCP servers，把外部能力暴露给 agent
- MCP 工具会以 `mcp__<server>__<tool>` 这种形式出现
- 适合把独立工具、外部服务、平台接口包装为结构化工具

对本项目的意义：

- 你的 CTF 工具层应该优先考虑 MCP 化
- 尤其适合：
  - 比赛平台 API
  - 题目下载/启动
  - 漏洞扫描器封装
  - 逆向分析器封装
  - 提交 flag 接口

## 5. Custom Tools

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/custom-tools

关键点：

- SDK 支持定义自定义工具
- 自定义工具适合宿主进程内、参数稳定、输出结构化的能力
- 比独立 MCP server 更轻量

对本项目的意义：

- 首版可以先做 custom tools，再把成熟能力拆成 MCP
- 适合最先实现的几个工具：
  - `init_challenge`
  - `inspect_artifact`
  - `query_playbook`
  - `run_solver`
  - `submit_flag`

## 6. Skills

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/skills

关键点：

- Skills 是专门能力包，不是普通工具
- 项目级 skills 通常来自 `.claude/skills/*/SKILL.md`
- 要在 SDK 中启用项目配置，通常需要开启 project settings source
- 要允许 agent 使用 skills，主工具权限里需要允许 `Skill`

对本项目的意义：

- 题型 SOP、攻略、排障套路应优先沉淀成 Skills
- 例如：
  - Web 初筛
  - Pwn 初始分析
  - Reverse 解包与字符串定位
  - Crypto 编码判别树

## 7. Plugins

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/plugins

关键点：

- 插件可打包多个扩展能力
- 可包含 skills、agents、hooks、MCP 配置等

对本项目的意义：

- 如果后续要把整套 CTF 能力做成可复用组件，插件是合适封装方式
- 这比把逻辑散落在宿主程序里更易维护

## 8. Permissions

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/permissions

关键点：

- SDK 支持权限模式控制
- 文档中包含 `acceptEdits`、`bypassPermissions` 等模式
- 权限不是附属配置，而是 agent 运行边界的一部分

对本项目的意义：

- 开发期建议偏向保守模式
- `bypassPermissions` 只适合明确隔离的环境
- 不要默认给 CTF agent 宿主机的高权限执行能力

## 9. Hooks

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/hooks

关键点：

- SDK 支持 hooks，在 agent 执行流程的关键节点介入
- hooks 可用于校验、审计、阻断、补充上下文、打日志

对本项目的意义：

- 非常适合做：
  - 高危命令拦截
  - 文件访问限制
  - 统一日志
  - 自动记录 challenge state
  - 提交 flag 前校验

## 10. Secure Deployment

官方页面：

- https://platform.claude.com/docs/en/agent-sdk/secure-deployment

关键点：

- 官方明确强调高风险 agent 的安全部署
- 建议使用最小权限、凭据隔离、网络控制、代理注入、环境隔离
- 文档提到 `sandbox-runtime`
- `sandbox-runtime` 可做文件系统和网络限制，适合轻量隔离

对本项目的意义：

- CTF agent 默认处理的是不可信输入，安全隔离不是可选项
- 至少要做到：
  - challenge workspace 隔离
  - 域名/网络 allowlist
  - 凭据不直接暴露给 agent
  - 高危工具在容器或沙箱内执行

## 11. Claude Code 相关文档里仍值得参考的部分

官方页面：

- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/sub-agents

关键点：

- Claude Code 文档里对 MCP 的使用细节仍然有参考价值
- sub-agents 文档说明了 specialized agents 的组织方式

对本项目的意义：

- 后续如果做题型专家协作，可参考 sub-agents 模式
- 但宿主集成层的正式名称和主入口，仍然应以 `Claude Agent SDK` 为准

## 12. 对本项目的命名约定

从现在开始统一使用：

- `Claude Agent SDK`
- `Agent SDK`
- `Claude agent runtime`

避免继续使用：

- `Claude Code SDK`

允许出现旧名的唯一场景：

- 解释历史资料或迁移背景时，明确写成“原 Claude Code SDK，现 Claude Agent SDK”

## 13. 建议的后续本地资料组织方式

推荐后续继续按下面方式积累：

- `docs/agent-sdk-official-notes.md`
  - 官方摘要
- `docs/claude-agent-sdk-ctf-agent-design.md`
  - 项目设计
- `docs/mcp-tooling-notes.md`
  - 你自己的 MCP 设计约束
- `docs/skills-playbook.md`
  - 哪些攻略适合做 Skills

## 14. 本地速查结论

一句话总结：

- 用 `Claude Agent SDK` 做宿主
- 用 `MCP / custom tools` 接 CTF 能力
- 用 `Skills` 放题型攻略
- 用 `hooks + permissions + sandbox` 管边界
- 名称上不再继续使用 `Claude Code SDK`

