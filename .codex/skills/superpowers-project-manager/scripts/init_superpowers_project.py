#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化版本化 superpowers 项目文档区。"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+$")
VALID_FLOW_TYPES = {"feature", "small-change", "bugfix"}
PHASE_BY_TYPE = {
    "feature": "brainstorming",
    "small-change": "execute",
    "bugfix": "execute",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="初始化或新增 docs/superpowers 版本化项目文档区。"
    )
    parser.add_argument("repo_root", help="目标仓库根目录。")
    parser.add_argument("--project-name", help="项目名称；首次初始化时必填。")
    parser.add_argument("--version", required=True, help="版本号，格式为 vX.Y.Z。")
    parser.add_argument(
        "--type",
        required=True,
        choices=sorted(VALID_FLOW_TYPES),
        help="流程类型：feature、small-change 或 bugfix。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖当前版本目录中的基础模板文件；不会覆盖 project-memory.md。",
    )
    return parser.parse_args(argv)


def current_timestamp() -> str:
    """读取系统当前时间并格式化为 yyyy-MM-dd HH:mm:ss。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_version(version: str) -> None:
    """校验版本号是否符合 vX.Y.Z 格式。"""
    if not VERSION_PATTERN.match(version):
        raise ValueError(f"版本号必须符合 vX.Y.Z 格式，当前值：{version}")


def validate_flow_type(flow_type: str) -> None:
    """校验流程类型是否为 feature、small-change 或 bugfix。"""
    if flow_type not in VALID_FLOW_TYPES:
        allowed = ", ".join(sorted(VALID_FLOW_TYPES))
        raise ValueError(f"流程类型必须是 {allowed}，当前值：{flow_type}")


def render_template(template: str, values: dict[str, str]) -> str:
    """使用变量替换渲染模板内容。"""
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def read_template(skill_root: Path, relative_path: str) -> str:
    """读取 skill 内置模板文件。"""
    template_path = skill_root / "assets" / "docs" / relative_path
    return template_path.read_text(encoding="utf-8")


def yaml_quote(value: str) -> str:
    """将字符串转换为当前 manifest 使用的双引号 YAML 标量。"""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_unquote(value: str) -> str:
    """解析当前 manifest 使用的简单 YAML 标量。"""
    text = value.strip()
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return text


def load_manifest(path: Path) -> dict[str, object]:
    """读取已有 manifest.yaml，并解析为固定结构字典。"""
    manifest: dict[str, object] = {"versions": {}}
    versions = manifest["versions"]
    current_version = ""

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if not raw_line.startswith(" "):
            if ":" not in raw_line:
                continue
            key, value = raw_line.split(":", 1)
            if key == "versions":
                continue
            manifest[key] = yaml_unquote(value)
            continue

        if raw_line.startswith("  ") and not raw_line.startswith("    "):
            current_version = raw_line.strip().rstrip(":")
            if isinstance(versions, dict):
                versions.setdefault(current_version, {})
            continue

        if raw_line.startswith("    ") and current_version:
            if ":" not in raw_line:
                continue
            key, value = raw_line.strip().split(":", 1)
            if isinstance(versions, dict):
                version_data = versions.setdefault(current_version, {})
                if isinstance(version_data, dict):
                    version_data[key] = yaml_unquote(value)

    return manifest


def dump_manifest(path: Path, manifest: dict[str, object]) -> None:
    """按固定结构写入 manifest.yaml。"""
    versions = manifest.get("versions", {})
    if not isinstance(versions, dict):
        raise ValueError("manifest.versions 必须是字典结构。")

    lines = [
        f"project_name: {yaml_quote(str(manifest.get('project_name', '')))}",
        f"current_version: {yaml_quote(str(manifest.get('current_version', '')))}",
        f"current_phase: {yaml_quote(str(manifest.get('current_phase', '')))}",
        f"updated_at: {yaml_quote(str(manifest.get('updated_at', '')))}",
        "",
        "versions:",
    ]

    for version, version_data in versions.items():
        if not isinstance(version_data, dict):
            raise ValueError(f"versions.{version} 必须是字典结构。")
        lines.extend(
            [
                f"  {version}:",
                f"    status: {yaml_quote(str(version_data.get('status', 'active')))}",
                f"    phase: {yaml_quote(str(version_data.get('phase', '')))}",
                f"    type: {yaml_quote(str(version_data.get('type', '')))}",
                f"    spec: {yaml_quote(str(version_data.get('spec', '')))}",
                f"    plan: {yaml_quote(str(version_data.get('plan', '')))}",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_text_if_needed(path: Path, content: str, force: bool = False) -> bool:
    """在文件不存在或允许覆盖时写入文本，返回是否发生写入。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def template_values(
    project_name: str, version: str, flow_type: str, timestamp: str
) -> dict[str, str]:
    """生成模板渲染所需的变量集合。"""
    return {
        "PROJECT_NAME": project_name,
        "VERSION": version,
        "TYPE": flow_type,
        "PHASE": PHASE_BY_TYPE[flow_type],
        "TIMESTAMP": timestamp,
    }


def ensure_project_memory(
    docs_root: Path, skill_root: Path, values: dict[str, str]
) -> bool:
    """确保 project-memory.md 存在，且不覆盖已有项目记忆。"""
    content = render_template(read_template(skill_root, "project-memory.md.tmpl"), values)
    return write_text_if_needed(docs_root / "project-memory.md", content, force=False)


def ensure_version_workspace(
    docs_root: Path,
    skill_root: Path,
    values: dict[str, str],
    force: bool = False,
) -> list[Path]:
    """创建指定版本的 superpowers 文档目录和基础文件。"""
    version_root = docs_root / values["VERSION"]
    written: list[Path] = []
    version_root.mkdir(parents=True, exist_ok=True)

    execution_log = render_template(
        read_template(skill_root, "version/execution-log.md.tmpl"), values
    )
    delivery = render_template(read_template(skill_root, "version/delivery.md.tmpl"), values)

    for path, content in (
        (version_root / "execution-log.md", execution_log),
        (version_root / "delivery.md", delivery),
    ):
        if write_text_if_needed(path, content, force=force):
            written.append(path)

    return written


def create_initial_manifest(values: dict[str, str]) -> dict[str, object]:
    """创建首次初始化所需的 manifest 数据结构。"""
    version = values["VERSION"]
    phase = values["PHASE"]
    return {
        "project_name": values["PROJECT_NAME"],
        "current_version": version,
        "current_phase": phase,
        "updated_at": values["TIMESTAMP"],
        "versions": {
            version: {
                "status": "active",
                "phase": phase,
                "type": values["TYPE"],
                "spec": "",
                "plan": "",
            }
        },
    }


def add_version_to_manifest(
    manifest: dict[str, object], values: dict[str, str]
) -> tuple[dict[str, object], bool]:
    """在已有 manifest 中新增版本，并返回是否发生新增。"""
    versions = manifest.setdefault("versions", {})
    if not isinstance(versions, dict):
        raise ValueError("manifest.versions 必须是字典结构。")

    version = values["VERSION"]
    if version in versions:
        return manifest, False

    phase = values["PHASE"]
    versions[version] = {
        "status": "active",
        "phase": phase,
        "type": values["TYPE"],
        "spec": "",
        "plan": "",
    }
    manifest["current_version"] = version
    manifest["current_phase"] = phase
    manifest["updated_at"] = values["TIMESTAMP"]
    return manifest, True


def initialize_or_update_project(
    repo_root: Path, project_name: str | None, version: str, flow_type: str, force: bool
) -> int:
    """初始化项目文档区或在已有 manifest 中新增版本。"""
    validate_version(version)
    validate_flow_type(flow_type)

    repo_root = repo_root.resolve()
    skill_root = Path(__file__).resolve().parents[1]
    docs_root = repo_root / "docs" / "superpowers"
    manifest_path = docs_root / "manifest.yaml"
    timestamp = current_timestamp()

    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        resolved_project_name = project_name or str(manifest.get("project_name", "")).strip()
        if not resolved_project_name:
            raise ValueError("已有 manifest 缺少 project_name，请使用 --project-name 指定。")
    else:
        if not project_name:
            raise ValueError("首次初始化必须提供 --project-name。")
        resolved_project_name = project_name
        manifest = {}

    values = template_values(resolved_project_name, version, flow_type, timestamp)
    docs_root.mkdir(parents=True, exist_ok=True)
    ensure_project_memory(docs_root, skill_root, values)
    ensure_version_workspace(docs_root, skill_root, values, force=force)

    if manifest_path.exists():
        manifest, added = add_version_to_manifest(manifest, values)
        if not added:
            print(f"版本已存在，已检查目录骨架：{version}")
            return 0
    else:
        manifest = create_initial_manifest(values)

    dump_manifest(manifest_path, manifest)
    print(f"已初始化 superpowers 文档区：{docs_root}")
    print(f"当前版本：{version}")
    print(f"当前阶段：{values['PHASE']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """执行命令行入口。"""
    args = parse_args(argv)
    try:
        return initialize_or_update_project(
            Path(args.repo_root), args.project_name, args.version, args.type, args.force
        )
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
