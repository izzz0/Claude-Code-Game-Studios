## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Step / agent | Writes to |
|---|---|
| 1 ccgs-audio-director | `production/audio/[feature]/direction.md` |
| 2 ccgs-sound-designer | `production/audio/[feature]/sfx-spec.md` |
| 2 ccgs-accessibility-specialist | `production/audio/[feature]/accessibility.md` |
| 3 ccgs-technical-artist | `production/audio/[feature]/integration-plan.md` |
| 3 engine specialist | `production/audio/[feature]/engine-notes.md` |
| 4 ccgs-gameplay-programmer | accepted code/asset/test files assigned by the coordinator |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Audio

If no argument is provided, output usage guidance and exit without spawning any agents:
> Usage: `$ccgs-team-audio [feature or area to design audio for] [--review full|lean|solo]` — specify the feature or area to design audio for (e.g., `combat`, `main menu`, `forest biome`, `boss encounter`). Do not use `the host input tool` here; output the guidance directly.

When this skill is invoked with an argument, orchestrate the audio team through a structured pipeline.

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
- **`individual`** (default): `ccgs-sound-designer` only. Other agents consulted via the ccgs-sound-designer, not spawned separately.
- **`small`**: + `ccgs-audio-director` + `ccgs-technical-artist` + `ccgs-gameplay-programmer`.
- **`studio`**: + `ccgs-accessibility-specialist` + the primary engine specialist (the full pipeline as documented).
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

1. **Read the argument** for the target feature or area (e.g., `combat`,
   `main menu`, `forest biome`, `boss encounter`).

2. **Gather context**:
   - Read relevant design docs in `design/gdd/` for the feature, by section: find the
     headings you need with the search tool (pattern `^#`, content mode) and Read
     those ranges with offset and limit
   - Read the sound bible at `design/audio/sound-bible.md` if it exists. If only
     `design/gdd/sound-bible.md` exists (where earlier versions put it), read that
     and recommend moving it to `design/audio/` — in `design/gdd/` the GDD checks
     count every file as a system GDD. If neither exists,
     say so in one line — "No sound bible at `design/audio/sound-bible.md`; audio
     direction starts from the GDDs alone" — so the gap is visible in the output.
     Carry the gap forward: say so in the ccgs-audio-director's Step 1 brief, and
     recommend creating a sound bible in Next Steps.
   - Read existing audio asset lists in `assets/audio/`
   - Read any existing sound design docs for this area

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** Working artifacts go under
`production/audio/[feature]/`, where `[feature]` is the argument as a slug —
lowercase, spaces → hyphens (`boss encounter` → `boss-encounter`), the same slug
the "Save to" step uses. One file per agent, so parallel steps never share one:

The coordinator retains authorized phase outputs at `production/audio/[feature]/direction.md`, `production/audio/[feature]/sfx-spec.md`, `production/audio/[feature]/accessibility.md`, `production/audio/[feature]/integration-plan.md`, `production/audio/[feature]/engine-notes.md`. Implementation follows the accepted file ownership; independent review returns findings read-only.

These are working drafts; the durable record is the audio design document you
compile from them.

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


3. **Orchestrate the audio team** in sequence:

### Step 1: Audio Direction (ccgs-audio-director)
Spawn the `ccgs-audio-director` agent to:
- Define the sonic identity for this feature/area
- Specify the emotional tone and audio palette
- Set music direction (adaptive layers, stems, transitions)
- Define audio priorities and mix targets
- Establish any adaptive audio rules (combat intensity, exploration, tension)

### Step 2: Sound Design and Audio Accessibility (parallel)
Spawn the `ccgs-sound-designer` agent to:
- Create detailed SFX specifications for every audio event
- Define sound categories (ambient, UI, gameplay, music, dialogue)
- Specify per-sound parameters (volume range, pitch variation, attenuation)
- Plan audio event list with trigger conditions
- Define mixing groups and ducking rules

Spawn the `ccgs-accessibility-specialist` agent in parallel to:
- Identify which audio events carry critical gameplay information (damage received, enemy nearby, objective complete) and require visual alternatives for hearing-impaired players
- Specify subtitle requirements: which audio events need captions, what text format, on-screen duration
- Check that no gameplay state is communicated by audio alone (all must have a visual fallback)
- Review the audio event list for any that could cause issues for players with auditory sensitivities (high-frequency alerts, sudden loud events)
- Output: audio accessibility requirements list integrated into the audio event spec

A gameplay-critical audio event with no visual cue or subtitle is labelled
**BLOCKING** in the report, not advisory. Step 3 does not start until the user
resolves it or explicitly accepts it at the Step 2 decision point, which offers
the fix (a visual cue, subtitle or haptic fallback) and a stop; an accepted gap
is listed among the open questions in the summary.

### Step 3: Technical Implementation (parallel)
Spawn the `ccgs-technical-artist` agent to:
- Design the audio middleware integration (Wwise/FMOD/native)
- Define audio bus structure and routing
- Specify memory budgets for audio assets per platform
- Plan streaming vs preloaded asset strategy
- Design any audio-reactive visual effects

Spawn the **primary engine specialist** in parallel (`<engine>-specialist` derived from `engine.name` — Godot→`ccgs-godot-specialist`, Unity→`ccgs-unity-specialist`, Unreal→`ccgs-unreal-specialist`; fall back to the Primary line of `## Engine Specialists` in `docs/technical-preferences.md`) to validate the integration approach:
- Is the proposed audio middleware integration idiomatic for the engine? (e.g., Godot's built-in AudioStreamPlayer vs FMOD, Unity's Audio Mixer vs Wwise, Unreal's MetaSounds vs FMOD)
- Any engine-specific audio node/component patterns that should be used?
- Known audio system changes in the pinned engine version that affect the integration plan?
- Output: engine audio integration notes to merge with the ccgs-technical-artist's plan

If no engine is configured, skip the specialist spawn. **Record ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)`` in this run's output.** A skipped check that says nothing is indistinguishable from a check that passed; the reader cannot tell engine guidance was never sought.

### Step 4: Code Integration (ccgs-gameplay-programmer)
Spawn the `ccgs-gameplay-programmer` agent to:
- Implement audio manager system or review existing
- Wire up audio events to gameplay triggers
- Implement adaptive music system (if specified)
- Set up audio occlusion/reverb zones
- Write unit tests for audio event triggers

4. **Compile the audio design document** combining all team outputs.

The coordinator retains authorized phase outputs at `design/audio/audio-[feature].md`. Implementation follows the accepted file ownership; independent review returns findings read-only.

   Note: If `design/audio/` does not exist, writing the file creates it.

6. **Output a summary** with: audio event count, estimated asset count,
   implementation tasks, and any open questions between team members.

Verdict: **COMPLETE** — audio design document produced and team pipeline finished.

If the engine validation was skipped (no engine configured), the verdict says
so — never a plain COMPLETE:

Verdict: **COMPLETE — engine validation NOT ASSESSED ([reason])** — audio design document produced; the engine specialist never reviewed the integration plan.

If the pipeline stops because a dependency is unresolved (e.g., critical accessibility gap or missing GDD not resolved by the user):

Verdict: **BLOCKED** — [reason]


## Next Steps

- Review the audio design doc with the ccgs-audio-director before implementation begins.
- Use `$ccgs-dev-story` to implement the audio manager and event system once the design is approved.
- Run `$ccgs-asset-audit` after audio assets are created to verify naming and format compliance.
- If there was no sound bible, create one before the next audio pass: ask the
  `ccgs-audio-director` agent to draft `design/audio/sound-bible.md` from
  `.agents/studio/docs/templates/sound-bible.md`, starting from this run's Step 1
  direction (it asks before writing under `design/`).

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
