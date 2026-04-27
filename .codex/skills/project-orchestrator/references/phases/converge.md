# 收敛阶段

在 `manifest.yaml` 中 `current_phase == "converge"` 时读取本文件。
开始前先读取：

1. `docs/project-memory.md`
2. `references/workflow.md`
3. 如需横切规则，再读取 `references/shared.md`

## 阶段目标

- 将 `prd.md` 收敛为可执行的 `plan.md`
- 生成单任务文件和进度文件
- 在不丢失上下文边界的前提下，为执行阶段准备足够细的任务颗粒度

## 触发条件

`manifest.yaml` 中 `current_phase == "converge"`

## 执行流程

1. 读取 `docs/v{X}/prd.md`
2. 先读取 `docs/project-memory.md`
3. 生成 `docs/v{X}/plan.md`
4. 将版本目标拆成 3 到 10 个 task
5. 为每个 task 创建 `docs/v{X}/tasks/task001.md` 这类单任务文件
6. 生成 `docs/v{X}/progress.md`
7. 更新 `manifest.yaml`
   - 将当前版本的 `base_branch` 设为当前基线分支
   - 将当前版本的 `execute_branch` 设为空字符串
   - 将 `current_phase` 更新为 `execute`
8. 向用户展示 plan 概览和 `progress.md` 中的任务摘要

## 收敛要求

- 先提炼版本目标、范围边界、关键约束和验收标准
- 再将版本实现拆成 3 到 10 个可执行 task
- `plan.md` 只保留计划层信息，不重复展开完整任务流水
- `progress.md` 作为任务摘要与进度面板的唯一入口
- 为执行阶段预留 Git 分支信息：至少明确当前版本的 `base_branch`

## Task 粒度标准

- 单个 task 变更文件数尽量不超过 5
- 单个 task 尽量能在一次 Codex 执行中完成
- 单个 task 必须有明确 done criteria
- 单个 task 关联代码行数建议不超过 300 行
- 标注 `depends_on` 关系
- 标注哪些 task 可以并行
- `progress.md` 只保留任务级摘要、状态、依赖和入口路径，不堆叠完整任务细节
- 每个 `tasks/task001.md` 必须同时包含任务定义、执行记录、验证记录和阻塞说明，避免拆分出额外记忆文件

## 用户交互

- 建议用户确认收敛结果
- 如果用户直接说“开始”，可以不阻塞，直接进入执行阶段
