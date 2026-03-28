# 第一阶段：直接使用 Claude Code 的 CTF 工作流

更新时间：2026-03-28

## 目标

这一阶段不写 Python 宿主程序，直接使用 `Claude Code`。

你要做的是：

- 启动 `Claude Code`
- 用自然语言告诉它题目、附件路径、目标和限制
- 让它调用你配置好的工具、MCP、Skills、攻略去分析和尝试

这一阶段的目标不是“全自动”，而是验证交互式工作流是否成立。

重点验证三件事：

1. Claude Code 能不能理解你的 CTF 工作流
2. 你提供的工具和攻略，能不能被它顺畅调用
3. 哪些能力适合做成 `MCP`，哪些适合做成 `Skills`

## 为什么先做这一阶段

原因很简单：

- 成本最低
- 反馈最快
- 不需要先写 orchestration
- 能最快暴露“工具设计不好”还是“攻略结构不好”

如果这一阶段都跑不顺，直接上 Python 自动化只会更乱。

## Claude 在这一阶段的定位

不要把 Claude 当“内置所有 CTF 技术细节的模型”。

更合理的定位是：

- Claude 负责：推理、规划、调度、总结
- 你负责：提供工具、攻略、约束、安全边界

这些能力应拆成三类接入物：

- `Tools`：执行命令、跑脚本、调用现成 CTF 工具、访问题目环境
- `Skills`：攻略、SOP、解题套路、题型识别和决策规则
- `Hooks / Permissions / Sandbox`：约束它怎么用工具，避免乱跑和越权

## 这一阶段你能直接怎么用

你可以直接启动 `Claude Code`，然后自然语言下达任务，例如：

- 这是一个 web 题，附件在某个目录，先做初筛
- 这是一个 ELF，先判断是 pwn 还是 reverse
- 这是一个题目附件目录，请按我的 playbook 先整理环境

只要你提前把下面这些东西配好，它就可以直接帮你做：

- `.claude/skills/` 里的题型 SOP
- `.mcp.json` 里的 MCP 工具
- 本地可执行的 CTF 工具
- `CLAUDE.md` 里的项目约束和行为规则

## 这一阶段适合接入什么

优先做：

- `Skills`
- `MCP`
- 少量项目级配置
- challenge workspace 目录约定

先不要急着做：

- Python orchestration
- 任务队列
- 自动批量跑题
- 自动 flag 提交系统
- 复杂状态机

## 推荐的最小目录结构

```text
ctfagent/
├── .claude/
│   ├── skills/
│   │   ├── pwn-initial-recon/
│   │   │   └── SKILL.md
│   │   ├── web-sqli-triage/
│   │   │   └── SKILL.md
│   │   └── crypto-encoding-decision-tree/
│   │       └── SKILL.md
│   ├── CLAUDE.md
│   └── settings.json
├── knowledge/
│   ├── writeups/
│   ├── playbooks/
│   └── templates/
├── workspaces/
│   └── <challenge-id>/
├── docs/
│   └── phase1-claude-code-ctf-workflow.md
└── .mcp.json
```

## Skills 应该放什么

很适合沉淀为 Skills 的内容：

- Web 常见渗透 checklist
- Pwn 初始分析 SOP
- Reverse 定位字符串/控制流/加解密套路
- Crypto 题型识别树
- Forensics 文件恢复流程
- Misc 编解码和隐写排查顺序

Skill 里应该写：

- 什么时候该调用
- 调用后先做哪几步
- 哪些结果意味着切换方向
- 哪些工具优先

## MCP 应该先接什么

建议先接 1 到 2 个最关键的能力，不要一开始接太多。

适合最早接入 MCP 的工具：

- 比赛平台 API
- 题目下载/启动
- 常用扫描器封装
- 提交 flag 接口

适合放进 MCP 的典型工具：

- `nmap`、`ffuf`、`sqlmap`、`gobuster`、`dirsearch`
- `pwntools` 脚本执行器
- `gdb` / `gef` / `pwndbg` 包装器
- `angr`、`z3`、`binwalk`、`foremost`、`exiftool`
- `ghidra` / `IDA` / `rizin` / `radare2` 的批处理接口

## 攻略接入策略

不要把“任务、攻略、经验”都塞进同一个 prompt。

建议拆分：

### 1. Skills 放“短而硬”的套路

例如：

- `web-sqli-triage`
- `web-ssti-triage`
- `pwn-initial-recon`
- `rev-unpack-and-trace`
- `crypto-encoding-decision-tree`

### 2. 知识库放“长文和案例”

例如：

- 历年 writeup
- 某类漏洞总结
- 工具长教程
- 你自己的复盘笔记

通过检索或按需读取使用，而不是完整注入 prompt。

## 安全边界

这一阶段虽然不是全自动，但仍然要做边界控制。

至少做到：

- 每个 challenge 一个独立工作目录
- 敏感凭据不进 agent 工作区
- 高危工具尽量放进容器或受限运行时
- 出网做 allowlist
- 比赛平台 token 通过代理或单独提交工具处理

不要让 Claude 直接在宿主机裸跑高权限 bash。

## 阶段 1 MVP

只支持：

- 手动给题目描述
- 手动给附件路径
- 手动在 Claude Code 中下指令
- 本地保存分析过程和工件

目标：

- Claude Code 能自己整理附件
- 会调用知识和工具
- 能产出中间分析结论
- 你能发现哪些动作值得固化成结构化工具

## 推荐的首版决策

如果现在就开工，我建议先这样定：

- 直接用 `Claude Code`
- 首批能力：3 到 5 个核心 Skills + 1 到 2 个 MCP 工具
- 工作模式：单 challenge 单 workspace
- 目标题型：先只做 Web 或 Reverse
- 隔离：Docker 容器内执行高风险命令
- 权限：默认保守，不在宿主机上放开危险执行

## 现在就做的事情

1. 选定首个题型，只做一个
2. 先列出你已有工具和攻略
3. 把它们归类成 `tool / skill / knowledge`
4. 配置 `.claude/skills/`、`.mcp.json`、`CLAUDE.md`
5. 直接启动 Claude Code 和它聊天打题

## 这一阶段完成的标志

下面几件事成立，就说明第一阶段跑顺了：

1. Claude Code 能独立完成单题多步分析
2. 它会稳定调用你的工具和攻略
3. 你能明确看出高频重复动作
4. 你已经知道哪些能力下一步要程序化

