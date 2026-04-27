---
name: bugfix-orchestrator
description: 在已经使用 `project-orchestrator` 管理 `docs/` 的仓库中，围绕当前版本执行基于文档的缺陷登记、分析、修复与验证流程。使用场景包括：分析 BUG、定位异常、处理回归、整理根因、在当前版本的 `docs/.../fix/` 目录下维护 `index.md` 与 `bug_名称.md`，以及根据单个缺陷文档推进修复并沉淀验证结果。用户提到“修 bug”“分析报错”“定位问题”“处理线上缺陷”“hotfix”时使用。
---

# Bugfix 编排器

## 概述

使用这个技能在当前版本目录下维护一套轻量的缺陷工作流。
它不创建新版本，也不改变 `manifest.yaml` 的阶段，而是在 `docs/<version>/fix/` 下用索引文件和单缺陷文件把分析、执行、验证收拢到一起。

## 快速开始

1. 先读取 `docs/project-memory.md` 和 `docs/manifest.yaml`。
2. 再读取 `references/workflow.md`，确认当前缺陷流的约束、状态和文档结构。
3. 第一次登记缺陷时，优先运行 `scripts/init_bugfix.py` 创建：
   - `docs/<version>/fix/index.md`
   - `docs/<version>/fix/bug_<slug>.md`
4. 初始化完成后，只加载当前缺陷对应的 `bug_<slug>.md` 和必要代码，不要回放整套版本历史。

## 工作流

### Step 1：登记缺陷

- 缺陷工作流依赖现有的 `docs/` 骨架；如果 `docs/project-memory.md` 或 `docs/manifest.yaml` 不存在，先提示用户使用 `project-orchestrator` 完成初始化。
- 缺陷文档统一放在 `docs/<version>/fix/`。
- 每个缺陷使用单文件承载完整过程，文件名为 `bug_<slug>.md`。
- `index.md` 作为索引，记录缺陷 ID、标题、状态、优先级、文档链接和最后更新时间。

### Step 2：分析问题

- 先补全现象、影响范围、复现条件、期望结果、实际结果和初步判断。
- 如果关键信息不足，一次只追问 1 个最阻塞定位的问题。
- 在根因未确认前，明确区分“已确认事实”“推测”“待验证项”，不要把猜测写成结论。

### Step 3：推进修复

- 在同一个 `bug_<slug>.md` 中记录修复方案、涉及文件、执行记录和关键决策。
- 修复期间不额外拆出 task 文件；单缺陷文档就是该问题的分析单、执行单和验证单。
- 只修改当前缺陷直接相关的代码和文档，避免把无关整理混入同一工作单。

### Step 4：验证与关闭

- 把测试命令、手动验证步骤、验证结果和回归范围写回 `bug_<slug>.md`。
- 更新 `index.md` 中该缺陷的状态和最后更新时间。
- 缺陷确认关闭后，在单文件中补全结论与关闭记录。

## 状态约定

缺陷状态默认使用以下集合：

- `reported`
- `analyzing`
- `ready_to_fix`
- `fixing`
- `verifying`
- `closed`
- `blocked`

如果没有充分理由，不要自创新的状态值。

## 关键约束

- 不修改 `docs/manifest.yaml` 中的 `current_version` 和 `current_phase`。
- 不把缺陷修复强行提升为新版本迭代。
- 不主动写入 `docs/project-memory.md`；只有用户明确要求“记住”时才落盘。
- 除非用户明确要求子代理，否则默认由主代理独立完成缺陷分析与修复。

## 资源

- `references/workflow.md`：缺陷工作流的详细规则、读取顺序和索引维护方式。
- `scripts/init_bugfix.py`：初始化 `fix/index.md` 和单个 `bug_<slug>.md`。
- `assets/docs/.templates/fix-index-template.md`：缺陷索引模板。
- `assets/docs/.templates/bug-template.md`：单缺陷工作单模板。
