# 仓库定位

更新时间：2026-03-29

## 这是什么

`CTFAgent` 是一个以 `Claude Code` 为前门的 CTF 工作仓库。

它的目标不是做一个重型宿主程序，而是把解题时真正可复用的东西组织起来，让 agent 更稳定地分析、验证、沉淀和复用。

这轮整理的标准是：

- 便于维护
- 便于理解和查看
- 便于 agent 解题

## 这不是什么

当前它不是：

- 自动批量跑题平台
- 比赛平台集成层
- 统一状态机或任务编排器
- 默认自动提交 flag 的系统

## 核心资产

- `.claude/skills/`
  - 题型 SOP、前门流程、维护约束
- `scripts/`
  - 高频薄工具
- `knowledge/`
  - writeup、pattern、索引
- `targets/`
  - 本地靶场和回归样例
- `workspaces/`
  - 单题工作目录

## 当前主线

当前主线很简单：

1. 用户配置 `Claude Code`
2. 用户运行 `/setup`
3. agent 整理 challenge workspace
4. agent 按证据切到具体 skill
5. 结果沉淀回 `knowledge/`

## 为什么当前默认不需要 platform

如果用户已经能直接把题目描述、URL、附件路径交给 `Claude Code`，那么仓库已经可以开始工作。

当前默认不需要额外 platform，因为：

- 页面访问和解题分析由 `Claude Code` 完成
- 题目整理由 `/setup` 和 workspace 完成
- 经验沉淀由 `knowledge/` 完成

platform 只在下面这些场景才有价值：

- 自动拉题
- 自动下载附件
- 动态申请或重置实例
- 统一提交 flag
- 屏蔽不同比赛平台的差异

## 设计取向

当前优先建设的是：

- 可复用的 skill
- 薄脚本
- 本地回归靶场
- Markdown 知识库

当前不优先建设的是：

- 重型 orchestration
- 批量自动化
- 大而全的平台适配
- 复杂状态总线
