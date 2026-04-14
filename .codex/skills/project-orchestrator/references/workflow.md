# 工作流参考

## 核心工作流

整个项目遵循五阶段流水线，并按顺序推进：

```text
PRD（需求定义）→ 收敛（生成 plan/tasks/progress）→ 执行循环 → 交付 → 版本迭代
```

每次启动时，先读取 `docs/project-memory.md`，再读取 `docs/manifest.yaml` 判断当前阶段和活跃版本，从断点恢复。
如果 `docs/manifest.yaml` 不存在，则先执行项目初始化。

## 文件结构总览

初始化后应具备如下基础结构：

```text
docs/
├── project-memory.md
├── .templates/
│   ├── analysis-summary-template.md
│   ├── brainstorm-round-template.md
│   ├── delivery-template.md
│   ├── plan-template.md
│   ├── project-memory-template.md
│   ├── prd-template.md
│   ├── progress-template.md
│   ├── task-index-template.md
│   ├── task-item-template.md
│   └── task-memory-template.md
├── manifest.yaml
└── v1.0/
    └── brainstorm/
```

随着工作流推进，再逐步创建当前版本下的 `prd.md`、`plan.md`、`tasks/`、`progress.md` 和 `delivery.md`：

```text
docs/
├── project-memory.md
├── .templates/
│   ├── analysis-summary-template.md
│   ├── brainstorm-round-template.md
│   ├── delivery-template.md
│   ├── plan-template.md
│   ├── project-memory-template.md
│   ├── prd-template.md
│   ├── progress-template.md
│   ├── task-index-template.md
│   ├── task-item-template.md
│   └── task-memory-template.md
├── manifest.yaml
└── v1.0/
    ├── prd.md
    ├── plan.md
    ├── progress.md
    ├── tasks/
    │   ├── index.md
    │   ├── T001/
    │   │   ├── task.md
    │   │   └── memory.md
    │   └── T002/
    │       ├── task.md
    │       └── memory.md
    ├── brainstorm/
    │   ├── round-1.md
    │   ├── round-2.md
    │   ├── ... 按需追加更多 round 文档
    │   └── analysis/
    │       ├── perspective-1-proposal.md
    │       ├── perspective-2-proposal.md
    │       ├── perspective-3-proposal.md
    │       ├── analysis-summary.md
    │       └── consolidated.md
    └── delivery.md
```

## Manifest 结构

`docs/manifest.yaml` 使用如下结构：

```yaml
project_name: "Example Project"
current_version: "v1.0"
current_phase: "prd"
created_at: "【2026-03-27 22:00:00】"
versions:
  v1.0:
    status: "active"
    phase: "prd"
    started_at: "【2026-03-27 22:00:00】"
    completed_at: ""
```

### 时间格式

- 所有时间字段统一使用本地时区格式 `【YYYY-MM-DD HH:MM:SS】`
- `created_at`、`started_at`、`completed_at` 以及各类文档中的时间字段都遵循这一格式

### 字段含义

- `current_phase`：取值为 `prd`、`converge`、`execute` 或 `deliver`
- `versions.<version>.status`：取值为 `active` 或 `completed`
- `versions.<version>.phase`：该版本当前记录下来的阶段快照

## 项目级记忆

`docs/project-memory.md` 是跨 phase、跨 task、跨版本共享的项目级记忆文件。

### 读取规则

- 每次启动 workflow 时必须优先读取 `docs/project-memory.md`
- 进入任何 phase 前，先检查本文件是否包含与当前工作直接相关的项目级约束或偏好
- 向子代理分发上下文时，只传递与当前任务或当前分析直接相关的记忆条目摘要

### 写入规则

- 当用户明确要求“记住”某条信息时，必须落盘到本文件
- 默认不要主动写入；如果没有用户明确要求记住，就不要落盘
- 每条记忆必须包含：
  - `记录时间`
  - `记录原因`
  - `内容主体`

### 质量约束

- `内容主体` 必须精简，只保留后续判断真正需要的事实、约束、偏好、术语或决策
- 不记录一次性探索日志、临时猜测或 task 级别细节
- 不记录每一步操作、普通执行进展、命令输出或过程流水
- 如果新信息覆盖旧记忆，优先更新同主题条目，避免重复堆积

## Phase 0：项目初始化

当 `docs/manifest.yaml` 不存在时执行：

1. 创建 `docs/` 和 `docs/.templates/`
2. 将模板文件写入 `docs/.templates/`
3. 创建 `docs/project-memory.md`
4. 创建 `docs/manifest.yaml`
5. 创建 `docs/v1.0/` 和 `docs/v1.0/brainstorm/`
6. 然后进入 Phase 1

如果只需要创建基础结构，直接运行 `scripts/init_orchestrator.py` 即可。

## Phase 0：项目初始化

当 `docs/manifest.yaml` 不存在时执行：

1. 创建 `docs/` 和 `docs/.templates/`
2. 将模板文件写入 `docs/.templates/`
3. 创建 `docs/project-memory.md`
4. 创建 `docs/manifest.yaml`
5. 创建 `docs/v1.0/` 和 `docs/v1.0/brainstorm/`
6. 然后进入 Phase 1

如果只需要创建基础结构，直接运行 `scripts/init_orchestrator.py` 即可。

## 阶段导航

将 `workflow.md` 视为总纲与导航，不要默认把所有 phase 细则一次性读入上下文。
根据当前阶段按需读取以下文件：

| 场景 | 需要读取的文件 |
|------|----------------|
| `current_phase == "prd"` | `references/phases/prd.md` |
| `current_phase == "converge"` | `references/phases/converge.md` |
| `current_phase == "execute"` | `references/phases/execute.md` |
| `current_phase == "deliver"` 或交付后出现新需求 | `references/phases/deliver-iterate.md` |
| 需要上下文边界、检查点、Git 规则 | `references/shared.md` |

## 推荐读取顺序

1. `docs/project-memory.md`
2. `references/workflow.md`
3. 当前阶段对应的 `references/phases/*.md`
4. 如有需要，再读取 `references/shared.md`
5. 仅在用户明确要求子代理或当前阶段规则要求时，读取 `references/subagents.md`

## 设计原则

- `workflow.md` 只保留全局不变量、目录结构、manifest 结构和导航信息
- phase 文件只保留当前阶段的执行规则
- `shared.md` 只保留横切规则，例如上下文边界、用户检查点和 Git 规范
- PRD 分析默认使用 `solo`，只在需要时升级到多视角分析；具体视角由主代理按项目上下文定义
- PRD 澄清默认采用有限轮、单题推进的机制，不预设固定 R1 / R2 / R3 维度顺序
- 不要在多个 references 文件中重复维护同一段规则，避免后续漂移
