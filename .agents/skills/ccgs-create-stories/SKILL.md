---
name: ccgs-create-stories
description: Convert each MVP feature into one stable, non-overwriting implementation story with observable acceptance criteria and build order.
---

# Create stories

Read .agents/studio/docs/core-workflow.md, resolve the root, and read .agents/studio/docs/templates/game-brief.md and .agents/studio/docs/templates/story.md.

## Inputs

The brief's MVP list and Build order, existing production/epics/**/EPIC.md, stories, and resolved minimal workflow.

## Actions

- Resolve config with bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow; stop on unsupported tiers.
- Read every existing epic/story before allocating IDs. Match an existing feature by stable feature/title/scope; rerunning an unchanged brief creates nothing.
- For each new MVP feature, create or preserve its EPIC.md, then exactly one story at production/epics/<epic-slug>/story-NNN-<feature-slug>.md. Allocate max existing numeric ID + 1; never renumber or overwrite.
- One story is one MVP feature. The first vertical slice may cover only the first feature/build-order unit, not later MVP scope. Include dependencies, files/code root, parse/runtime evidence, and observable ACs.
- Use normal file editing; use bash .agents/studio/scripts/story-facts.sh and bash .agents/studio/scripts/story-status.sh only to inspect. Update checkpoint with bash .agents/studio/scripts/session-state.sh checkpoint.

## Output

Return created/preserved paths, IDs, build order, and first actionable story. Route only that story to ccgs-dev-story.
