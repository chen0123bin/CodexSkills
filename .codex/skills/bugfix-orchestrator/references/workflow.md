# 缺陷工作流参考

## 定位

这个技能是 `project-orchestrator` 的并行补充流程，用于处理当前版本中的缺陷修复工作。
它复用已有的 `docs/project-memory.md` 与 `docs/manifest.yaml`，但不进入版本级 PRD / plan / delivery 状态机。

## 前置条件

开始前应确认仓库已经存在以下文件：

- `docs/project-memory.md`
- `docs/manifest.yaml`

如果缺少这些基础文件，先使用 `project-orchestrator` 初始化文档骨架，再回到当前技能。

## 读取顺序

每次启动缺陷工作流时，按以下顺序加载上下文：

1. `docs/project-memory.md`
2. `docs/manifest.yaml`
3. 当前技能的 `references/workflow.md`
4. `docs/<version>/fix/index.md`
5. 当前缺陷对应的 `docs/<version>/fix/bug_<slug>.md`
6. 与当前缺陷直接相关的代码与测试

除非用户明确需要，不要为了一个 bug 重新读取整个版本目录下的所有历史文档。

## 目录结构

```text
docs/
├── project-memory.md
├── manifest.yaml
└── v1.0/
    ├── ...
    └── fix/
        ├── index.md
        ├── bug_login-timeout.md
        └── bug_order-submit-error.md
```

## 文档职责

### `docs/<version>/fix/index.md`

用于汇总当前版本下所有缺陷工作单，避免文件散乱。

索引至少包含：

- 缺陷 ID
- 标题
- 状态
- 优先级
- 文档链接
- 最后更新时间

### `docs/<version>/fix/bug_<slug>.md`

单缺陷工作单同时承担三类职责：

1. 分析单：记录现象、影响、复现信息、期望与实际表现、根因判断
2. 执行单：记录修复方案、涉及文件、执行动作和关键决策
3. 验证单：记录测试命令、手动验证、回归范围、结果与关闭结论

不要把同一个 bug 再拆成额外 task 文档，除非用户明确要求。

## 标准流程

### 1. 建档

- 读取 `docs/manifest.yaml` 中的 `current_version`
- 确保 `docs/<version>/fix/` 存在
- 如果 `index.md` 不存在，先创建它
- 为当前问题创建 `bug_<slug>.md`
- 在 `index.md` 中登记一条记录

### 2. 分析

至少补齐以下内容：

- 现象描述
- 影响范围
- 复现条件
- 复现步骤
- 期望结果
- 实际结果
- 初步根因假设
- 待确认点

如果问题信息不足，一次只追问 1 个最阻塞的澄清问题。

### 3. 修复

- 基于当前缺陷文档补全修复方案
- 执行代码修改
- 把涉及文件、关键决策和执行记录写回同一个 `bug_<slug>.md`

### 4. 验证

至少记录：

- 自动化测试命令
- 手动验证步骤
- 验证结果
- 回归检查范围
- 未解决风险

### 5. 关闭

- 将状态更新为 `closed`，或根据实际情况保留为 `blocked`
- 在 `bug_<slug>.md` 中写明最终结论与关闭时间
- 在 `index.md` 中同步最后更新时间和最终状态

## 状态规则

推荐状态集合：

- `reported`
- `analyzing`
- `ready_to_fix`
- `fixing`
- `verifying`
- `closed`
- `blocked`

工作流应保持简单，默认不要扩展更多状态。

## Manifest 约束

- `docs/manifest.yaml` 仍然只表示版本级主流程状态
- 缺陷工作流不修改 `current_version`
- 缺陷工作流不修改 `current_phase`
- 缺陷修复完成后，也不要自动触发新的版本迭代

## 项目级记忆约束

- `docs/project-memory.md` 只存放跨版本、跨问题长期有效的信息
- 普通缺陷过程、执行记录、一次性判断和临时日志不要写入项目级记忆
- 只有当用户明确表示“记住这个”时，才把缺陷相关的长期结论落盘

## 上下文控制

- 优先加载当前缺陷文档，而不是一次性读取多个 bug 文件
- 多个缺陷并行时，每次只把当前正在处理的那个工作单带入主上下文
- 回答用户时优先总结结论，不回放大量命令输出或探索日志
