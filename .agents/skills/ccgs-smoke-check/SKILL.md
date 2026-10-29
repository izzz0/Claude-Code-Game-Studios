---
name: ccgs-smoke-check
description: "Critical-path smoke gate before QA hand-off — runs the automated suite. A failed check means the build is not QA-ready."
---

# Smoke Check

Resolve the repository root and effective configuration before acting:
`bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values`.
Read `.agents/studio/docs/core-workflow.md` and the relevant engine reference.

## Gate invariants

- Resolve the repository root and run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values` before interpreting the result.
- Keep compile/import parsing, automated tests, and player-visible runtime observation as separate facts. A helper exit code of 0 is not a test pass.
- A configured suite with zero tests, missing results, or an unavailable runner is `NOT ASSESSED`, never a pass or waiver. A configured test failure is `FAIL`; a required timeout is also `FAIL`, never `NOT ASSESSED`. Minimal waiver applies only to genuinely unconfigured automated tests when no stricter story requirement exists.
- At `qa.level: minimal`, an unconfigured automated suite may be explicitly `WAIVED` only when no stricter story requirement exists. If a suite is configured and runs, `FAIL` remains `FAIL` and holds hand-off; it is never downgraded to an advisory result. At `standard` and `full`, a required failed or unassessed smoke gate also holds QA hand-off.
- Required runtime/screenshot evidence is never waived; missing mandatory observation blocks the gate. Preserve `Run result: OBSERVED — ...` or `Run result: NOT VERIFIED — ...` exactly.
- Do not edit implementation or tests to make a smoke result pass; return findings and keep the story open when the gate is not established.

## Detailed contract

Read `references/source-contract.md` for the source-derived workflow and artifact contract.
Detailed phase references are loaded conditionally:
- `references/1-detect-setup.md`
- `references/2-run-tests.md`
- `references/3-coverage.md`
- `references/4-manual-checks.md`
- `references/5-report.md`
- `references/6-write-gate.md`
