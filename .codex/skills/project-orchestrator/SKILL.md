---
name: project-orchestrator
description: 在 Codex 中初始化并驱动基于文档的 Debate 驱动 PRD→plan/task/progress→delivery 项目编排流程。适用于需要在仓库中维护 docs/manifest.yaml、docs/.templates/、版本化 docs/vX.Y/ 工件、按 1-3 轮 Debate 做需求澄清、再进行计划拆解、以 tasks/ 目录管理单任务文件与记忆文件、执行跟踪、交付总结与版本迭代的场景。
---

# 项目编排器

## 概述

使用这个技能在当前仓库中运行一套以文档为中心的项目工作流。
将这套流程视为“调用本技能时生效”的方法论，并把所有状态与工件都收敛到 `docs/` 目录中。
执行阶段使用 `docs/<version>/tasks/index.md` 维护任务索引，并为每个任务创建独立的 `task.md` 与 `memory.md`，避免单文件任务历史持续膨胀。

## 快速开始

1. 检查目标仓库中是否存在 `docs/manifest.yaml`。
2. 如果不存在，使用 `scripts/init_orchestrator.py` 对仓库根目录进行初始化。
3. 在创建或更新工作流工件前，先阅读 `references/workflow.md`。
4. PRD 阶段默认按 Debate 工作流组织 `docs/<version>/brainstorm/round-N/` 产物。
5. 如果用户明确提到 Debate、subagents、CTO/CPO/CMO 或并行辩论，直接阅读 `references/subagents.md` 并启用真实 Debate 子代理。
6. 如果用户没有显式授权 Debate 子代理，先询问一次；若用户拒绝，则保留同样的 Debate 文件结构，但改由主代理串行生成三份角色提案。
7. 执行阶段仍默认优先单代理完成；只有在用户明确要求子代理、委派或并行代理工作时，才切换到执行期子代理模式。

## 运行方式

- 根据 `docs/manifest.yaml` 中记录的阶段决定下一步动作。
- 将工作流产物限定在 `docs/` 和版本化的 `docs/vX.Y/` 目录中。
- 执行阶段的任务工件统一放在 `docs/<version>/tasks/` 中，按 `tasks/<task-id>/task.md` 与 `tasks/<task-id>/memory.md` 局部加载。
- 让主线程专注于需求、决策和面向用户的总结。
- PRD 阶段使用 1-3 轮 Debate 收敛需求，固定围绕功能范围、技术架构和实现路径三个维度推进。
- 默认优先单代理执行；只有 Debate 经用户授权，或执行阶段用户明确要求子代理时，才实际调度子代理。
- Debate 阶段默认使用仓库中已存在的 `cto`、`cpo` 和 `cmo` 角色配置，约定路径为 `.codex/agents/`。
- 执行阶段沿用 `developer` 和 `reviewer` 角色约定，不改变其职责。
- 将内置模板视为文件结构的事实来源，更新项目工件时不要临时发明新的格式。

## 按阶段推进

### 初始化

- 使用 `scripts/init_orchestrator.py` 创建 `docs/.templates/`、`docs/manifest.yaml` 和 `docs/<version>/brainstorm/`。

### PRD 阶段

- 读取用户请求和 `docs/manifest.yaml`。
- 使用最多 3 轮 Debate 收敛关键决策，每轮都生成 `brief.md`、角色提案、`debate-summary.md` 和 `consolidated.md`。
- 仅在用户显式授权或确认后才启用真实 `cto`、`cpo`、`cmo` 子代理；否则由主代理串行产出同结构文件。
- 将确认后的 PRD 写入 `docs/<version>/prd.md`。
- 在离开 PRD 阶段前等待用户确认。

### 收敛阶段

- 读取 `docs/<version>/prd.md`。
- 基于内置模板生成 `plan.md`、`tasks/index.md`、每个任务的独立 `task.md` 与 `memory.md`，以及 `progress.md`。
- 可以建议用户确认，但也允许用户直接进入执行阶段。

### 执行阶段

- 只读取当前里程碑、当前任务文件、当前任务记忆文件，以及相关代码。
- 随着工作推进更新当前任务目录中的 `task.md`、`memory.md` 和 `progress.md`，必要时同步更新 `tasks/index.md`。
- 尽量把任务控制在一次 Codex 执行可完成的规模内，约 5 个文件以内，并带有清晰的完成标准。

### 交付阶段

- 在 `delivery.md` 中总结已交付功能、变更文件、已知问题、技术债和测试覆盖情况。
- 在交付后给出下一版本的方向建议。

### 迭代阶段

- 当用户在交付后提出新需求时，创建下一个版本目录，并从 PRD 阶段重新开始。
- 优先携带上一版本的 `delivery.md` 作为上下文，而不是重新加载整套历史文档。

## 控制上下文体积

- 只读取当前 phase 所需的文档。
- 使用 `references/workflow.md` 获取完整的 phase 规则、manifest 结构、检查点与模板语义。
- Debate 角色只加载维度简报和前序结论摘要，不加载其他角色提案或代码文件。
- 执行期优先读取 `tasks/index.md` 中的摘要，再只打开当前任务目录下的 `task.md` 与 `memory.md`，不要回放整份任务历史。
- 除非用户需要，不要在主回复中堆入头脑风暴原稿、原始命令输出或探索日志。
- 优先总结中间结果，而不是直接粘贴噪声内容。

## 使用内置资源

- `scripts/init_orchestrator.py`：将工作流目录和 Debate 模板写入目标仓库。
- `references/workflow.md`：完整的 phase 规则、manifest 结构、检查点、上下文边界和模板语义。
- `references/subagents.md`：PRD Debate 子代理与执行期子代理的使用边界、输入输出和调度协议。
- `assets/docs/`：初始化脚本复制到目标仓库中的模板文件。
