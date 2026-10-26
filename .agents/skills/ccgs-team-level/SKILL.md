---
name: ccgs-team-level
description: "Native level narrative, layout, systems, production, accessibility, and playtest pipeline."
---
# Level team
Read `references/workflow.md`, level brief, journey, canon, and constraints.
`individual` runs `ccgs-level-designer`; `small` adds systems-designer,
art-director, and qa-tester; `studio` adds narrative-director, world-builder,
and accessibility-specialist. Preserve source gates, no director panel, and
full/lean/solo semantics.

Use `.agents/studio/scripts/team-run.py` init/assign --depends-on TASK/event/show/resume for every run, retaining
actual IDs, output validation, ownership, fixed paths, failures, and resume.
Named artifacts are authorized without further prompts. Reviews/plans write no
QA, story, checkpoint, or evidence updates. Exact phase/path contracts are in
`references/workflow.md`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
