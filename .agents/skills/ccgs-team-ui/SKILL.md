---
name: ccgs-team-ui
description: "Native UX, visual design, UI implementation, accessibility, and polish pipeline."
---
# UI team
Read `references/workflow.md`, player journey, UI requirements, patterns,
accessibility tier, art bible, and engine settings. `individual` runs
`ccgs-ui-programmer` + `ccgs-ux-designer`; `small` adds accessibility + art
director; `studio` adds engine UI specialist and adversarial review. Preserve
source phases, gates, and full/lean/solo semantics; unavailable required review
is `NOT ASSESSED` and solo is self-review.

Use `.agents/studio/scripts/team-run.py` init/assign --depends-on TASK/event/show/resume, retaining
actual IDs, dependencies, ownership, artifacts, failures, and resume state.
Validate returned content; receipts do not prove work. Named artifacts are
authorized by the brief, with no per-file prompts. UI never owns game state;
reviews/plans write no QA, story, evidence, or checkpoints. See
`references/workflow.md` for exact phases and paths.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
