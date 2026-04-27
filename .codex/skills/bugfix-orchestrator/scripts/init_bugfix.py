#!/usr/bin/env python3
"""初始化当前版本下的缺陷索引与单缺陷工作单。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
INDEX_ROW_MARKER = "<!-- BUG_ROWS -->"


@dataclass(frozen=True)
class BugContext:
    """封装缺陷初始化所需的核心上下文。"""

    repo_root: Path
    version: str
    bug_title: str
    bug_slug: str
    priority: str
    timestamp: str

    @property
    def fix_dir(self) -> Path:
        """返回当前版本的 fix 目录。"""
        return self.repo_root / "docs" / self.version / "fix"

    @property
    def index_path(self) -> Path:
        """返回缺陷索引文件路径。"""
        return self.fix_dir / "index.md"

    @property
    def bug_path(self) -> Path:
        """返回单缺陷工作单路径。"""
        return self.fix_dir / f"bug_{self.bug_slug}.md"

    @property
    def bug_id(self) -> str:
        """返回缺陷 ID。"""
        return f"bug_{self.bug_slug}"


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Create docs/<version>/fix/index.md and a bug_<slug>.md work item.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="目标仓库根目录，默认为当前目录。",
    )
    parser.add_argument(
        "--bug-name",
        required=True,
        help="缺陷名称，用作标题和文件名来源。",
    )
    parser.add_argument(
        "--version",
        default="",
        help="目标版本；为空时从 docs/manifest.yaml 的 current_version 推断。",
    )
    parser.add_argument(
        "--priority",
        default="P1",
        help="缺陷优先级，默认为 P1。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的 bug_<slug>.md 文件。",
    )
    return parser.parse_args()


def current_timestamp() -> str:
    """生成统一格式的当前本地时间字符串。"""
    return datetime.now().astimezone().replace(microsecond=0).strftime(TIMESTAMP_FORMAT)


def normalize_bug_title(raw_title: str) -> str:
    """清洗用户输入的缺陷标题。"""
    title = raw_title.strip()
    if not title:
        raise ValueError("缺陷名称不能为空。")
    return title


def slugify_bug_title(title: str) -> str:
    """将缺陷标题转换为适合文件名的 slug。"""
    normalized = re.sub(r"[\\/:*?\"<>|]+", "-", title)
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    normalized = normalized.strip("-_")
    if not normalized:
        raise ValueError("缺陷名称无法转换为有效文件名。")
    return normalized


def detect_version(repo_root: Path) -> str:
    """从 manifest.yaml 中读取当前活跃版本。"""
    manifest_path = repo_root / "docs" / "manifest.yaml"
    if not manifest_path.exists():
        raise ValueError("未找到 docs/manifest.yaml，请先初始化 project-orchestrator 文档骨架。")

    content = manifest_path.read_text(encoding="utf-8")
    match = re.search(r"^current_version:\s*\"?([^\r\n\"]+)\"?\s*$", content, re.MULTILINE)
    if not match:
        raise ValueError("无法从 docs/manifest.yaml 解析 current_version。")
    return match.group(1).strip()


def load_template(skill_root: Path, relative_path: str) -> str:
    """读取技能目录中的模板文件。"""
    template_path = skill_root / relative_path
    if not template_path.exists():
        raise ValueError(f"缺少模板文件: {template_path}")
    return template_path.read_text(encoding="utf-8")


def render_template(template: str, replacements: dict[str, str]) -> str:
    """按占位符映射渲染模板内容。"""
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def ensure_fix_dir(path: Path) -> None:
    """确保 fix 目录存在。"""
    path.mkdir(parents=True, exist_ok=True)


def write_index_if_missing(index_path: Path, content: str) -> None:
    """在索引文件不存在时写入初始内容。"""
    if not index_path.exists():
        index_path.write_text(content, encoding="utf-8")


def update_index_header(content: str, version: str, timestamp: str) -> str:
    """刷新索引头部中的最后更新时间。"""
    return re.sub(
        r"^> 版本: .* \| 最后更新: .* \| 时间格式: `yyyy-MM-dd HH:mm:ss`$",
        f"> 版本: {version} | 最后更新: {timestamp} | 时间格式: `yyyy-MM-dd HH:mm:ss`",
        content,
        count=1,
        flags=re.MULTILINE,
    )


def append_index_row(content: str, row: str) -> str:
    """将新的缺陷记录追加到索引表格。"""
    if row in content:
        return content
    if INDEX_ROW_MARKER not in content:
        raise ValueError("index.md 缺少 BUG_ROWS 标记，无法安全追加缺陷记录。")
    return content.replace(INDEX_ROW_MARKER, f"{row}\n{INDEX_ROW_MARKER}")


def build_index_row(context: BugContext) -> str:
    """生成索引表中的一行记录。"""
    return (
        f"| `{context.bug_id}` | {context.bug_title} | `reported` | `{context.priority}` | "
        f"[`bug_{context.bug_slug}.md`](./bug_{context.bug_slug}.md) | {context.timestamp} |"
    )


def write_bug_file(path: Path, content: str, force: bool) -> None:
    """写入单缺陷工作单，必要时覆盖。"""
    if path.exists() and not force:
        raise ValueError(f"缺陷文件已存在：{path}；如需覆盖请使用 --force。")
    path.write_text(content, encoding="utf-8")


def build_context(args: argparse.Namespace) -> BugContext:
    """根据命令行参数构建缺陷初始化上下文。"""
    repo_root = Path(args.repo_root).resolve()
    version = args.version.strip() or detect_version(repo_root)
    bug_title = normalize_bug_title(args.bug_name)
    bug_slug = slugify_bug_title(bug_title)
    timestamp = current_timestamp()
    return BugContext(
        repo_root=repo_root,
        version=version,
        bug_title=bug_title,
        bug_slug=bug_slug,
        priority=args.priority.strip() or "P1",
        timestamp=timestamp,
    )


def main() -> int:
    """执行缺陷工作流初始化。"""
    args = parse_args()
    context = build_context(args)

    skill_root = Path(__file__).resolve().parent.parent
    index_template = load_template(skill_root, "assets/docs/.templates/fix-index-template.md")
    bug_template = load_template(skill_root, "assets/docs/.templates/bug-template.md")

    replacements = {
        "VERSION": context.version,
        "TIMESTAMP": context.timestamp,
        "BUG_TITLE": context.bug_title,
        "BUG_SLUG": context.bug_slug,
        "PRIORITY": context.priority,
    }

    ensure_fix_dir(context.fix_dir)

    index_content = render_template(index_template, replacements)
    write_index_if_missing(context.index_path, index_content)

    current_index = context.index_path.read_text(encoding="utf-8")
    current_index = update_index_header(current_index, context.version, context.timestamp)
    current_index = append_index_row(current_index, build_index_row(context))
    context.index_path.write_text(current_index, encoding="utf-8")

    bug_content = render_template(bug_template, replacements)
    write_bug_file(context.bug_path, bug_content, args.force)

    print(f"[ok] version     {context.version}")
    print(f"[ok] fix dir     {context.fix_dir}")
    print(f"[ok] index file  {context.index_path}")
    print(f"[ok] bug file    {context.bug_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"[error] {exc}")
        raise SystemExit(1) from exc
