# 交付与迭代

在以下场景读取本文件：

- `manifest.yaml` 中 `current_phase == "deliver"`
- 当前版本即将交付
- 交付后用户提出了新需求，需要启动下一版本

开始前先读取：

1. `docs/project-memory.md`
2. `docs/manifest.yaml`
3. `references/workflow.md`
4. 如需横切规则，再读取 `references/shared.md`

## Phase 4：交付

### 触发条件

所有 task 状态为 `done`，或者 `blocked` task 已被用户确认跳过

### 执行流程

1. 生成 `docs/v{X}/delivery.md`
2. 检查当前版本所有 task 已完成或已被用户确认跳过，且工作区为干净状态
3. 如果用户明确要求记住新的长期信息，再更新 `docs/project-memory.md`
4. 在用户确认交付后，切回 `base_branch` 并合并 `execute_branch`
5. 只有在合并成功后才删除 `execute_branch`
6. 基于当前版本能力提出 3 到 5 个可能的扩展方向
7. 更新 `manifest.yaml`
8. 向用户呈现交付清单，等待确认或新需求

### 交付内容

- 功能清单
- 文件变更清单
- 已知问题清单
- 技术债务清单
- 测试覆盖情况
- 下一步建议
- 文件变更清单优先从各任务文件中的执行记录与验证记录聚合，而不是回放完整对话或代码探索日志

### 状态更新

- 将当前版本的 `status` 设为 `completed`
- 填写 `completed_at`
- 将 `current_phase` 设为 `deliver`
- 保留当前版本的 `base_branch` 与 `execute_branch` 记录，作为交付审计信息

### Git 集成要求

- 交付阶段默认合并回当前版本在 `manifest.yaml` 中记录的 `base_branch`，不要硬编码为 `main`
- 合并前必须确认工作区干净，避免把无关未提交改动带入基线分支
- 如果 `execute_branch` 为空，视为该版本尚未启用独立执行分支；此时不要伪造合并记录
- 如果 merge 发生冲突，立即停止自动流程并请求用户介入
- 只有 merge 成功后才允许删除 `execute_branch`

## Phase 5：版本迭代

### 触发条件

用户在交付后提出新的需求

### 执行流程

1. 版本号递增，例如 `v1.0` → `v2.0`
2. 创建新版本目录和 `discovery/` 子目录
3. 更新 `manifest.yaml`
   - `current_version` 改为新版本
   - `current_phase` 设为 `prd`
   - 新增对应版本条目
   - 新版本条目的 `base_branch` 设为当前基线分支，`execute_branch` 设为空字符串
4. 新版本 PRD 阶段优先引用 `docs/project-memory.md` 和上一版本的 `delivery.md` 作为上下文
5. 回到 Phase 1 开始新一轮循环
