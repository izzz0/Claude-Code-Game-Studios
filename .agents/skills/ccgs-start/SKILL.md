---
name: ccgs-start
description: Start or resume a CCGS project by resolving configuration, preserving existing choices, and routing to the next step for its configured workflow tier.
---

# Start

Read `.agents/studio/docs/core-workflow.md` once. Resolve the nearest active `project.yaml` separately from the Git/framework root, and run project commands from that active project directory. A nested project configuration inside the same Git checkout does not need its own `.git` marker. Use its local resource layout; never borrow another Git project's runtime.

## Inputs

- Existing `project.yaml`, stage, brief, stories, and `production/session-state/active.md`.
- User intent: new project, returning project, or an existing game.

## Actions

1. Check prerequisites with `bash --version` and `python --version`.
2. Resolve configuration explicitly:
   `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,review_mode,testing.strict,engine_values`.
3. Inspect facts: `bash .agents/studio/scripts/project-state.sh` and `bash .agents/studio/scripts/story-status.sh`.
   Run `python .agents/studio/scripts/studio-inspect.py .` and report its `configured`, `discovered`, `observed`, and `trust_unconfirmed` fields separately; role/profile presence is not proof of execution or host trust.
4. For a new project, initialize only absent `modes.rigor=minimal` and `modes.automation=guided` via `bash .agents/studio/scripts/config-set.sh modes.rigor minimal --dry-run` then the authorized write (and the same for automation). Do not seed workflow or other expanded knobs.
5. Preserve the resolved workflow and rigor independently. Minimal follows its short path; standard and full follow their configured artifact paths. Never downgrade a configured standard/full project to minimal. Check the checkpoint against actual story status and branch before resuming.

## Output

Report engine, preserved settings, studio inspection counts, and exactly one next skill from the discovered/configured skill set. A valid checkpoint may resume smoke-check, review or closure. Without one, prioritize an In Review story's missing check/review/closure, then an In Progress story, then the first Ready story in build order. New projects route to setup-engine, brainstorm or create-stories as needed. Report blockers or a finished backlog without inventing a new task.

## Workflow tiers

When the resolved workflow is `standard` or `full`, read `references/full-workflow.md` and apply its required artifacts, review, and evidence phases. The `minimal` route remains independent of the phase ladder; do not reset an existing project's stage or concept to fit it.
