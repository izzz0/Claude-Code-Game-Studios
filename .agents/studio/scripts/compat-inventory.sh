#!/usr/bin/env bash
# Inventory native resources and report (without deleting) legacy compatibility text.
set -u
ROOT="${1:-}"
if [ -z "$ROOT" ]; then ROOT="$(cd "$(dirname "$0")/../../.." && pwd -W 2>/dev/null || pwd)"; fi
PYBIN="$(command -v python3 || command -v py || command -v python || true)"; [ -n "$PYBIN" ] || { echo 'compat-inventory: Python 3 required' >&2; exit 1; }
exec "$PYBIN" - "$ROOT" <<'PY'
import sys,re
from pathlib import Path
root=Path(sys.argv[1]); paths=[root/'AGENTS.md',root/'README.md',root/'.agents',root/'.codex']
files=[]
for base in paths:
    if base.is_file(): files.append(base)
    elif base.is_dir(): files.extend(p for p in base.rglob('*') if p.is_file() and p.suffix in {'.md','.sh','.py','.toml','.json','.yaml'})
legacy=re.compile(r'\.claude/|CLAUDE_(?:SKILL|PROJECT)_DIR|allowed-tools:|AskUserQuestion')
hits=[]
for p in sorted(set(files)):
    for n,line in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1):
        if legacy.search(line): hits.append((p.relative_to(root),n,line.strip()))
print(f'ROOT: {root}')
print(f'NATIVE_SKILLS: {len(list((root/".agents/skills").glob("*/SKILL.md")))}')
print(f'NATIVE_ROLES: {len(list((root/".codex/agents").glob("*.toml")))}')
print(f'NATIVE_HOOKS: {1 if (root/".codex/hooks.json").is_file() else 0}')
print(f'LEGACY_PATTERNS: {len(hits)} (diagnostic only; no blanket stripping)')
for path,n,line in hits: print(f'LEGACY: {path}:{n}: {line}')
PY
