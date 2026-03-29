# Skills Roadmap

更新时间：2026-03-29

这份 roadmap 只回答一个问题：

下一阶段怎样建设 `Skills`，才能让 `CTFAgent` 变强，而不是只把技能数量堆上去。

当前判断很明确：

- 继续完善 `Skills` 这条路线是对的
- 但后面不能再按“想到一个题型就加一个”推进
- 应该同时建设三层东西：
  - 前门工作流约束
  - 具体题型 triage
  - 跨 skill 的回归与质量能力

## 当前阶段的主问题

当前仓库已经有：

- 前门 workflow：`challenge-workspace-bootstrap`、`ctf-solver-profile`
- Web triage：`web-ssrf-to-rce-triage`、`web-sqli-triage`、`web-deserialization-triage`、`web-ssti-triage`、`web-jwt-triage`、`web-xss-triage`
- Pwn 主路径：`pwn-initial-recon`、`pwn-stack-overflow-exploit-dev`
- 支撑能力：`browser-automation-playwright`、`network-search-ddg`
- 结果沉淀：`ctf-knowledge-capture`
- 维护闭环：`skill-maintainer`

当前真正的缺口不是“skill 太少”，而是下面四件事还没完全成体系：

1. 新 skill 的验收标准还不够显式
2. `targets/` 已存在，但还没成为 skill 的硬门槛
3. Pwn 路径正在补齐，但还需要继续扩展到更复杂的 leak / canary / PIE case
4. 新 skill 需要继续保持脚本、lab 和文档同步，而不是只新增目录
5. 需要一个受约束的自维护机制，避免 skill 树重复和膨胀

## 建设原则

后面的 skill 只在满足下面条件时再新增：

1. 能补一条明确主路径，不是只是补知识点
2. 能配一个最小脚本或工具接口，不靠纯口头 SOP
3. 能配一个本地 lab 或回归样例，不做“看起来合理”的文档
4. 能写出清晰退出条件，知道什么时候算“skill 已经够用”

另外再加一条：

5. 如果问题能通过更新已有 skill、加脚本、加测试或加 lab 解决，就不要新建 skill

## 分层看待 skill 系统

### 1. 前门工作流层

负责：

- 统一输入
- 固定 evidence-first 姿势
- 规定 category 切换时机
- 规范沉淀方式
- 约束 skill 系统自身的增长方式

当前已有基础，但还缺“质量门槛”和“回归约束”。

### 2. 题型 triage 层

负责：

- 某一类题从识别到最低成本验证，再到最小必要利用
- 题型边界和误判信号
- 常见分支的升级路径

这是接下来最值得继续扩的层。

### 3. 跨 skill 支撑层

负责：

- 浏览器、搜索、通用分析脚本
- 靶场、fixture、回归 harness
- 报告格式、JSON schema、命名一致性

这层不直接解题，但决定 skill 是否能长期复用。

## 分阶段路线

### Phase 0：先把地基收紧

这一阶段不追求多做 skill，先把“新增 skill 的质量标准”固定下来。

#### 1. `skill-quality-bar-and-doc-alignment`

- 目的：统一 skill 命名、文档入口、backlog 维护方式和验收标准
- 为什么现在做：`CLAUDE.md` 已经出现 backlog 漂移，说明“加 skill”开始快于“整理 skill”
- 依赖：无
- 需要的脚本/工具：
  - 一个轻量检查脚本，检查 `.claude/skills/`、`README.md`、`CLAUDE.md`、`docs/` 的 skill 列表是否一致
- 建议的本地样例：
  - `tests/` 下增加文档一致性测试
- 退出条件：
  - 新增或删除 skill 时，至少有一个自动检查会提示文档未同步

#### 1.5 `skill-maintainer`

- 目的：让 agent 能把解题反馈转成最小维护动作，同时默认优先收敛而不是扩目录
- 为什么现在做：
  - 仓库已经开始形成 skill 树，如果没有维护约束，很快会出现重复、重叠和文档漂移
- 依赖：
  - `ctf-knowledge-capture`
  - `skill-quality-bar-and-doc-alignment`
- 需要的脚本/工具：
  - `skill_gap_report.py`
  - `check_skill_inventory.py`
  - `knowledge/skill-backlog.md`
- 建议的本地样例：
  - 用真实 solve 反馈和文档状态做轻量测试，而不是再建一个虚假题型
- 当前状态：
  - 已落地第一版 skill、反馈分类脚本、库存检查脚本和 backlog 文件
- 退出条件：
  - solve 结束后，agent 能先判断“更新已有资产还是新建目录”，而不是默认加新 skill

#### 2. `regression-target-convention`

- 目的：把 `targets/` 从“有一些 lab”升级成“skill 的标准配套”
- 为什么现在做：现有 web lab 已经证明方向是对的，但还没有统一约束新 skill 必须附什么样的回归样例
- 依赖：`skill-quality-bar-and-doc-alignment`
- 需要的脚本/工具：
  - 一个 `scripts/run_skill_smoke.py` 或类似脚本
  - 每个 lab 至少支持启动、探针、预期结果验证
- 建议的本地样例：
  - `targets/regression-smoke/` 或在每个 `targets/<lab>/` 下补 smoke 说明
- 退出条件：
  - 新增题型 skill 时，能跑一个最小 smoke 流程证明 SOP 不是纸上谈兵

### Phase 1：先补现有主路径的短板

这一阶段优先补 Web 高 ROI 缺口和 Pwn 的后半程。

#### 3. `pwn-stack-overflow-exploit-dev`

- 目的：承接 `pwn-initial-recon`，把 offset、崩溃定位、泄漏、ret2libc/ROP 起手式固定下来
- 为什么现在做：
  - 现在 pwn 只有侦察，没有 exploitation 主路径
  - 没有这个 skill，`pwn-initial-recon` 的价值只能停在“分析报告”
- 依赖：
  - `pwn-initial-recon`
- 需要的脚本/工具：
  - cyclic offset helper
  - pwntools exploit 模板生成
  - 本地/远程切换骨架
  - gdb/gef/pwndbg 命令模板
- 建议的本地样例：
  - `targets/pwn-ret2win-lab/`
  - `targets/pwn-ret2libc-lab/`
- 当前状态：
  - 已落地第一版 skill、scaffold 脚本和 `ret2win` / `ret2libc` 本地 lab
- 后续缺口：
  - 继续补 offset 自动化、canary/PIE 泄漏、更多 ROP 场景
- 退出条件：
  - agent 能从 binary recon 结果直接推进到一个可运行的最小 exploit 骨架

#### 4. `web-jwt-triage`

- 目的：覆盖 JWT 常见失误面，包括 `none`、弱密钥、`kid` 路径问题、`jku/jwk` 混淆和 claim 篡改
- 为什么现在做：
  - Web 里高频且实战常见
  - 但它更像一组分散问题的集合，所以优先级放在 SSTI 后面
- 依赖：
  - `ctf-solver-profile`
- 需要的脚本/工具：
  - header/payload 解码器
  - alg/kid/jku 风险检查脚本
  - 弱密钥和重签名辅助脚本
- 建议的本地样例：
  - `targets/web-jwt-lab/`
  - 至少包含 `alg=none` 和弱密钥两个 case
- 当前状态：
  - 已落地第一版 skill、JWT 工具脚本和包含 `alg=none` + weak secret 的本地 lab
- 后续缺口：
  - 继续补 `kid` / `jku` / `jwk` 场景和更完整的自动请求验证
- 退出条件：
  - agent 能先判断“JWT 问题是密码学问题、配置问题还是业务授权问题”，再进入对应测试路径

### Phase 2：扩题型覆盖，但继续守住质量

这一阶段开始横向扩类目，但仍然要求 lab 和脚本同时到位。

#### 5. `web-xss-triage`

- 目的：把反射型、存储型、DOM 型 XSS 的识别和验证流程与 Playwright 真正接起来
- 为什么现在做：
  - 仓库已经有 `browser-automation-playwright`，但还没有与之配套的 XSS triage skill
  - 这是很明显的“工具已到位、SOP 还缺位”
- 依赖：
  - `browser-automation-playwright`
  - `ctf-solver-profile`
- 需要的脚本/工具：
  - payload 编码/变体生成器
  - DOM sink 检测辅助脚本
  - 浏览器验证模板
- 建议的本地样例：
  - `targets/web-xss-lab/`
  - 至少包含反射型和 DOM 型两个 case
- 当前状态：
  - 已落地第一版 skill、反射上下文探针脚本和包含 reflected/attribute/DOM sink 的本地 lab
- 后续缺口：
  - 继续补 stored XSS、CSP 场景和更完整的自动浏览器 smoke
- 退出条件：
  - agent 不只会“试 payload”，而是能判断上下文、选择编码方式，并用浏览器自动化确认执行

#### 6. `rev-unpack-and-trace`

- 目的：补上基础逆向路径，覆盖 `file/strings`、打包识别、简单解密、动态追踪入口
- 为什么现在做：
  - 当前完全缺 rev 主路径
  - 这是很多“看起来像杂项”的题真正的分流入口
- 依赖：
  - `ctf-solver-profile`
- 需要的脚本/工具：
  - 打包壳/压缩识别
  - 常见字符串和常量抽取
  - 简单 trace/gdb/rizin 模板
- 建议的本地样例：
  - `targets/rev-packme-lab/`
  - `targets/rev-xor-loader-lab/`
- 退出条件：
  - agent 能把“文件像乱码”这件事快速分流成编码、压缩、简单加密还是二进制逻辑

#### 7. `crypto-encoding-decision-tree`

- 目的：先把 crypto 里的前置分流做好，避免把编码题、异或题和真正密码学题混在一起
- 为什么现在做：
  - 这是低成本高收益的前门 skill
  - 适合快速提升 agent 在 crypto/misc 题上的第一步判断质量
- 依赖：
  - `ctf-solver-profile`
- 需要的脚本/工具：
  - base 系列编码识别
  - XOR / repeating-key XOR 检测
  - 熵值、字节分布、可打印性分析
- 建议的本地样例：
  - `targets/crypto-encoding-lab/`
  - `targets/crypto-xor-lab/`
- 退出条件：
  - agent 能先把“编码/混淆/简单异或”快速排干净，再决定是否进入更重的密码学分析

## 近期推荐顺序

`web-ssti-triage`、`pwn-stack-overflow-exploit-dev`、`web-jwt-triage`、`web-xss-triage` 已经落地，接下来建议按这个顺序推进：

1. `rev-unpack-and-trace` 或 `crypto-encoding-decision-tree`
2. `web-backdoor-triage`
3. `artifact-inspection-utility`
4. `regression-target-convention`
5. `pwn-canary-and-pie-follow-up`

## 新 skill 的轻量质量门槛

以后接受一个新 skill，至少满足下面 6 条：

1. 有明确适用场景和不适用场景
2. 有 1 个以上薄脚本或固定命令模板
3. 有 1 个本地 lab、fixture 或 smoke case
4. 有最小 probe 顺序，而不是只给 payload 清单
5. 有退出条件，说明什么时候该切别的 skill
6. `README.md`、`CLAUDE.md`、`docs/` 至少同步一处统一入口

## 命名和文档规则

后续建议统一下面几条：

- triage 类 skill 用 `<category>-<topic>-triage`
- 前门和沉淀类 skill 保持动宾或职责命名，例如 `challenge-workspace-bootstrap`
- 一个 skill 名称只表达一个主问题，不要把两个阶段混在同一个名字里
- `CLAUDE.md` 只保留“当前 active skills”和“近期待建优先级”，不要混历史和远期 wishlist
- `README.md` 负责给新读者看当前可用能力，不承担完整 roadmap

## 推荐执行顺序

如果按 4 到 6 周节奏推进，建议这样排：

1. 先完成文档对齐和 skill 质量门槛
2. 补 `regression-target-convention`
3. 然后在 `rev-unpack-and-trace`、`crypto-encoding-decision-tree` 里按比赛需求择二推进
4. 再补 `web-backdoor-triage`
5. 回头补 `artifact-inspection-utility` 和 `regression-target-convention`

## 一句话判断标准

下一阶段的目标不是“仓库里有更多 skill”，而是：

给一个新题，agent 更容易走到正确方向，更少乱试，更快复用已有资产，而且每条常用路径都能在本地回归。
