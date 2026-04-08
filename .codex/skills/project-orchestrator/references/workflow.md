# 工作流参考

## 核心工作流

整个项目遵循五阶段流水线，并按顺序推进：

```text
PRD（需求定义）→ 收敛（生成 plan/tasks/progress）→ 执行循环 → 交付 → 版本迭代
```

每次启动时，先读取 `docs/manifest.yaml` 判断当前阶段和活跃版本，从断点恢复。
如果 `docs/manifest.yaml` 不存在，则先执行项目初始化。

## 文件结构总览

初始化后应具备如下基础结构：

```text
docs/
├── .templates/
│   ├── debate-round-template.md
│   ├── delivery-template.md
│   ├── plan-template.md
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
├── .templates/
│   ├── debate-round-template.md
│   ├── delivery-template.md
│   ├── plan-template.md
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
    │   ├── round-1/
    │   │   ├── brief.md
    │   │   ├── cto-proposal.md
    │   │   ├── cpo-proposal.md
    │   │   ├── cmo-proposal.md
    │   │   ├── debate-summary.md
    │   │   └── consolidated.md
    │   └── round-2/
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
- `versions.<version>.phase`：该版本当前记录下来的阶段快照

## Phase 0：项目初始化

当 `docs/manifest.yaml` 不存在时执行：

1. 创建 `docs/` 和 `docs/.templates/`
2. 将模板文件写入 `docs/.templates/`
3. 创建 `docs/manifest.yaml`
4. 创建 `docs/v1.0/` 和 `docs/v1.0/brainstorm/`
5. 然后进入 Phase 1

如果只需要创建基础结构，直接运行 `scripts/init_orchestrator.py` 即可。

## Phase 1：PRD 需求定义（Debate 驱动的头脑风暴）

### 触发条件

`manifest.yaml` 中 `current_phase == "prd"`

### Debate 启用规则

- 如果用户明确提到 Debate、subagents、CTO/CPO/CMO、委派或并行辩论，直接启用真实 Debate 子代理。
- 如果用户没有显式授权真实 Debate 子代理，先询问一次。
- 如果用户拒绝或不希望使用真实子代理，则保持相同的文件结构和回合流程，但由主代理串行完成三份角色提案，不启动子代理。
- Debate 默认依赖仓库中已存在的 `.codex/agents/cto.toml`、`.codex/agents/cpo.toml` 和 `.codex/agents/cmo.toml`，初始化脚本不负责创建它们。

### 执行流程

#### Step 1：需求理解

仔细分析用户提供的需求描述，提取：

- 核心目标
- 约束条件
- 用户画像
- 技术偏好
- 商业背景（如果有）

#### Step 2：Debate 驱动的头脑风暴（最多 3 轮）

每一轮遵循以下四步流程。

##### ① 主代理出题（Framing）

主代理根据当前轮次维度，构造一份维度简报并写入 `docs/v{X}/brainstorm/round-{N}/brief.md`。简报必须包含：

- 本轮讨论的核心问题
- 用户原始需求上下文的精简版
- 前序轮次的已确认结论
- 本轮必须遵守的约束

各轮维度固定如下：

| 轮次 | 维度 | 核心问题 |
|------|------|---------|
| R1 | 功能范围方案 | 明确做多少、做哪些、MVP 边界 |
| R2 | 技术架构方向 | 明确技术栈、架构模式、关键设计决策 |
| R3 | 实现路径方案 | 明确分期策略、优先级和风险规避路径 |

##### ② 三方独立提案（Independent Proposals）

将维度简报同时分发给三个角色：

- `cto`：技术可行性、架构、工程成本
- `cpo`：用户价值、产品体验、MVP 边界
- `cmo`：市场定位、竞争差异化、增长潜力

真实子代理模式下，三个角色必须互相不可见对方输出，只读取：

- 当前轮次 `brief.md`
- 前序轮次 `consolidated.md` 摘要

禁止传入：

- 其他角色提案
- 代码文件
- 完整 PRD

将结果分别写入：

- `docs/v{X}/brainstorm/round-{N}/cto-proposal.md`
- `docs/v{X}/brainstorm/round-{N}/cpo-proposal.md`
- `docs/v{X}/brainstorm/round-{N}/cmo-proposal.md`

##### ③ 主代理综合辩论（Debate Synthesis）

主代理收到三份提案后，按 `docs/.templates/debate-round-template.md` 生成 `docs/v{X}/brainstorm/round-{N}/debate-summary.md`，并至少包含：

- 共识提取：三方都同意的结论
- 分歧识别：逐项列出冲突点和各方立场
- 辩论裁决：分析分歧本质、各方论据的合理性和局限性
- 方案蒸馏：整理为 2-3 个可落地的综合方案，并标注各自偏向

综合方案必须是三方视角的组合，不得只是单一角色观点的复述。

##### ④ 用户决策（Decision）

向用户呈现：

- 三方共识
- 关键分歧与各方立场
- 2-3 个综合方案
- 主代理的协调者推荐

等待用户确认后，将最终选择写入 `docs/v{X}/brainstorm/round-{N}/consolidated.md`。
`consolidated.md` 只保留供下一轮和 PRD 生成使用的最终结论，不重复完整辩论过程。

#### 提前结束机制

满足以下任一条件时可提前结束 Debate：

- 用户明确表示需求已清晰，不需要继续讨论
- 连续两轮提案高度一致，共识超过 80%，且无重大分歧
- 主代理判断剩余维度已被前序轮次充分覆盖

提前结束时，必须明确告诉用户跳过了哪些维度以及原因，并等待用户确认。

#### Step 3：生成 PRD

- 基于所有已确认轮次的 `consolidated.md` 生成 `docs/v{X}/prd.md`
- PRD 必须包含新增章节“Debate 决策记录”
- PRD 中记录实际完成的 Debate 轮次、关键分歧、最终决策理由和被否决的重要方案
- 生成 PRD 后必须等待用户确认，不能自动进入下一阶段

#### Step 4：更新状态

用户确认 PRD 后，再更新 `manifest.yaml` 中 `current_phase` 为 `converge`。

### 约束

- Debate 最少 1 轮，最多 3 轮
- 真实子代理模式下，三个角色必须独立提案，不可互相看到对方输出
- 主代理作为辩论综合者必须保持中立，不预设倾向
- 分歧无法调和时由用户裁决，不由主代理单方面定论
- 后续轮次必须建立在前序轮次 `consolidated.md` 的确认结论之上
- 在此阶段不要开始编写业务代码

## Phase 2：收敛（PRD → plan / tasks / progress）

### 触发条件

`manifest.yaml` 中 `current_phase == "converge"`

### 执行流程

1. 读取 `docs/v{X}/prd.md`
2. 生成 `docs/v{X}/plan.md`
3. 生成 `docs/v{X}/tasks/index.md`
4. 为每个 task 创建 `docs/v{X}/tasks/T{XXX}/task.md` 和 `docs/v{X}/tasks/T{XXX}/memory.md`
5. 生成 `docs/v{X}/progress.md`
6. 向用户展示 plan 概览和 task 索引
7. 将 `manifest.yaml` 中 `current_phase` 更新为 `execute`

### 收敛要求

- 将 PRD 拆成 5 到 9 个里程碑
- 每个 milestone 要有明确交付物和验收标准
- 将 milestone 继续拆为可执行 task

### Task 粒度标准

- 单个 task 变更文件数尽量不超过 5
- 单个 task 尽量能在一次 Codex 执行中完成
- 单个 task 必须有明确 done criteria
- 单个 task 关联代码行数建议不超过 300 行
- 标注 `depends_on` 关系
- 标注哪些 task 可以并行
- `tasks/index.md` 只保留任务级摘要、状态、依赖和入口路径，不堆叠完整任务细节
- 每个 `tasks/T{XXX}/memory.md` 只记录已发生的事实，包括修改过的文件、变更摘要、关键决策和验证结果

### 用户交互

- 建议用户确认收敛结果
- 如果用户直接说“开始”，可以不阻塞，直接进入执行阶段

## Phase 3：执行循环

### 触发条件

`manifest.yaml` 中 `current_phase == "execute"`

### 执行模式选择

- 如果用户明确指定使用执行期子代理处理，进入子代理执行模式，并严格按 `references/subagents.md` 的分工处理
- 如果用户没有明确指定，默认由主代理自行完成开发与审查，不启用执行期子代理

### 执行流程（循环）

对于 `tasks/index.md` 中每一个状态为 `pending` 且依赖已满足的 task，按优先级顺序执行：

#### Step 1：任务准备

1. 读取 `docs/v{X}/plan.md` 和 `docs/v{X}/tasks/index.md`
2. 选取下一个可执行的 task，并打开对应的 `docs/v{X}/tasks/T{XXX}/task.md` 与 `docs/v{X}/tasks/T{XXX}/memory.md`
3. 将 task 状态更新为 `in_progress`
4. 准备任务上下文：
   - 当前 task 的完整描述和 done criteria
   - 当前 task `memory.md` 中保留的已知事实与历史变更摘要
   - 相关代码文件路径
   - 相关 milestone 的必要背景
   - 已完成相关 task 的摘要

#### Step 2：开发执行

- 子代理模式：把任务上下文包传给 `developer`
- 默认模式：由主代理自己完成当前 task 的代码开发、测试和最小必要验证
- 如果开发阶段发现缺少必要信息或真实技术阻塞，将 task 标记为 `blocked`
- 开发过程中持续更新当前 task 的 `memory.md`，记录实际修改文件、变更内容摘要和新的局部约束

#### Step 3：审查

- 子代理模式：把当前 task 描述、done criteria、当前 task 的 `memory.md`、代码变更和开发结果传给 `reviewer`
- 默认模式：由主代理按 `reviewer` 的审查标准对当前改动做自审
- 根据审查结果分流：
  - `APPROVED`：进入 Step 4
  - `NEEDS_CHANGES`：返回 Step 2 进行返工
  - `REJECTED`：将 task 标记为 `blocked`

#### Step 4：主代理验证与收拢

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

#### Step 5：循环判断

- 如果还有 `pending` 状态的 task，回到 Step 1
- 如果存在 `blocked` 的 task 且无更多 `pending` task，向用户汇报阻塞情况，等待指示
- 如果所有 task 都 `done`，进入 Phase 4

### 异常处理

- 开发与审查的返工循环最多进行 2 次，仍未收敛则标记为 `blocked`
- 全量验证失败时，先尝试自动修复一次；仍失败则标记为 `blocked`
- 连续 3 个 task 被标记为 `blocked` 时，暂停执行并请求用户介入
- 任务被标记为 `blocked` 时，也要同步更新该任务目录中的 `memory.md`，明确阻塞原因、已修改文件和待用户决策点

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
4. 新版本 PRD 阶段优先引用上一版本的 `delivery.md` 作为上下文
5. 回到 Phase 1 开始新一轮循环

## 上下文管理规则

为避免上下文溢出，优先遵循以下加载边界：

| 阶段 | 加载的文件 | 默认不加载 |
|------|-----------|-----------|
| PRD-主代理 | 用户需求 + `manifest.yaml` + 已确认的 `consolidated.md` 摘要 | 代码文件、历史版本完整栈 |
| Debate-CTO | 当前轮次 `brief.md` + 前序结论摘要 | 其他角色提案、代码文件、完整 PRD |
| Debate-CPO | 当前轮次 `brief.md` + 前序结论摘要 | 其他角色提案、代码文件、完整 PRD |
| Debate-CMO | 当前轮次 `brief.md` + 前序结论摘要 | 其他角色提案、代码文件、完整 PRD |
| Debate-综合 | 三方提案 + 当前轮次 `brief.md` + 前序结论摘要 | 代码文件 |
| 收敛 | `prd.md` + `manifest.yaml` | 代码文件、历史版本细节 |
| 执行-当前任务 | `tasks/index.md` 中的当前任务摘要 + 当前任务 `task.md` + 当前任务 `memory.md` + 相关代码文件 + milestone 摘要 | 完整 PRD、其他任务目录、全量历史 |
| 执行-验证 | `progress.md` + `tasks/index.md` + 当前任务 `memory.md` + 变更文件 | 完整 PRD、brainstorm 全量内容 |
| 交付 | `progress.md` + `tasks/index.md` + `plan.md` + 必要的任务 `memory.md` 摘要 | 代码细节、brainstorm 原稿 |
| 版本迭代 | 上一版本 `delivery.md` | 上一版本其他完整文档 |

## 用户交互检查点

| 阶段 | 是否需要用户介入 |
|------|----------------|
| 每轮 Debate 综合方案选择 | 必须 |
| 提前结束 Debate 确认 | 必须 |
| PRD 最终确认 | 必须 |
| plan/tasks 收敛确认 | 建议 |
| 每个 task 执行 | 自动 |
| review 结果 | 自动 |
| 连续阻塞介入 | 必须 |
| 交付确认 | 必须 |
| 新版本启动 | 必须 |

## Git 规范

如果仓库使用 Git 且用户要求提交：

- 每个 task 完成后尽量立即 commit
- commit message 可采用 `[v{版本号}][M{里程碑号}] T{任务号}: {任务标题}` 这类稳定格式
- docs 状态变更尽量与对应工作一并提交
- 交付阶段的文档更新可单独作为一次交付提交

如果用户没有要求提交，也要保持 docs 状态与实际进度一致。
