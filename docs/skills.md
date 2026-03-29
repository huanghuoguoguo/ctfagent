# Skill 系统

更新时间：2026-03-29

## 目标

skill 系统的目标只有三个：

- 便于维护
- 便于查看
- 便于 agent 解题

## 分层

- 前门与整理
  - `setup`
  - `challenge-workspace-bootstrap`
  - `ctf-solver-profile`
- 题型 triage
  - `web-*`
  - `pwn-*`
- 能力辅助
  - `browser-automation-playwright`
  - `network-search-ddg`
- 沉淀与维护
  - `ctf-knowledge-capture`
  - `skill-maintainer`

## 规则

- skill 负责方法和顺序，不负责平台接线
- 一个 skill 应说明：什么时候用、先做什么、何时切方向、何时退出
- 如果一个问题能通过更新已有 skill 或加脚本解决，就不要新建 skill

## 质量门槛

新增一个 skill，至少满足这些条件：

1. 有明确适用场景和不适用场景
2. 有 1 个以上薄脚本或固定命令模板
3. 有 1 个本地 lab、fixture 或 smoke case
4. 有最小 probe 顺序，不只是 payload 清单
5. 有退出条件
6. `README.md`、`CLAUDE.md`、`docs/` 至少同步一处入口

## 增长顺序

默认优先这样补：

1. 更新已有 skill
2. 加脚本
3. 加测试
4. 加 lab
5. 加 pattern
6. 最后才新增 skill

## 命名

- 题型流程优先用 `*-triage`
- 前门和沉淀类保持职责命名
- 一个 skill 名字只表达一个主问题
