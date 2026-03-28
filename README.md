# CTFAgent

`CTFAgent` 是一个以 `Claude Code` 为核心的 CTF 工作仓库。

它的目标不是先做一个重型宿主程序，而是把真正能提升打题效率的资产组织起来，让 `Claude Code` 在真实题目里更稳定地分析、调用工具、复用经验和沉淀结果。

当前仓库的核心资产包括：

- `Skills`：题型 SOP、决策顺序、切换条件
- `scripts/`：可直接调用的薄工具
- `knowledge/`：本地 Markdown 知识库
- `targets/`：本地靶场和回归样例
- `workspaces/`：每道题的独立工作目录

## 目前能做什么

当前仓库已经可以支撑这样一条单题工作流：

- 把新题整理成统一的 challenge workspace
- 让 `Claude Code` 按既定 solver workflow 做分析
- 根据证据切换到具体题型 `Skill`
- 查询本地历史 writeup 和 exploit pattern
- 保存工件、笔记和解题结论
- 把已验证的方法在本地靶场里回归复现

这意味着它已经不是“临时聊天解题”，而是一套可以持续积累的工作仓库。

## 推荐怎么用

### 1. 先把题目整理成 workspace

```bash
python3 scripts/init_challenge.py \
  --title "Internal Resource Viewer" \
  --category web \
  --url http://127.0.0.1:8080/ \
  --content "The site previews internal resources."
```

生成的目录结构：

```text
workspaces/<challenge-id>/
├── challenge.md
├── metadata.json
├── attachments/
├── notes.md
└── artifacts/
```

查看已整理题目：

```bash
python3 scripts/show_challenge.py workspaces/internal-resource-viewer
```

### 2. 在 `Claude Code` 中按顺序使用 skill

推荐顺序：

1. `challenge-workspace-bootstrap`
2. `ctf-solver-profile`
3. 一个具体题型 `Skill`
4. `ctf-knowledge-capture`

这条顺序的意义是：

- 先固定题目入口
- 先建立 evidence-first 的解题姿势
- 再进入具体题型流程
- 最后把结果沉淀回知识库

### 3. 用知识库回查历史经验

```bash
python3 scripts/query_markdown.py --kind writeup --category web --tag sqlite --json
```

`knowledge/` 里的 Markdown 使用统一 frontmatter，既方便人读，也方便 agent 检索。

### 4. 用本地靶场做回归验证

当前内置的 web 靶场包括：

- `targets/web-ssrf-lab/`
- `targets/web-sqli-lab/`
- `targets/web-rce-lab/`
- `targets/web-advanced-chain/`

例如启动 SQLite blind SQLi 靶场：

```bash
cd targets/web-sqli-lab
docker compose up -d
```

## 当前 Skills

当前已实现 5 个核心 skill，位于 [.claude/skills/](/home/yhh/ctfagent/.claude/skills)：

### `challenge-workspace-bootstrap`

作用：

- 接收散乱的题面、附件目录、目标 URL
- 标准化成 `workspaces/<challenge-id>/`
- 给后续分析提供稳定入口

### `ctf-solver-profile`

作用：

- 规定 evidence-first 的解题姿势
- 强调先做低成本验证，再升级利用链
- 约束题型切换、死路处理和笔记纪律

### `web-ssrf-to-rce-triage`

作用：

- 处理 SSRF 风格 fetcher
- 验证 `file://` 本地文件读
- 分析源码和 localhost-only 行为
- 从 SSRF / LFI / localhost pivot 推进到 RCE 和 flag 提取

### `web-sqli-triage`

作用：

- 处理 web SQL injection 初筛
- 稳定 true/false oracle
- 优先支持 boolean-blind SQLite 风格提取
- 从确认注入推进到最小必要的 schema / flag 抽取

### `ctf-knowledge-capture`

作用：

- 把已解题目沉淀成 `knowledge/writeups/`
- 抽取可复用的 exploit chain 到 `knowledge/patterns/`
- 让后续题目可以检索、对照和复用

## 项目实现了什么效果

当前仓库已经形成了比较清晰的效果闭环：

- 新题不再散落在临时目录里，而是进入统一 workspace
- 解题过程不再只存在于聊天上下文里，而是能留下工件和笔记
- 经验不再只是一篇篇独立 writeup，而是能抽成 pattern 和 skill
- 技能不再只是文档说明，而是可以在 `targets/` 里回归验证
- `Claude Code` 的输出更容易围绕证据和流程组织，而不是随机试 payload

换句话说，这个项目已经把 “Claude Code + 技能 + 本地工具 + 知识库 + 靶场” 组合成了一套能持续演化的 CTF 工作方式。

## 仓库结构

```text
ctfagent/
├── .claude/skills/      # Claude Code skills
├── ctfagent/            # 薄辅助库：workspace / markdown / query
├── docs/                # 设计与使用文档
├── knowledge/           # 本地 writeup / pattern 知识库
├── scripts/             # 可直接被 Claude Code 调用的工具脚本
├── targets/             # 本地靶场
└── tests/               # 基础测试
```

## 文档

- [docs/README.md](/home/yhh/ctfagent/docs/README.md)
- [docs/claude-agent-sdk-ctf-agent-design.md](/home/yhh/ctfagent/docs/claude-agent-sdk-ctf-agent-design.md)
- [docs/phase1-claude-code-ctf-workflow.md](/home/yhh/ctfagent/docs/phase1-claude-code-ctf-workflow.md)
- [docs/challenge-package-and-platform-interface.md](/home/yhh/ctfagent/docs/challenge-package-and-platform-interface.md)

## 测试

```bash
python3 -m unittest discover -s tests -v
```
