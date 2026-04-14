#!/usr/bin/env python3
"""初始化一个基于文档的项目编排工作流。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sys


VERSION_RE = re.compile(r"^v\d+\.\d+$")
LOCAL_TIMESTAMP_FORMAT = "【%Y-%m-%d %H:%M:%S】"


@dataclass(frozen=True)
class FileTemplate:
    source: str
    destination: str
    render_as_project_memory: bool = False


FILE_TEMPLATES = [
    FileTemplate("docs/.templates/analysis-summary-template.md", "docs/.templates/analysis-summary-template.md"),
    FileTemplate("docs/.templates/discovery-round-template.md", "docs/.templates/discovery-round-template.md"),
    FileTemplate("docs/.templates/project-memory-template.md", "docs/.templates/project-memory-template.md"),
    FileTemplate("docs/.templates/project-memory-template.md", "docs/project-memory.md", render_as_project_memory=True),
    FileTemplate("docs/.templates/prd-template.md", "docs/.templates/prd-template.md"),
    FileTemplate("docs/.templates/plan-template.md", "docs/.templates/plan-template.md"),
    FileTemplate("docs/.templates/task-index-template.md", "docs/.templates/task-index-template.md"),
    FileTemplate("docs/.templates/task-template.md", "docs/.templates/task-template.md"),
    FileTemplate("docs/.templates/progress-template.md", "docs/.templates/progress-template.md"),
    FileTemplate("docs/.templates/delivery-template.md", "docs/.templates/delivery-template.md"),
    FileTemplate("docs/manifest.yaml.tmpl", "docs/manifest.yaml"),
]


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Scaffold docs-first project orchestration files into a repository.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Target repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--project-name",
        default="",
        help="Project name stored in docs/manifest.yaml. Defaults to the repository directory name.",
    )
    parser.add_argument(
        "--version",
        default="v1.0",
        help="Initial workflow version, for example v1.0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing workflow files instead of skipping them.",
    )
    return parser.parse_args()


def local_timestamp() -> str:
    """生成本地时区的统一时间戳字符串。"""
    return datetime.now().astimezone().replace(microsecond=0).strftime(LOCAL_TIMESTAMP_FORMAT)


def normalize_project_name(repo_root: Path, raw_name: str) -> str:
    """标准化项目名称，优先使用用户输入，其次使用仓库目录名。"""
    candidate = raw_name.strip() or repo_root.name.strip() or "project"
    return candidate


def validate_version(version: str) -> None:
    """校验版本号是否符合 v<major>.<minor> 约定。"""
    if not VERSION_RE.match(version):
        raise ValueError("Version must match v<major>.<minor>, for example v1.0")


def render_template(text: str, replacements: dict[str, str]) -> str:
    """按占位符映射渲染普通模板文本。"""
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def render_project_memory(text: str, project_name: str, timestamp: str) -> str:
    """渲染项目级记忆模板，并写入初始化默认条目。"""
    rendered = text
    rendered = rendered.replace("{项目名称}", project_name)
    rendered = rendered.replace("{date}", timestamp)
    rendered = rendered.replace(
        "| {datetime} | {为什么要记住} | {精简后的项目级事实/约束/偏好/术语/决策} |",
        f"| {timestamp} | 初始化 | 暂无项目级记忆 |",
    )
    return rendered


def ensure_directory(path: Path, dry_run: bool) -> None:
    """按需创建目录，并在 dry-run 模式下仅输出计划动作。"""
    if path.exists():
        print(f"[skip] dir  {path}")
        return
    print(f"[create] dir  {path}")
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def write_file(
    source_path: Path,
    destination_path: Path,
    replacements: dict[str, str],
    force: bool,
    dry_run: bool,
    render_as_project_memory: bool,
) -> None:
    """将模板渲染后写入目标文件，必要时覆盖已有内容。"""
    exists = destination_path.exists()
    if exists and not force:
        print(f"[skip] file {destination_path}")
        return

    action = "[overwrite]" if exists else "[create]"
    print(f"{action} file {destination_path}")
    if dry_run:
        return

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_text = source_path.read_text(encoding="utf-8")
    if render_as_project_memory:
        content = render_project_memory(source_text, replacements["PROJECT_NAME"], replacements["TIMESTAMP"])
    else:
        content = render_template(source_text, replacements)
    destination_path.write_text(content, encoding="utf-8")


def main() -> int:
    """执行初始化主流程，生成 docs 工作流骨架。"""
    args = parse_args()

    repo_root = Path(args.repo_root).resolve()
    validate_version(args.version)
    project_name = normalize_project_name(repo_root, args.project_name)
    timestamp = local_timestamp()

    skill_root = Path(__file__).resolve().parent.parent
    template_root = skill_root / "assets"

    if not template_root.exists():
        print(f"[error] Missing template directory: {template_root}")
        return 1

    replacements = {
        "PROJECT_NAME": project_name,
        "VERSION": args.version,
        "TIMESTAMP": timestamp,
    }

    print(f"Repository root: {repo_root}")
    print(f"Project name: {project_name}")
    print(f"Version: {args.version}")
    if args.dry_run:
        print("Mode: dry-run")
    elif args.force:
        print("Mode: write with overwrite")
    else:
        print("Mode: write missing files only")
    print()

    if not repo_root.exists():
        print(f"[create] dir  {repo_root}")
        if not args.dry_run:
            repo_root.mkdir(parents=True, exist_ok=True)

    ensure_directory(repo_root / "docs", args.dry_run)
    ensure_directory(repo_root / "docs" / ".templates", args.dry_run)
    ensure_directory(repo_root / "docs" / args.version, args.dry_run)
    ensure_directory(repo_root / "docs" / args.version / "discovery", args.dry_run)

    for template in FILE_TEMPLATES:
        source_path = template_root / template.source
        destination_path = repo_root / template.destination
        if not source_path.exists():
            print(f"[error] Missing template file: {source_path}")
            return 1
        write_file(
            source_path,
            destination_path,
            replacements,
            args.force,
            args.dry_run,
            template.render_as_project_memory,
        )

    print()
    if args.dry_run:
        print("Dry run completed.")
    else:
        print("Initialization completed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"[error] {exc}")
        raise SystemExit(1) from exc
