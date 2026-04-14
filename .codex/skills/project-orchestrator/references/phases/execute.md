# 执行阶段

在 `manifest.yaml` 中 `current_phase == "execute"` 时读取本文件。
开始前先读取：

1. `docs/project-memory.md`
2. `references/workflow.md`
3. 如需横切规则，再读取 `references/shared.md`
4. 如需真实执行子代理，再读取 `references/subagents.md`

## 阶段目标

- 按任务粒度推进代码实现
- 通过 task memory 保持局部上下文
- 在不回放全量历史的前提下完成开发、审查、验证和进度更新

## 触发条件

`manifest.yaml` 中 `current_phase == "execute"`

## 执行模式选择

- 如果用户明确指定使用执行期子代理处理，进入子代理执行模式，并严格按 `references/subagents.md` 的分工处理
- 如果用户没有明确指定，默认由主代理自行完成开发与审查，不启用执行期子代理

## 执行流程（循环）

对于 `tasks/index.md` 中每一个状态为 `pending` 且依赖已满足的 task，按优先级顺序执行：

### Step 1：任务准备

1. 读取 `docs/project-memory.md`
2. 读取 `docs/v{X}/plan.md` 和 `docs/v{X}/tasks/index.md`
3. 选取下一个可执行的 task，并打开对应的 `docs/v{X}/tasks/T{XXX}/task.md` 与 `docs/v{X}/tasks/T{XXX}/memory.md`
4. 将 task 状态更新为 `in_progress`
5. 准备任务上下文：
   - 与当前任务直接相关的项目级记忆摘要
   - 当前 task 的完整描述和 done criteria
   - 当前 task `memory.md` 中保留的已知事实与历史变更摘要
   - 相关代码文件路径
   - 相关 milestone 的必要背景
   - 已完成相关 task 的摘要

### Step 2：开发执行

- 子代理模式：把任务上下文包传给 `developer`
- 默认模式：由主代理自己完成当前 task 的代码开发、测试和最小必要验证
- 如果开发阶段发现缺少必要信息或真实技术阻塞，将 task 标记为 `blocked`
- 开发过程中持续更新当前 task 的 `memory.md`，记录实际修改文件、变更内容摘要和新的局部约束

### Step 3：审查

- 子代理模式：把当前 task 描述、done criteria、当前 task 的 `memory.md`、代码变更和开发结果传给 `reviewer`
- 默认模式：由主代理按 `reviewer` 的审查标准对当前改动做自审
- 根据审查结果分流：
  - `APPROVED`：进入 Step 4
  - `NEEDS_CHANGES`：返回 Step 2 进行返工
  - `REJECTED`：将 task 标记为 `blocked`

### Step 4：主代理验证与收拢

1. 检查变更文件是否符合项目结构
2. 运行项目已有的测试、lint、build 命令（如果存在）
3. 验证 done criteria 是否满足
4. 检查是否引入了对其他模块的破坏性变更
5. 更新当前 task 的 `task.md`，将状态更新为 `done`，并记录完成时间
6. 更新当前 task 的 `memory.md`，补充最终修改文件清单、验证结论和交接摘要
7. 更新 `tasks/index.md` 中该任务的摘要状态
8. 更新 `progress.md`
   - 更新该 task 所属 milestone 的完成百分比
   - 如果 milestone 下所有 task 都 `done`，将 milestone 标记为 `completed`
   - 更新整体项目进度

### Step 5：循环判断

- 如果还有 `pending` 状态的 task，回到 Step 1
- 如果存在 `blocked` 的 task 且无更多 `pending` task，向用户汇报阻塞情况，等待指示
- 如果所有 task 都 `done`，进入 Phase 4

## 异常处理

- 开发与审查的返工循环最多进行 2 次，仍未收敛则标记为 `blocked`
- 全量验证失败时，先尝试自动修复一次；仍失败则标记为 `blocked`
- 连续 3 个 task 被标记为 `blocked` 时，暂停执行并请求用户介入
- 任务被标记为 `blocked` 时，也要同步更新该任务目录中的 `memory.md`，明确阻塞原因、已修改文件和待用户决策点
