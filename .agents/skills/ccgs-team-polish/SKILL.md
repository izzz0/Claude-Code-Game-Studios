---
name: ccgs-team-polish
description: "Native performance, rendering, audio, tooling, regression, and adversarial polish pipeline."
---
# Polish team
Read `references/workflow.md`, budgets, diff, findings, and regression scope.
`individual` runs `ccgs-performance-analyst` + `ccgs-technical-artist` only;
no programmer is active. `small` adds sound-designer, qa-tester,
engine-programmer, and conditional tools-programmer; `studio` is the small set
plus adversarial QA. Preserve source phases and no-director-panel behavior.
Solo is self-review; unavailable required review is `NOT ASSESSED`.

Use `.agents/studio/scripts/team-run.py` for init/assign --depends-on TASK/event/show/resume,
with actual IDs, dependencies, ownership, fixed artifacts, failures, and
resume. Validate output; receipts are not proof. Named artifacts are already
authorized. Review/plan runs are read-only. Exact phase/path contracts are in
`references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
