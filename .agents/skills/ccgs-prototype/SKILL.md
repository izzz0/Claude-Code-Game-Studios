---
name: ccgs-prototype
description: Test one uncertain game hypothesis with the smallest throwaway prototype and record an evidence-based decision.
---
Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` from the repository root and use its output.


# Prototype

Read `.agents/studio/docs/core-workflow.md`, resolve the root, the brief, and `docs/engine-reference/<engine>/VERSION.md`.

## Inputs

One brief hypothesis, pinned engine/version/commands, and an explicit time box. Existing prototype files are preserved.

## Actions

- Resolve config explicitly and stop on unsupported workflow/rigor.
- Define one observable hypothesis and use a separate engine project under prototypes/<slug>/, with that engine's native code root inside it. Do not modify production source or promote prototype code automatically.
- Target that project explicitly in editor commands. If using project-aware helpers, pass --root prototypes/<slug>/ and keep its own configuration there; default helper roots would target the production project instead.
- Parse/import, run the real engine window, reach the criterion, and retain screenshots under `production/qa/evidence/<slug>/` plus an evidence note. Text or headless output is not visual evidence.
- Classify `PROCEED`, `PIVOT`, `KILL`, or `NOT ASSESSED`; missing runtime, timeout, or missing screenshot is `NOT ASSESSED`.
- Record stage with `bash .agents/studio/scripts/set-stage.sh <Stage>` and checkpoint with `bash .agents/studio/scripts/session-state.sh checkpoint` (stdin).

## Output

Return decision, hypothesis evidence, paths, and blocker. Only `PROCEED` routes to `ccgs-create-stories`; all other outcomes leave implementation incomplete.

## Standard/full workflow

Resolve workflow with the command above. For standard or full, read references/full-workflow.md and apply its artifact, review, and evidence phases, subject to .agents/studio/docs/core-workflow.md; minimal remains the default and stops at the minimal contract.