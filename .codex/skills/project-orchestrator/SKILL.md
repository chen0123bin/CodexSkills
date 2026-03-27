---
name: project-orchestrator
description: 在 Codex 中初始化并驱动基于文档的 PRD→plan/task/progress→delivery 项目编排流程。适用于需要在仓库中维护 docs/manifest.yaml、docs/.templates/、版本化 docs/vX.Y/ 工件、分阶段需求澄清、里程碑与任务拆解、执行跟踪、交付总结与版本迭代的场景。
---

# 项目编排器

## 概述

使用这个技能在当前仓库中运行一套以文档为中心的项目工作流。
将这套流程视为“调用本技能时生效”的方法论，并把所有状态与工件都收敛到 `docs/` 目录中。

## 快速开始

1. 检查目标仓库中是否存在 `docs/manifest.yaml`。
2. 如果不存在，使用 `scripts/init_orchestrator.py` 对仓库根目录进行初始化。
3. 在创建或更新工作流工件前，先阅读 `references/workflow.md`。
4. 只有在用户明确要求子代理（subagents）、委派或并行代理工作时，才阅读 `references/subagents.md`。

## 运行方式

- 根据 `docs/manifest.yaml` 中记录的阶段（`phase`）决定下一步动作。
- 将工作流产物限定在 `docs/` 和版本化的 `docs/vX.Y/` 目录中。
- 让主线程专注于需求、决策和面向用户的总结。
- 默认优先单代理执行。
- 只有在用户明确要求，或任务本身明确需要并行代理时，才使用子代理（subagents）。
- 将内置模板视为文件结构的事实来源，更新项目工件时不要临时发明新的格式。

## 按阶段推进

### 初始化

- 使用 `scripts/init_orchestrator.py` 创建 `docs/.templates/`、`docs/manifest.yaml` 和 `docs/<version>/brainstorm/`。

### PRD 阶段

- 读取用户请求和 `docs/manifest.yaml`。
- 最多进行 3 轮头脑风暴，并且只在它们能实质性改善范围、架构或交付路径时才展开。
- 将确认后的方案写入 `docs/<version>/brainstorm/round-N.md`。
- 将确认后的 PRD 写入 `docs/<version>/prd.md`。
- 在离开 PRD 阶段前等待用户确认。

### 收敛阶段

- 读取 `docs/<version>/prd.md`。
- 基于内置模板生成 `plan.md`、`task.md` 和 `progress.md`。
- 可以建议用户确认，但也允许用户直接进入执行阶段。

### 执行阶段

- 只读取当前里程碑或当前任务上下文，以及相关代码。
- 随着工作推进更新 `task.md` 和 `progress.md`。
- 尽量把任务控制在一次 Codex 执行可完成的规模内，约 5 个文件以内，并带有清晰的完成标准。

### 交付阶段

- 在 `delivery.md` 中总结已交付功能、变更文件、已知问题、技术债和测试覆盖情况。
- 在交付后给出下一版本的方向建议。

### 迭代阶段

- 当用户在交付后提出新需求时，创建下一个版本目录，并从 PRD 阶段重新开始。
- 优先携带上一版本的 `delivery.md` 作为上下文，而不是重新加载整套历史文档。

## 控制上下文体积

- 只读取当前 phase 所需的文档。
- 使用 `references/workflow.md` 获取完整的加载矩阵、manifest 结构、检查点与模板语义。
- 除非用户需要，不要在主回复中堆入头脑风暴原稿、原始命令输出或探索日志。
- 优先总结中间结果，而不是直接粘贴噪声内容。

## 使用内置资源

- `scripts/init_orchestrator.py`：将工作流目录和模板脚手架写入目标仓库。
- `references/workflow.md`：完整的 phase 规则、manifest 结构、检查点、上下文边界和模板语义。
- `references/subagents.md`：与官方一致的可选 subagent 使用说明。
- `assets/docs/`：初始化脚本复制到目标仓库中的模板文件。
