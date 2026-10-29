---
name: ccgs-team-qa
description: "Native QA strategy, test planning, execution, bugs, evidence, regression, and sign-off pipeline."
---
# QA team
Read `references/workflow.md`, scope, stage, open bugs, smoke report, criteria,
runner configuration, and evidence. `individual` runs qa-tester only; qa-lead
is invoked at phase gates. `small` runs qa-lead + qa-tester; `studio` runs
qa-lead plus per-story qa-tester and sign-off. Preserve smoke-failure stops,
evidence rules, verdict ordering, and full/lean/solo semantics.

Use `.agents/studio/scripts/team-run.py` init/assign --depends-on TASK/event/show/resume, with
dependencies at phase gates. Retain actual IDs, validate returned content, and
record ownership, artifacts, failures, and resume. Receipts/manifests are not
test evidence. Fixed QA paths are pre-authorized; no per-file prompts.
Review/planning runs do not write QA/checkpoint records; parent owns durable
updates. Exact paths and verdict rules are in `references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
