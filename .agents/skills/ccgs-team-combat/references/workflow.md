## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Phase / agent | Writes to | Destination fixed by |
|---|---|---|
| 1 ccgs-game-designer (draft) | `production/combat/[feature]-gdd-draft.md` | this skill — you write the final `design/gdd/[feature].md` (Phase 1) |
| 2 ccgs-gameplay-programmer | `docs/architecture/[feature]-sketch.md` | see note below |
| 2 engine specialist | `docs/architecture/[feature]-engine-notes.md` | see note below |
| 3 ccgs-gameplay-programmer, ccgs-ai-programmer, ccgs-technical-artist | accepted code/asset/test files assigned by the coordinator |
| 3 ccgs-sound-designer | `production/combat/[feature]-audio-events.md` | this skill |
| 5 ccgs-qa-tester (test cases) | `production/qa/test-cases/[feature]-cases.md` | `$ccgs-team-qa` Phase 4 |
| 5 ccgs-qa-tester (bugs) | `production/qa/bugs/BUG-[NNNN].md` | `$ccgs-team-qa` Phase 5 |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Combat

**Argument check:** If no combat feature description is provided, output:
> "Usage: `$ccgs-team-combat [combat feature description] [--review full|lean|solo]` — Provide a description of the combat feature to design and implement (e.g., `melee parry system`, `ranged weapon spread`)."
Then stop immediately without spawning any subagents or reading any files.

When this skill is invoked with a valid argument, orchestrate the combat team through a structured pipeline.

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

`workflow` sizes the Phase 1 design document the way `$ccgs-design-system` does:
`## Summary` plus all 8 sections at `full`; at `standard`, Overview, Detailed
Design, Edge Cases, Dependencies and Acceptance Criteria, plus Formulas whenever
the mechanic defines numeric rules (a combat mechanic almost always does); at
`minimal` the game brief is the design record and the GDD is optional — draft
those five sections and tell the user it is optional at this workflow level.

**`team.size`**: which agents are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `ccgs-gameplay-programmer` runs the pipeline; escalate `ccgs-ai-programmer` only if the feature flags AI work. Other Team Composition agents are consulted via the ccgs-gameplay-programmer, not spawned separately.
- **`small`**: the full Team Composition pipeline below, as documented.
- **`studio`**: full pipeline + engine sub-specialists + an adversarial review pass. *Engine sub-specialists*: the primary engine specialist's prompt says it may hand parts of its review to the registered task-relevant engine sub-specialists (for example `ccgs-ue-gas-specialist` for abilities); below `studio` it answers alone. *Adversarial review pass*: Phase 5's ccgs-qa-tester is told "your job is not to confirm this works — find how it breaks", and the report says the pass ran.
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
- **ccgs-game-designer** — Design the mechanic, define formulas and edge cases
- **ccgs-gameplay-programmer** — Implement the core gameplay code
- **ccgs-ai-programmer** — Implement NPC/enemy AI behavior for the feature
- **ccgs-technical-artist** — Create VFX, shader effects, and visual feedback
- **ccgs-sound-designer** — Define audio events, impact sounds, and ambient combat audio
- **engine specialist** (primary) — Validate architecture and implementation patterns are idiomatic for the engine (the primary specialist is `<engine>-specialist` from `engine.name` — Godot→`ccgs-godot-specialist`, Unity→`ccgs-unity-specialist`, Unreal→`ccgs-unreal-specialist`; fall back to the Primary line of `## Engine Specialists` in `technical-preferences.md`)
- **ccgs-qa-tester** — Write test cases and validate the implementation

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** Every phase that produces an artifact
names one; most are fixed by the skill that already reads them:

The coordinator retains authorized phase outputs at `production/combat/[feature]-gdd-draft.md`, `design/gdd/[feature].md`, `docs/architecture/[feature]-sketch.md`, `docs/architecture/[feature]-engine-notes.md`, `production/combat/[feature]-audio-events.md`, `production/qa/test-cases/[feature]-cases.md`, `production/qa/bugs/BUG-[NNNN].md`. Implementation follows the accepted file ownership; independent review returns findings read-only.

Phase 6 is a spoken status report, not an artifact — no path, and none needed.

> **Every phase above names a concrete destination, deliberately.** The Error
> Recovery Protocol below says "a named artifact that is not on disk is a failed
> phase" — a check that cannot run when no path was named.
>
> **The two `docs/architecture/` entries are a judgement call, not a convention.**
> That directory holds ADRs (`adr-NNNN-*.md`); a sketch is a precursor to one, not
> one itself, and **nothing in the repo reads either file**. Say so when
> reporting, so the sketch is understood as a record rather than an input to a
> later gate.

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


Launch independent agents in parallel where the pipeline allows it (e.g., Phase 3 agents can run simultaneously).

## Pipeline

### Phase 1: Design
Delegate to **ccgs-game-designer**:
- Create or update the design document for `design/gdd/[feature].md` from `.agents/studio/docs/templates/game-design-document.md`, with `## Summary` and the sections `workflow` requires (Phase 0) — at `full`: mechanic overview, player fantasy, detailed rules, formulas with variable definitions, edge cases, dependencies, tuning knobs with safe ranges, and acceptance criteria
- Output: completed design document, drafted to `production/combat/[feature]-gdd-draft.md`

The coordinator retains authorized phase outputs at `design/gdd/[feature].md`. Implementation follows the accepted file ownership; independent review returns findings read-only.

### Phase 2: Architecture
Delegate to **ccgs-gameplay-programmer** (with **ccgs-ai-programmer** if AI is involved):
- Review the design document, reading it by section: find the headings you need with the search tool (pattern `^#`, content mode) and read only those sections
- Design the code architecture: class structure, interfaces, data flow
- Identify integration points with existing systems
- Output: architecture sketch with file list and interface definitions

Then spawn the **primary engine specialist** to validate the proposed architecture:
- Is the class/node/component structure idiomatic for the pinned engine? (e.g., Godot node hierarchy, Unity MonoBehaviour vs DOTS, Unreal Actor/Component design)
- Are there engine-native systems that should be used instead of custom implementations?
- Any proposed APIs that are deprecated or changed in the pinned engine version?
- Output: engine architecture notes — incorporate into the architecture before Phase 3 begins

If no engine is configured, skip the specialist spawn. **Record ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)`` in this run's output.** A skipped check that says nothing is indistinguishable from a check that passed.

Use `the host input tool`:
- Prompt: "Architecture sketch complete. Approve to proceed with parallel implementation."
- Options:
  - `[A] Proceed — spawn implementation agents (ccgs-gameplay-programmer, ccgs-ai-programmer, ccgs-technical-artist, ccgs-sound-designer)`
  - `[B] Revise the architecture first — I'll describe what needs to change`
  - `[C] Stop here — I'll continue later`

Only spawn implementation agents if user selects [A]. (In `guided`/`autonomous`
mode this architecture gate is a normal phase transition — proceed to
implementation unless the architecture sketch came back BLOCKED, recording the
decision via `log_decision` in autonomous mode. The gate is not a release-
critical or irreversible decision, so it follows the standard pipeline rule.)

### Phase 3: Implementation (parallel where possible)
Delegate in parallel:
- **ccgs-gameplay-programmer**: Implement core combat mechanic code
- **ccgs-ai-programmer**: Implement AI behaviors (if the feature involves NPC reactions)
- **ccgs-technical-artist**: Create VFX and shader effects
- **ccgs-sound-designer**: Define audio event list and mixing notes, drafted to `production/combat/[feature]-audio-events.md`

The coordinator retains authorized phase outputs. Implementation follows the accepted file ownership; independent review returns findings read-only.

### Phase 4: Integration
- Wire together gameplay code, AI, VFX, and audio
- Ensure all tuning knobs are exposed and data-driven
- Verify the feature works with existing combat systems

**Gate**: Present the integration result; guided advances when the gate has no blockers, while consequential unresolved decisions remain pending.

### Phase 5: Validation
Delegate to **ccgs-qa-tester**:
- Write test cases from the acceptance criteria
- Test all edge cases documented in the design
- Verify performance impact is within budget
- File bug reports for any issues found

### Phase 6: Sign-off
- Collect results from all team members
- Report feature status: COMPLETE / NEEDS WORK / BLOCKED
- List any outstanding issues and their assigned owners

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

A summary report covering: design completion status, implementation status per team member, test results, and any open issues.

Verdict: **COMPLETE** — combat feature designed, implemented, and validated.

If the engine validation was skipped (Phase 2, no engine configured), the verdict
says so — never a plain COMPLETE:

Verdict: **COMPLETE — engine validation NOT ASSESSED ([reason])** — combat feature designed, implemented, and validated; the engine specialist never reviewed the architecture.

Verdict: **NEEDS WORK** — every phase ran, but Phase 5 validation left failures or open bugs unresolved; the report lists each with its owner.

Verdict: **BLOCKED** — one or more phases could not complete, or an agent was skipped (`.agents/studio/docs/error-recovery-protocol.md` step 5); partial report produced with unresolved items listed.

## Next Steps

- Run `$ccgs-code-review` on the implemented combat code before closing stories.
- Run `$ccgs-balance-check` to validate combat formulas and tuning values.
- Run `$ccgs-team-polish` if VFX, audio, or performance polish is needed.
