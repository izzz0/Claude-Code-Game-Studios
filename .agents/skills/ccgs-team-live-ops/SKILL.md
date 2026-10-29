---
name: ccgs-team-live-ops
description: "Native seasonal live-ops design, economy, analytics, narrative, copy, and comms pipeline."
---
# Live-ops team
Read `references/workflow.md`, cadence, economy, telemetry, policy, and brief.
`individual` runs live-ops-designer + economy-designer; `small` adds
analytics-engineer + community-manager; `studio` adds writer + narrative-
director. Preserve phases, decision points, no director panel, and full/lean/
solo behavior.

Use `.agents/studio/scripts/team-run.py` init/assign --depends-on TASK/event/show/resume for each
native run. Record actual IDs, dependencies, ownership, fixed paths, failures,
and resume; validate returned content. Named artifacts are authorized without
per-file prompts. Planning/review is read-only; parent owns economy, telemetry,
story, QA, and checkpoints. Exact contracts are in `references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
