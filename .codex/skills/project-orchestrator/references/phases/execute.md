# 执行阶段

在 `manifest.yaml` 中 `current_phase == "execute"` 时读取本文件。
开始前先读取：

1. `docs/project-memory.md`
2. `docs/manifest.yaml`
3. `references/workflow.md`
4. 如需横切规则，再读取 `references/shared.md`
5. 如需真实执行子代理，再读取 `references/subagents.md`

## 阶段目标

- 按任务粒度推进代码实现
- 通过单个 task 文档保持局部上下文
- 在不回放全量历史的前提下完成开发、审查、验证和进度更新

## 触发条件

`manifest.yaml` 中 `current_phase == "execute"`

## 执行模式选择

- 如果用户明确指定使用执行期子代理处理，进入子代理执行模式，并严格按 `references/subagents.md` 的分工处理
- 如果用户没有明确指定，默认由主代理自行完成开发与审查，不启用执行期子代理

## 执行流程（循环）

先完成 Git 准备，再对于 `progress.md` 中每一个状态为 `pending` 且依赖已满足的 task，按优先级顺序执行：

### Step 0：Git 准备

1. 读取 `docs/manifest.yaml` 中当前版本的 `base_branch` 与 `execute_branch`
2. 执行 `git status --short --branch`
3. 判断当前工作区状态：
   - 如果工作区干净，继续后续分支准备
   - 如果工作区不干净且当前分支不是当前版本的 `execute_branch`，暂停执行并请求用户处理；不要自动 stash、reset 或提交
   - 如果工作区不干净但当前分支就是当前版本的 `execute_branch`，视为当前版本已有未提交中的执行状态，可继续在该分支上推进
4. 准备分支：
   - 如果 `execute_branch` 已记录，优先复用它；若当前不在该分支且工作区干净，则切换到该分支
   - 如果 `execute_branch` 为空且工作区干净，则基于 `base_branch` 创建 `codex/v{X}-execute` 这类执行分支，切换后回填到 `manifest.yaml`
   - 如果 `execute_branch` 已记录但本地分支不存在，标记为 `blocked`，等待用户决定如何恢复
5. Git 准备完成后，确认当前分支就是当前版本的 `execute_branch`

### Step 1：任务准备

1. 读取 `docs/project-memory.md`
2. 读取 `docs/manifest.yaml`、`docs/v{X}/plan.md` 和 `docs/v{X}/progress.md`
3. 选取下一个可执行的 task，并打开对应的 `docs/v{X}/tasks/task001.md` 这类单任务文件
4. 将 task 状态更新为 `in_progress`
5. 准备任务上下文：
   - 与当前任务直接相关的项目级记忆摘要
   - 当前版本在 `manifest.yaml` 中记录的 `base_branch` / `execute_branch`
   - 当前版本在 `plan.md` 中记录的目标、约束和验收标准摘要
   - 当前 task 的完整描述和 done criteria
   - 当前 task 文件中保留的执行记录、验证记录和阻塞摘要
   - `progress.md` 中当前任务与相关已完成任务的摘要
   - 相关代码文件路径

### Step 2：开发执行

- 子代理模式：把任务上下文包传给 `developer`
- 默认模式：由主代理自己完成当前 task 的代码开发、测试和最小必要验证
- 如果开发阶段发现缺少必要信息或真实技术阻塞，将 task 标记为 `blocked`
- 开发过程中持续更新当前 task 文件，记录实际修改文件、变更内容摘要和新的局部约束

### Step 3：审查

- 子代理模式：把当前 task 描述、done criteria、当前 task 文件、代码变更和开发结果传给 `reviewer`
- 默认模式：由主代理按 `reviewer` 的审查标准对当前改动做自审
- 根据审查结果分流：
  - `APPROVED`：进入 Step 4
  - `NEEDS_CHANGES`：返回 Step 2 进行返工
  - `REJECTED`：将 task 标记为 `blocked`

### Step 4：主代理验证与收拢

1. 检查变更文件是否符合项目结构
2. 检查当前仍位于当前版本的 `execute_branch`
3. 运行项目已有的测试、lint、build 命令（如果存在）
4. 验证 done criteria 是否满足
5. 检查是否引入了对其他模块的破坏性变更
6. 更新当前 task 文件，将状态更新为 `done`，并补充最终修改文件清单、验证结论和交接摘要
7. 更新 `progress.md`
   - 更新该 task 的摘要状态、最后更新时间和一句话摘要
   - 更新整体项目进度
   - 如有阻塞或返工，保持阻塞清单和最近变更同步

### Step 5：循环判断

- 如果还有 `pending` 状态的 task，回到 Step 1
- 如果存在 `blocked` 的 task 且无更多 `pending` task，向用户汇报阻塞情况，等待指示
- 如果所有 task 都 `done`，进入 Phase 4

## 异常处理

- 开发与审查的返工循环最多进行 2 次，仍未收敛则标记为 `blocked`
- 全量验证失败时，先尝试自动修复一次；仍失败则标记为 `blocked`
- 连续 3 个 task 被标记为 `blocked` 时，暂停执行并请求用户介入
- 任务被标记为 `blocked` 时，也要同步更新该任务文件，明确阻塞原因、已修改文件和待用户决策点
- Git 准备失败、分支切换失败或执行分支缺失时，也要同步标记为 `blocked`
