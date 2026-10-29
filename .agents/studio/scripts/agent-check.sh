#!/usr/bin/env bash
# Native role/skill observations. Supports --root DIR, --skill NAME, --agent NAME.
set -u
ROOT=""; SKILL=""; AGENT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -gt 1 ] || { echo 'agent-check: --root needs a value' >&2; exit 2; }; ROOT="$2"; shift 2;;
    --root=*) ROOT="${1#--root=}"; shift;;
    --skill) [ $# -gt 1 ] || { echo 'agent-check: --skill needs a value' >&2; exit 2; }; SKILL="$2"; shift 2;;
    --skill=*) SKILL="${1#--skill=}"; shift;;
    --agent) [ $# -gt 1 ] || { echo 'agent-check: --agent needs a value' >&2; exit 2; }; AGENT="$2"; shift 2;;
    --agent=*) AGENT="${1#--agent=}"; shift;;
    -h|--help) sed -n '2,/^$/p' "$0"; exit 0;;
    *) echo "agent-check: unknown argument $1" >&2; exit 2;;
  esac
done
[ -n "$ROOT" ] || ROOT="$(cd "$(dirname "$0")/../../.." && pwd -W 2>/dev/null || pwd)"
PYBIN="$(command -v python3 || command -v py || command -v python || true)"; [ -n "$PYBIN" ] || { echo 'agent-check: Python 3 required' >&2; exit 1; }
exec "$PYBIN" - "$ROOT" "$SKILL" "$AGENT" <<'PY'
import re, sys, tomllib
from pathlib import Path
start=Path(sys.argv[1]).expanduser().resolve(); sf=sys.argv[2]; af=sys.argv[3]
root=start
while root != root.parent and not ((root/'project.yaml').is_file() and (root/'.git').exists()): root=root.parent
if not (root/'project.yaml').is_file(): print(f'agent-check: no project.yaml under {start}',file=sys.stderr); raise SystemExit(1)
roles=root/'.codex/agents'; skills=root/'.agents/skills'
if not roles.is_dir() or not skills.is_dir(): print('agent-check: native folders missing',file=sys.stderr); raise SystemExit(1)
rp=sorted(roles.glob('*.toml')); sp=sorted(skills.glob('*/SKILL.md')); rn={p.stem for p in rp}; sn={p.parent.name for p in sp}
print(f'ROOT: {root}'); print(f'AGENTS: {len(rp)}  SKILLS: {len(sn)}  SKILL_FILES: {len(sp)}')
if af and af not in rn: print(f'NOT FOUND: agent {af}')
if sf and sf not in sn: print(f'NOT FOUND: skill {sf}')
for p in rp:
    if sf or (af and p.stem != af): continue
    notes=[]
    try: d=tomllib.loads(p.read_text(encoding='utf-8')); status='ok'
    except Exception as exc: d={}; status='invalid'; notes.append(str(exc))
    if d.get('name') != p.stem: notes.append('name does not match filename')
    if not isinstance(d.get('description'),str) or not d['description'].strip(): notes.append('missing description')
    unknown=set(d)-{'name','description','developer_instructions'}
    if unknown: notes.append('unknown keys: '+','.join(sorted(unknown)))
    refs=set(re.findall(r'\bccgs-[a-z0-9-]+',str(d.get('developer_instructions',''))))
    missing=sorted(x for x in refs if x not in sn and x not in rn)
    if missing: notes.append('unknown native references: '+','.join(missing))
    print(f'AGENT: {p.stem} toml={status} description={d.get("description","")}')
    for n in notes: print(f'  NOTE: {n}')
for p in sp:
    if sf and p.parent.name != sf: continue
    refs=sorted(set(re.findall(r'\bccgs-[a-z0-9-]+',p.read_text(encoding='utf-8',errors='replace')))); unknown=[x for x in refs if x not in sn and x not in rn]
    print(f'SKILL: {p.parent.name} routes={",".join(refs) if refs else "none"}')
    if unknown: print('  NOTE: unknown native references: '+','.join(unknown))
PY
