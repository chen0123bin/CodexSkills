---
name: superpowers-project-manager
description: Use when Codex 需要用版本化 docs/superpowers 管理 superpowers 项目流程、启动或继续版本、保存 brainstorming/spec/plan/review/delivery 文档、维护 manifest.yaml/project-memory.md，或处理 feature/small-change/bugfix 流程。
---

# Superpowers 项目管理器

## 目标

使用本技能为 superpowers 原生工作流提供轻量项目管理层。它只维护版本、阶段、产物路径和项目记忆；不维护独立任务系统。任务定义和执行顺序保留在 superpowers plan 文件中。

本技能不替代 `superpowers:brainstorming`、`superpowers:writing-plans`、`superpowers:using-git-worktrees`、`superpowers:executing-plans`、`superpowers:subagent-driven-development`、`superpowers:systematic-debugging`、`superpowers:verification-before-completion`、`superpowers:finishing-a-development-branch` 等技能。

## 固定结构

项目文档根目录固定为：

```text
docs/superpowers/
```

初始化后的结构：

```text
docs/superpowers/
├── manifest.yaml
├── project-memory.md
└── v0.0.1/
    ├── execution-log.md
    └── delivery.md
```

禁止默认创建：

```text
brainstorming/
specs/
plans/
reviews/
tasks/
task001.md
fixes/
```

版本目录保持扁平。superpowers 生成的 spec、plan、review 或 brainstorming 记录按文件直接写入当前版本根目录，并由 manifest 指向当前 spec 和 plan。

## 初始化

如果 `docs/superpowers/manifest.yaml` 不存在，先运行脚本：

```bash
python .codex/skills/superpowers-project-manager/scripts/init_superpowers_project.py <repo-root> --project-name "项目名称" --version v0.0.1 --type feature
```

已有 manifest 时新增版本：

```bash
python .codex/skills/superpowers-project-manager/scripts/init_superpowers_project.py <repo-root> --version v0.0.2 --type bugfix
```

`type` 允许值：

```text
feature | small-change | bugfix
```

## Manifest

`docs/superpowers/manifest.yaml` 是唯一导航文件。

```yaml
project_name: "项目名称"
current_version: "v0.0.1"
current_phase: "brainstorming"
updated_at: "yyyy-MM-dd HH:mm:ss"

versions:
  v0.0.1:
    status: "active"
    phase: "brainstorming"
    type: "feature"
    spec: ""
    plan: ""
```

允许值：

```text
status: active | delivered | archived
phase: brainstorming | spec | plan | execute | review | delivery
type: feature | small-change | bugfix
```

约束：

- 不在 manifest 中记录 task。
- 不在 manifest 中记录执行日志、review、delivery 路径。
- 每次阶段变化时更新 `current_phase`、`updated_at`、`versions.<current_version>.phase`。
- 写入 spec 后更新 `versions.<current_version>.spec`。
- 写入 plan 后更新 `versions.<current_version>.plan`。
- 交付后更新 `versions.<current_version>.status = delivered` 和 `current_phase = delivery`。

## 每次启动

每次使用本技能时，先按顺序读取：

1. `docs/superpowers/project-memory.md`
2. `docs/superpowers/manifest.yaml`
3. 当前版本目录下与 `current_phase` 相关的文件

如果 manifest 指向的 spec 或 plan 不存在，停止并请求用户确认正确路径，不要猜测。

## 项目记忆

`project-memory.md` 只记录跨版本、跨阶段仍然有效的信息。

写入规则：

- 只有用户明确说“记住”“以后都按这个”“作为项目约定”等，才写入。
- 每条记忆包含时间、原因、内容。
- 时间格式统一为 `yyyy-MM-dd HH:mm:ss`。
- 不记录普通执行过程、命令输出、阶段总结、临时判断或 task 级流水。
- 如果新记忆覆盖旧记忆，优先更新旧条目，不重复堆积。

## 流程类型

### feature

用于完整功能、复杂改动、跨模块项目。

```text
brainstorming -> spec -> plan -> execute -> review -> delivery
```

规则：

- 使用 `superpowers:brainstorming` 进行需求澄清和设计。
- spec 写入 `docs/superpowers/<version>/`。
- 使用 `superpowers:writing-plans` 生成 plan。
- plan 写入 `docs/superpowers/<version>/`。
- plan 内 `### Task N` 是任务事实来源。
- 进入 execute 前，**REQUIRED SUB-SKILL:** Use `superpowers:using-git-worktrees` 建立或确认隔离工作区。
- 使用 `superpowers:executing-plans` 或 `superpowers:subagent-driven-development` 执行 plan。
- 执行进展、worktree 路径、阻塞、验证结果和关键决策写入 `execution-log.md`。
- review 结果写入当前版本根目录。
- 进入 delivery 时，**REQUIRED SUB-SKILL:** Use `superpowers:finishing-a-development-branch` 完成测试确认、合并/PR/保留/丢弃选择和 worktree 清理。
- finishing 完成后，将最终选择、分支结果和交付总结写入 `delivery.md`。

### small-change

用于简单明确、低风险的小改动。

```text
execute -> review -> delivery
```

规则：

- 不强制生成 spec。
- 不强制生成 plan。
- 开始前在 `execution-log.md` 写清修改意图、影响范围和验证方式。
- 进入 execute 前，**REQUIRED SUB-SKILL:** Use `superpowers:using-git-worktrees` 建立或确认隔离工作区。
- 进入 delivery 时，**REQUIRED SUB-SKILL:** Use `superpowers:finishing-a-development-branch` 完成分支收尾。
- 如果改动跨多个模块或风险升高，建议升级为 `feature`。

### bugfix

用于 BUG、异常、回归、报错定位。

```text
systematic-debugging -> execute -> review -> delivery
```

规则：

- 必须使用 `superpowers:systematic-debugging`。
- 不强制生成 spec。
- 不强制生成 plan。
- 进入 execute 前，**REQUIRED SUB-SKILL:** Use `superpowers:using-git-worktrees` 建立或确认隔离工作区。
- 在 `execution-log.md` 记录问题现象、复现方式、已确认事实、假设、验证、根因、修复摘要和回归验证。
- 根因不明确时，不进入修复；先继续排查。
- 进入 delivery 时，**REQUIRED SUB-SKILL:** Use `superpowers:finishing-a-development-branch` 完成分支收尾。
- 不默认创建 `fixes/` 或单 BUG 文件。

## 阶段协作

### execute

进入任何 execute 阶段前，先使用 `superpowers:using-git-worktrees`。如果当前会话已经位于本版本对应的隔离 worktree 中，记录该路径并继续；否则按该技能创建 worktree、完成基线检查，再开始执行。

不要在 main/master 或未确认的普通工作区直接执行实现计划，除非用户明确要求这样做；如果用户要求例外，把例外原因写入 `execution-log.md`。

### delivery

实现完成且验证记录已写入后，delivery 阶段对应 `superpowers:finishing-a-development-branch`。

先让 finishing 技能验证测试并向用户提供合并、创建 PR、保留分支或丢弃工作的选项。只有 finishing 流程完成后，才更新 `delivery.md` 和 manifest 的交付状态。

## 路径覆盖

当本技能与 superpowers 默认保存路径冲突时，以当前版本目录为准。

```text
docs/superpowers/specs/   -> docs/superpowers/<version>/
docs/superpowers/plans/   -> docs/superpowers/<version>/
```

如果用户明确要求“只分析，不写文件”，停在设计草案，不进入写 spec、写 plan 或初始化动作。

## 执行日志

`execution-log.md` 记录当前版本的过程信息。

阶段切换时写入阶段记录。验证必须写入验证记录；如果无法验证，也要写明原因。

允许在日志中记录“开始执行 plan 中 Task 2”这类事件，但这只是执行证据，不是任务状态系统。

## 恢复上下文

用户说“继续当前项目”时：

1. 读取 `project-memory.md`。
2. 读取 `manifest.yaml`。
3. 定位 `current_version`、`current_phase` 和 `type`。
4. 如果有 plan，读取 manifest 指向的 plan。
5. 读取当前版本的 `execution-log.md`。
6. 总结当前状态并继续对应 superpowers 流程。

## 下一版本

用户要求进入下一版本时：

1. 如果当前版本未 delivery，先提示是否仍要切换。
2. 运行初始化脚本创建新版本目录并更新 manifest。
3. 新版本初始阶段：
   - `feature`: `brainstorming`
   - `small-change`: `execute`
   - `bugfix`: `execute`

## 常见错误

- 不要创建 `tasks/`、`task001.md` 或默认 `fixes/`。
- 不要默认创建 `brainstorming/`、`specs/`、`plans/` 或 `reviews/`。
- 不要把 plan 内任务同步成独立文件。
- 不要把执行日志、测试结果或阶段总结写入 `project-memory.md`。
- 不要扩展或依赖 `project-orchestrator`。
- 不要一次性加载所有历史版本文档。
