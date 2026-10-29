## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Agent | Drafts to (`[path]`) | Final document (you write it) |
|---|---|---|
| ccgs-narrative-director | `production/narrative/[content-slug]/brief.md` | `design/narrative/[content-slug]-brief.md` |
| ccgs-world-builder | `production/narrative/[content-slug]/lore-[topic].md` | `design/narrative/lore/[topic].md` |
| ccgs-writer | `production/narrative/[content-slug]/dialogue-[scene-slug].md` | `design/narrative/dialogue/[scene-slug].md` |
| ccgs-art-director | `production/narrative/[content-slug]/visual-direction.md` | `design/narrative/[content-slug]-visual-direction.md` |
| ccgs-level-designer | `production/narrative/[content-slug]/level-integration.md` | `design/narrative/[content-slug]-level-integration.md` |
| ccgs-localization-lead | `production/narrative/[content-slug]/i18n-review.md` | stays in `production/` — a review, not a design document |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Narrative

If no argument is provided, output usage guidance and exit without spawning any agents:
> Usage: `$ccgs-team-narrative [narrative content description] [--review full|lean|solo]` — describe the story content, scene, or narrative area to work on (e.g., `boss encounter cutscene`, `faction intro dialogue`, `tutorial narrative`). Do not use `the host input tool` here; output the guidance directly.

When this skill is invoked with an argument, orchestrate the narrative team through a structured pipeline.

Guided advances ordinary authorized phases automatically. Collaborative reviews major drafts; material product/scope changes still require the user.

## Phase 0: Resolve Config

Run explicitly: `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys review_mode,automation,team.size,workflow`.
Use the explicit helper result; --review overrides only review_mode. If configuration cannot be resolved, report NOT ASSESSED and the error; do not substitute guessed defaults.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below spawns CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the agents that work at them are team members, not director gates.

Phase 4's ND-CONSISTENCY is the exception in every mode: it is this pipeline's own
review, not an optional director gate, so `review_mode` never skips it (`team.size`
still decides who runs it — see Phase 4).

`automation` drives the Decision Points note above. See the Decision Points note above and
`.agents/studio/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which agents are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `ccgs-writer` only; `ccgs-narrative-director` invoked only on an explicit pillar conflict. Other agents consulted via the ccgs-writer, not spawned separately.
- **`small`**: `ccgs-narrative-director` + `ccgs-writer`, plus `ccgs-localization-lead` and `ccgs-world-builder` when `review_mode` is `full` (at `lean` and `solo` they are consulted through the ccgs-writer).
- **`studio`**: all six Team Composition agents, whatever the `review_mode` (the full pipeline as documented).
A non-core agent needed at `individual` routes through the nearest active core agent with an informational note. **"Phase gate" means any phase that ends in an `the host input tool` decision point this pipeline itself lists** — a transition under Decision Points above, or a **Gate** step written into the pipeline below — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so bounded-exception condition (3) below holds at it in every mode. An agent restricted to "phase gates only" is spawned at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names an agent outside the active set routes through the nearest core agent rather than spawning it.

**Announce the active set before Phase 1 — never let the collapse be silent.**
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

## Team Composition
- **ccgs-narrative-director** — Story arcs, character design, dialogue strategy, narrative vision
- **ccgs-writer** — Dialogue writing, lore entries, item descriptions, in-game text
- **ccgs-world-builder** — World rules, faction design, history, geography, environmental storytelling
- **ccgs-art-director** — Character visual design, environmental visual storytelling, cutscene/cinematic tone
- **ccgs-level-designer** — Level layouts that serve the narrative, pacing, environmental storytelling beats
- **ccgs-localization-lead** — Localization readiness — flags non-localizable strings, cultural assumptions, and i18n gaps

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** Agents write drafts under
`production/narrative/[content-slug]/` — within the accepted task authorization. The
finished documents belong in `design/narrative/`, which the exception does **not**
cover, so **you** write those within the accepted task (see "Write the finals"):

| Agent | Drafts to (`[path]`) | Final document (you write it) |
|---|---|---|
| ccgs-narrative-director | `production/narrative/[content-slug]/brief.md` | `design/narrative/[content-slug]-brief.md` |
| ccgs-world-builder | `production/narrative/[content-slug]/lore-[topic].md` | `design/narrative/lore/[topic].md` |
| ccgs-writer | `production/narrative/[content-slug]/dialogue-[scene-slug].md` | `design/narrative/dialogue/[scene-slug].md` |
| ccgs-art-director | `production/narrative/[content-slug]/visual-direction.md` | `design/narrative/[content-slug]-visual-direction.md` |
| ccgs-level-designer | `production/narrative/[content-slug]/level-integration.md` | `design/narrative/[content-slug]-level-integration.md` |
| ccgs-localization-lead | `production/narrative/[content-slug]/i18n-review.md` | stays in `production/` — a review, not a design document |

> **The final destination is not a free choice.** `design/narrative/` is read by
> `$ccgs-asset-spec`, `$ccgs-design-review`, `$ccgs-localize`, `$ccgs-onboard`,
> `$ccgs-project-stage-detect`, `$ccgs-team-level` and the `cd-narrative` director gate.
> An artifact written anywhere else is invisible to all seven.
>
> The `[path]` contract above has a precondition: the path is one *you* named. A
> skill that states the contract but names no concrete destination leaves every
> run to invent one, which defeats it. `$ccgs-team-qa` Phase 4 carries the same
> requirement for the same reason.

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


Launch independent agents in parallel where the pipeline allows it (e.g., Phase 2 agents can run simultaneously).

## Pipeline

### Phase 1: Narrative Direction
Delegate to **ccgs-narrative-director**:
- Define the narrative purpose of this content: what story beat does it serve?
- Identify characters involved, their motivations, and how this fits the overall arc
- Set the emotional tone and pacing targets
- Specify any lore dependencies or new lore this introduces
- Output: narrative brief with story requirements

### Phase 2: World Foundation (parallel)
Delegate in parallel — issue all three the native role tool calls simultaneously before waiting for any result:
- **ccgs-world-builder**: Create or update lore entries for factions, locations, and history relevant to this content. Cross-reference against existing lore for contradictions. Set canon level for new entries.
- **ccgs-writer**: Draft character dialogue using voice profiles. Ensure all lines are under 120 characters, use named placeholders for variables, and are localization-ready.
- **ccgs-art-director**: Define character visual design direction for key characters appearing in this content (silhouette, visual archetype, distinguishing features). Specify environmental visual storytelling elements for each key space (prop composition, lighting notes, spatial arrangement). Define tone palette and cinematic direction for any cutscenes or scripted sequences.

**Phase gate:** collect all three Phase 2 outputs, then apply the Decision Points
rule before starting Phase 3 — present the lore, dialogue, and visual direction
summaries and capture approval via `the host input tool` in `collaborative` mode
(auto-advance in `guided` unless a result is BLOCKED; `log_decision` in
`autonomous`).

### Phase 3: Level Narrative Integration
Delegate to **ccgs-level-designer**:
- Review the narrative brief and lore foundation
- Design environmental storytelling elements in the level
- Place narrative triggers, dialogue zones, and discovery points
- Ensure pacing serves both gameplay and story

### Phase 4: Review and Consistency
Spawn `ccgs-narrative-director` via the native role tool using gate **ND-CONSISTENCY**
(`.agents/studio/docs/director-gates/nd-consistency.md`). This phase runs in every review
mode — it is this pipeline's own review, not an optional director gate. Pass the
context that gate lists (the Phase 2–3 draft paths, the narrative bible or tone
guide, the world rules, the affected character and faction profiles) — named
here, so do not read the gate file in this session — and add:
- Confirm narrative pacing aligns with level design
- Check that all mysteries have documented "true answers"

Act on the verdict: **APPROVE** → Phase 5. **CONCERNS** → show the listed
inconsistencies and ask via `the host input tool` whether to revise them (re-spawn the
agent that owns each) or accept them. **REJECT** → do not start Phase 5; the
contradictions are fixed first. **NOT ASSESSED [missing input]** → name the
missing input, then supply it and re-run the gate, or carry
`ND-CONSISTENCY: NOT ASSESSED — [input]` into the report's consistency review
results; it is never read as APPROVE (`.agents/studio/docs/director-gates.md`).

**At `team.size: individual`** ccgs-narrative-director is not in the active set, so the
gate is not spawned. The ccgs-writer checks the drafts against the same criteria, and
the output says so by name: "ND-CONSISTENCY not run — ccgs-narrative-director is not
active at `team.size: individual`; consistency self-checked by ccgs-writer." A
self-check is not the gate's verdict, and the report must not present it as one.

### Phase 5: Polish (parallel)
Delegate in parallel — issue every the native role tool call before waiting for any result:
- **ccgs-writer**: Final self-review — verify no line exceeds dialogue box constraints, all text uses string keys (not raw strings), placeholder variable names are consistent
- **ccgs-localization-lead**: Validate i18n compliance — check string key naming conventions, flag any strings with hardcoded formatting that won't survive translation, verify character limit headroom for languages that expand (German/Finnish typically +30%), confirm no cultural assumptions in text that would need locale-specific variants
- **ccgs-world-builder**: Finalize canon levels for all new lore entries

The coordinator retains authorized phase outputs. Implementation follows the accepted file ownership; independent review returns findings read-only.

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


## Output

A summary report covering: narrative brief status, lore entries created/updated, dialogue lines written, level narrative integration points, consistency review results, and any unresolved contradictions — including any localization issue the user chose to leave unfixed, by string key.

Verdict: **COMPLETE** — narrative content delivered.

If ND-CONSISTENCY answered NOT ASSESSED and that was carried into the report
(Phase 4), the verdict says so — never a plain COMPLETE:

Verdict: **COMPLETE — consistency NOT ASSESSED ([input])** — narrative content delivered; the consistency review could not run for want of [input].

If the pipeline stops because a dependency is unresolved (e.g., lore contradiction or missing prerequisite not resolved by the user):

Verdict: **BLOCKED** — [reason]

## Next Steps

- Run `$ccgs-design-review` on the narrative documents for consistency validation.
- Run `$ccgs-localize extract` to extract new strings for translation after dialogue is finalized.
- Run `$ccgs-dev-story` to implement dialogue triggers and narrative events in-engine.
