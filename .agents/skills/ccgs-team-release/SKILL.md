---
name: ccgs-team-release
description: "Coordinate release planning, quality gates and a verified local release package with native roles."
---
# Release team
Read `references/workflow.md`, stage, milestones, build evidence, platform
requirements, QA, security, and rollback inputs. Preserve the release-stage
gate, explicit acceptance of CONCERNS, no-director-panel rule, and exact full/lean/solo
behavior and team-size sets in the contract.

Every role uses `.agents/studio/scripts/team-run.py` init, `assign --depends-on TASK`,
event, show, and resume. Retain actual IDs and validate content;
record ownership, artifacts, failures, and resume. Named artifacts are
pre-authorized, no per-file prompts. Do not publish or message external systems
without a corresponding explicit request. Acceptance stops at a runnable local package. Reviews/plans are read-only; parent owns release status,
QA, checkpoint, and durable writes. Missing evidence is `NOT ASSESSED`.

For each command, include the same `python .agents/studio/scripts/team-run.py --root ROOT` prefix. Register read-only reviewers with `assign --read-only`; list only writable ownership under `--files`. The CLI records observations and cannot attest that an agent executed.
