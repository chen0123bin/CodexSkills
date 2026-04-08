# 子代理执行模式

## 启用边界

只有在以下两类场景中，才使用子代理：

- PRD 阶段的 Debate：用户明确提到 Debate、subagent、CTO/CPO/CMO、委派、并行辩论，或在主代理询问后明确同意
- 执行阶段的开发与审查：用户明确要求使用子代理、delegation、并行处理或多人分工

如果用户没有明确授权真实子代理，默认由主代理执行。PRD 阶段在用户拒绝真实 Debate 子代理时，仍保留相同文件结构，但改为主代理串行完成三份角色提案。

## PRD Debate 角色

PRD 阶段默认配套三个 Debate 角色：

- `cto`
- `cpo`
- `cmo`

默认配置路径为：

- `.codex/agents/cto.toml`
- `.codex/agents/cpo.toml`
- `.codex/agents/cmo.toml`

默认假定这些文件已存在于仓库 `.codex/agents/` 中，本技能初始化不负责创建它们。

### Debate 主代理职责

主代理在 Debate 阶段负责任务编排与裁决收拢：

1. 生成当前轮次 `brief.md`
2. 决定使用真实子代理还是单代理串行 fallback
3. 向 `cto`、`cpo`、`cmo` 分发相同的维度简报
4. 等待三份提案全部完成
5. 提取共识、分歧和折中空间
6. 生成 `debate-summary.md`
7. 向用户呈现综合方案和推荐意见
8. 根据用户选择写入 `consolidated.md`
9. 关闭已完成的 Debate agent thread

### Debate 输入上下文

三个 Debate 角色只接收：

1. 当前轮次 `brief.md`
2. 前序轮次 `consolidated.md` 的摘要

禁止提供：

- 其他角色提案
- 代码文件
- 完整 PRD
- 当前轮次之外的无关噪声上下文

### Debate 输出要求

#### `cto`

职责：

- 从技术可行性、架构适配、复杂度、可扩展性和技术债角度独立提案
- 明确给出最低可行技术路径、关键风险和不可突破的技术边界

返回：

- 一份结构化 `CTO Proposal`
- 明确的推荐方向
- 风险与缓解方案
- 与 CPO/CMO 可能产生的分歧点

#### `cpo`

职责：

- 从用户价值、体验一致性、MVP 边界和优先级角度独立提案
- 坚持用户价值优先和明确的范围裁剪

返回：

- 一份结构化 `CPO Proposal`
- Must/Should/Won't MVP 边界
- Success metrics
- 与 CTO/CMO 可能产生的分歧点

#### `cmo`

职责：

- 从市场定位、竞争差异化、增长与叙事角度独立提案
- 评估每个方向的市场感知和传播价值

返回：

- 一份结构化 `CMO Proposal`
- Competitive analysis
- Growth impact assessment
- Narrative and timing judgment
- 与 CTO/CPO 可能产生的分歧点

## 执行期角色

执行阶段沿用两个角色：

- `developer`
- `reviewer`

默认约定配置路径为：

- `.codex/agents/developer.toml`
- `.codex/agents/reviewer.toml`

### 执行期主代理职责

1. 选择下一个可执行 task
2. 准备任务上下文包
3. 调度 `developer`
4. 调度 `reviewer`
5. 根据审查结果决定通过、返工或阻塞
6. 做最终验证并更新 `tasks/index.md`、当前 task 的 `task.md` / `memory.md`、`progress.md`

### `developer`

输入上下文：

1. `task_description`
2. `done_criteria`
3. `related_files`
4. `milestone_context`
5. `task_memory`
6. `review_feedback`（仅返工时提供）

职责：

- 完成当前 task 的代码开发
- 补充必要测试
- 返回 `DONE` 或 `BLOCKED`
- 报告改动文件、测试情况和需要注意的事项
- 为主代理更新当前 task 的 `memory.md` 提供结构化事实摘要

### `reviewer`

输入上下文：

1. `task_description`
2. `done_criteria`
3. `task_memory`
4. `code_changes`
5. `developer_report`

职责：

- 检查功能正确性、代码质量、范围合规、测试覆盖、安全与性能
- 返回 `APPROVED`、`NEEDS_CHANGES` 或 `REJECTED`
- 提供具体修改建议或根本性问题说明
- 优先基于当前 task 的 `memory.md` 快速理解既有改动，不要求重新扫描完整任务列表

## 调度协议

- 不要把“暂时没有回复”或“可用时间内未返回结果”直接等同于失败，更不要立刻让主代理接手兜底实现。
- 在子代理返回最终结果前，不要进入依赖该结果的下一个 step。
- 当主代理接手兜底实现时，先检查子代理已完成部分，不要重复工作。
- Debate 子代理必须相互隔离，只有主代理可以看到三方完整输出。
- 任务完成后关闭已完成的 agent thread，避免遗留噪声线程影响后续判断。
