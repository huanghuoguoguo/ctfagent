# 第二阶段：基于 Claude Agent SDK 的 Python 自动化

更新时间：2026-03-28

## 目标

这一阶段建立在第一阶段已经跑顺的前提上。

此时你再做：

- 用 `Claude Agent SDK` 写 Python 宿主程序
- 把“手工聊天触发”改成“程序化调度”
- 增加 challenge state、日志、任务队列、批量运行、自动提交等能力

一句话概括：

- 第一阶段验证“Claude Code 能不能用”
- 第二阶段解决“怎么把它做成系统”

## 为什么第二阶段才做

因为自动化不是第一性问题。

真正的第一性问题是：

- 你的工具是否好用
- 你的攻略是否结构化
- Claude 是否能顺利走完单题工作流

只有这些问题在第一阶段被验证过，第二阶段的 Python 自动化才有意义。

## 这一阶段的总体架构

推荐采用 5 层结构：

### 第 1 层：Orchestrator

你自己的主程序，建议用 Python。

理由：

- CTF 工具生态主要在 Python / shell
- 更容易集成 `pwntools`、`angr`、`z3-solver`、脚本资产
- 更适合做批量跑题、状态机、任务队列

职责：

- 创建 Agent SDK 会话
- 注入 system prompt
- 装载 MCP / custom tools / skills / plugins
- 控制权限模式
- 保存任务状态、日志、工件
- 接受用户任务或比赛平台任务

### 第 2 层：Claude Agent Runtime

这里就是 `Claude Agent SDK`。

职责：

- 运行 agent loop
- 自主决定何时读文件、调用工具、继续推理
- 在多轮里保持上下文
- 调用 Skills

### 第 3 层：CTF Tool Plane

这是你的能力面，建议拆成两类：

1. `Local execution tools`
   - 执行本地命令
   - 调用脚本
   - 操作附件和工件目录

2. `Structured CTF tools`
   - 高层语义工具，而不是裸命令
   - 例如 `analyze_elf`、`scan_web_target`、`extract_archive`、`solve_hash`、`submit_flag`

经验上，裸 `Bash` 很强，但过于宽泛。CTF 场景更适合在保留 `Bash` 的同时，补一批“高层专用工具”，降低 agent 的搜索空间。

### 第 4 层：Knowledge Plane

这一层专门放攻略和经验，不要混在主 prompt 里。

建议来源：

- 你自己的 writeup
- 常见题型 SOP
- 工具使用模板
- exploit 模板
- 某题型的失败案例和判断条件

落地方式：

- `.claude/skills/` 下的 Skills
- 或者一个本地知识库检索工具

建议两者都要：

- 高频套路放 Skills，让模型主动调用
- 长文资料和详细笔记放知识库检索工具，按需提取

### 第 5 层：Sandbox / Isolation

CTF 的对象本来就常常是不可信样本：

- 恶意二进制
- 附件中的脚本
- 需要联网交互的题目环境
- 未知 pcap、文档、镜像

所以不要让 Claude 直接在宿主机裸跑高权限 bash。

推荐最少做到：

- 每个 challenge 一个独立工作目录
- 敏感凭据不进 agent 工作区
- 工具执行放进容器或受限运行时
- 出网做 allowlist
- 比赛平台 token 通过代理或单独提交工具处理

## 这一阶段的实现建议

优先建议：

- 宿主语言：Python
- Claude 集成：`claude-agent-sdk`
- 工具扩展：`MCP + 少量 custom tools`
- 攻略沉淀：`.claude/skills/`
- 权限控制：`acceptEdits` + hooks + allowlist
- 隔离：Docker / nsjail / sandbox runtime

不建议一上来就：

- 只靠超长 prompt
- 只暴露 `Bash`
- 让 agent 直接拿到比赛账号的全量凭据
- 在宿主机上对未知附件和未知二进制直接执行

## 工具接入策略

建议按下面优先级设计工具：

### A. 通用内置工具

先启用 SDK 自带能力：

- `Read`
- `Edit`
- `Write`
- `Glob`
- `Grep`
- `Bash`
- `WebSearch`
- `Skill`

但 `Bash` 不要无限开放，后面要配 hook 和容器。

### B. 高价值 custom tools

先做最小闭环的 6 个：

1. `init_challenge`
   - 创建工作目录
   - 下载附件
   - 解压并整理文件

2. `submit_flag`
   - 只负责向比赛平台提交
   - 不把 token 暴露给模型

3. `query_playbook`
   - 检索本地攻略库 / SOP

4. `run_solver`
   - 在受限环境里执行指定 solver

5. `inspect_artifact`
   - 返回文件类型、hash、基础元信息

6. `spawn_target`
   - 启动 docker 题目环境或连接远端实例

### C. MCP servers

把更复杂、独立性更强的工具做成 MCP：

- `ctf-pwn-mcp`
- `ctf-web-mcp`
- `ctf-re-mcp`
- `ctf-crypto-mcp`
- `ctf-forensics-mcp`
- `ctf-platform-mcp`

这样做的好处：

- 解耦
- 方便单独测试
- 以后可以给别的 agent 复用
- Claude 调用时有更稳定的结构化接口

## 题目状态管理

进入自动化阶段后，每个 challenge 都要有自己的状态：

- 元数据
- 附件路径
- 已执行命令
- 关键观察
- 待办
- 失败尝试
- 候选 flag

否则 agent 容易反复试错和遗忘中间状态。

## 推荐的最小目录结构

```text
ctfagent/
├── app/
│   ├── main.py
│   ├── orchestrator.py
│   ├── session_store.py
│   ├── challenge_state.py
│   └── prompts/
│       └── system_prompt.md
├── mcp/
│   ├── ctf-platform/
│   ├── ctf-pwn/
│   ├── ctf-web/
│   └── ctf-re/
├── .claude/
│   ├── skills/
│   │   ├── pwn-initial-recon/
│   │   │   └── SKILL.md
│   │   ├── web-sqli-triage/
│   │   │   └── SKILL.md
│   │   └── crypto-encoding-decision-tree/
│   │       └── SKILL.md
│   ├── agents/
│   │   ├── pwn-specialist.md
│   │   └── web-specialist.md
│   └── settings.json
├── knowledge/
│   ├── writeups/
│   ├── playbooks/
│   └── templates/
├── workspaces/
│   └── <challenge-id>/
├── docs/
│   └── phase2-agent-sdk-python-automation.md
└── .mcp.json
```

## 阶段 2 MVP

在第一阶段验证通过后，再做下面 4 步：

### 第一步：先做单题工作流

只支持：

- 手动给题目描述
- 手动给附件路径
- 手动触发 agent
- 本地保存分析过程

目标：

- agent 能自己整理附件
- 会调用知识和工具
- 能产出中间分析结论

### 第二步：只打一个题型

先选一个你最熟的方向：

- Web
- Pwn
- Reverse

建议优先 `Web` 或 `Reverse`。

原因：

- Web 更容易工具化和 checklist 化
- Reverse 更容易离线工作，不依赖比赛网络状态

不建议先做 Pwn 全自动，因为环境变量更多，利用链更脆弱。

### 第三步：把攻略从 prompt 迁到 Skills

这是关键分水岭。

如果你一开始把 SOP 直接写在 system prompt 里，后期会越来越乱。
应该尽快把题型经验拆成 Skills，让 Claude 按需调用。

### 第四步：把高频工具 MCP 化

当某些流程稳定后，再把它们从 bash 脚本升级为 MCP server。

判断标准：

- 经常调用
- 参数结构稳定
- 输出可结构化
- 需要独立测试

## 阶段 2 后续增强

MVP 跑通后，再做这些：

1. 题型路由
2. 多 agent 协作
3. 回放与评测
4. 工件索引
5. 经验蒸馏

## 第二阶段开始前要满足的条件

下面这些事成立，才值得进入第二阶段：

1. Claude Code 已经能稳定完成单题分析
2. 你的 Skills 和工具已经比较稳定
3. 你已经识别出高频重复动作
4. 你明确需要批量化、评测或自动提交

