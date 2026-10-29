#!/usr/bin/env python3
"""Project-scoped atomic compare-and-swap writes; never starts an agent."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
import sys


class StateError(Exception):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def root_path(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise StateError(f"root is not a directory: {value}")
    return root


def safe_target(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise StateError("path resolves outside project root")
    if candidate == root:
        raise StateError("path must name a file")
    return candidate


def digest(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    if not path.is_file():
        raise StateError(f"target is not a regular file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextmanager
def file_lock(path: Path, timeout: float = 10):
    """A crash releases this OS lock; a live writer is never age-evicted.

    Keep the file in place: unlinking it could create two different lock inodes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        deadline = time.monotonic() + timeout
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    raise StateError("state lock timeout", 4)
                time.sleep(0.02)
        try:
            # Initialize the lock byte only while holding the OS lock. Otherwise
            # simultaneous first users can race while extending the empty file.
            if path.stat().st_size == 0:
                handle.seek(0)
                handle.write(b"\0")
                handle.flush()
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def lock_path(root: Path, target: Path) -> Path:
    identity = os.path.normcase(str(target.resolve()))
    key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return root / ".scratch/runtime/locks" / f"{key}.lock"


def atomic_bytes(target: Path, content: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = target.stat().st_mode & 0o777 if target.exists() else 0o666
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_cas(root: Path, target: Path, source: str, expected: str, operation: str) -> dict:
    if expected != "MISSING" and not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise StateError("expected-sha256 must be a SHA-256 digest or MISSING")
    source_path = Path(source)
    if not source_path.is_file():
        raise StateError("source must be an existing temporary file")
    content = source_path.read_bytes()
    new_digest = hashlib.sha256(content).hexdigest()
    with file_lock(lock_path(root, target)):
        actual = digest(target)
        unchanged = actual.lower() == new_digest
        if not unchanged and actual.lower() != expected.lower():
            raise StateError(f"stale state: expected {expected}, found {actual}", 3)
        if not unchanged:
            atomic_bytes(target, content)
    return {"ok": True, "unchanged": unchanged, "operation": operation,
            "path": str(target), "sha256": new_digest}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--source", required=True, help="Path to an existing temporary file")
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--operation", required=True)
    args = parser.parse_args(argv)
    try:
        root = root_path(args.root)
        result = write_cas(root, safe_target(root, args.path), args.source,
                           args.expected_sha256, args.operation)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except StateError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": exc.code}), file=sys.stderr)
        return exc.code
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": 1}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
