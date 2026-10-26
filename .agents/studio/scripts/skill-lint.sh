#!/usr/bin/env bash
# Native skill observations; preserves the upstream TSV row families.
set -u
NAME=""; ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -gt 1 ] || { echo 'skill-lint: --root needs a value' >&2; exit 2; }; ROOT="$2"; shift 2;;
    --root=*) ROOT="${1#--root=}"; shift;;
    -h|--help) sed -n '2,/^$/p' "$0"; exit 0;;
    -*) echo "skill-lint: unknown argument $1" >&2; exit 2;;
    *) [ -z "$NAME" ] || { echo 'skill-lint: one skill name or all' >&2; exit 2; }; NAME="$1"; shift;;
  esac
done
[ -n "$NAME" ] || { echo 'skill-lint: no skill name given' >&2; exit 2; }
[ -n "$ROOT" ] || ROOT="$(cd "$(dirname "$0")/../../.." && pwd -W 2>/dev/null || pwd)"
PYBIN="$(command -v python3 || command -v py || command -v python || true)"; [ -n "$PYBIN" ] || { echo 'skill-lint: Python 3 required' >&2; exit 1; }
exec "$PYBIN" - "$ROOT" "$NAME" <<'PY'
import re,sys
from pathlib import Path
start=Path(sys.argv[1]).expanduser().resolve(); wanted=sys.argv[2]; root=start
while root!=root.parent and not ((root/'project.yaml').is_file() and (root/'.git').exists()): root=root.parent
base=root/'.agents/skills'
if not base.is_dir(): print(f'skill-lint: no {base}',file=sys.stderr); raise SystemExit(1)
names=sorted(p.name for p in base.iterdir() if p.is_dir() and (p/'SKILL.md').is_file())
if wanted!='all' and wanted not in names: print(f'skill-lint: no skill folder {base/wanted}',file=sys.stderr); raise SystemExit(3)
selected=names if wanted=='all' else [wanted]
print(f'skills\t{len(selected)}\t.agents/skills')
role_names={p.stem for p in (root/'.codex/agents').glob('*.toml')}
for name in selected:
    folder=base/name; main=folder/'SKILL.md'
    if not main.is_file(): print(f'NOT_READ\t{name}\tno SKILL.md'); continue
    paths=[main]+sorted((folder/'references').glob('*.md')) if (folder/'references').is_dir() else [main]
    text='\n'.join(p.read_text(encoding='utf-8',errors='replace') for p in paths); lines=main.read_text(encoding='utf-8',errors='replace').splitlines()
    end=next((i for i,x in enumerate(lines[1:],1) if x.strip()=='---'),None); fm={}
    if lines and lines[0].strip()=='---' and end is not None:
        for x in lines[1:end]:
            m=re.match(r'^([A-Za-z][\w-]*):(.*)$',x)
            if m: fm[m.group(1)]=m.group(2).strip()
        status='ok'
    else: status='missing' if not lines or lines[0].strip()!='---' else 'unclosed'
    miss=','.join(k for k in ('name','description') if k not in fm) or '-'
    nm='match' if fm.get('name','').strip(" '\"")==name else ('absent' if 'name' not in fm else 'mismatch:'+fm['name'])
    h2=[x[3:].strip() for x in lines if x.startswith('## ')]; phases=[x for x in h2 if re.match(r'(Phase\s+\d+|\d+\.)',x)]
    verdicts=[]
    for word in ('PASS','FAIL','CONCERNS','APPROVED','BLOCKED','COMPLETE','READY','COMPLIANT','NON-COMPLIANT','PROCEED','PIVOT','KILL','GO','NO-GO','CRITICAL','HIGH','MEDIUM','LOW'):
        n=len(re.findall(r'(?<![A-Za-z0-9_-])'+re.escape(word)+r'(?![A-Za-z0-9_-])',text));
        if n: verdicts.append(f'{word}:{n}')
    refs=sorted(set(re.findall(r'\bccgs-[a-z0-9-]+',text))); unknown=[r for r in refs if r not in names and r not in role_names]
    print(f'skill\t{name}\tfiles={len(paths)}\tlines={sum(len(p.read_text(encoding="utf-8",errors="replace").splitlines()) for p in paths)}')
    print(f'check1\t{name}\tfrontmatter={status}\tmissing={miss}\tname={nm}')
    print(f'check2\t{name}\tphases={len(set(phases))}\th2={len(set(h2))}\th2_total={len(h2)}')
    print(f'check3\t{name}\tverdicts={",".join(verdicts) or "-"}\tassessment_words={"-"}')
    print(f'check4\t{name}\tmay_i_write={len(re.findall("may i write",text,re.I))}\tbefore_writing={len(re.findall("before writing",text,re.I))}\tapproval={len(re.findall("approval",text,re.I))}\task_write_lines={sum("ask" in x.lower() and "writ" in x.lower() for x in text.splitlines())}\twrite_tools={"Write,Edit" if re.search(r"Write|Edit",fm.get("allowed-tools", "")) else "-"}')
    print(f'check5\t{name}\tlast_section={h2[-1] if h2 else "-"}\tskills_named={",".join(r for r in refs if r in names) or "-"}\tnext_phrases={len(re.findall(r"next step|recommended next|follow[- ]up|after this",text,re.I))}/0')
    print(f'check6\t{name}\tcontext_fork={"yes" if "context: fork" in text else "no"}\tphases={len(set(phases))}\th2={len(set(h2))}')
    print(f'check7\t{name}\thint={fm.get("argument-hint", "absent")}\targs_section={next((x for x in h2 if "argument" in x.lower() or "parse" in x.lower()), "-")}')
    if unknown: print(f'native-handoff\t{name}\tunknown={",".join(unknown)}')
print(f'checked\t{len(selected)} of {len(names)}')
PY
