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

1. `challenge-workspace-bootstrap` - 初始化题目 workspace
2. `ctf-solver-profile` - 建立 evidence-first 解题姿势
3. 一个具体题型 `Skill`（如 `web-ssrf-to-rce-triage`、`web-sqli-triage`、`web-jwt-triage`、`pwn-initial-recon`）
4. `browser-automation-playwright` - 需要 XSS 验证、DOM 提取、截图等浏览器操作时
5. `network-search-ddg` - WebSearch 不可用时查 CVE、工具文档
6. `ctf-knowledge-capture` - 保存解题结果到知识库

这条顺序的意义是：

- 先固定题目入口
- 先建立 evidence-first 的解题姿势
- 再进入具体题型流程
- 需要时调用浏览器自动化和网络搜索
- 最后把结果沉淀回知识库

### 3. 用知识库回查历史经验

```bash
python3 scripts/query_markdown.py --kind writeup --category web --tag sqlite --json
```

`knowledge/` 里的 Markdown 使用统一 frontmatter，既方便人读，也方便 agent 检索。

### 4. 用本地靶场做回归验证

当前内置的靶场包括：

- `targets/web-ssrf-lab/`
- `targets/web-sqli-lab/`
- `targets/web-rce-lab/`
- `targets/web-ssti-lab/`
- `targets/web-jwt-lab/`
- `targets/web-xss-lab/`
- `targets/web-advanced-chain/`
- `targets/pwn-ret2win-lab/`
- `targets/pwn-ret2libc-lab/`

例如启动 SQLite blind SQLi 靶场：

```bash
cd targets/web-sqli-lab
docker compose up -d
```

例如编译一个本地 pwn lab：

```bash
cd targets/pwn-ret2win-lab
make
```

### 5. 如果要完整使用浏览器/XSS 能力，先装 Playwright 依赖

`browser-automation-playwright` 和 `web-xss-triage` 这类能力，除了 Python 包之外，还依赖 Chromium 的系统库。

推荐安装顺序：

```bash
pip3 install playwright
playwright install chromium
```

如果要安装 Chromium 的 Linux 系统依赖，优先用：

```bash
which playwright
sudo /home/yhh/.local/bin/playwright install-deps chromium
```

如果 `sudo` 下找不到 `playwright`，直接手动安装这些库：

```bash
sudo apt-get update
sudo apt-get install -y \
  libgbm1 \
  libnss3 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libcups2 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libcairo2 \
  libatspi2.0-0 \
  libgtk-3-0
```

安装完成后，建议验证：

```bash
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py check
```

## 我们的工作方式

这个仓库不是把 agent 当成“万能解题黑盒”来用。

更接近的做法是：

1. 先把题目整理成稳定 workspace
2. 再让 `Claude Code` 按 evidence-first workflow 做判断
3. 只有在证据足够时，才切到具体题型 `Skill`
4. 让 `scripts/` 承担高频动作，避免每次临场手搓
5. 用 `targets/` 回归验证 skill 和 exploit path
6. 最后把结论和模式沉淀回 `knowledge/`

也就是说，这个 agent 的能力不是只长在聊天上下文里，而是长在下面这些资产的组合上：

- `Skills`：规定某类题先看什么、先试什么、什么情况下切方向
- `scripts/`：把高频探针、提取、脚手架动作固定成稳定接口
- `targets/`：给 skill 和 exploit path 一个能回归的本地样例
- `knowledge/`：把一次次具体题目的经验抽成可复用 pattern
- `workspaces/`：把每道题的输入、笔记和工件固定下来
- `skill-maintainer`：把解题反馈转成最小维护动作，避免 skill 树无控制膨胀

## Agent 是怎么增强的

这个仓库增强 agent，不靠“再写一段更长的 prompt”，而是靠持续建设可复用资产。

增强路径大致是这样的：

1. 先在真实题目里暴露一个高频问题
2. 把这类问题的最小验证顺序整理成一个 `Skill`
3. 把重复动作收成脚本，而不是留在描述里
4. 给这个 skill 配一个本地 lab，确认流程真的能跑通
5. 给核心脚本补一个轻量测试，防止后面越改越飘
6. 把真实题目的成功路径和误判路径沉到 `knowledge/`
7. 再回头改 skill，让它越来越像“走得通的 SOP”，而不是“看起来懂”

这意味着 agent 每强一点，背后通常都对应一次明确的资产增量：

- 多了一个题型 `Skill`
- 多了一个薄脚本
- 多了一个本地靶场
- 多了一条知识 pattern
- 多了一条测试或回归样例

## 一次迭代怎么做

我们当前更偏好的迭代单位，不是一次做很多题型，而是一次补齐一条能力切片。

一个完整切片通常包括：

1. 一个明确题型或 exploit phase
2. 一个 `SKILL.md`
3. 一个或多个薄脚本
4. 一个最小本地 lab
5. 一个轻量测试
6. `README.md`、`CLAUDE.md`、`docs/` 的同步更新

最近几次迭代就是按这个方式推进的：

- `web-ssti-triage`：skill + probe 脚本 + Flask/Jinja2 lab + 测试
- `pwn-stack-overflow-exploit-dev`：skill + exploit scaffold + ret2win/ret2libc lab + 测试
- `web-jwt-triage`：skill + JWT 工具脚本 + 本地 lab + 测试

现在还多了一层维护能力：

- `skill-maintainer`：把一次解题后的反馈分类成 `update_skill`、`new_script`、`new_target`、`new_test`、`new_pattern`、`new_skill` 或 `backlog_only`

它的作用不是继续堆 skill，而是控制增长方向。

默认优先级是：

1. 更新已有 skill
2. 加薄脚本
3. 加测试
4. 加 lab
5. 加 pattern
6. 最后才允许新增 skill

这种做法的好处是，仓库不会被一堆“只有名字的 skill”淹没。

每次新增能力，都必须同时回答：

- agent 到底该怎么想
- agent 到底该怎么做
- 这个做法有没有本地样例能验证
- 以后改动时怎么知道自己没改坏

如果这些问题答不出来，就先进 `knowledge/skill-backlog.md`，而不是立刻加新 skill。

## 我们怎么判断这条路是不是对的

如果这套工作方式是有效的，仓库会越来越明显地呈现出这些特征：

- 新题进入仓库后，不需要从零组织上下文
- agent 更少乱试 payload，更早做出正确分流
- 一类题第二次出现时，不需要从聊天历史里重新发明流程
- 脚本和靶场越来越多，纯文字 SOP 越来越少
- 成功经验不只留在单篇 writeup 里，而会回流到 skill 和 pattern

所以这个项目的目标不是“把 agent 包装得像什么都懂”。

目标是把 `Claude Code + Skills + scripts + targets + knowledge + workspaces` 组织成一套能持续迭代、持续验证、持续积累的 CTF 工作流。

## 当前 Skills

当前已实现 **14 个核心 skill**，位于 [.claude/skills/](/home/yhh/ctfagent/.claude/skills)：

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

### `web-deserialization-triage`

作用：

- Java/Python/PHP 反序列化漏洞检测
- 自动识别序列化格式（Java `rO0AB`, Python `gASV`, PHP `O:8:`）
- 支持 ysoserial、pickle、phar 等 gadget chain
- 从格式检测推进到 RCE payload 生成

### `web-ssti-triage`

作用：

- 处理 server-side template injection 初筛
- 用小探针区分 Jinja2、Twig、Freemarker、ERB/JSP 风格
- 先确认表达式执行，再做对象读取和后续升级
- 默认配合 `targets/web-ssti-lab/` 做回归验证

### `web-jwt-triage`

作用：

- 处理基于 JWT 的认证和授权初筛
- 自动解码 header / payload，提示 `alg`、`kid`、`jku`、`jwk` 风险点
- 支持 `alg=none` token 构造、弱 HS256 secret 重签名、简单字典爆破
- 默认配合 `targets/web-jwt-lab/` 做回归验证

### `web-xss-triage`

作用：

- 处理 reflected 和 DOM-based XSS 初筛
- 先判断 payload 是否反射，以及反射在 HTML、属性还是脚本上下文
- 默认复用 `browser-automation-playwright` 做真实浏览器执行验证
- 默认配合 `targets/web-xss-lab/` 做回归验证

### `pwn-initial-recon`

作用：

- ELF 二进制分析起手式
- 自动检测保护机制（NX、Canary、PIE、RELRO）
- libc 版本识别和符号分析
- 检测危险函数（gets、strcpy、printf 等）
- 输出推荐利用策略（ret2system、ROP、one_gadget 等）

### `pwn-stack-overflow-exploit-dev`

作用：

- 承接 `pwn-initial-recon` 的 JSON 输出
- 自动生成 `ret2win`、`ret2libc` 或通用 overflow 的 pwntools exploit 骨架
- 固定 offset、泄漏、二阶段利用的起手顺序
- 默认配合 `targets/pwn-ret2win-lab/` 和 `targets/pwn-ret2libc-lab/` 做本地回归

### `browser-automation-playwright`

作用：

- 无头浏览器控制（无需 GUI）
- XSS payload 验证和 console 捕获
- DOM 内容提取（JavaScript 渲染后的页面）
- 截图、Cookie/Session 操作、表单自动化
- 支持多步骤 action chain

### `network-search-ddg`

作用：

- 当 Claude Code 内置 WebSearch 不可用时备用
- DuckDuckGo 网络搜索
- CTF 技术研究、CVE 查询、工具文档查找

### `ctf-knowledge-capture`

作用：

- 把已解题目沉淀成 `knowledge/writeups/`
- 抽取可复用的 exploit chain 到 `knowledge/patterns/`
- 让后续题目可以检索、对照和复用

### `skill-maintainer`

作用：

- 把解题后的反馈分类成最小维护动作
- 默认优先更新已有 skill，而不是继续建新目录
- 检查 skill 清单、文档入口和 roadmap 是否漂移
- 把一次性想法先沉到 `knowledge/skill-backlog.md`，避免仓库熵增

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
