# 当前工作流：直接用 Claude Code 解题

更新时间：2026-03-28

## 目标

当前工作流解决的是：如何让 `Claude Code` 在真实 CTF 场景里，稳定地完成单题分析、工具调用、知识回查和结果沉淀。

这不是“全自动跑题”流程，而是一条高反馈、可验证、可积累的对话式工作流。

## 当前能跑通的解题链路

一条完整的单题流程通常是：

1. 初始化 challenge workspace
2. 让 `Claude Code` 读取题面、附件和限制
3. 先调用 `ctf-solver-profile` 约束解题姿势
4. 根据证据切换到具体题型 `Skill`
5. 调用本地工具、脚本、靶场完成验证
6. 记录工件、结论和失败路径
7. 解完后沉淀到 `knowledge/`

这条链路已经对应到仓库里的现有资产：

- `scripts/init_challenge.py`
- `scripts/show_challenge.py`
- `scripts/query_markdown.py`
- `.claude/skills/ctf-solver-profile/`
- `.claude/skills/challenge-workspace-bootstrap/`
- `.claude/skills/web-ssrf-to-rce-triage/`
- `.claude/skills/web-sqli-triage/`
- `.claude/skills/ctf-knowledge-capture/`
- `knowledge/writeups/`
- `knowledge/patterns/`
- `targets/`

## 输入是什么

当前工作流的输入很简单：

- 题目描述
- 附件路径
- 目标 URL、端口或连接方式
- 题目限制条件

为了让输入稳定，建议统一整理到 `workspaces/<challenge-id>/` 下：

```text
workspaces/
└── <challenge-id>/
    ├── challenge.md
    ├── metadata.json
    ├── attachments/
    ├── notes.md
    └── artifacts/
```

其中：

- `challenge.md` 负责给 `Claude Code` 直接阅读
- `metadata.json` 负责结构化字段
- `notes.md` 负责 challenge 级过程记录
- `artifacts/` 负责保存脚本、导出文件和中间产物

## Claude 在这条工作流里的职责

`Claude Code` 不是“替你记住所有 CTF 技巧的黑盒”。

更合理的职责分工是：

- `Claude Code` 负责推理、规划、调度、总结
- `Skills` 负责提供题型 SOP 和切换规则
- `scripts/` 与后续 `MCP` 负责提供能力接口
- `knowledge/` 负责提供可检索历史经验
- 你负责定义边界、工具、权限和回归方式

## 当前推荐使用方式

### 1. 先整理 challenge

把题目标准化到 workspace。

这样做的价值是：

- 题面入口固定
- 附件路径固定
- 工件位置固定
- 后续沉淀更容易

### 2. 先走 solver posture，再走题型 skill

不要一开始就让模型直接生成长 payload 或盲目爆破。

推荐顺序是：

1. `challenge-workspace-bootstrap`
2. `ctf-solver-profile`
3. 一个具体题型 `Skill`
4. `ctf-knowledge-capture`

### 3. 优先做低成本验证

当前工作流强调：

- 先读源码和元信息
- 先做短探针验证
- 先找证据，再升级攻击链
- 先记录失败路径，再切方向

### 4. 用知识库回查历史模式

如果发现题型与历史 writeup 或 pattern 相似，应优先回查 `knowledge/`，而不是每次从零开始。

### 5. 解完后立刻沉淀

解题结束不是流程终点。

应把以下内容沉淀回仓库：

- 关键观察
- 触发条件
- 成功路径
- 失败路径
- 可复用 pattern

## 当前最适合接入什么

优先建设：

- `Skills`
- 查询和整理类脚本
- 本地靶场
- 知识沉淀
- 少量高频工具封装

当前不应优先建设：

- Python orchestration
- 复杂任务编排
- 自动批量跑题
- 复杂状态机
- 大而全的比赛平台集成

## 当前工作流的效果

这条工作流的核心效果不是“自动化程度高”，而是“单题分析质量和复用性更高”。

它带来的直接收益包括：

- 新题进入统一工作目录
- 题型思路可以复用
- 工具使用方式更稳定
- 解题经验可搜索、可追溯
- 已有结论可以在靶场回归验证

## 当前边界

当前工作流默认只解决这些问题：

- 单题分析
- 人在回路中的工具调用
- 本地知识回查
- 工件与结论沉淀

它暂时不默认解决：

- 批量题目调度
- 自动 flag 提交
- 统一状态总线
- 多 agent 编排

如果未来这些问题变成真实瓶颈，再进入下一阶段即可。

## 当前工作流已经跑顺的标志

下面几件事成立，就说明第一阶段已经具备稳定价值：

1. Claude Code 能独立完成单题多步分析
2. 它会稳定调用你的工具和攻略
3. 你能明确看出高频重复动作
4. 你已经知道哪些能力下一步要程序化
