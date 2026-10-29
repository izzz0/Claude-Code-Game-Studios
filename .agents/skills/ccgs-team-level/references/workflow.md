## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Step / agent | Writes to |
|---|---|
| 1 ccgs-narrative-director | `production/levels/[level-name]/narrative.md` |
| 1 ccgs-world-builder | `production/levels/[level-name]/lore.md` |
| 1 ccgs-art-director | `production/levels/[level-name]/visual-direction.md` |
| 2 ccgs-level-designer | `production/levels/[level-name]/layout.md` |
| 3 ccgs-systems-designer | `production/levels/[level-name]/systems.md` |
| 4 ccgs-art-director | `production/levels/[level-name]/production-concepts.md` |
| 4 ccgs-accessibility-specialist | `production/levels/[level-name]/accessibility.md` |
| 5 ccgs-qa-tester | `production/qa/test-cases/[level-name]-cases.md` — test cases, edge cases, playtest checklist, acceptance criteria |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Level

If no argument is provided, output usage guidance and exit without spawning any agents or reading any design files:
> Usage: `$ccgs-team-level [level name or area to design] [--review full|lean|solo]` — specify the level or area to design (e.g., `forest temple`, `tutorial village`, `final boss arena`). Do not use `the host input tool` here; output the guidance directly.

When this skill is invoked:

Guided advances ordinary authorized phases automatically. Collaborative reviews major drafts; material product/scope changes still require the user.

## Phase 0: Resolve Config

Run explicitly: `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys review_mode,automation,team.size,workflow`.
Use the explicit helper result; --review overrides only review_mode. If configuration cannot be resolved, report NOT ASSESSED and the error; do not substitute guessed defaults.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below spawns CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the agents that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.agents/studio/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which agents are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `ccgs-level-designer` only. Other agents consulted via the ccgs-level-designer, not spawned separately.
- **`small`**: + `ccgs-systems-designer` + `ccgs-art-director` + `ccgs-qa-tester`.
- **`studio`**: + `ccgs-narrative-director` + `ccgs-world-builder` + `ccgs-accessibility-specialist` (the full pipeline as documented).
A non-core agent needed at `individual` routes through the nearest active core agent with an informational note. **"Phase gate" means any phase that ends in an `the host input tool` decision point this pipeline itself lists** — a transition under Decision Points above, or a **Gate** step written into the pipeline below — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so bounded-exception condition (3) below holds at it in every mode. An agent restricted to "phase gates only" is spawned at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names an agent outside the active set routes through the nearest core agent rather than spawning it.

**Announce the active set before Step 1 — never let the collapse be silent.**
Before spawning anything, state in one line which agents this run will actually
spawn, and which the pipeline below names but will **not** spawn at the resolved
`team.size`. For example:

> `Active set (team.size: <resolved>): <the agents listed for that size above>.`
> `Not spawned this run: <every other agent this pipeline names> — consulted`
> `through <nearest active core agent>. Raise team.size (or modes.rigor) to widen.`

Fill it from the `team.size` list directly above and the agents this file's own
pipeline names — not from an example. Both sets differ per orchestrator.

The pipeline below reads as a multi-agent fan-out and at the shipped default it
is one or two agents — `team-release` names ten and runs one, `team-narrative`
names six across five phases and runs `ccgs-writer` alone. **The collapse is correct**:
`team.size` is rigor-fronted and the narrow default is the token lever.
Without saying so, a reader cannot
distinguish a correctly-collapsed run from a broken pipeline, and the per-agent
"routes through the nearest core agent with an informational note" rule above
fires at routing time and never states the shape of the run as a whole.

This is the same rule as the skipped-check reporting elsewhere in this file: **a constraint that is enforced but never surfaced is
indistinguishable, to the person reading the output, from one that was never
enforced.**

1. **Read the argument** for the target level or area (e.g., `tutorial`,
   `forest dungeon`, `hub town`, `final boss arena`).

2. **Gather context** (read each design doc by section: find the headings you need
   with the search tool with pattern `^#` in content mode, and Read those ranges
   with offset and limit):
   - Read the game concept at `design/gdd/game-concept.md` — or `design/game-brief.md`,
     the one-page brief that replaces it at `rigor: minimal` — if either exists
   - Read game pillars at `design/gdd/game-pillars.md`
   - Read existing level docs in `design/levels/`
   - Read relevant narrative docs in `design/narrative/`
   - Read world-building docs for the area's region/faction

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** Working artifacts go under
`production/levels/[level-name]/`, slugged as in the "Save to" step below. One
file per agent, so the parallel steps never share one:

| Step / agent | Writes to |
|---|---|
| 1 ccgs-narrative-director | `production/levels/[level-name]/narrative.md` |
| 1 ccgs-world-builder | `production/levels/[level-name]/lore.md` |
| 1 ccgs-art-director | `production/levels/[level-name]/visual-direction.md` |
| 2 ccgs-level-designer | `production/levels/[level-name]/layout.md` |
| 3 ccgs-systems-designer | `production/levels/[level-name]/systems.md` |
| 4 ccgs-art-director | `production/levels/[level-name]/production-concepts.md` |
| 4 ccgs-accessibility-specialist | `production/levels/[level-name]/accessibility.md` |
| 5 ccgs-qa-tester | `production/qa/test-cases/[level-name]-cases.md` — test cases, edge cases, playtest checklist, acceptance criteria |

These are working drafts; the durable record is the level design document you
compile from them (`design/levels/[level-name].md`).

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


3. **Orchestrate the level design team** in sequence:

### Step 1: Narrative + Visual Direction (ccgs-narrative-director + ccgs-world-builder + ccgs-art-director, parallel)

Spawn all three agents simultaneously — issue all three the native role tool calls before waiting for any result.

Spawn the `ccgs-narrative-director` agent to:
- Define the narrative purpose of this area (what story beats happen here?)
- Identify key characters, dialogue triggers, and lore elements
- Specify emotional arc (how should the player feel entering, during, leaving?)

Spawn the `ccgs-world-builder` agent to:
- Provide lore context for the area (history, faction presence, ecology)
- Define environmental storytelling opportunities
- Specify any world rules that affect gameplay in this area

Spawn the `ccgs-art-director` agent to:
- Establish visual theme targets for this area — these are INPUTS to layout, not outputs of it
- Define the color temperature and lighting mood for this area (how does it differ from adjacent areas?)
- Specify shape language direction (angular fortress? organic cave? decayed grandeur?)
- Name the primary visual landmarks that will orient the player
- Read `design/art/art-bible.md` if it exists — anchor all direction in the established art bible. Read it by section: find the headings you need with the search tool (pattern `^#`, content mode) and read only those sections.

**The ccgs-art-director's visual targets from Step 1 must be passed to the ccgs-level-designer in Step 2** as explicit constraints. Layout decisions happen within the visual direction, not before it.

**Gate**: Use `the host input tool` to present all three Step 1 outputs (narrative brief, lore foundation, visual direction targets) and confirm before proceeding to Step 2.

### Step 2: Layout and Encounter Design (ccgs-level-designer)
Spawn the `ccgs-level-designer` agent with the full Step 1 output as context:
- Narrative brief (from ccgs-narrative-director)
- Lore foundation (from ccgs-world-builder)
- **Visual direction targets (from ccgs-art-director)** — layout must work within these targets, not contradict them

The ccgs-level-designer should:
- Design the spatial layout (critical path, optional paths, secrets) — ensuring primary routes align with the visual landmark targets from Step 1
- Define pacing curve (tension peaks, rest areas, exploration zones) — coordinated with the emotional arc from ccgs-narrative-director
- Place encounters with difficulty progression
- Design environmental puzzles or navigation challenges
- Define points of interest and landmarks for wayfinding — these must match the visual landmarks the ccgs-art-director specified
- Specify entry/exit points and connections to adjacent areas

**Adjacent area dependency check**: After the layout is produced, check `design/levels/` for each adjacent area referenced by the ccgs-level-designer. If any referenced area's `.md` file does not exist, surface the gap:
> "Level references [area-name] as an adjacent area but `design/levels/[area-name].md` does not exist."

Use `the host input tool` with options:
- (a) Proceed with a placeholder reference — mark the connection as UNRESOLVED in the level doc and list it in the open cross-level dependencies section of the summary report
- (b) Pause and run `$ccgs-team-level [area-name]` first to establish that area

Do NOT invent content for the missing adjacent area.

**Gate**: Use `the host input tool` to present Step 2 layout (including any unresolved adjacent area dependencies) and confirm before proceeding to Step 3.

### Step 3: Systems Integration (ccgs-systems-designer)
Spawn the `ccgs-systems-designer` agent to:
- Specify enemy compositions and encounter formulas
- Define loot tables and reward placement
- Balance difficulty relative to expected player level/gear
- Design any area-specific mechanics or environmental hazards
- Specify resource distribution (health pickups, save points, shops)

**Gate**: Use `the host input tool` to present Step 3 outputs and confirm before proceeding to Step 4.

### Step 4: Production Concepts + Accessibility (ccgs-art-director + ccgs-accessibility-specialist, parallel)

**Note**: The ccgs-art-director's directional pass (visual theme, color targets, mood) happened in Step 1. This pass is location-specific production concepts — given the finalized layout, what does each specific space look like?

Spawn the `ccgs-art-director` agent with the finalized layout from Step 2:
- Produce location-specific concept specs for key spaces (entrance, key encounter zones, landmarks, exits)
- Specify which art assets are unique to this area vs. shared from the global pool
- Define sight-line and lighting setups per key space (these are now layout-informed, not directional)
- Specify VFX needs that are specific to this area's layout (weather volumes, particles, atmospheric effects)
- Flag any locations where the layout creates visual direction conflicts with the Step 1 targets — surface these as production risks

Spawn the `ccgs-accessibility-specialist` agent in parallel to:
- Review the level layout for navigation clarity (can players orient themselves without relying on color alone?)
- Check that critical path signposting uses shape/icon/sound cues in addition to color
- Review any puzzle mechanics for cognitive load — flag anything that requires holding more than 3 simultaneous states
- Check that key gameplay areas have sufficient contrast for colorblind players
- Output: accessibility concerns list with severity (BLOCKING / RECOMMENDED / NICE TO HAVE)

Wait for both agents to return before proceeding.

**Gate**: Use `the host input tool` to present both Step 4 results. If the ccgs-accessibility-specialist returned any BLOCKING concerns, highlight them prominently and offer:
- (a) Return to ccgs-level-designer and ccgs-art-director to redesign the flagged elements before Step 5
- (b) Document as a known accessibility gap and proceed to Step 5 with the concern explicitly logged in the final report

Do NOT proceed to Step 5 without the user acknowledging any BLOCKING accessibility concerns.

### Step 5: QA Planning (ccgs-qa-tester)
Spawn the `ccgs-qa-tester` agent to:
- Write test cases for the critical path
- Identify boundary and edge cases (sequence breaks, softlocks)
- Create a playtest checklist for the area
- Define acceptance criteria for level completion

4. **Compile the level design document** combining all team outputs into the
   level design template format.

The coordinator retains authorized phase outputs at `design/levels/[level-name].md`. Implementation follows the accepted file ownership; independent review returns findings read-only.

5. **Save to** `design/levels/[level-name].md` after the applicable design decision is resolved.
   `[level-name]` is the argument as a slug — lowercase, spaces → hyphens
   (`forest dungeon` → `forest-dungeon.md`) — and `[area-name]` in the adjacent
   area check is slugged the same way.

6. **Output a summary** with: area overview, encounter count, estimated asset
   list, narrative beats, any cross-team dependencies or open questions, open
   cross-level dependencies (adjacent areas referenced but not yet designed, each
   marked UNRESOLVED), and accessibility concerns with their resolution status.


## Next Steps

- Run `$ccgs-design-review design/levels/[level-name].md` to validate the completed level design doc.
- Run `$ccgs-dev-story` to implement level content once the design is approved.
- Run `$ccgs-qa-plan` to generate a QA test plan for this level.

## Error Recovery Protocol

**First, verify the artifact.** If the return contract named a path, check the
path exists before treating the phase as done — **a named artifact that is not
on disk is a failed phase, however fluent the response reads.** An agent can
burn a full phase and return a plausible preamble having written nothing, which
is neither BLOCKED nor an error nor "cannot complete", so the trigger below
never fires. Resume it naming the unmet contract; the context is
usually still there.

If any spawned agent returns BLOCKED, errors, or cannot complete: **surface it
immediately, don't proceed past a dependency it blocks, and always produce a
partial report.** A skipped agent's section stays a named gap — never fill it with content of your own. Full procedure: `.agents/studio/docs/error-recovery-protocol.md`.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; once it is decided, accept it with `$ccgs-architecture-decision accept ADR-NNNN`
- Scope too large → split into two stories via `$ccgs-create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess
