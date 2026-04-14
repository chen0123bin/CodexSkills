# 子代理执行模式

## 启用边界

只有在以下两类场景中，才使用子代理：

- PRD 阶段的多视角分析：用户明确提到 Debate、subagent、多视角分析、委派、并行分析，或在主代理询问后明确同意
- 执行阶段的开发与审查：用户明确要求使用子代理、delegation、并行处理或多人分工

如果用户没有明确授权真实子代理，默认由主代理执行。PRD 阶段在用户拒绝真实分析子代理时，仍保留相同分析模式，但改为主代理串行完成对应视角分析。

## PRD 多视角分析模式

PRD 阶段支持以下分析模式：

- `solo`
- `multi-perspective`
- `custom`

默认配置路径为：

- `.codex/agents/analysis.toml`

默认假定这些文件已存在于仓库 `.codex/agents/` 中，本技能初始化不负责创建它们。
### 分析阶段主代理职责

主代理在 PRD 阶段先完成需求自分析与有限轮单题澄清，再负责编排可选多视角分析与裁决收拢：

1. 先读取 `docs/project-memory.md`，再做详细需求分析，识别需要确认的关键问题
2. 先整理必问 / 可问清单，再按阻塞程度按需生成有限轮 `round-{N}.md`，每轮只问 1 个问题并等待用户回答
3. 决定分析模式是 `solo`、`multi-perspective` 还是 `custom`
4. 决定 Step 2 使用真实子代理还是单代理串行 fallback
5. 如果启用多视角分析，先定义 2 到 3 个互补视角及各自关注点
6. 仅向已启用视角分发相同的已完成 round 文档和各自视角简报
7. 等待所有已启用视角完成分析
8. 提取共识、分歧和折中空间
9. 生成 `analysis-summary.md`
10. 向用户呈现综合方案和推荐意见
11. 根据用户选择写入 `consolidated.md`
12. 关闭已完成的分析 agent thread

### 分析输入上下文

已启用的分析子代理只接收：

1. `project-memory.md` 中与当前分析直接相关的条目摘要
2. 已完成的 `round-{N}.md`
3. 当前视角的简报

禁止提供：

- 其他视角分析
- 代码文件
- 完整 PRD
- 与已完成问答无关的噪声上下文

### 分析输出要求

每个多视角分析子代理都应按收到的视角简报独立输出，至少包含：

- 当前视角名称
- 该视角下的推荐方向
- 关键判断依据
- 风险与缓解方案
- 非妥协约束
- 与其他潜在视角可能产生的分歧点

推荐输出格式：

## Perspective Proposal

### Perspective Name
{当前视角名称}

### Recommended Approach
{该视角下的推荐方向}

### Core Reasoning
{这一视角的关键判断依据}

### Risks
1. {风险}: {缓解}
2. {风险}: {缓解}

### Hard Constraints
{该视角下不能忽略的边界}

### Dissent Points
{你预期会和其他视角产生分歧的地方}

### 澄清预算提醒

- 问题数量不按固定维度绑定，而由未解决的必问项决定
- 默认优先在 5 个问题内完成收口；如果仍有关键阻塞点，先由主代理汇总假设与风险，再请求用户决定是否追加 1 个定点问题
- 未经用户明确同意，不要把 PRD 阶段扩展成无限循环的问答流程

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
3. `project_memory`
4. `related_files`
5. `milestone_context`
6. `task_memory`
7. `review_feedback`（仅返工时提供）

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
3. `project_memory`
4. `task_memory`
5. `code_changes`
6. `developer_report`

职责：

- 检查功能正确性、代码质量、范围合规、测试覆盖、安全与性能
- 返回 `APPROVED`、`NEEDS_CHANGES` 或 `REJECTED`
- 提供具体修改建议或根本性问题说明
- 优先基于相关项目级记忆检查是否违反长期约束、偏好或已确认决策
- 优先基于当前 task 的 `memory.md` 快速理解既有改动，不要求重新扫描完整任务列表

## 调度协议

- 不要把“暂时没有回复”或“可用时间内未返回结果”直接等同于失败，更不要立刻让主代理接手兜底实现。
- 在子代理返回最终结果前，不要进入依赖该结果的下一个 step。
- 当主代理接手兜底实现时，先检查子代理已完成部分，不要重复工作。
- 分析子代理必须相互隔离，只有主代理可以看到全部视角的完整输出。
- 任务完成后关闭已完成的 agent thread，避免遗留噪声线程影响后续判断。
