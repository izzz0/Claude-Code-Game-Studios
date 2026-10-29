## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Phase / agent | Writes to |
|---|---|
| 1 ccgs-live-ops-designer | `production/live-ops/[season-slug]/brief.md` |
| 2 ccgs-narrative-director | `production/live-ops/[season-slug]/narrative.md` |
| 3 ccgs-economy-designer | `production/live-ops/[season-slug]/economy.md` |
| 4 ccgs-analytics-engineer | `production/live-ops/[season-slug]/analytics.md` |
| 5 ccgs-narrative-director | `production/live-ops/[season-slug]/narrative-text.md` |
| 5 ccgs-writer | `production/live-ops/[season-slug]/copy.md` |
| 6 ccgs-community-manager | `production/live-ops/[season-slug]/comms.md` |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Live Ops

**Argument check:** If no season name or event description is provided, output:
> "Usage: `$ccgs-team-live-ops [season name or event description] [--review full|lean|solo]` — Provide the name or description of the season or live event to plan."
Then stop immediately without spawning any subagents or reading any files.

When this skill is invoked with a valid argument, orchestrate the live-ops team through a structured planning pipeline.

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
- **`individual`** (default): `ccgs-live-ops-designer` + `ccgs-economy-designer`. Other agents consulted via these two, not spawned separately.
- **`small`**: + `ccgs-analytics-engineer` + `ccgs-community-manager`.
- **`studio`**: + `ccgs-writer` + `ccgs-narrative-director` (the full pipeline as documented).
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
- **ccgs-live-ops-designer** — Season structure, event cadence, retention mechanics, battle pass
- **ccgs-economy-designer** — Live economy balance, store rotation contents and prices (ccgs-live-ops-designer sets its cadence), currency pricing, pity timers
- **ccgs-analytics-engineer** — Success metrics, A/B test design, event tracking, dashboard specs
- **ccgs-community-manager** — Player-facing announcements, event descriptions, seasonal messaging
- **ccgs-narrative-director** — Seasonal narrative theme, story arc, world event framing
- **ccgs-writer** — Event descriptions, reward item names, seasonal flavor text, announcement copy

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** Working artifacts go under
`production/live-ops/[season-slug]/`, where `[season-slug]` is the argument as a
slug — lowercase, spaces → hyphens. One file per agent, so the parallel phases
never share one:

| Phase / agent | Writes to |
|---|---|
| 1 ccgs-live-ops-designer | `production/live-ops/[season-slug]/brief.md` |
| 2 ccgs-narrative-director | `production/live-ops/[season-slug]/narrative.md` |
| 3 ccgs-economy-designer | `production/live-ops/[season-slug]/economy.md` |
| 4 ccgs-analytics-engineer | `production/live-ops/[season-slug]/analytics.md` |
| 5 ccgs-narrative-director | `production/live-ops/[season-slug]/narrative-text.md` |
| 5 ccgs-writer | `production/live-ops/[season-slug]/copy.md` |
| 6 ccgs-community-manager | `production/live-ops/[season-slug]/comms.md` |

These are working drafts; the final documents under `design/live-ops/seasons/`
are compiled from them (Output Documents).

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


Launch independent agents in parallel where the pipeline allows it (Phases 3 and 4 can run simultaneously).

## Pipeline

### Phase 1: Season/Event Scoping
Delegate to **ccgs-live-ops-designer**:
- Define the season or event: type (seasonal, limited-time event, challenge), duration, theme direction
- Outline the content list: what's new (modes, items, challenges, story beats)
- Define the retention hook: what brings players back daily/weekly during this season
- Identify resource budget: how much new content needs to be created vs. reused
- Output: season brief with scope, content list, and retention mechanic overview

### Phase 2: Narrative Theme
Delegate to **ccgs-narrative-director**:
- Read the season brief from Phase 1
- Design the seasonal narrative theme: how does this event connect to the game world?
- Define the central story hook players will discover during the event
- Identify which existing lore threads this season can advance
- Output: narrative framing document (theme, story hook, lore connections)

### Phase 3: Economy Design (parallel with Phase 4)
Delegate to **ccgs-economy-designer**:
- Read the season brief and existing economy rules from `design/live-ops/economy-rules.md`
- Design the reward track: free tier progression, premium tier value proposition
- Plan the in-season economy: seasonal currency, store rotation contents, pricing
- Define pity timer mechanics and bad-luck protection for any random elements
- Verify no pay-to-win items in premium track
- Output: economy design doc with reward tables, pricing, and currency flow

### Phase 4: Analytics and Success Metrics (parallel with Phase 3)
Delegate to **ccgs-analytics-engineer**:
- Read the season brief
- Define success metrics: participation rate target, retention lift target, battle pass completion rate
- Design any A/B tests to run during the season (e.g., different reward cadences)
- Specify new telemetry events needed for this season's content
- Output: analytics plan with success criteria and instrumentation requirements

### Phase 5: Content Writing (parallel)
Start only after both Phase 3 and Phase 4 results are collected. Delegate in parallel:
- **ccgs-narrative-director** (if needed): Write any in-game narrative text (cutscene scripts, NPC dialogue, world event descriptions) for the season
- **ccgs-writer**: Write all player-facing text — event names, reward item descriptions, challenge objective text, seasonal flavor text
- Both should read the narrative framing doc from Phase 2

### Phase 6: Player Communication Plan
Delegate to **ccgs-community-manager**:
- Read the season brief, economy design, and narrative framing
- Draft the season launch announcement (tone, key highlights, platform-specific versions)
- Plan the communication cadence: pre-launch teaser, launch day post, mid-season reminder, final week FOMO push
- Draft known-issues section placeholder for day-1 patch notes
- Output: communication calendar with draft copy for each touchpoint

### Phase 7: Review and Sign-off
Collect outputs from all phases and present a consolidated season plan:
- Season brief (Phase 1)
- Narrative framing (Phase 2)
- Economy design and reward tables (Phase 3)
- Analytics plan and success metrics (Phase 4)
- Written content inventory (Phase 5)
- Communication calendar (Phase 6)

Present a summary to the user with:
- **Content scope**: what is being created
- **Economy health check**: does the reward track feel fair and non-predatory?
- **Analytics readiness**: are success criteria defined and instrumented?
- **Ethics review**: check the Phase 3 economy design against `design/live-ops/ethics-policy.md`
  - If the file does not exist: flag "ETHICS REVIEW SKIPPED: `design/live-ops/ethics-policy.md` not found. Economy design was not reviewed against an ethics policy. Recommend creating one before production begins." Include this flag in the season design output document. Add to next steps: create `design/live-ops/ethics-policy.md`.
  - If the file exists and a violation is found: flag "ETHICS FLAG: [element] in Phase 3 economy design violates [policy rule]. Approval is blocked until this is resolved." Do NOT issue a COMPLETE verdict or write output documents. Use `the host input tool` with options: revise economy design / override with documented rationale / cancel. If user chooses to revise: re-spawn ccgs-economy-designer to produce a corrected design, then return to Phase 7 review. If user selects Cancel: end with Verdict: BLOCKED — "Live ops design cancelled due to unresolved ethics violation. Resolve the flagged issues and re-run $ccgs-team-live-ops."
- **Open questions**: decisions still needed before production begins

Ask the user to approve the season plan before delegating to production teams. Issue the COMPLETE verdict only after the user approves and no unresolved ethics violations remain. If an ethics violation is unresolved, end with Verdict: **BLOCKED**.

## Output Documents

The coordinator retains authorized phase outputs. Implementation follows the accepted file ownership; independent review returns findings read-only.

Paths:
- `seasons/S[N]_[name].md` — Season design document (from Phase 1-3)
- `seasons/S[N]_[name]_analytics.md` — Analytics plan (from Phase 4)
- `seasons/S[N]_[name]_comms.md` — Communication calendar (from Phase 6)

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

If a BLOCKED state is unresolvable, end with Verdict: **BLOCKED** instead of COMPLETE.


## Output

A summary covering: season theme and scope, economy design highlights, success metrics, content list, communication plan, and any open decisions needing user input before production.

Verdict: **COMPLETE** — season plan produced and handed off for production.

## Next Steps

- Run `$ccgs-design-review` on the season design document for consistency validation.
- Run `$ccgs-sprint-plan` to schedule content creation work for the season (at `workflow: minimal`, which has no sprints, add it to the brief's build order instead).
- Run `$ccgs-team-release` when the season content is ready to deploy.
- If the run ended **BLOCKED** on an ethics flag: revise the economy design against
  `design/live-ops/ethics-policy.md` and re-run `$ccgs-team-live-ops`; the three steps
  above wait for a COMPLETE plan.
