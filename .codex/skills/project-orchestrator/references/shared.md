# 共享规则

在需要跨 phase 规则时读取本文件。
如果当前任务只依赖某个 phase 的步骤，不要默认把本文件和所有 phase 文件一起读入上下文。

## 上下文管理规则

为避免上下文溢出，优先遵循以下加载边界：

| 阶段 | 加载的文件 | 默认不加载 |
|------|-----------|-----------|
| 全阶段共享 | `project-memory.md` | 无 |
| PRD-当前轮问答 | `project-memory.md` + 用户需求 + `manifest.yaml` + 前序 `round-{N}.md` 摘要 | 代码文件、历史版本完整栈 |
| 分析-单视角子代理 | 相关的 `project-memory.md` 条目 + 已完成的 `round-{N}.md` + 当前视角简报 | 其他视角分析、代码文件、完整 PRD |
| 分析-综合 | 相关的 `project-memory.md` 条目 + `perspective-*-proposal.md` + 已完成的 `round-{N}.md` | 代码文件 |
| 收敛 | `project-memory.md` + `prd.md` + `manifest.yaml` | 代码文件、历史版本细节 |
| 执行-当前任务 | `project-memory.md` 中相关条目 + `manifest.yaml` 中当前版本的分支信息 + `progress.md` 中的当前任务摘要 + 当前任务文件 + `plan.md` 中的必要约束 + 相关代码文件 | 完整 PRD、其他任务文件、全量历史 |
| 执行-验证 | `project-memory.md` 中相关条目 + `manifest.yaml` + `progress.md` + 当前任务文件 + 变更文件 | 完整 PRD、discovery 全量内容 |
| 交付 | `project-memory.md` + `manifest.yaml` + `progress.md` + `plan.md` + 必要的任务文件摘要 | 代码细节、discovery 原稿 |
| 版本迭代 | `project-memory.md` + 上一版本 `delivery.md` | 上一版本其他完整文档 |

## 用户交互检查点

| 阶段 | 是否需要用户介入 |
|------|----------------|
| 每轮问答回答 | 必须 |
| 多视角分析综合方案选择 | 必须 |
| PRD 最终确认 | 必须 |
| plan/progress 收敛确认 | 建议 |
| 每个 task 执行 | 自动 |
| review 结果 | 自动 |
| 执行前 Git 状态冲突 | 必须 |
| 连续阻塞介入 | 必须 |
| 交付确认 | 必须 |
| 交付期 merge 冲突 | 必须 |
| 新版本启动 | 必须 |

## Git 规范

如果仓库使用 Git 且用户要求提交：

- 执行阶段开始前先检查 `git status --short --branch`
- 当前版本的 `base_branch` 与 `execute_branch` 必须记录到 `manifest.yaml`
- 执行分支建议命名为 `codex/v{版本号}-execute`
- 如果当前版本已有 `execute_branch`，优先复用；不要重复创建多个执行分支
- 如果工作区在非当前版本执行分支上存在未提交改动，不自动 stash、reset 或强行提交
- 每个 task 完成后尽量立即 commit
- commit message 可采用 `[v{版本号}] task001: {任务标题}` 这类稳定格式
- docs 状态变更尽量与对应工作一并提交
- 交付阶段在用户确认后切回 `base_branch`，merge `execute_branch`；只有成功后才删除执行分支
- 交付阶段的文档更新可单独作为一次交付提交

如果用户没有要求提交，也要保持 docs 状态与实际进度一致。
