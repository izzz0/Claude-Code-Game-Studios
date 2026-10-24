---
name: ccgs-start
description: Start or resume a CCGS project by resolving configuration, preserving existing choices, and routing to the next supported minimal workflow step.
---

# Start

Read `.agents/studio/docs/core-workflow.md` once, resolve the repository root (the directory containing `project.yaml` and `.git`), and run every command from it.

## Inputs

- Existing `project.yaml`, stage, brief, stories, and `production/session-state/active.md`.
- User intent: new project, returning project, or an existing game.

## Actions

1. Check prerequisites with `bash --version` and `python --version`.
2. Resolve configuration explicitly:
   `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,review_mode,testing.strict,engine_values`.
3. Inspect facts: `bash .agents/studio/scripts/project-state.sh` and `bash .agents/studio/scripts/story-status.sh`.
4. For a new project, initialize only absent `modes.rigor=minimal` and `modes.automation=guided` via `bash .agents/studio/scripts/config-set.sh modes.rigor minimal --dry-run` then the authorized write (and the same for automation). Do not seed workflow or other expanded knobs.
5. If `workflow` or effective `rigor` is not `minimal`, report the unsupported tier and stop. Check the checkpoint against actual story status and branch before resuming.

## Output

Report engine, preserved settings and exactly one next skill from the nine installed entrypoints. A valid checkpoint may resume smoke-check, review or closure. Without one, prioritize an In Review story's missing check/review/closure, then an In Progress story, then the first Ready story in build order. New projects route to setup-engine, brainstorm or create-stories as needed. Report blockers or a finished backlog without inventing a new task.
