#!/usr/bin/env python3
"""Read-only discovery; configuration/receipts never attest native trust or role execution."""
import argparse
import json
from pathlib import Path
import subprocess


def roots(start):
    project = None
    for candidate in (start, *start.parents):
        if project is None and ((candidate / "project.yaml").is_file() or
                                (candidate / "project.local.yaml").is_file()):
            project = candidate
        if (candidate / ".agents/studio/VERSION").is_file():
            return project or candidate, candidate
        if (candidate / ".git").exists():
            break
    raise ValueError("no studio resources inside this project boundary")


def inspect(start):
    project, framework = roots(start)
    skill_names = {p.parent.name for p in (framework / ".agents/skills").glob("*/SKILL.md")}
    configured = {"project_root": str(project), "resource_root": str(framework),
                  "project_yaml": (project / "project.yaml").is_file(),
                  "hooks_json": (framework / ".codex/hooks.json").is_file(),
                  "version": (framework / ".agents/studio/VERSION").read_text(encoding="utf-8").strip()}
    discovered = {"skills": len(skill_names),
                  "roles": len(list((framework / ".codex/agents").glob("*.toml"))),
                  "teams": len([name for name in skill_names if name.startswith("ccgs-team-")])}
    observed = {"git_branch": None, "hook_observed": None, "adapter_receipts": 0,
                "context_window": "UNAVAILABLE", "run_cost": "UNAVAILABLE"}
    branch = subprocess.run(["git", "-C", str(project), "branch", "--show-current"],
                            capture_output=True, encoding="utf-8", errors="replace")
    if branch.returncode == 0:
        observed["git_branch"] = branch.stdout.strip() or None
    for path in (project / ".scratch/runtime/receipts").glob("*.json"):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
            identity = receipt.get("identity", {})
            if (isinstance(identity, dict) and identity.get("hook_event_name") and
                identity.get("session_id") and len(receipt.get("payload_sha256", "")) == 64):
                observed["adapter_receipts"] += 1
        except (OSError, ValueError, AttributeError, TypeError):
            continue
    # Protocol fixtures can produce these same receipts; native execution needs
    # a separately retained host trace, and exact definition trust is host-owned.
    return {"configured": configured, "discovered": discovered, "observed": observed,
            "trust_unconfirmed": ["role_execution", "team_execution", "host_hook_execution",
                                  "host_trust", "context_window", "run_cost"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = inspect(Path(args.root).expanduser().resolve())
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=True))
        else:
            for group, facts in report.items():
                print(group.upper() + ":")
                if isinstance(facts, dict):
                    for name, value in facts.items():
                        print(f"  {name}: {value}")
                else:
                    print("  " + ", ".join(facts))
        return 0
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
