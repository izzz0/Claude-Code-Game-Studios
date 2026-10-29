---
name: ccgs-soak-test
description: "Soak test protocol for extended play — what to observe and log for slow leaks, fatigue, late-appearing edge cases."
---

# Soak Test

Resolve the repository root and effective configuration before acting:
`bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,testing.strict,engine_values`.
Read `.agents/studio/docs/core-workflow.md` and the relevant engine reference.

## Evidence limits

- Do not infer performance or soak metrics from logs that do not report them. Mark unavailable measurements `NOT ASSESSED` and name the missing source.
- Do not publish messages, close bugs, or claim release readiness without explicit authorization from the caller.

## Detailed contract

Read `references/source-contract.md` for the source-derived workflow and artifact contract.
