## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Agent | Writes to |
|---|---|
| ccgs-performance-analyst | `production/polish/[area]-report-[date].md` |
| ccgs-technical-artist | `production/polish/[area]-render-notes-[date].md` |
| ccgs-engine-programmer | `production/polish/[area]-engine-fixes-[date].md` |
| ccgs-tools-programmer | `production/polish/[area]-tool-fixes-[date].md` |
| ccgs-sound-designer | `production/polish/[area]-audio-notes-[date].md` |
| ccgs-qa-tester | `production/polish/[area]-verification-[date].md` |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Polish

If no argument is provided, output usage guidance and exit without spawning any agents:
> Usage: `$ccgs-team-polish [feature or area to polish] [--review full|lean|solo]` — specify the feature or area to polish (e.g., `combat`, `main menu`, `inventory system`, `level-1`). Do not use `the host input tool` here; output the guidance directly.

When this skill is invoked with an argument, orchestrate the polish team through a structured pipeline.

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
- **`individual`** (default): `ccgs-performance-analyst` + `ccgs-technical-artist`. Other agents consulted via these two, not spawned separately. No programmer is active, so the optimisation list's programmer items are not implemented in this run — the report names the list as handed to `$ccgs-dev-story` (Phase 2).
- **`small`**: + `ccgs-sound-designer` + `ccgs-qa-tester` + `ccgs-engine-programmer`, and `ccgs-tools-programmer` when Phase 1 traces a cause to a content authoring tool (the full pipeline as documented).
- **`studio`**: the `small` set, `ccgs-engine-programmer` included, + an adversarial review pass: Phase 5's ccgs-qa-tester is told "your job is not to confirm this holds — find how it breaks", and the report says the pass ran. This pipeline has no engine specialist to widen; engine-level work stays with `ccgs-engine-programmer`.
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
- **ccgs-performance-analyst** — Profiling, memory analysis, frame budget, and the optimisation list — it writes no game code
- **ccgs-engine-programmer** — Implements the optimisation list's engine-level items: rendering pipeline, memory, resource loading, hot paths (invoke when ccgs-performance-analyst identifies low-level root causes)
- **ccgs-technical-artist** — VFX polish, shader optimization, visual quality
- **ccgs-sound-designer** — Audio polish, mixing, ambient layers, feedback sounds
- **ccgs-tools-programmer** — Content pipeline tool verification, editor tool stability, automation fixes (Phase 2, when Phase 1 traces a cause to a content authoring tool)
- **ccgs-qa-tester** — Edge case testing, regression testing, soak testing

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]` — this skill's destination is
`production/polish/`.** Name it per agent, one file each:

| Agent | Writes to |
|---|---|
| ccgs-performance-analyst | `production/polish/[area]-report-[date].md` |
| ccgs-technical-artist | `production/polish/[area]-render-notes-[date].md` |
| ccgs-engine-programmer | `production/polish/[area]-engine-fixes-[date].md` |
| ccgs-tools-programmer | `production/polish/[area]-tool-fixes-[date].md` |
| ccgs-sound-designer | `production/polish/[area]-audio-notes-[date].md` |
| ccgs-qa-tester | `production/polish/[area]-verification-[date].md` |

> **Why `production/` and not `docs/`.** These are date-stamped measurements of
> one run, the same shape as `production/qa/smoke-[date].md` — not durable
> specifications like `docs/architecture/`. Keeping them beside the other
> point-in-time process artifacts is what makes a later comparison possible.
>
> The `[path]` contract above has a precondition: the path is one *you* named, so
> a concrete destination must be stated here or every run invents one. Unlike
> `$ccgs-team-qa` and `$ccgs-team-narrative`, whose destinations are fixed by their
> consumers, this location has no reader in the repo and was chosen deliberately.
> **Nothing reads `production/polish/` yet** — say so when reporting, so the user
> knows the report is a record rather than an input to a later gate.

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


Launch independent agents in parallel where the pipeline allows it (e.g., Phases 3 and 4 can run simultaneously).

## Pipeline

### Phase 1: Assessment
Delegate to **ccgs-performance-analyst**:
- Profile the target feature/area using `$ccgs-perf-profile`
- Identify performance bottlenecks and frame budget violations
- Measure memory usage and check for leaks
- Benchmark against target hardware specs
- Output: performance report with the prioritized **optimisation list** — for each item, the change, its expected gain against the budget, and its owner (ccgs-technical-artist for rendering-side changes, ccgs-engine-programmer for engine systems and hot paths, ccgs-tools-programmer for a content authoring tool, otherwise the programmer who owns the system)

### Phase 2: Optimization
ccgs-performance-analyst writes no game code ("recommend and assign", its agent file),
so Phase 2 implements its Phase 1 list through the owners in the active set:
- **ccgs-engine-programmer** — spawned only when Phase 1 identified engine-level root causes (rendering pipeline, resource loading, memory allocator, hot paths in core loops): implement those items, fix allocation pressure, verify gameplay behavior is unchanged. Output: engine-level fixes with before/after metrics and profiler validation
- **ccgs-tools-programmer** — only when Phase 1 traced a cause to a content authoring tool: fix the tool. Output: tool fixes with before/after metrics
- **ccgs-technical-artist** — rendering-side items (draw calls, overdraw, particles, shaders, LOD) join its Phase 3 brief

The coordinator retains authorized phase outputs. Implementation follows the accepted file ownership; independent review returns findings read-only.

**An item whose owner is not in the active set is not implemented in this run.**
At `team.size: individual` that is every programmer item, since no programmer is
active; at any size it includes an item owned by a programmer this pipeline does
not name (e.g. ccgs-gameplay-programmer for a gameplay-script hot spot). The report
lists those items with their owners under
"Optimisation list handed to `$ccgs-dev-story`: `production/polish/[area]-report-[date].md`".
A metric they target that is over budget stays a known problem at Phase 6.

### Phase 3: Visual Polish (parallel with Phase 2)
Delegate to **ccgs-technical-artist**:
- Review VFX for quality and consistency with art bible
- Optimize particle systems and shader effects
- Add screen shake, camera effects, and visual juice where appropriate
- Ensure effects degrade gracefully on lower settings
- Output: polished visual effects

### Phase 4: Audio Polish (parallel with Phase 2)
Delegate to **ccgs-sound-designer**:
- Review audio events for completeness (are any actions missing sound feedback?)
- Check audio mix levels — nothing too loud or too quiet relative to the mix
- Add ambient audio layers for atmosphere
- Verify audio plays correctly with spatial positioning
- Output: audio polish list and mixing notes

### Phase 5: Hardening
Delegate to **ccgs-qa-tester**:
- Test all edge cases: boundary conditions, rapid inputs, unusual sequences
- Soak test: run the feature for extended periods checking for degradation
- Stress test: maximum entities, worst-case scenarios
- Regression test: verify polish changes haven't broken existing functionality — each Phase 2–4 change by name, engine-level fixes included
- Test on minimum spec hardware (if available)
- Output: test results with any remaining issues

### Phase 6: Sign-off
- Collect results from all team members
- Compare performance metrics against budgets
- Report: READY FOR RELEASE / NOT ASSESSED / NEEDS MORE WORK
- List every remaining issue with its severity (S1–S4), the measured gap where there is one (e.g. "9 ms against a 6 ms budget — 3 ms over"), and a recommendation; a regression also names the broken behavior and the polish change that caused it

**NOT ASSESSED ranks above READY FOR RELEASE and below NEEDS MORE WORK.** A known
problem — a metric over budget, an unresolved regression — makes it NEEDS MORE
WORK whatever else went unchecked. Otherwise, if any part of the scope could not
be checked, the result is NOT ASSESSED, never READY FOR RELEASE, and the report
names each gap:
- A metric with no committed budget. `performance.target_framerate`,
  `performance.frame_budget_ms`, `performance.draw_call_limit` and
  `performance.memory_ceiling_mb` have no default, and `$ccgs-perf-profile` reports an
  unset one as NOT ASSESSED — nothing was compared, so no budget was met.
- A phase that did not run: BLOCKED, skipped, or its agent outside the active set.
  At `team.size: individual`, ccgs-sound-designer's audio polish and ccgs-qa-tester's
  hardening are only consulted through the active agents, not run, and Phase 2's
  programmer items are handed to `$ccgs-dev-story` rather than implemented.

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

A summary report covering: performance before/after metrics, visual polish changes, audio polish changes, test results, any optimisation list handed to `$ccgs-dev-story`, and release readiness assessment.

## Next Steps

- If READY FOR RELEASE: run `$ccgs-release-checklist` for the final pre-release validation.
- If NEEDS MORE WORK: schedule remaining issues in `$ccgs-sprint-plan update` (at `workflow: minimal`, which has no sprints, add them to the brief's build order) and re-run `$ccgs-team-polish` after fixes.
- If NOT ASSESSED: supply what was missing — commit the unset `performance.*` budgets in `project.yaml` (`$ccgs-settings`), or run the phases that did not run (raise `team.size`) — then re-run `$ccgs-team-polish`. Do not treat the area as release-ready.
- If the report handed an optimisation list to `$ccgs-dev-story`: implement those items there, then re-run `$ccgs-team-polish` to measure the gain.
- Run `$ccgs-gate-check` for a formal phase gate verdict before handing off to release.
