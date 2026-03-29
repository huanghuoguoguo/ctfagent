# Workspace 约定

更新时间：2026-03-29

## 目标

workspace 是单题入口，不是隐藏状态系统。

它的目标是让题目对人和 `Claude Code` 都可读，并且有稳定的工件落点。

## 推荐结构

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

- `challenge.md`
  - 给人和模型直接阅读的题面入口
- `metadata.json`
  - 给脚本和后续自动化读取的结构化字段
- `attachments/`
  - 原始附件
- `notes.md`
  - 过程性记录、假设、死路、临时 payload
- `artifacts/`
  - exploit、导出文件、抓包结果、反编译产物等

## 边界

应该写进 workspace 的内容：

- 单题题面
- 单题附件
- 单题笔记
- 单题工件

不应该写进 workspace 的内容：

- 平台拉题逻辑
- flag 提交逻辑
- 通用题型经验
- 平台账号和敏感凭据

## 为什么不是 platform

workspace 解决的是“这道题在本地如何落地”。

platform 解决的是“怎么和题目来源交互”，例如：

- 拉题
- 下载附件
- 申请实例
- 提交 flag

如果当前工作方式已经是直接把题目信息交给 `Claude Code`，那 workspace 是必需的，platform 不是。

## 与其他层的分工

- `Skills`
  - 负责“怎么想、先做什么、何时切方向”
- `scripts/`
  - 负责执行能力
- `knowledge/`
  - 负责沉淀可复用经验
- `workspaces/`
  - 负责当前题目的上下文与产物
