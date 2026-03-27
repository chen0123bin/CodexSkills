# 子代理执行模式

## 进入条件

只有在用户明确表达以下意图时，才进入子代理执行模式：

- 要求使用子代理、subagent、委派、delegation
- 要求并行处理、多人分工、代理协作
- 明确指定用子代理完成开发和审查

如果用户没有明确提出上述要求，默认仍由主代理单独执行，不主动启用子代理。

## 默认子代理角色

本技能默认配套两个子代理角色：

- `fullstack-developer`
- `code-reviewer`

默认对应的代理配置路径为：

- `.codex/agents/fullstack-developer.toml`
- `.codex/agents/code-reviewer.toml`

## 角色分工

### 主代理

主代理负责任务编排与最终收拢：

1. 选择下一个可执行 task
2. 准备任务上下文包
3. 调度 `fullstack-developer`
4. 调度 `code-reviewer`
5. 根据审查结果决定通过、返工或阻塞
6. 做最终验证并更新 `task.md`、`progress.md`

### `fullstack-developer`

`fullstack-developer` 负责代码开发与实现。

输入上下文：

1. `task_description`
2. `done_criteria`
3. `related_files`
4. `milestone_context`
5. `review_feedback`（仅返工时提供）

职责：

- 完成当前 task 的代码开发
- 补充必要测试
- 返回 `DONE` 或 `BLOCKED`
- 报告改动文件、测试情况和需要注意的事项

### `code-reviewer`

`code-reviewer` 负责独立代码审查。

输入上下文：

1. `task_description`
2. `done_criteria`
3. `code_changes`
4. `developer_report`

职责：

- 检查功能正确性、代码质量、范围合规、测试覆盖、安全与性能
- 返回 `APPROVED`、`NEEDS_CHANGES` 或 `REJECTED`
- 提供具体修改建议或根本性问题说明


