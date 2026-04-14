# 交付与迭代

在以下场景读取本文件：

- `manifest.yaml` 中 `current_phase == "deliver"`
- 当前版本即将交付
- 交付后用户提出了新需求，需要启动下一版本

开始前先读取：

1. `docs/project-memory.md`
2. `references/workflow.md`
3. 如需横切规则，再读取 `references/shared.md`

## Phase 4：交付

### 触发条件

所有 task 状态为 `done`，或者 `blocked` task 已被用户确认跳过

### 执行流程

1. 生成 `docs/v{X}/delivery.md`
2. 如果用户明确要求记住新的长期信息，再更新 `docs/project-memory.md`
3. 基于当前版本能力提出 3 到 5 个可能的扩展方向
4. 更新 `manifest.yaml`
5. 向用户呈现交付清单，等待确认或新需求

### 交付内容

- 功能清单
- 文件变更清单
- 已知问题清单
- 技术债务清单
- 测试覆盖情况
- 下一步建议
- 文件变更清单优先从各任务目录下的 `memory.md` 聚合，而不是回放完整对话或代码探索日志

### 状态更新

- 将当前版本的 `status` 设为 `completed`
- 填写 `completed_at`
- 将 `current_phase` 设为 `deliver`

## Phase 5：版本迭代

### 触发条件

用户在交付后提出新的需求

### 执行流程

1. 版本号递增，例如 `v1.0` → `v2.0`
2. 创建新版本目录和 `brainstorm/` 子目录
3. 更新 `manifest.yaml`
   - `current_version` 改为新版本
   - `current_phase` 设为 `prd`
   - 新增对应版本条目
4. 新版本 PRD 阶段优先引用 `docs/project-memory.md` 和上一版本的 `delivery.md` 作为上下文
5. 回到 Phase 1 开始新一轮循环
