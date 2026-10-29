---
name: ccgs-gate-check
description: "Ready to advance between development phases? PASS/CONCERNS/NOT ASSESSED/FAIL with blockers and required artifacts. 'Can we move to production?'"
---

# Gate Check

Resolve the repository root and effective configuration before acting:
`bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values`.
Read `.agents/studio/docs/core-workflow.md` and the relevant engine reference.

## Gate invariants

- Resolve the root and effective configuration before selecting a gate; default to the project's existing minimal/guided configuration when present.
- `FAIL` and `NOT ASSESSED` hold the stage. `CONCERNS` is non-blocking only after an identified human explicitly accepts the listed risks; policy/configuration alone is not acceptance. `strict_gate_checks` is reserved and has no effect unless a future contract explicitly enables it.
- A configured numeric coverage threshold requires an actual numeric coverage report; if the threshold is configured but the report is absent, non-numeric, or unreadable, return `NOT ASSESSED`. A null or absent threshold is not a numeric gate.
- Update stage only after recording evidence; keep read-only audits read-only and return the caller's response rather than publishing or mutating unrelated artifacts.

## Detailed contract

Read `references/source-contract.md` for the source-derived workflow and artifact contract.
Detailed phase references are loaded conditionally:
- `references/2b-workflow-tier.md`
- `references/3-run-gate-check.md`
- `references/4-assessment.md`
- `references/5-verdict.md`
- `references/6-update-stage.md`
- `references/7-next-steps.md`
- `references/gate-polish.md`
- `references/gate-pre-production.md`
- `references/gate-production.md`
- `references/gate-release.md`
- `references/gate-systems-design.md`
- `references/gate-technical-setup.md`
