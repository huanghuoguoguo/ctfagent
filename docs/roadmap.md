# 近期路线

更新时间：2026-03-29

## 目标

路线图只回答一个问题：

下一步补什么，能让仓库更强，而不是更复杂。

## 当前优先级

1. `rev-unpack-and-trace`
   - 给逆向和“伪 misc”题补一个基础主路径
2. `crypto-encoding-decision-tree`
   - 先把编码、异或和真正密码学问题分流开
3. `web-backdoor-triage`
   - 处理空白页、动态页、源码后门、参数门等场景
4. `artifact-inspection-utility`
   - 统一文件类型、hash、strings、metadata 等基础检查
5. `regression-target-convention`
   - 给新 skill 统一 lab / smoke / 回归约定
6. `pwn-canary-and-pie-follow-up`
   - 补强已有 pwn 路径的泄漏与保护绕过部分

## 排序标准

一个候选项排得靠前，通常因为它满足这些条件中的多数：

- 能补一条明确主路径
- 能复用到多道题
- 能配脚本
- 能配 lab 或 smoke
- 能减少 agent 乱试

## 不做什么

近期不以这些事情为主：

- 为了“覆盖率”盲目加 skill
- 先写重型 orchestration
- 先接比赛平台和自动提交
- 先做复杂状态管理
