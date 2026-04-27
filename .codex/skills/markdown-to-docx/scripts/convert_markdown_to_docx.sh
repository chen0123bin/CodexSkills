#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  convert_markdown_to_docx.sh <source-path> <output-dir> [resource-root] [template-dotx-or-docx]

Arguments:
  source-path             A single .md file or a directory containing .md files
  output-dir              Destination directory for generated .docx files
  resource-root           Optional root directory for shared assets such as resources/
  template-dotx-or-docx   Optional Word template. Defaults to references/默认模板.dotx
EOF
  exit 1
}

[[ $# -lt 2 || $# -gt 4 ]] && usage

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
DEFAULT_TEMPLATE="$SCRIPT_DIR/../references/默认模板.dotx"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Error: pandoc is not installed or not in PATH." >&2
  exit 1
fi

SOURCE_PATH="$1"
OUTPUT_DIR="$2"

if [[ -f "$SOURCE_PATH" ]]; then
  SOURCE_DIR="$(cd "$(dirname "$SOURCE_PATH")" && pwd -P)"
elif [[ -d "$SOURCE_PATH" ]]; then
  SOURCE_DIR="$(cd "$SOURCE_PATH" && pwd -P)"
else
  echo "Error: source path not found: $SOURCE_PATH" >&2
  exit 1
fi

SOURCE_PARENT="$(cd "$SOURCE_DIR/.." && pwd -P)"
RESOURCE_ROOT="${3:-$SOURCE_PARENT}"
TEMPLATE_DOC="${4:-$DEFAULT_TEMPLATE}"

if [[ ! -f "$TEMPLATE_DOC" ]]; then
  echo "Error: template file not found: $TEMPLATE_DOC" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# 函数用途：收集单文件或目录顶层 Markdown 源文件。
collect_sources() {
  if [[ -f "$SOURCE_PATH" ]]; then
    printf '%s\n' "$SOURCE_PATH"
    return
  fi

  find "$SOURCE_PATH" -maxdepth 1 -type f -name '*.md' | sort
}

# 函数用途：将一个 Markdown 文件转换为 DOCX，未显式传模板时使用技能内置默认模板。
convert_one() {
  local src_file="$1"
  local base_name output_file

  base_name="$(basename "$src_file" .md)"
  output_file="$OUTPUT_DIR/$base_name.docx"

  "$SCRIPT_DIR/render_markdown_with_dotx.sh" \
    "$src_file" \
    "$output_file" \
    "$TEMPLATE_DOC" \
    "" \
    "$RESOURCE_ROOT"
}

converted_count=0

while IFS= read -r src_file; do
  [[ -n "$src_file" ]] || continue
  convert_one "$src_file"
  converted_count=$((converted_count + 1))
done < <(collect_sources)

if [[ "$converted_count" -eq 0 ]]; then
  echo "Error: no Markdown files found to convert." >&2
  exit 1
fi

printf 'Converted %d file(s) into %s\n' "$converted_count" "$OUTPUT_DIR"
