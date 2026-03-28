# Challenge Workspace 与平台边界

更新时间：2026-03-28

## 目标

这份文档只回答一个问题：一题在本地应该如何组织，以及哪些职责应该属于 workspace、`Skill`、工具层和平台层。

当前这份约定服务于 Phase 1 主线：

- 让 `Claude Code` 能直接读取并处理 challenge
- 让结果可以稳定沉淀和回归
- 给未来自动化保留清晰边界，但不提前把逻辑塞进宿主程序

## 核心原则

### 1. 先让 challenge 对人和模型都可读

workspace 不是数据库，也不是隐藏状态容器。

它首先应该做到：

- 人能直接打开看
- `Claude Code` 能直接读取
- 手工创建和修正成本低
- 后续程序化处理也方便

### 2. 解题逻辑与平台逻辑分离

解题逻辑属于：

- `Skills`
- `knowledge/`
- solver workflow

平台逻辑属于：

- 拉题
- 下载附件
- 获取靶机地址
- 启动实例
- 提交 flag

不要把平台细节写进 `Skill`，也不要把题型经验写进平台适配层。

### 3. 结构先稳定，再谈自动化

只要 workspace 结构稳定，后续无论是脚本、`MCP` 还是 Python 宿主程序，都只是围绕这套结构做读写。

程序不应该承载核心解题知识。

## 推荐 workspace 结构

```text
workspaces/
└── <challenge-id>/
    ├── challenge.md
    ├── metadata.json
    ├── attachments/
    ├── notes.md
    └── artifacts/
```

## 各文件职责

### `challenge.md`

这是当前最重要的题面入口文件，优先给 `Claude Code` 阅读。

建议包含：

- 题目标题
- 分类
- 平台来源
- URL / 连接信息
- 题目正文
- 附件列表
- 限制条件

### `metadata.json`

这是结构化元数据入口，服务于脚本查询和后续自动化。

建议最少包含：

- `id`
- `title`
- `category`
- `platform`
- `platform_id`
- `url`
- `attachments`
- `tags`
- `status`

### `notes.md`

这是 challenge 级工作笔记，记录当前题的过程性信息：

- 假设
- 已验证线索
- 死路
- 临时 payload
- 未整理的命令摘要

它不是最终 writeup。

### `artifacts/`

这里保存与当前题强绑定的工件，例如：

- exploit 脚本
- 导出的源码
- 解密中间文件
- 抓包结果
- 反编译产物

## 与 `Skills` 的边界

应该放在 `Skills` 里的内容：

- 什么时候调用
- 先做哪几步
- 哪些结果意味着切换方向
- 哪些工具优先
- 常见误判与避坑

不应该放在 `Skills` 里的内容：

- 平台账号信息
- 拉题逻辑
- 附件下载逻辑
- flag 提交逻辑
- 与某个平台强绑定的字段处理

## 与工具层的边界

工具层负责“执行能力”，例如：

- 初始化 workspace
- 查询知识库
- 展示 challenge 元数据
- 执行扫描器
- 启动靶场

如果某个能力满足“高频、参数稳定、输出可结构化”，就适合往 `MCP` 或 custom tool 方向演化。

## 与平台层的边界

平台层只负责和题目来源、实例、提交目标交互。

平台层典型职责：

- 拉取题面
- 下载附件
- 获取连接信息
- 启动或查询远端实例
- 提交 flag

平台层不负责：

- 题型判断
- payload 选择
- exploit 决策
- writeup 结论

## 为什么这套边界有效

这样划分之后：

- workspace 保持清晰且可读
- `Claude Code` 有稳定入口可读题
- skill 可以专注沉淀方法而不是平台细节
- 工具层可以逐步结构化，而不是一开始就过度设计
- 未来如果接入 BUUCTF、CTFd 或其他平台，也不会污染解题逻辑

这套边界本质上是在保证一件事：仓库的核心资产始终是解题能力本身，而不是平台接线代码。
