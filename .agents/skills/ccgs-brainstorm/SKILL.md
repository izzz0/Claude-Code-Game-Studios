---
name: ccgs-brainstorm
description: Turn a theme or open question into a minimal game brief with an explicit MVP feature list and build order.
---

# Brainstorm

Read `.agents/studio/docs/core-workflow.md`, resolve the root, and read `.agents/studio/docs/templates/game-brief.md`.

## Inputs

User seed, audience/platform/constraints, existing `design/game-brief.md`, and resolved minimal/guided configuration.

## Actions

- Resolve config with `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow`; stop for unsupported non-minimal tiers.
- Ask only questions that change the smallest viable game. Write player goal, core loop, boundaries, risks, success criteria, MVP features, and ordered Build order.
- Never overwrite a non-empty brief. Use normal file editing and preserve existing decisions; a replacement needs explicit approval.
- Use `bash .agents/studio/scripts/set-stage.sh <Stage>` after the brief is saved. Do not create code or stories here.

## Output

Return the brief path and MVP/build-order summary. Route to `ccgs-prototype` when the central hypothesis is uncertain; otherwise route to `ccgs-create-stories`.
