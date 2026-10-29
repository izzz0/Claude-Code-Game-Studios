---
name: ccgs-dev-story
description: Implement one Ready story through a planned engine workflow, preserving status, files, runtime evidence, and recovery checkpoints.
---

# Develop a story

Read .agents/studio/docs/core-workflow.md, resolve the root, the story template, and docs/engine-reference/<engine>/VERSION.md.

## Inputs

One story in production/epics/**, pinned engine commands, existing files/tests, and current checkpoint. Resolve:
bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values.

## Required sequence

1. Accept Ready, an interrupted In Progress story, or In Review work returned for fixes. Verify dependencies are Complete and named ADRs Accepted. Set Status "In Progress" through md-section.sh set-field and read back; do not reopen Complete work without a requested change.
2. Plan five phases: understand/AC map, design/scope, implement, verify, handoff. Record actual Files before editing.
3. Implement only the story in src/, Assets/, or Source/; preserve unrelated work and remove only new orphans.
4. Create production/qa/, parse/import the actual changed files, then run game tests as described in core-workflow.md. For a supported built-in runner, use bash .agents/studio/scripts/test-run.sh <engine> --log production/qa/test.log (<engine> is godot, unity or unreal). Run a configured custom runner directly under a timeout and inspect its own results. Never equate a helper exit with test success.
5. Run the real game and retain evidence under production/qa/evidence/<story-slug>/; emit exactly one Run result: line in the evidence note. If interrupted, keep In Progress and checkpoint the next action.
6. Replace the story's Files with actual changes, write its evidence note and hash stamp, and keep any matching sprint entry consistent. On verified handoff (including an applicable minimal test waiver), set Status "In Review"; checkpoint actual files, run result and next skill. Failures or missing mandatory evidence keep In Progress.

## Output and route

Report Files, commands/results, evidence paths, and stamp. Then invoke ccgs-smoke-check, followed by ccgs-code-review, followed by ccgs-story-done; do not jump directly to closure. Missing runtime is NOT ASSESSED, never a pass.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.