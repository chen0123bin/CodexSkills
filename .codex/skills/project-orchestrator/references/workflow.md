# 工作流参考

## 核心工作流

整个项目遵循五阶段流水线，并且应按顺序推进：

```text
PRD（需求定义）→ 收敛（生成 plan/task/progress）→ 执行循环 → 交付 → 版本迭代
```

每次启动时，先读取 `docs/manifest.yaml` 判断当前所处阶段和活跃版本，从断点恢复。
如果 `docs/manifest.yaml` 不存在，则先执行项目初始化。

## 文件结构总览

初始化后应具备如下基础结构：

```text
docs/
├── .templates/
│   ├── prd-template.md
│   ├── plan-template.md
│   ├── task-template.md
│   ├── progress-template.md
│   └── delivery-template.md
├── manifest.yaml
└── v1.0/
    └── brainstorm/

```

随着工作流推进，再逐步创建当前版本下的 `prd.md`、`plan.md`、`task.md`、`progress.md` 和 `delivery.md`，参考以下。


```text
docs/
├── .templates/                    # 工件模板（不随版本变化）
│   ├── prd-template.md
│   ├── plan-template.md
│   ├── task-template.md
│   ├── progress-template.md
│   └── delivery-template.md
├── manifest.yaml                  # 全局状态追踪
└── v1.0/                          # 版本目录（按版本递增）
    ├── prd.md
    ├── plan.md
    ├── task.md
    ├── progress.md
    ├── brainstorm/
    │   ├── round-1.md
    │   └── round-2.md
    └── delivery.md

```

## Manifest 结构

`docs/manifest.yaml` 使用如下结构：

```yaml
project_name: "Example Project"
current_version: "v1.0"
current_phase: "prd"
created_at: "2026-03-27T14:00:00Z"
versions:
  v1.0:
    status: "active"
    phase: "prd"
    started_at: "2026-03-27T14:00:00Z"
    completed_at: ""
```

### 字段含义

- `current_phase`：取值为 `prd`、`converge`、`execute` 或 `deliver`
- `versions.<version>.status`：取值为 `active` 或 `completed`
- `versions.<version>.phase`：该版本当前记录下来的阶段（`phase`）快照

## Phase 0：项目初始化

当 `docs/manifest.yaml` 不存在时执行：

1. 创建 `docs/` 和 `docs/.templates/`
2. 将模板文件写入 `docs/.templates/`
3. 创建 `docs/manifest.yaml`
4. 创建 `docs/v1.0/` 和 `docs/v1.0/brainstorm/`
5. 然后进入 Phase 1

如果只需要创建基础结构，直接运行 `scripts/init_orchestrator.py` 即可。

## Phase 1：PRD 需求定义（头脑风暴）

### 触发条件

`manifest.yaml` 中 `current_phase == "prd"`

### 执行流程

1. 理解用户需求，提取核心目标、约束条件、用户画像和技术偏好
2. 在最多 3 轮头脑风暴中收敛关键决策
3. 基于确认结果生成 `docs/v{X}/prd.md`
4. 将 `manifest.yaml` 中 `current_phase` 更新为 `converge`

### 头脑风暴轮次建议

- 第 1 轮：功能范围方案，明确做多少、做哪些、MVP 边界
- 第 2 轮：技术架构方向，明确技术栈、架构模式、关键设计决策
- 第 3 轮：实现路径方案，明确分期策略、优先级和风险规避路径

### 写入要求

- 每轮将结果写入 `docs/v{X}/brainstorm/round-{N}.md`
- 每轮方案都应包含：方案概述、优势、劣势、适用场景
- 用户在第 1 轮就已表达清晰需求时，可以提前结束头脑风暴

### 约束

- 每轮结束后等待用户确认，再进入下一轮
- 生成完整 PRD 后，也要等待用户确认
- 在此阶段不要开始编写业务代码

## Phase 2：收敛（PRD → plan / task / progress）

### 触发条件

`manifest.yaml` 中 `current_phase == "converge"`

### 执行流程

1. 读取 `docs/v{X}/prd.md`
2. 生成 `docs/v{X}/plan.md`
3. 生成 `docs/v{X}/task.md`
4. 生成 `docs/v{X}/progress.md`
5. 向用户展示 plan 概览和 task 清单
6. 将 `manifest.yaml` 中 `current_phase` 更新为 `execute`

### 收敛要求

- 将 PRD 拆成 5 到 9 个里程碑（milestone）
- 每个 milestone 要有明确交付物和验收标准
- 将 milestone 继续拆为可执行 task

### Task 粒度标准

- 单个 task 变更文件数尽量不超过 5
- 单个 task 尽量能在一次 Codex 执行中完成
- 单个 task 必须有明确 done criteria
- 单个 task 关联代码行数建议不超过 300 行
- 标注 `depends_on` 关系
- 标注哪些 task 可以并行

### 用户交互

- 建议用户确认收敛结果
- 如果用户直接说“开始”，可以不阻塞，直接进入执行阶段

## Phase 3：执行循环

### 触发条件

`manifest.yaml` 中 `current_phase == "execute"`

### 执行模式选择

- 如果用户明确指定使用子代理处理，进入子代理执行模式，并按 `references/subagents.md` 的执行顺序处理
- 如果用户没有明确指定，默认由主代理自行完成开发与审查，不启用子代理

### 执行流程（循环）

对于 `task.md` 中每一个状态为 `pending` 且依赖已满足的 task，按优先级顺序执行：

#### Step 1：任务准备

1. 读取 `docs/v{X}/plan.md` 和 `docs/v{X}/task.md`
2. 选取下一个可执行的 task
3. 将 task 状态更新为 `in_progress`
4. 准备任务上下文：
   - 当前 task 的完整描述和 done criteria
   - 相关代码文件路径
   - 相关 milestone 的必要背景
   - 已完成相关 task 的摘要

#### Step 2：开发执行

- 子代理模式：把任务上下文包传给 `fullstack-developer`
- 默认模式：由主代理自己完成当前 task 的代码开发、测试和最小必要验证
- 如果开发阶段发现缺少必要信息或真实技术阻塞，将 task 标记为 `blocked`

#### Step 3：审查

- 子代理模式：把当前 task 描述、done criteria、代码变更和开发结果传给 `code-reviewer`
- 默认模式：由主代理按 `code-reviewer` 的审查标准对当前改动做自审
- 根据审查结果分流：
  - `APPROVED`：进入 Step 4
  - `NEEDS_CHANGES`：返回 Step 2 进行返工
  - `REJECTED`：将 task 标记为 `blocked`

#### Step 4：主代理验证与收拢

1. 检查变更文件是否符合项目结构
2. 运行项目已有的测试、lint、build 命令（如果存在）
3. 验证 done criteria 是否满足
4. 检查是否引入了对其他模块的破坏性变更
5. 更新 `task.md`，将当前 task 状态更新为 `done`，并记录完成时间
6. 更新 `progress.md`
   - 更新该 task 所属 milestone 的完成百分比
   - 如果 milestone 下所有 task 都 `done`，将 milestone 标记为 `completed`
   - 更新整体项目进度

#### Step 5：循环判断

- 如果还有 `pending` 状态的 task，回到 Step 1
- 如果存在 `blocked` 的 task 且无更多 `pending` task，向用户汇报阻塞情况，等待指示
- 如果所有 task 都 `done`，进入 Phase 4

### 异常处理

- 开发与审查的返工循环最多进行 2 次，仍未收敛则标记为 `blocked`
- 全量验证失败时，先尝试自动修复一次；仍失败则标记为 `blocked`
- 连续 3 个 task 被标记为 `blocked` 时，暂停执行并请求用户介入

## Phase 4：交付

### 触发条件

所有 task 状态为 `done`，或者 `blocked` task 已被用户确认跳过

### 执行流程

1. 生成 `docs/v{X}/delivery.md`
2. 基于当前版本能力提出 3 到 5 个可能的扩展方向
3. 更新 `manifest.yaml`
4. 向用户呈现交付清单，等待确认或新需求

### 交付内容

- 功能清单
- 文件变更清单
- 已知问题清单
- 技术债务清单
- 测试覆盖情况
- 下一步建议

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
4. 新版本 PRD 阶段优先引用上一版本的 `delivery.md` 作为上下文
5. 回到 Phase 1 开始新一轮循环

## 上下文管理规则

为避免上下文溢出，优先遵循以下加载边界：

| 阶段 | 加载的文件 | 默认不加载 |
|------|-----------|-----------|
| PRD | 用户需求 + `manifest.yaml` | 代码文件、历史版本完整栈 |
| 收敛 | `prd.md` + `manifest.yaml` | 代码文件、历史版本细节 |
| 执行-当前任务 | 当前 task + 相关代码文件 + milestone 摘要 | 完整 PRD、其他 milestone、全量历史 |
| 执行-验证 | `progress.md` + `task.md` + 变更文件 | 完整 PRD、brainstorm 全量内容 |
| 交付 | `progress.md` + `task.md` + `plan.md` | 代码细节、brainstorm 原稿 |
| 版本迭代 | 上一版本 `delivery.md` | 上一版本其他完整文档 |

## 用户交互检查点

以下节点必须等待用户确认后再继续：

- 每轮头脑风暴方案选择
- PRD 最终确认
- 连续阻塞后的介入处理
- 最终交付确认
- 新版本启动确认

以下节点可自动推进：

- 已批准计划下的常规 task 执行
- 常规 review 与验证结果处理
- 常规 progress 更新

## Git 规范

如果仓库使用 Git 且用户要求提交：

- 每个 task 完成后尽量立即 commit
- commit message 可采用 `[v{版本号}][M{里程碑号}] T{任务号}: {任务标题}` 这类稳定格式
- docs 状态变更尽量与对应工作一并提交
- 交付阶段的文档更新可单独作为一次交付提交

如果用户没有要求提交，也要保持 docs 状态与实际进度一致。
