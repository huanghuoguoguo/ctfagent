# CTFAgent

`CTFAgent` 是一个以 `Claude Code` 为前门的 CTF 工作仓库。

你不需要先读完内部设计，也不需要先学会仓库里的脚本。默认使用方式就是：

1. 配好 `Claude Code`
2. 进入这个仓库
3. 运行 `/setup`
4. 把题目交给它

## 快速开始

1. 安装并打开 `Claude Code`。
2. 在这个仓库根目录启动会话。
3. 配置你自己的 Claude Code 账号或仓库本地设置。
4. 在会话里直接运行 `/setup`。

如果这个仓库使用本地配置文件，就编辑：

- `.claude/settings.local.json`

你至少需要确认这些内容已经按你自己的环境配置好：

- 模型
- API endpoint
- 认证信息
- 你希望允许的工具权限

不要直接沿用别人仓库里的敏感配置。

## `/setup` 会做什么

`/setup` 是这个仓库的用户入口。它会帮助你完成这些事：

- 用几句话介绍这个项目该怎么用
- 检查 Claude Code 还缺不缺关键配置
- 告诉你开始一道题至少要提供什么信息
- 在信息足够时帮你整理 challenge workspace
- 告诉你下一步该继续做什么

也就是说，正常情况下你不需要先手动建目录、翻技能列表、找初始化脚本。

## 你只需要准备什么

把下面这些信息尽量给全即可：

- 题目标题
- 题目分类
- 题目描述
- 目标 URL / 主机 / 端口 / 连接方式
- 附件路径
- 限制条件

你可以直接这样说：

```text
/setup

题目标题：Internal Resource Viewer
分类：web
目标：http://127.0.0.1:8080/
附件：/path/to/app.zip
题目描述：The site previews internal resources.
限制：先做低成本验证，不要直接爆破。
```

如果这些信息已经给全，`/setup` 会直接创建 workspace。

如果信息还不完整，`/setup` 会继续向你补齐最小必要字段。

## 开始之后会发生什么

当题目信息足够时，agent 会把它整理成一个可持续工作的 workspace，然后继续进入后续分析流程。

你可以把这个仓库理解成：

- `Claude Code` 负责对话、分析、调度
- 仓库负责提供稳定的 workspace、skills、知识库和本地工具

但这些内部细节不需要成为你的起点。你的起点就是 `/setup`。

## 文档在哪里

根目录 `README` 只保留上手信息。

如果你之后想看内部设计、工作流和文档总览，请去：

- [docs/README.md](docs/README.md)
