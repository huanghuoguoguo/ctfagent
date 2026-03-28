# CTFAgent 设计总览

更新时间：2026-03-28

## 一句话概括

`CTFAgent` 现在不是一个“自动批量跑题平台”，而是一个以 `Claude Code` 为核心的 CTF 工作仓库。

它已经能把下面这些资产组织成一条可复用的解题链路：

- `Skills`：题型 SOP、决策顺序、切换条件
- `scripts/`：薄工具脚本
- `knowledge/`：本地 Markdown 知识库
- `targets/`：本地靶场与回归样例
- `workspaces/`：每道题的独立工作目录

## 我们现在能做什么

当前能力的重点是“辅助真实打题”，不是“代替整套比赛系统”。

现在已经能做的事：

- 把新题整理成统一的 challenge workspace
- 让 `Claude Code` 按既定 solver workflow 做单题分析
- 按证据调用具体题型 `Skill`
- 查询本地历史 writeup 和 pattern
- 把解题结果沉淀回 `knowledge/`
- 用本地靶场回归验证 skill 和 exploit pattern

当前仓库已经落地的代表性资产包括：

- `ctf-solver-profile`
- `challenge-workspace-bootstrap`
- `web-ssrf-to-rce-triage`
- `web-sqli-triage`
- `ctf-knowledge-capture`
- `scripts/init_challenge.py`
- `scripts/query_markdown.py`
- `targets/web-sqli-lab/`
- `targets/web-ssrf-lab/`
- `targets/web-rce-lab/`
- `targets/web-advanced-chain/`

## 现在怎么设计

当前设计围绕 5 个部分展开：

### 1. `Claude Code` 负责推理和调度

主 agent 不是 Python 宿主程序，而是 `Claude Code`。

它负责：

- 阅读题目和附件
- 规划分析步骤
- 调用本地工具
- 根据证据切换 skill
- 汇总中间结论和最终结论

### 2. `Skills` 承载题型经验

`Skills` 用来沉淀：

- 题型 SOP
- 低成本验证顺序
- 常见分支与切换条件
- 常见误判和避坑规则

`Skills` 解决的是“怎么想、先做什么、什么情况下换方向”。

### 3. `scripts/` 和后续 `MCP` 承载能力接口

当前先以薄脚本为主，例如：

- 初始化 challenge
- 查询知识库
- 展示 challenge 元数据

当某些动作高频、参数稳定、输出可结构化时，再考虑升格为 `MCP` 或 custom tool。

### 4. `knowledge/` 作为知识真源

当前优先使用 Markdown，而不是先上数据库。

这样做的好处是：

- 人可读
- Git 可追溯
- 容易维护
- 也能通过 frontmatter 和查询脚本被 agent 使用

### 5. `targets/` 和 `workspaces/` 提供验证闭环

- `workspaces/` 用来隔离单题上下文、附件、笔记和工件
- `targets/` 用来回归验证 skill、payload 和 exploit pattern

这让仓库不只是“写攻略”，而是能验证攻略是否真能复用。

## 为什么这样设计

核心原因有四个：

### 1. 当前主问题不是 orchestration

在现阶段，真正要验证的是：

- `Claude Code` 是否能理解你的解题方式
- 哪些知识适合做成 `Skill`
- 哪些能力适合做成工具接口
- 哪些结果值得进入 `knowledge/`

如果这些都还没稳定，先写 Python orchestration 只会把不成熟的流程自动化。

### 2. CTF 能力首先是经验和边界，不是状态机

很多解题质量差异来自：

- 是否先做低成本验证
- 是否能识别题型切换信号
- 是否知道哪些爆破不值得做
- 是否会优先找源码、元数据、内部面

这些内容更适合沉淀成 `Skills`，而不是先做任务队列和 session store。

### 3. Markdown 知识库比早期数据库更适合当前阶段

当前知识量还在沉淀期。

这时最重要的是：

- 可读
- 可修改
- 可复盘
- 能快速总结成 writeup 和 pattern

所以当前设计先把 Markdown 作为 source of truth，再按需派生检索层。

### 4. 回归靶场让设计可验证

如果没有 `targets/`，很多 skill 只是“看起来合理”。

有了本地靶场，你可以检验：

- 某个流程是否稳定
- 某个 payload 是否过于偶然
- 某个 pattern 是否值得进入知识库

## 这样做带来了什么效果

当前这条路线的实际效果是：

- 解题流程从“临场发挥”变成“可复用工作流”
- 经验证的技巧可以沉淀成可搜索的本地知识
- 新题可以快速进入统一 workspace，而不是散落目录
- 常见题型的思考路径可以复用给后续题目
- skill、knowledge、target 三者形成了可迭代闭环

换句话说，仓库现在已经不仅是在“记笔记”，而是在逐步形成一套可验证、可积累、可回放的解题系统。

## 当前边界

当前主线仍然明确停留在以 `Claude Code` 为核心的阶段：

- 人在回路中
- 以单题 workflow 为主
- 不追求自动批量跑题
- 不默认做统一 state manager
- 不把比赛平台自动提交作为核心能力

如果后续真的出现批量化、自动提交、统一状态管理的明确需求，再在主文档里补充后续设计即可。

## 文档导航

- 当前工作流：[`phase1-claude-code-ctf-workflow.md`](/home/yhh/ctfagent/docs/phase1-claude-code-ctf-workflow.md)
- challenge 结构和平台边界：[`challenge-package-and-platform-interface.md`](/home/yhh/ctfagent/docs/challenge-package-and-platform-interface.md)
- 文档入口：[`README.md`](/home/yhh/ctfagent/docs/README.md)
