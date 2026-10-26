---
name: ccgs-story-done
description: Verify and close one story using acceptance, parse/runtime, review, and evidence gates with precise final status.
---

# Story close

Read .agents/studio/docs/core-workflow.md, resolve the root, the story template, .agents/studio/docs/templates/session-state.md, and docs/engine-reference/<engine>/VERSION.md.

## Inputs

An In Review story, changed files, review receipt, test output, parse result, runtime evidence, and screenshots.

## Actions

- Resolve config with bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values; stop on unsupported tiers.
- Read the story, facts, receipt, logs, evidence note, and screenshots. Verify each AC; never infer absent evidence.
- A failing AC is BLOCKED; missing mandatory evidence or unavailable checks are NOT ASSESSED. Actual test failures/timeouts remain failures. An applicable minimal automated-test waiver is explicit WAIVED, never test PASS; it permits completion only when every remaining required criterion is established.
- Only after all required criteria pass, use bash .agents/studio/scripts/md-section.sh set-field <story> Status Complete and update matching sprint status if present. Do not use read-only fact/status scripts to write.
- Retain the review response/hashes with the completion evidence. Update session-state.sh checkpoint via stdin with verdict, actual files, next step, blockers and run result, unless session state is disabled.

## Output

Return criterion matrix, review receipt, evidence paths, verdict (COMPLETE, COMPLETE WITH NOTES, NOT ASSESSED, or BLOCKED), and next story. Do not close incomplete work.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.