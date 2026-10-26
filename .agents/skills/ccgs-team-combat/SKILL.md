---
name: ccgs-team-combat
description: "Native combat design, implementation, integration, and validation pipeline."
---
# Combat team
Read `.agents/studio/docs/core-workflow.md` and `references/workflow.md` first. Run the configuration helper explicitly before selecting the team. Resolve `review_mode`, `automation`, `workflow`,
and `team.size`; this pipeline has no director panel. `individual` runs
`ccgs-gameplay-programmer`, escalating `ccgs-ai-programmer` only for flagged AI;
`small` runs the full Team Composition; `studio` adds the configured engine
specialist and adversarial QA. Preserve full/lean/solo semantics; solo is
self-review and unavailable required review is `NOT ASSESSED`.

Use the provided runner for every native role run:
`python .agents/studio/scripts/team-run.py --root ROOT init --id ID --team team-combat --size SIZE --host-limit N`;
then `assign --id ID --task T --role ccgs-ROLE --files FILE... [--depends-on TASK...]`,
`event --id ID --task T --status running|completed|failed|interrupted --agent-id ACTUAL --summary SUMMARY [--artifact PATH]`,
`show --id ID`, and `resume --id ID`. Retain actual IDs, validate returned content,
and record ownership, artifacts, failures, and resume state. Receipts are not
proof of work. Named artifacts are pre-authorized; no per-file prompts. Review
and plans are read-only; parent owns story, QA, checkpoint, and durable writes.
See `references/workflow.md` for exact phases and paths.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
