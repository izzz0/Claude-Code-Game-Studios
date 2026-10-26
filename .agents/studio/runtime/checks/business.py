"""Adapt native file payloads to the preserved read-only business helpers."""
from pathlib import Path
import subprocess
import tempfile
import time

from context import helper


def native_input(data):
    inp = data.get("tool_input", {})
    if not isinstance(inp, dict):
        return {"command": str(inp)}
    if "command" not in inp:
        for key in ("cmd", "freeform_input", "input"):
            if key in inp:
                return {**inp, "command": inp[key]}
    return inp


def patch_contents(root, data, paths):
    """Reconstruct exact-context native hunks; unsupported fuzz is explicitly unassessed."""
    inp = native_input(data)
    tool = str(data.get("tool_name", "")).rsplit(".", 1)[-1]
    if tool == "Write":
        return {p: str(inp["content"]) for p, _ in paths} if "content" in inp else {}
    if tool == "Edit":
        p = paths[0][0] if paths else None
        if p is None or not p.is_file() or "old_string" not in inp or "new_string" not in inp:
            return {}
        text = p.read_text(encoding="utf-8-sig")
        old = str(inp["old_string"])
        if not old or text.count(old) == 0 or (text.count(old) != 1 and not inp.get("replace_all")):
            return {}
        return {p: text.replace(old, str(inp["new_string"]), -1 if inp.get("replace_all") else 1)}
    if tool not in {"apply_patch", "ApplyPatch"}:
        return {}
    cwd = Path(data.get("cwd") or root).resolve()
    lines = str(inp.get("command", inp.get("patch", ""))).splitlines()
    result, index = {}, 0
    while index < len(lines):
        header = lines[index]
        if not header.startswith(("*** Add File: ", "*** Update File: ", "*** Delete File: ")):
            index += 1
            continue
        action, name = header[4:].split(" File: ", 1)
        original = (cwd / name.replace("\\", "/")).resolve()
        target = original
        index += 1
        block = []
        while index < len(lines) and not lines[index].startswith(("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** End Patch")):
            if lines[index].startswith("*** Move to: "):
                target = (cwd / lines[index].split(": ", 1)[1].replace("\\", "/")).resolve()
            else:
                block.append(lines[index])
            index += 1
        if action == "Delete":
            result[original] = ""
        elif action == "Add":
            if all(line.startswith("+") for line in block):
                result[target] = "\n".join(line[1:] for line in block) + "\n"
        elif original.is_file():
            old = original.read_text(encoding="utf-8-sig").splitlines()
            chunks, chunk = [], []
            for line in block:
                if line.startswith("@@"):
                    if chunk:
                        chunks.append(chunk)
                    chunk = []
                elif line != "*** End of File":
                    chunk.append(line if line else " ")
            if chunk:
                chunks.append(chunk)
            cursor, output, supported = 0, [], True
            for chunk in chunks:
                before = [line[1:] for line in chunk if line.startswith((" ", "-"))]
                after = [line[1:] for line in chunk if line.startswith((" ", "+"))]
                if not before or any(not line.startswith((" ", "-", "+")) for line in chunk):
                    supported = False
                    break
                locations = [i for i in range(cursor, len(old) - len(before) + 1) if old[i:i+len(before)] == before]
                if len(locations) != 1:
                    supported = False
                    break
                at = locations[0]
                output.extend(old[cursor:at])
                output.extend(after)
                cursor = at + len(before)
            if supported:
                result[target] = "\n".join(output + old[cursor:]) + "\n"
                if target != original:
                    result[original] = ""
    return result


def meaningful(result):
    rows = [line for line in result.stdout.splitlines()
            if line.split("\t", 1)[0] in {
                "OVERWRITE", "ENUM", "NOT_LOCAL", "REVIEW_MODE", "PROTOTYPE_HEADER",
                "PROTOTYPE_IMPORT", "FREEZE", "REMOVED", "STATUS", "LAYOUT",
                "DUPLICATE", "TR_UNKNOWN", "PATH_MISSING", "UNQUOTED", "SKIPPED", "LARGE"}]
    if result.returncode:
        rows.append("NOT ASSESSED: helper failed: " + result.stderr.strip())
    return rows


def check(root, data, paths=(), after=False, budget=6):
    root = Path(root).resolve()
    paths = [((root / target).resolve(), relative) for target, relative in paths]
    notes = []
    deadline = time.monotonic() + budget
    def run(*args):
        remaining = deadline - time.monotonic()
        if remaining <= 0.1:
            raise TimeoutError("business-check budget exhausted")
        try:
            return helper(root, *args, timeout=min(5, remaining))
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"helper timed out after {remaining:.2f}s") from exc
    proposed = {} if after else patch_contents(root, data, paths)
    directory = root / ".scratch/runtime/tmp"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=directory) as temporary:
        for number, (target, relative) in enumerate(paths):
            if time.monotonic() >= deadline - 0.1:
                notes.append(f"NOT ASSESSED: business checks exceeded the hook budget; {len(paths) - number} paths require explicit checks.")
                break
            content = proposed.get(target)
            temp = Path(temporary) / f"proposed-{number}"
            if content is not None:
                temp.write_text(content, encoding="utf-8")
            guarded = relative.startswith(("production/epics/", "docs/engine-reference/", "tests/helpers/",
                                           "prototypes/", "src/", "Assets/", "Source/", "assets/data/strings/")) or relative in {
                                               "project.yaml", "project.local.yaml", "project.godot",
                                               "production/review-mode.txt", "docs/tech-debt-register.md"}
            if not after and guarded:
                if content is None:
                    notes.append(f"NOT ASSESSED: proposed content could not be reconstructed: {relative}; run the explicit checks against the intended content before proceeding.")
                    continue
                args = ["--root", str(root), "check", relative]
                if content is not None:
                    args.append(str(temp))
                args += ["--tool", "Edit" if target.exists() else "Write"]
                # A native Write replacing an existing file remains an overwrite.
                tool = str(data.get("tool_name", "")).rsplit(".", 1)[-1]
                patch = str(native_input(data).get("command", ""))
                added = any(line.startswith("*** Add File: ") and
                            (Path(data.get("cwd") or root) / line.split(": ", 1)[1].replace("\\", "/")).resolve() == target
                            for line in patch.splitlines())
                if tool == "Write" or added:
                    args[-1] = "Write"
                try:
                    notes.extend(meaningful(run(".agents/studio/scripts/write-guard.sh", *args)))
                except (TimeoutError, subprocess.TimeoutExpired):
                    notes.append(f"NOT ASSESSED: business checks timed out at {relative}; run the explicit helper checks.")
                    break
            registry = {"design/registry/entities.yaml": "entities",
                        "docs/architecture/tr-registry.yaml": "tr",
                        "docs/registry/architecture.yaml": "architecture"}.get(relative)
            if registry:
                try:
                    if after:
                        notes.extend(meaningful(run(".agents/studio/scripts/registry.sh", "--root", str(root), "validate")))
                    elif content is None:
                        notes.append(f"NOT ASSESSED: proposed registry content could not be reconstructed: {relative}; compare it explicitly before proceeding.")
                    else:
                        notes.extend(meaningful(run(".agents/studio/scripts/registry.sh", "--root", str(root),
                                                   "compare", registry, str(target), str(temp))))
                except (TimeoutError, subprocess.TimeoutExpired):
                    notes.append(f"NOT ASSESSED: registry checks timed out at {relative}; compare/validate explicitly.")
                    break
    return notes
