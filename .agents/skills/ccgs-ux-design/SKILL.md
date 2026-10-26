---
name: ccgs-ux-design
description: "Section-by-section UX spec authoring for a screen, flow or HUD. Reads the player journey to provide context; also project-wide accessibility."
---

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.

Run `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow` and use its output.
`.agents/studio/docs/config-resolution.md`.

# UX Design

When this skill is invoked:

Every
`native user-input mechanism` call follows `.agents/studio/docs/automation-modes.md`
(collaborative reviews major drafts · guided raises material decisions · autonomous records decisions;
`automation_always_ask` categories always prompt).

**Authoring guidance**: the skeletons below are self-contained — author from them
directly. When a section needs depth (worked examples, pattern catalogs,
accessibility criteria), the matching guide has it:

| Producing | Guide |
|---|---|
| UX spec | `.agents/studio/docs/templates/guidance/ux-spec-guide.md` |
| HUD design | `.agents/studio/docs/templates/guidance/hud-design-guide.md` |
| Interaction patterns | `.agents/studio/docs/templates/guidance/interaction-pattern-library-guide.md` (routes to three topic files) |
| Accessibility requirements | `.agents/studio/docs/templates/guidance/accessibility-requirements-guide.md` |

**Load a guide per-section, never whole** — each is organised by section and the
pointers in the templates name the exact section to read.

**`workflow`** (see `.agents/studio/docs/workflow-modes.md`):
- `full` — a UX spec is required per screen.
- `standard` — core screens only (main menu, HUD, primary game loop).
- `minimal` — not required. Can still be run voluntarily.

**`docs.density`** — it controls per-section *depth*, where `workflow`
controls which screens are specced. `modes.rigor` sets both together; set
`docs.density` explicitly to vary depth alone: `terse` (the default, via `rigor: minimal`) = wireframe descriptions +
interaction bullets; `balanced` = wireframes + paragraph descriptions of flows
(`rigor: standard`); `thorough` = full prose including user-research summaries and
alternative flow considerations. Apply it to every section you author.

## 1. Parse Arguments & Determine Mode

Four authoring modes exist based on the argument:

| Argument | Mode | Output file |
|----------|------|-------------|
| `hud` | HUD design | `design/ux/hud.md` |
| `patterns` | Interaction pattern library | `design/ux/interaction-patterns.md` |
| `accessibility` | Project-wide accessibility requirements | `design/accessibility-requirements.md` |
| Any other value (e.g., `main-menu`, `inventory`) | UX spec for a screen or flow | `design/ux/[argument].md` |
| No argument | Ask the user | (see below) |

> **`accessibility` is the only mode that writes outside `design/ux/`.** Its
> output is a project-wide standard the per-screen specs consult, not a spec for
> one screen — `.agents/studio/docs/workflow-catalog.yaml`, the Pre-Production and
> Polish gates, and `$ccgs-architecture-review` all check
> `design/accessibility-requirements.md` at that exact path. Do not "tidy" it
> under `design/ux/`: every one of those checks would stop matching, and the
> Technical Setup → Pre-Production gate would become unpassable.

**If no argument is provided**, do not fail — ask instead. Use
`native user-input mechanism`:
- "What are we designing today?"
  - Options: "A specific screen or flow (I'll name it)", "The game HUD", "The interaction pattern library", "The project-wide accessibility requirements", "I'm not sure — help me figure it out"

If the user selects "I'll name it" or types a screen name, normalize it to kebab-case
for the filename (e.g., "Main Menu" becomes `main-menu`).

---

## 2. Gather Context (Read Phase)

**Read `references/2-gather-context.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 3. Create File Skeleton

**Read `references/3-file-skeleton.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 4. Section-by-Section Authoring

**Read `references/4-authoring.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

### Section guidance — read the ONE file for the active mode

Per-section authoring guidance lives in its own file per mode. **When you reach
Phase 4, read only the file matching the mode resolved in Section 1; never load
the other two.**

| Mode | Guidance file |
|------|---------------|
| UX Spec (screen or flow) | `references/sections-ux-spec.md` |
| HUD Design | `references/sections-hud.md` |
| Interaction Pattern Library | `references/sections-patterns.md` |
| Accessibility Requirements | `.agents/studio/docs/templates/guidance/accessibility-requirements-guide.md` |

> The accessibility guidance lives under `templates/guidance/` rather than this
> skill's `references/` because the template it documents
> (`.agents/studio/docs/templates/accessibility-requirements.md`) is consumed by
> `$ccgs-ux-review` and the gate files too. Same rule applies: load only the part
> covering the section you are authoring, never the whole file.

Apply `docs.density` (Section 1) to whatever that file tells you to author — it
controls the depth of each section, not which sections exist.

## 5. Cross-Reference Check

**Read `references/5-crossref-handoff.md` now and follow it** — this phase's steps are in that file, not here. Read it again if the conversation was compacted or resumed during this phase.

## 7. Recovery & Resume

If the session is interrupted (compaction, crash, new session):

1. Read `production/session-state/active.md` — it records the current screen
   and which sections are complete.
2. Read `design/ux/[filename].md` — sections with real content are done;
   sections with `[To be designed]` still need work.
3. Resume from the next incomplete section — no need to re-discuss completed ones.

This is why incremental writing matters: every approved section survives any
disruption.

---

## 8. Specialist Native Delegation Routing

This skill uses `ccgs-ux-designer` as the primary agent (set in frontmatter). For
specific sub-topics, additional context or coordination may be needed:

| Topic | Coordinate with |
|-------|----------------|
| Visual aesthetics, color, layout feel | `ccgs-art-director` — UX spec defines zones; art defines how they look |
| Implementation feasibility (engine constraints) | `ccgs-ui-programmer` — before finalizing component inventory |
| Gameplay data requirements | `ccgs-game-designer` — when data ownership is unclear |
| Narrative/lore visible in the UI | `ccgs-narrative-director` — for flavor text, item names, lore panels |
| Accessibility tier decisions | Recorded by this session (`$ccgs-ux-design accessibility`; the user picks the tier) against the criteria `ccgs-accessibility-specialist` defines and audits — consult it when a requirement's criterion is unclear |

When delegating to another agent via the
`native delegation` tool:
- Provide: screen name, game concept summary, the specific question needing expert input
- The agent returns analysis to this session
- This session presents the agent's output to the user
- The user decides; this session writes to file
- Agents do NOT write to files directly — this session owns all file writes

---

## Collaborative Protocol

**In `collaborative` mode (the default).** For `guided` and `autonomous` modes,
see the per-mode rules in `.agents/studio/docs/automation-modes.md` — the steps below
describe what collaborative mode requires, not what applies universally.

This skill follows the collaborative design principle at every step:

1. **Question -> Options -> Decision -> Draft -> Approval** for every section
2. **`native user-input mechanism`** at every decision point (Explain -> Capture pattern):
   - Phase 2: "Ready to start, or need more context?"
   - Phase 3: create the skeleton after the context phase
   - Phase 4 (each section): design questions, approach options, draft approval
   - Phase 5: "Run cross-reference check? What's next?"
3. Write the skeleton and each approved section to `[filepath]` directly; do not add per-file permission prompts
4. **Incremental writing**: Each section is written to file immediately after approval
5. **Session state updates**: After every section write

**Aesthetic deference**: When layout or visual choices come down to personal taste,
present the options and ask. Do not select a layout because it is "standard" — always
confirm. The user is the creative director.

**Conflict surfacing**: When a GDD requirement and the available screen real estate
conflict, surface the conflict and present resolution options. Never silently drop
a requirement. Never silently expand the layout without flagging it.

**Never** auto-generate the full spec and present it as a fait accompli.
**Never** write a section without user approval.
**Never** contradict an existing approved UX spec without flagging the conflict.
**Always** show where decisions come from (GDD requirements, player journey, user choices).

Verdict: **COMPLETE** — UX spec written and approved section by section.

---

## Recommended Next Steps

- Run `$ccgs-ux-review [filename]` to validate this spec before it enters the implementation pipeline
- Run `$ccgs-ux-design [next-screen]` to continue designing remaining screens or flows
- Run `$ccgs-gate-check production` once all key screens have approved UX specs
