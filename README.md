# CTFAgent

`CTFAgent` 是一个以 `Claude Code` 为核心的 CTF 工作仓库。

当前主线不是再造一个 Python 宿主 Agent，而是把真正能提升打题效率的资产沉淀出来：

- `Skills`：题型 SOP、决策顺序、分支切换规则
- `knowledge/`：可搜索、可追溯的本地 Markdown 知识库
- `scripts/`：给 `Claude Code` 直接调用的薄工具
- `targets/`：本地靶场和回归样例

## 当前定位

这个仓库当前处于 Phase 1：

- 主 agent 是 `Claude Code`
- 工作流是对话驱动
- 人在回路中
- 优先打磨 `Skills`、本地工具、知识沉淀和回归靶场

这意味着：

- `cc` 负责推理、规划、调用工具和整理结论
- Python 代码只做辅助，不承担完整 orchestration
- 默认使用 Markdown 作为知识真源，而不是先引入数据库

相关设计文档：

- [docs/phase1-claude-code-ctf-workflow.md](/home/yhh/ctfagent/docs/phase1-claude-code-ctf-workflow.md)
- [docs/phase1-cc-first-development-strategy.md](/home/yhh/ctfagent/docs/phase1-cc-first-development-strategy.md)
- [docs/phase2-agent-sdk-python-automation.md](/home/yhh/ctfagent/docs/phase2-agent-sdk-python-automation.md)

## 已有能力

### 1. Challenge Workspace Bootstrap

新题先整理成统一目录：

```text
workspaces/<challenge-id>/
├── challenge.md
├── metadata.json
├── attachments/
├── notes.md
└── artifacts/
```

脚本入口：

```bash
python3 scripts/init_challenge.py \
  --title "Internal Resource Viewer" \
  --category web \
  --url http://127.0.0.1:8080/ \
  --content "The site previews internal resources."
```

查看已整理题目：

```bash
python3 scripts/show_challenge.py workspaces/internal-resource-viewer
```

### 2. Markdown Knowledge Base

知识库保存在 `knowledge/` 下，使用统一 frontmatter 元数据，便于 agent 检索：

- `doc_kind`
- `title`
- `category`
- `slug`
- `created`
- `status`
- `tags`

查询脚本：

```bash
python3 scripts/query_markdown.py --kind writeup --category web --tag sqlite --json
```

说明：

- Markdown 是 source of truth
- frontmatter 负责 agent 可检索元数据
- 如果以后需要更快检索，可以在 Markdown 之上派生 SQLite / 向量索引，但不反转为主存储

### 3. Skills

当前已实现的技能：

- `ctf-solver-profile`
- `challenge-workspace-bootstrap`
- `web-ssrf-to-rce-triage`
- `web-sqli-triage`
- `ctf-knowledge-capture`

这些 skill 位于：

- [.claude/skills/](/home/yhh/ctfagent/.claude/skills)

### 4. Local Labs

仓库内置了若干本地靶场用于回归验证：

- `targets/web-ssrf-lab/`
- `targets/web-sqli-lab/`
- `targets/web-rce-lab/`

例如启动 SQLite blind SQLi 靶场：

```bash
cd targets/web-sqli-lab
docker compose up -d
```

## 典型工作流

1. 用 `scripts/init_challenge.py` 创建 challenge workspace
2. 在 `Claude Code` 中先调用 `ctf-solver-profile`
3. 根据证据切换到具体 skill，例如 `web-sqli-triage`
4. 用本地脚本和靶场完成验证
5. 解完后用 `ctf-knowledge-capture` 沉淀 writeup / pattern
6. 用 `scripts/query_markdown.py` 回查历史知识

## 仓库结构

```text
ctfagent/
├── .claude/skills/      # Claude Code skills
├── ctfagent/            # 薄辅助库：workspace / markdown / query
├── docs/                # 路线与设计文档
├── knowledge/           # 本地 writeup / pattern 知识库
├── scripts/             # 可直接被 cc 调用的工具脚本
├── targets/             # 本地靶场
└── tests/               # 基础测试
```

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 原则

- 不把 Phase 1 做成另一个独立 Agent 框架
- 优先沉淀对 `cc` 真正有复用价值的东西
- 优先 Markdown 可读性和 Git 可追溯性
- 有检索需求时，先加元数据和查询脚本，再考虑数据库
