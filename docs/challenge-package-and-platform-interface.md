# Challenge Package 与 Platform Interface 约定

更新时间：2026-03-28

## 目标

这份文档定义当前仓库自己的 challenge 组织方式与 platform 接口边界。

它的作用不是马上进入 Phase 2 自动化，而是先把下面几件事定清楚：

1. 一个 challenge 在本地应该长什么样
2. `Claude Code` 在 Phase 1 应该从哪里读取题目信息
3. 后续如果接 BUUCTF、CTFd 或其他平台，接口边界在哪里
4. 什么应该放在 `Skill`，什么应该放在 platform 层

这份约定应服务于当前主路线：

- **Phase 1：`Claude Code` 对话驱动解题**
- **扩展优先：`Skills` 与 `MCP`**
- **Phase 2：再进入 Python 程序驱动**

## 设计原则

### 1. 先服务 Phase 1

当前最重要的是让 `Claude Code` 能直接基于本地 challenge 包进行对话式解题。

所以 challenge 格式必须：

- 简单
- 可手工创建
- 对模型可读
- 对后续程序化也友好

### 2. 解题逻辑与平台逻辑分离

解题逻辑属于：

- `Skills`
- `knowledge/`
- solver workflow

平台逻辑属于：

- 拉题
- 附件下载
- 靶机地址获取
- flag 提交

不要把平台细节混进 skill。

### 3. 结构先定，自动化后补

现在可以先手动维护 challenge 包。

后续 Python 程序只负责：

- 生成 challenge 包
- 更新 metadata
- 下载附件
- 提交 flag

程序不应该承载核心解题知识。

## 推荐目录结构

每个 challenge 未来都应有一个独立目录：

```text
workspaces/
└── <challenge-id>/
    ├── challenge.md
    ├── metadata.json
    ├── attachments/
    ├── notes.md
    └── artifacts/
```

说明：

- `challenge.md`：给 `Claude Code` 直接阅读的题面入口
- `metadata.json`：结构化字段，方便后续自动化
- `attachments/`：原始附件
- `notes.md`：当前 challenge 的临时过程记录
- `artifacts/`：脚本、抓包、导出文件、样本、截图等工件

## 文件职责

### `challenge.md`

这是 Phase 1 最重要的文件。

它应包含：

- 题目标题
- 题目分类
- 平台来源
- 目标 URL 或连接方式
- 题目正文
- 附件列表
- 限制条件

建议格式：

```md
# Challenge Title

- Category: web
- Platform: manual
- URL: http://target:port
- Attachments:
  - attachments/app.zip

## Description

...

## Constraints

...
```

### `metadata.json`

这是给后续平台适配与自动化准备的结构化文件。

建议最小字段：

```json
{
  "id": "",
  "title": "",
  "category": "",
  "platform": "manual",
  "platform_id": "",
  "url": "",
  "attachments": [],
  "tags": [],
  "status": "new"
}
```

字段说明：

- `id`：本地 challenge 标识
- `title`：题目名
- `category`：`web/pwn/rev/crypto/misc/forensics`
- `platform`：如 `manual`、`buuctf`、`ctfd`
- `platform_id`：平台侧题目 ID
- `url`：靶机地址
- `attachments`：附件路径列表
- `tags`：可选标签
- `status`：如 `new/in-progress/solved`

### `notes.md`

这是 challenge 级别的临时过程记录，不等同于最终 `knowledge/writeups/`。

它适合记录：

- 当前假设
- 已验证的线索
- 死路
- 临时 payload
- 未整理的命令输出摘要

challenge 解完后，应将最终结论沉淀到 `knowledge/`，而不是只留在 `notes.md`。

### `artifacts/`

用于保存：

- exploit 脚本
- 抓包结果
- 导出的源码
- 解密中间文件
- 反编译产物
- challenge 专用工具脚本

## Platform Interface 目标

platform 层只负责与题目来源和提交目标交互，不负责解题。

当前建议定义两个核心接口：

1. `QuestionInputer`
2. `FlagSubmitter`

## `QuestionInputer`

作用：

- 拉取题面
- 获取靶机地址
- 下载附件
- 生成本地 challenge 包

一个输入器最终至少应产出：

- `challenge.md`
- `metadata.json`
- `attachments/`

### 推荐最小抽象

```python
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ChallengeInfo:
    id: str
    title: str
    category: str
    content: str
    platform: str = "manual"
    platform_id: str = ""
    url: str = ""
    attachments: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
```

```python
class QuestionInputer:
    def fetch(self) -> ChallengeInfo:
        ...
```

## `FlagSubmitter`

作用：

- 接收候选 flag
- 根据 challenge metadata 定位题目
- 提交到平台或进行人工确认

推荐最小抽象：

```python
from dataclasses import dataclass


@dataclass
class SubmitResult:
    success: bool
    message: str = ""
```

```python
class FlagSubmitter:
    def submit(self, flag: str, challenge: ChallengeInfo) -> SubmitResult:
        ...
```

## 当前阶段推荐实现

虽然接口现在就应定义，但 Phase 1 只建议先实现最小版本：

### Inputer

- `manual`：手动填写 challenge 包
- `file`：从本地题面文件和附件目录生成 challenge 包

### Submitter

- `manual`：手动确认 flag 是否正确

先不要急着实现：

- BUUCTF 自动拉题
- CTFd 自动拉题
- 平台自动提交
- 复杂账号管理

这些应放到 Phase 2。

## 与 Skills 的边界

### 应该由 `Skills` 处理

- 题型识别后的分析流程
- 低成本验证顺序
- 常见 payload 选择
- exploit chain 决策
- 记录哪些信息值得沉淀到 `knowledge/`

### 不应该由 `Skills` 处理

- 平台 cookie
- 拉题接口细节
- 提交 API
- 附件下载认证流程
- challenge 状态同步

如果一个 skill 里出现大量平台字段，说明边界已经错了。

## 与 `knowledge/` 的边界

### Challenge Package

保存单题当前上下文：

- 题面
- 附件
- 当前 notes
- 当前 artifacts

### `knowledge/`

保存可复用知识：

- 解题复盘
- exploit pattern
- skill 应更新的规则

一个 challenge 解完后：

1. 保留 `workspaces/<challenge-id>/`
2. 产出 `knowledge/writeups/<category>/...`
3. 如有共性，产出或更新 `knowledge/patterns/<category>/...`

## 与 `targets/` 的关系

`targets/` 不是 challenge package。

`targets/` 的职责是：

- 本地靶场
- skill 回归验证
- 漏洞模式测试

它更接近“训练与回归环境”，不是单题工作区。

## 当前推荐工作流

在 Phase 1 中，建议采用：

1. 为新题创建 `workspaces/<challenge-id>/`
2. 手工写入 `challenge.md`
3. 补齐 `metadata.json`
4. 放入 `attachments/`
5. 用 `Claude Code` 结合 `ctf-solver-profile` 开始解题
6. 按题型调用对应 `Skill`
7. 在 `notes.md` 和 `artifacts/` 中保留过程
8. 解完后调用 `ctf-knowledge-capture`

## 什么时候再程序化

只有在下面这些能力稳定后，才建议继续实现真正的 platform 代码：

1. challenge 包结构已经稳定
2. 你已经知道 metadata 里哪些字段真的有用
3. 你已经明确哪些平台需要接
4. 你已经明确附件下载与 flag 提交的边界
5. 你已经不再频繁修改解题主流程

## 当前结论

对你们来说，吸收别的 CTF Agent 项目时，最值得借鉴的是：

- challenge 数据结构
- platform input / submit 边界
- 附件处理方式
- 本地靶场组织方式

最不值得直接搬的是：

- agent 编排
- prompt 外壳
- UI
- 多模型调度

当前最合理的做法，是先把 challenge package 和 platform interface 定成你们自己的标准，再让 `Skills`、`knowledge/`、`targets/` 围绕这个标准协同。
