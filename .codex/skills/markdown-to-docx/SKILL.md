---
name: markdown-to-docx
description: 使用 pandoc 将单个 Markdown 文件或顶层 Markdown 文章目录转换为 DOCX，未指定模板时默认使用 references/默认模板.dotx，并保留 Obsidian 图片嵌入、共享资源目录、图表题注、Mermaid 图表和可选 Word 参考模板。用于将 Markdown 导出为 Word 文档。
---

# 技能：Markdown 转 DOCX

当用户希望用 `pandoc` 将 `.md` 文件导出为 `.docx` 时使用此技能。

## 功能范围

- 转换单个 Markdown 文件，或转换目录下所有顶层 Markdown 文件。
- 为每个源 `.md` 文件生成一个 `.docx` 文件。
- 通过设置较宽的 `--resource-path` 保留图片资源。
- 转换前规范化 Obsidian 图片嵌入，例如 `![[image.png]]` 和 `![[image.png|697]]`。
- 修复图题与 Obsidian 图片被误合并到同一行的常见情况。
- 未指定模板时自动使用 `references/默认模板.dotx` 渲染 Markdown。
- 可使用显式 Word `.dotx`/`.docx` 参考模板覆盖默认模板，并执行后处理以得到更规范的 Word 输出。
- 当 Node.js 和 `npx` 可用时，将 Mermaid 代码块渲染为 PNG 图片。

## 工作流

1. 使用 `pandoc --version` 确认已安装 `pandoc`。
2. 按需检查源目录中的 Markdown 文件和图片语法。
3. 从此技能目录运行内置脚本：

```bash
SKILL_DIR="/path/to/markdown-to-docx"
"$SKILL_DIR/scripts/convert_markdown_to_docx.sh" \
  "<source-path>" \
  "<output-dir>" \
  "[resource-root]" \
  "[template-dotx-or-docx]"
```

## 参数

- `source-path`：单个 `.md` 文件，或包含 `.md` 文件的目录。
- `output-dir`：生成 `.docx` 文件的目标目录。
- `resource-root`（可选）：包含共享资源的根目录，例如 `resources/`。未提供时，脚本会根据源文件位置推断可能的根目录。
- `template-dotx-or-docx`（可选）：Word 参考模板。未提供时，脚本使用 `references/默认模板.dotx`。

## 模板工作流

当用户提供 Word 模板，或需要指定单个输出 DOCX 路径时：

### 第 1 步：转换（自动修复题注）

转换脚本会在调用 pandoc 前，向规范化后的 Markdown 中**自动插入缺失的表题/图题**。无需手动预检查，流水线会：

1. 规范化 Obsidian 嵌入和 Markdown 语法。
2. 运行 `validate_captions.py fix` 自动插入缺失的 `表N-M` / `图N-M` 题注，题注来自表头或周边上下文。
3. 使用 pandoc 和 Lua 样式过滤器完成转换。
4. 对 docx 执行后处理，包括字体、样式、表格、边框和页眉。

仍可手动运行预检查，提前查看将被修复的内容：

```bash
SKILL_DIR="/path/to/markdown-to-docx"
python3 "$SKILL_DIR/scripts/validate_captions.py" \
  pre "<source-md>"
```

```bash
SKILL_DIR="/path/to/markdown-to-docx"
"$SKILL_DIR/scripts/render_markdown_with_dotx.sh" \
  "<source-md>" \
  "<output-docx>" \
  "[template-dotx-or-docx]" \
  "[book-title]" \
  "[resource-root]" \
  "[shortcut-template]"
```

如果未传入 `template-dotx-or-docx`，或传入空字符串，脚本会使用 `references/默认模板.dotx`。如果希望使用默认模板但继续传入书名、资源根目录或快捷键模板，请把第三个参数传为空字符串，例如：

```bash
SKILL_DIR="/path/to/markdown-to-docx"
"$SKILL_DIR/scripts/render_markdown_with_dotx.sh" \
  "<source-md>" \
  "<output-docx>" \
  "" \
  "[book-title]" \
  "[resource-root]" \
  "[shortcut-template]"
```

该脚本会自动执行：

- 自动插入缺失的 `表N-M` / `图N-M` 题注，题注来自表头或周边上下文。
- 通过 Lua 过滤器将图片块、图题和表题映射到出版社段落样式。
- 后处理代码样式、字体（Times New Roman + 宋体）、表格边框和版式。
- 重写无序列表缩进，使项目符号文本与中文段落首行缩进对齐，而不是使用 Word 默认的过深缩进。
- 重写有序列表和无序列表，使标号列与中文正文段落的两字首行缩进对齐，避免过度左移。
- 对图片段落和表题应用 Word `keep with next`，确保图片与图题、表题与表格保持在一起。
- 移除导出的 `Source Code` 段落样式中的代码块首行缩进。
- 清除每个表格单元格段落中的首行缩进，避免表格内容继承正文缩进。
- 将页眉文本替换为章节标题。
- 当标题已包含显式章节编号时，抑制模板自动编号。
- 提取图注说明，并按编辑样式缩短题注。
- 可选地从原始 `.dotx` 模板注入 Word 快捷键绑定。
- 当提供的模板已包含 `word/customizations.xml` 时，自动保留 Word 快捷键绑定。

### 第 2 步：后检查，验证生成的 docx

```bash
SKILL_DIR="/path/to/markdown-to-docx"
python3 "$SKILL_DIR/scripts/validate_captions.py" \
  post "<output-docx>"
```

检查内容：

1. 不存在 `Compact` 样式段落，避免未定义样式。
2. 不存在 VML 水平线（`o:hr="t"`）。
3. 默认字体为 Times New Roman + 宋体，而不是 Calibri。
4. `Normal` 样式存在首行缩进。
5. 所有表格都有边框（tblBorders 或 tcBorders）。
6. 图片段落（`图`）和表题（`表题1-1`）包含 `keep with next`。
7. 代码块样式没有首行缩进。
8. 有序列表和无序列表的版式让标号列与中文段落首行缩进对齐。
9. 表格单元格段落显式清除首行缩进。
10. 表题（表X-Y）存在且编号连续。
11. 图题（图X-Y）存在且编号连续。

**如果后检查报告 ERROR，必须调查并修复。** 最常见的后检查错误是缺失题注，这通常表示 Markdown 源文件本身缺少题注，需要回到第 1 步处理。

当前编辑规则记录在：

- `references/editorial-template-rules.md`

## 注意事项

- 当传入目录时，脚本只转换顶层 `.md` 文件。
- 不修改源 Markdown 文件。规范化处理发生在临时目录中。
- `references/默认模板.dotx` 是默认 Word 模板；只有用户显式给出模板路径时才改用该模板。
- 如果用户需要递归转换，先修改脚本，不要临时重新实现一套流程。
- 如果出版社模板包含 `word/customizations.xml`，渲染脚本会自动把这些快捷键自定义注入生成的 `.docx`。当快捷键来源不同于参考模板时，仍可显式传入 `shortcut-template`。
- **强制要求**：转换后始终运行后检查。不要跳过验证。题注自动修复会在转换过程中自动运行。
