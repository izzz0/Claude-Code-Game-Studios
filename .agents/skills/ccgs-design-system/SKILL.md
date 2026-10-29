---
name: ccgs-design-system
description: "Section-by-section GDD authoring for one system — walks through each required section, cross-references dependencies."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.
defaults in `.agents/studio/docs/config-resolution.md`.

# Design System

When this skill is invoked:

## 1. Parse Arguments & Validate

**Read `references/1-parse-arguments.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 2. Gather Context (Read Phase)

**Read `references/2-gather-context.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 3. Create File Skeleton

**Read `references/3-file-skeleton.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 4. Section-by-Section Design

**Read `references/4-section-design.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 5. Post-Design Validation

**Read `references/5-post-design.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 6. Specialist native delegation Routing

This skill delegates to specialist agents for domain expertise. The main session
orchestrates the overall flow; agents provide expert content.

**Rows here are finer-grained than the nine `Category` values on purpose** — the
right specialist for combat is not the right specialist for pathfinding, and both
are `Gameplay`. Resolve in two steps: take the system's `Category` from
`systems-index.md`, then pick the row within it that matches what the system
actually does. Every category has at least one row, so nothing falls through.

| `Category` | Rows below to choose from |
|---|---|
| `Gameplay` | Combat/damage/health · AI/pathfinding/behavior · Animation/character movement · Character systems · Camera/input/controls |
| `Core` | Foundation/Infrastructure · Camera/input/controls |
| `Persistence` | Foundation/Infrastructure |
| `Economy` | Economy/loot/crafting |
| `Progression` | Progression/XP/skills |
| `UI` | UI systems · Visual effects (when the system is HUD-adjacent VFX) |
| `Audio` | Audio systems |
| `Narrative` | Dialogue/quests/lore |
| `Meta` | Foundation/Infrastructure (analytics, tutorial plumbing) · UI systems (accessibility options screens) |

If two rows fit, spawn the union of their Primary agents and say why.

| System type | Primary native delegation | Supporting native delegation(s) |
|----------------|---------------|---------------------|
| **Foundation/Infrastructure** (event bus, save/load, scene mgmt, service locator) | `ccgs-systems-designer` | `ccgs-gameplay-programmer` (feasibility), `ccgs-engine-programmer` (engine integration) |
| Combat, damage, health | `ccgs-game-designer` | `ccgs-systems-designer` (formulas), `ccgs-ai-programmer` (enemy AI), `ccgs-art-director` (hit feedback visual direction, VFX intent) |
| Economy, loot, crafting | `ccgs-economy-designer` | `ccgs-systems-designer` (curves), `ccgs-game-designer` (loops) |
| Progression, XP, skills | `ccgs-game-designer` | `ccgs-systems-designer` (curves), `ccgs-economy-designer` (sinks) |
| Dialogue, quests, lore | `ccgs-game-designer` | `ccgs-narrative-director` (story), `ccgs-writer` (content), `ccgs-art-director` (character visual profiles, cinematic tone) |
| UI systems (HUD, menus) | `ccgs-game-designer` | `ccgs-ux-designer` (flows), `ccgs-ui-programmer` (feasibility), `ccgs-art-director` (visual style direction), `ccgs-technical-artist` (render/shader constraints) |
| Audio systems | `ccgs-game-designer` | `ccgs-audio-director` (direction), `ccgs-sound-designer` (specs) |
| AI, pathfinding, behavior | `ccgs-game-designer` | `ccgs-ai-programmer` (implementation), `ccgs-systems-designer` (scoring) |
| Level/world systems | `ccgs-game-designer` | `ccgs-level-designer` (spatial), `ccgs-world-builder` (lore) |
| Camera, input, controls | `ccgs-game-designer` | `ccgs-ux-designer` (feel), `ccgs-gameplay-programmer` (feasibility) |
| Animation, character movement | `ccgs-game-designer` | `ccgs-art-director` (animation style, pose language), `ccgs-technical-artist` (rig/blend constraints), `ccgs-gameplay-programmer` (feel) |
| Visual effects, particles, shaders | `ccgs-game-designer` | `ccgs-art-director` (VFX visual direction), `ccgs-technical-artist` (performance budget, shader complexity), `ccgs-systems-designer` (trigger/state integration) |
| Character systems (stats, archetypes) | `ccgs-game-designer` | `ccgs-art-director` (character visual archetype), `ccgs-narrative-director` (character arc alignment), `ccgs-systems-designer` (stat formulas) |

**When delegating via the
`native delegation` tool**:
- Provide: system name, game concept summary, dependency GDD excerpts, the specific
  section being worked on, and what question needs expert input
- The agent returns analysis/proposals to the main session
- The main session presents the agent's output to the user via
`native user-input mechanism`
- The user decides; the main session writes to file
- Agents do NOT write to files directly — the main session owns all file writes

---

## 7. Recovery & Resume

If the session is interrupted (compaction, crash, new session):

1. Read `production/session-state/active.md` — it records the current system and
   which sections are complete
2. Read `design/gdd/[system-name].md` — sections with real content are done;
   sections with `[To be designed]` still need work. Read it by section: find the
   headings with the Grep tool (pattern `^#`, content mode) and Read those
   ranges with offset and limit.
3. Resume from the next incomplete section — no need to re-discuss completed ones

This is why incremental writing matters: every approved section survives any
disruption.

---

## Collaborative Protocol

**In `collaborative` mode (the default).** For `guided` and `autonomous`
modes, see the per-mode rules in `.agents/studio/docs/automation-modes.md` — the
"Never" lines below describe what collaborative mode requires, not what
applies universally.

This skill follows the collaborative design principle at every step:

1. **Question -> Options -> Decision -> Draft -> Approval** for every section
2. **`native user-input mechanism` at every consequential decision point** (Explain -> Capture pattern):
   - Phase 2: "Ready to start, or need more context?"
      Decisions about content, conflicts, and hand-offs are explicit; ordinary in-scope writes proceed after the draft is accepted.
   - Phase 4 (each section): Design questions, approach options, draft approval
      Decisions about content, conflicts, and hand-offs are explicit; ordinary in-scope writes proceed after the draft is accepted.
     index? What's next?" — **not** "Run design review?": §5c forbids offering
     `$ccgs-design-review` inline, because the reviewing agent must not inherit this
     session's design history. Phase 5c presents the hand-off; it never asks.
      Decisions about content, conflicts, and hand-offs are explicit; ordinary in-scope writes proceed after the draft is accepted.
4. **Incremental writing**: Each section is written to file immediately after approval
5. **Session state updates**: After every section write
6. **Cross-referencing**: Every section checks existing GDDs for conflicts
7. **Specialist routing**: Complex sections get expert agent input, presented to
   the user for decision — never written silently

**Never** auto-generate the full GDD and present it as a fait accompli.
**Never** write a section whose content or conflict decision has not been accepted.
**Never** contradict an existing approved GDD without flagging the conflict.
**Always** show where decisions come from (dependency GDDs, pillars, user choices).

## Context Window Awareness

This is a long-running skill. After writing each section, check if the status line
shows context at or above 70%. If so, append this notice to the response:

> **Context is approaching the limit (≥70%).** Your progress is saved — all approved
> sections are written to `design/gdd/[system-name].md`. When you're ready to continue,
> start a new independent Codex run and run `$ccgs-design-system [system-name]` — it will
> detect which sections are complete and resume from the next one.

---

## Recommended Next Steps

- Run `$ccgs-design-review design/gdd/[system-name].md` in a **new independent Codex run** to validate the completed GDD independently
- Run `$ccgs-consistency-check` to verify this GDD's values don't conflict with other GDDs
- Run `$ccgs-map-systems next` to move to the next highest-priority undesigned system
- Run `$ccgs-gate-check technical-setup` when all MVP GDDs are authored and reviewed
