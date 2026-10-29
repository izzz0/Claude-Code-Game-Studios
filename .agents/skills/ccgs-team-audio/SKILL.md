---
name: ccgs-team-audio
description: "Native sonic direction, SFX, accessibility, integration, and audio review pipeline."
---
# Audio team
Read `references/workflow.md`, sound bible, assets, and brief. `individual` runs
`ccgs-sound-designer`; `small` adds audio-director, technical-artist, and
gameplay-programmer; `studio` adds accessibility and the primary engine
specialist. Preserve source phase gates, no director panel, and full/lean/solo
behavior; solo is self-review and unavailable required review is `NOT ASSESSED`.

Use `.agents/studio/scripts/team-run.py` init/assign --depends-on TASK/event/show/resume for all
native runs, retaining actual IDs, dependencies, ownership, paths, failures,
and resume. Validate content; receipts are not proof. Named artifacts need no
per-file prompt. Review/planning is read-only; parent owns durable audio/QA
updates. Exact phases, accessibility blockers, and paths are in
`references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
