---
name: ccgs-team-narrative
description: "Native narrative direction, canon, writing, localization, and review pipeline."
---
# Narrative team
Read `references/workflow.md`, canon, brief, and GDD sections. `individual` runs
`ccgs-writer`; `ccgs-narrative-director` is only for explicit pillar conflict.
`small` runs director + writer, adding localization/world-builder only at
`review_mode=full`; lean/solo consult them through writer. `studio` runs all
six composition roles regardless of review mode. Preserve decision points and
full/lean/solo independent-review semantics.

Use `.agents/studio/scripts/team-run.py` init, `assign --depends-on TASK`,
event, show, and resume for every native role run. Retain actual IDs, outputs,
ownership, fixed artifacts, failures, and resume state; validate content.
Named working artifacts are pre-authorized, so do not ask per-file permission.
Review/plan runs are read-only; parent owns durable design/story/checkpoint
writes. Exact phases and destinations are in `references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
