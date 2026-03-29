# CTFAgent 文档总览

更新时间：2026-03-28

`docs/` 的目标不是堆路线稿，而是清楚回答四件事：

1. 我们现在能做什么
2. 现在是怎么设计的
3. 为什么这样设计
4. 这样做带来了什么效果

当前主线已经明确：

- 现在以 `Claude Code` 为核心解题
- 优先沉淀 `Skills`、薄工具、知识库和回归靶场
- 文档只保留当前主线真正需要的部分

## 建议阅读顺序

1. [`claude-agent-sdk-ctf-agent-design.md`](/home/yhh/ctfagent/docs/claude-agent-sdk-ctf-agent-design.md)
   - 一页看懂项目现在能做什么、怎么设计、为什么这样做、带来了什么效果
2. [`phase1-claude-code-ctf-workflow.md`](/home/yhh/ctfagent/docs/phase1-claude-code-ctf-workflow.md)
   - 当前工作流：如何用 `Claude Code` 打题、产出什么结果
3. [`challenge-package-and-platform-interface.md`](/home/yhh/ctfagent/docs/challenge-package-and-platform-interface.md)
   - challenge workspace、平台接口、`Skill/MCP/knowledge` 的边界
4. [`skills-roadmap.md`](/home/yhh/ctfagent/docs/skills-roadmap.md)
   - 下一阶段该优先补哪些 skill、哪些基础能力，以及新 skill 的质量门槛

## 这套文档的定位

- 总览文档讲当前主线，不和未来路线混写
- 工作流文档讲怎么用
- 设计文档讲为什么这样做以及产生了什么效果
- 边界文档讲结构和职责划分
