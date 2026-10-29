#!/usr/bin/env python3
"""Small, dependency-free Cocos Creator 3.8.8 adapter.

The adapter deliberately owns observation only: it runs an explicitly supplied
Node/Cocos command, parses Node TAP, and emits TSV rows for test-run.sh.  It
does not install npm packages, start a game, or treat a process exit of zero as
test evidence.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import signal
from pathlib import Path


def parse_tap(text: str) -> dict[str, int | bool]:
    """Read complete flat TAP or Node TAP with per-record test/suite metadata."""
    empty = dict(recognized=False, total=0, passed=0, failed=0, skipped=0,
                 cancelled=0, todo=0, executed=0)
    summary, groups, records, plans, prefix_plans = {}, {}, [], {}, {}
    root_closed = False
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        indent = len(raw) - len(raw.lstrip())
        if re.match(r"Bail out!", line, re.I):
            return empty
        match = re.fullmatch(r"# (tests|suites|pass|fail|cancelled|skipped|todo) (\d+)", raw)
        if match:
            key, value = match.groups()
            if key in summary:
                return empty
            summary[key] = int(value)
            continue
        match = re.fullmatch(r"1\.\.(\d+)(?:\s+#.*)?", line)
        if match:
            count = int(match.group(1))
            pending = groups.get(indent, [])
            if pending or count == 0:
                if pending != list(range(1, count + 1)):
                    return empty
                groups[indent] = []
                if indent == 0:
                    root_closed = True
            else:
                prefix_plans[indent] = count
            plans[indent] = plans.get(indent, 0) + 1
            current = None
            continue
        match = re.fullmatch(r"(not ok|ok)\s+(\d+)(?:\s+-\s+[^#]+)?(?:\s+#\s*(.*))?", line, re.I)
        if match:
            if indent == 0 and root_closed:
                return empty
            ok, index, directive = match.groups()
            groups.setdefault(indent, []).append(int(index))
            current = dict(ok=ok.lower() == 'ok', directive=(directive or '').lower(),
                           suite=False, cancelled=False, indent=indent)
            records.append(current)
        elif current and indent > current['indent']:
            if re.fullmatch(r"type:\s*['\"]suite['\"]", line):
                current['suite'] = True
            if re.match(r"failureType:\s*['\"]?cancelled", line):
                current['cancelled'] = True
    for indent, count in prefix_plans.items():
        if groups.get(indent, []) != list(range(1, count + 1)):
            return empty
        groups[indent] = []
    if plans.get(0) != 1 or any(groups.values()):
        return empty
    tests = [r for r in records if not r['suite']]
    counts = dict(total=len(tests), passed=0, failed=0, skipped=0, cancelled=0, todo=0)
    for record in tests:
        directive = record['directive']
        if directive.startswith('skip'):
            counts['skipped'] += 1
        elif directive.startswith('todo'):
            counts['todo'] += 1
        elif record['cancelled']:
            counts['cancelled'] += 1
        else:
            counts['passed' if record['ok'] else 'failed'] += 1
    if summary:
        expected = dict(tests=counts['total'], **{key: counts[value] for key, value in
                        [('pass','passed'),('fail','failed'),('cancelled','cancelled'),
                         ('skipped','skipped'),('todo','todo')]})
        if any(summary.get(key) != value for key, value in expected.items()):
            return empty
        if 'suites' in summary and summary['suites'] != sum(r['suite'] for r in records):
            return empty
    elif any(r['indent'] for r in records):
        return empty
    return dict(recognized=True, **counts, executed=counts['passed'] + counts['failed'])


def _run(command: str, cwd: Path, timeout: int) -> tuple[int, str, bool, float]:
    """Bound a runner and its process group without inherited-pipe deadlocks."""
    started = time.time()
    # Regular files avoid communicate() waiting on a descendant's inherited pipe.
    import tempfile
    with tempfile.TemporaryFile() as log:
        kwargs = dict(cwd=str(cwd), shell=True, stdout=log, stderr=subprocess.STDOUT)
        if os.name == 'nt':
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        else:
            kwargs['start_new_session'] = True
        try:
            proc = subprocess.Popen(command, **kwargs)
        except OSError as exc:
            return 127, str(exc), False, started
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            if os.name == 'nt':
                try:
                    subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   timeout=5, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            else:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=2)
        log.seek(0)
        output = log.read().decode('utf-8', 'replace')
    return (124 if timed_out else proc.returncode), output, timed_out, started


def _read_reports(root: Path, explicit: str | None, started: float) -> tuple[str, str | None]:
    paths = [root / explicit] if explicit else []
    if not paths:
        for pattern in ("*.tap", "*.tap.txt", "test-results/*.tap", "reports/*.tap"):
            paths.extend(root.glob(pattern))
    fresh = [p for p in paths if p.is_file() and p.stat().st_mtime >= started - 0.01]
    if not fresh:
        return "", None
    chosen = max(fresh, key=lambda p: p.stat().st_mtime)
    try:
        return chosen.read_text(encoding="utf-8", errors="replace"), str(chosen)
    except OSError:
        return "", str(chosen)


def test(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    code, output, timed_out, started = _run(args.cmd, root, args.timeout)
    report_text, report_path = _read_reports(root, args.report, started)
    # An explicit report is authoritative.  Never let stdout rescue a missing
    # or stale report selected by the caller.
    parsed = parse_tap(report_text if args.report else output)
    if not parsed["recognized"] and not args.report:
        parsed = parse_tap(report_text)
    recognized = bool(parsed["recognized"])
    print("tests\ttotal=%s passed=%s failed=%s skipped=%s cancelled=%s todo=%s" %
          tuple(parsed[key] for key in ("total", "passed", "failed", "skipped", "cancelled", "todo")))
    print(f"zero_tests\t{'yes' if recognized and int(parsed['total']) == 0 else 'no' if recognized else 'unknown'}\t-")
    for key in ("total", "passed", "failed", "skipped", "cancelled", "todo"):
        print(f"{key}\t{parsed[key]}")
    print(f"report\t{report_path or '-'}")
    print(f"tap_recognized\t{'yes' if recognized else 'no'}")
    print(f"exit\t{code}")
    print(f"timed_out\t{'yes' if timed_out else 'no'}")
    if timed_out:
        rule = "timeout"
    elif code == 127:
        rule = "runner-unavailable"
    elif not recognized:
        rule = "missing-report"
    elif int(parsed["failed"]) or int(parsed["cancelled"]):
        rule = "cocos:test-fail"
    elif int(parsed["total"]) == 0 or int(parsed["executed"]) == 0:
        rule = "zero-tests"
    elif code != 0:
        rule = "cocos:runner-fail"
    else:
        rule = "cocos:pass"
    print(f"rule\t{rule}")
    print("result\tPASS" if rule == "cocos:pass" else "result\tNOT ASSESSED" if rule in ("missing-report", "zero-tests", "runner-unavailable") else "result\tFAIL")
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        evidence = output
        if report_text and report_text not in evidence:
            evidence += ("\n" if evidence else "") + report_text
        Path(args.log).write_text(evidence, encoding="utf-8")
    return 0


def build(args: argparse.Namespace) -> int:
    """Run an explicit build and verify a fresh runnable output exists."""
    root = Path(args.root).resolve()
    started = time.time()
    code, output, timed_out, _ = _run(args.cmd, root, args.timeout)
    output_path = (root / args.output).resolve() if args.output else None
    fresh = False
    artifact = False
    if output_path and output_path.exists():
        if output_path.is_file():
            artifact = True
            fresh = output_path.stat().st_mtime >= started - 0.01
        elif output_path.is_dir():
            entry = output_path / "index.html"
            artifact = entry.is_file()
            fresh = artifact and entry.stat().st_mtime >= started - 0.01
    web_entry = bool(output_path and output_path.is_dir() and (output_path / "index.html").is_file())
    print(f"build_exit\t{code}")
    print(f"build_timed_out\t{'yes' if timed_out else 'no'}")
    print(f"build_output\t{output_path or '-'}")
    print(f"build_fresh\t{'yes' if fresh else 'no'}")
    print(f"build_artifact\t{'yes' if artifact else 'no'}")
    print(f"build_web_entry\t{'yes' if web_entry else 'no'}")
    print("build_result\tPASS" if code == 0 and fresh and artifact else "build_result\tFAIL")
    print("build_runtime\tNOT ASSESSED")
    if args.log:
        Path(args.log).parent.mkdir(parents=True, exist_ok=True)
        Path(args.log).write_text(output, encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ("test", "build"):
        p = sub.add_parser(mode)
        p.add_argument("--root", required=True)
        p.add_argument("--cmd", required=True)
        p.add_argument("--timeout", type=int, default=900)
        p.add_argument("--log")
        if mode == "test":
            p.add_argument("--report")
        else:
            p.add_argument("--output", required=True)
        p.set_defaults(func=test if mode == "test" else build)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
