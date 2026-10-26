## Native artifact destinations

The original fixed destinations remain; review roles return read-only findings and the coordinator retains them afterwards. Tables describe destinations, not a grant to publish or overwrite.

| Phase / agent | Writes to | Destination fixed by |
|---|---|---|
| 1 ccgs-producer | `production/releases/release-plan-[version].md` | this skill |
| 2 ccgs-release-manager | `production/releases/release-checklist-[version].md` | `$ccgs-release-checklist` |
| 3 ccgs-qa-lead | `production/releases/qa-gate-[version].md` | this skill |
| 3 ccgs-devops-engineer | `production/releases/build-[version].md` | this skill |
| 3 ccgs-security-engineer | `production/releases/security-signoff-[version].md` | this skill |
| 3 ccgs-network-programmer | `production/releases/netcode-signoff-[version].md` | this skill |
| 4 ccgs-localization-lead | `production/releases/localization-signoff-[version].md` | this skill |
| 4 ccgs-performance-analyst | `production/releases/performance-signoff-[version].md` | this skill |
| 4 ccgs-analytics-engineer | `production/releases/analytics-signoff-[version].md` | this skill |
| 5 go/no-go | `production/releases/go-no-go-[version].md` | this skill |
| 6 ccgs-release-manager | `docs/patch-notes/[version].md` | `$ccgs-patch-notes` |
| 6 ccgs-community-manager | `production/releases/announcement-[version].md` | this skill |
| 7 ccgs-release-manager | `production/releases/release-report-[version].md` | this skill |

Common native gate rules: PASS permits advancement; CONCERNS requires the user's explicit acceptance of the listed risks; FAIL and NOT ASSESSED retain the stage. Source labels APPROVED/APPROVE/GO map to PASS, APPROVED WITH CONDITIONS maps to CONCERNS, and NOT APPROVED/REJECT/NO-GO maps to FAIL. A completed coordination task only means its returned work was collected, not that its quality gate passed.

Minimal test waiver is available only for genuinely unconfigured automated tests with no stricter story requirement. Configured failures/timeouts are FAIL; zero tests, absent runner/result/coverage reports and missing mandatory review/runtime/screenshots are NOT ASSESSED. All player-visible acceptance needs a real launch, saved and opened image, and input/runtime observations. Coverage percentages and performance claims require actual reports.

# Source-derived workflow

Migrated from fixed baseline 05ad7c8. The native execution contract in SKILL.md and shared core-workflow.md govern authorization, read-only reviews and evidence. Preserve the task-specific phases, size selection and artifact destinations below. Role viewpoints routed through an active worker are not independently executed roles.

# Team Release

**Argument check:** If no version number is provided:
1. Read `production/session-state/active.md` and the most recent file in `production/milestones/` (if they exist) to infer the target version.
2. If a version is found: report "No version argument provided — inferred [version] from milestone data. Proceeding." Then confirm with `the host input tool`: "Releasing [version]. Is this correct?"
3. If no version is discoverable: use `the host input tool` to ask "What version number should be released? (e.g., v1.0.0)" and wait for user input before proceeding. Do NOT default to a hardcoded version string.

When this skill is invoked, orchestrate the release team through a structured pipeline.

Guided advances ordinary authorized phases automatically. Collaborative reviews major drafts; material product/scope changes still require the user.

## Phase 0: Resolve Config

Run explicitly: `bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys review_mode,automation,team.size,workflow`.
Use the explicit helper result; --review overrides only review_mode. If configuration cannot be resolved, report NOT ASSESSED and the error; do not substitute guessed defaults.

**Readiness before dispatch.** At standard/full, require a current release-gate PASS (or its CONCERNS explicitly accepted by the user), with the corresponding authorized stage update. A Release label alone is not quality evidence. At minimal, keep the phase ladder inapplicable: check the accepted backlog, current tests/review/runtime evidence and local build requirements directly without forcing project.stage to Release.

FAIL or NOT ASSESSED stops the release pipeline. Return missing/failed requirements and permit only blocker remediation or clearly labeled local preparation; neither is release acceptance. Do not offer a stage-check override or proceed-anyway route.

`review_mode` sets director-gate depth, and this pipeline has no director gate:
no phase below spawns CD-, TD-, PR- or AD-PHASE-GATE, at any `review_mode`. Its
phase gates are the pipeline's own decision points (defined under `team.size`
below), and the agents that work at them are team members, not director gates.

`automation` drives the Decision Points note above. See the Decision Points note above and
`.agents/studio/docs/automation-modes.md` for how each mode changes pipeline behavior.

**`team.size`**: which agents are active (orthogonal to review_mode gate-depth and workflow docs).
- **`individual`** (default): `ccgs-release-manager` only. Other agents consulted via the ccgs-release-manager, not spawned separately.
- **`small`**: + `ccgs-producer` + `ccgs-devops-engineer` + `ccgs-qa-lead` + `ccgs-community-manager`.
- **`studio`**: + `ccgs-security-engineer` + `ccgs-analytics-engineer` + `ccgs-localization-lead` + `ccgs-performance-analyst`, and `ccgs-network-programmer` when the game is multiplayer (the full pipeline as documented).
A non-core agent needed at `individual` routes through the nearest active core agent with an informational note. **"Phase gate" means any phase that ends in an `the host input tool` decision point this pipeline itself lists** — a transition under Decision Points above, the stage check, or the Phase 6 deploy question — **whatever the `automation` mode.** `guided` and `autonomous` change how a gate is passed (it auto-advances, or is recorded with `log_decision`), not whether it is one, so bounded-exception condition (3) below holds at it in every mode. An agent restricted to "phase gates only" is spawned at those points and no others. This active-set scoping applies throughout the pipeline below: any phase that names an agent outside the active set routes through the nearest core agent rather than spawning it.

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
- **ccgs-release-manager** — Release tag, versioning, changelog, patch notes, deployment
- **ccgs-qa-lead** — Test sign-off, regression suite, release quality gate
- **ccgs-devops-engineer** — Build pipeline, artifacts, deployment automation
- **ccgs-security-engineer** — Pre-release security audit (invoke if game has online/multiplayer features or player data)
- **ccgs-network-programmer** — Netcode stability sign-off (invoke if game has multiplayer)
- **ccgs-analytics-engineer** — Verify telemetry events fire correctly and dashboards are live
- **ccgs-localization-lead** — Verify every shipped string is translated
- **ccgs-performance-analyst** — Benchmark the release build against its performance targets
- **ccgs-community-manager** — Launch announcement and player-facing messaging, written from the patch notes
- **ccgs-producer** — Go/no-go decision, stakeholder communication, scheduling

## How to Delegate

Use actual native Codex role runs with the return contract below.

**Brief each agent — do not dump context.** Read the shared inputs **once** and pass a distilled brief inline: the lines each agent actually needs, never a file path for a document you have already read (an agent handed a path re-reads the whole file). Pass a path only for a document you have not read and only that agent needs.

End every role brief with its actual owned files, required artifacts, acceptance criteria and a concise returned summary. Authorized implementation may edit those files. Review and plan roles return findings read-only; the coordinator retains their response at the listed destination afterwards.


**Substitute a real path for `[path]`.** One file per agent under
`production/releases/`, except the two whose homes are fixed elsewhere. An active
agent standing in for one outside the active set writes that agent's file:

| Phase / agent | Writes to | Destination fixed by |
|---|---|---|
| 1 ccgs-producer | `production/releases/release-plan-[version].md` | this skill |
| 2 ccgs-release-manager | `production/releases/release-checklist-[version].md` | `$ccgs-release-checklist` |
| 3 ccgs-qa-lead | `production/releases/qa-gate-[version].md` | this skill |
| 3 ccgs-devops-engineer | `production/releases/build-[version].md` | this skill |
| 3 ccgs-security-engineer | `production/releases/security-signoff-[version].md` | this skill |
| 3 ccgs-network-programmer | `production/releases/netcode-signoff-[version].md` | this skill |
| 4 ccgs-localization-lead | `production/releases/localization-signoff-[version].md` | this skill |
| 4 ccgs-performance-analyst | `production/releases/performance-signoff-[version].md` | this skill |
| 4 ccgs-analytics-engineer | `production/releases/analytics-signoff-[version].md` | this skill |
| 5 go/no-go | `production/releases/go-no-go-[version].md` | this skill |
| 6 ccgs-release-manager | `docs/patch-notes/[version].md` | `$ccgs-patch-notes` |
| 6 ccgs-community-manager | `production/releases/announcement-[version].md` | this skill |
| 7 ccgs-release-manager | `production/releases/release-report-[version].md` | this skill |

> **Every one of those thirteen outputs needs a stated destination.**
> `production/releases/` is where `$ccgs-release-checklist` already writes, and
> `docs/patch-notes/[version].md` is where `$ccgs-patch-notes` already writes, so the
> release record lands in one place regardless of which skill produced it.
>
> **A separate file per agent, not one appended record.** Phase 3 and Phase 4
> spawn agents in parallel; two agents appending to one file race, and the loser's
> section vanishes silently.

The accepted brief authorizes ordinary in-scope writes. Assign one ccgs-writer per file. Only the coordinator updates stories, durable QA records and checkpoints; review runs never write them.


Launch independent agents in parallel where the pipeline allows it (e.g., Phase 3 agents can run simultaneously).

## Pipeline

### Phase 1: Release Planning
Delegate to **ccgs-producer**:
- Confirm all milestone acceptance criteria are met
- Identify any scope items deferred from this release
- Set the target release date and record the intended team communication locally
- Output: release authorization with scope confirmation

### Phase 2: Release Candidate
Delegate to **ccgs-release-manager**:
- Prepare the release version on the accepted working branch; record the exact candidate revision without switching, merging or publishing branches implicitly
- Confirm the release checklist from Polish (`$ccgs-release-checklist`, run before `$ccgs-gate-check release`) is complete for this candidate; run it now only if none exists
- Cut a `release/[version]` branch from the candidate only if this release needs stabilising (a freeze, platform certification) — bug fixes only there, and every fix lands on `main` as well
- Output: release candidate commit (plus the `release/*` branch, if one was cut) and checklist

### Phase 3: Quality Gate (parallel)
Delegate in parallel:
- **ccgs-qa-lead**: Execute full regression test suite. Test all critical paths. Verify no open bugs at the severities `$ccgs-gate-check release` blocks for this `workflow`: S1 at every tier, S2 and S3 too at `full`. Sign off on quality.
- **ccgs-devops-engineer**: Build release artifacts for all target platforms. Verify builds are clean and reproducible. Run automated tests in CI.
- **ccgs-security-engineer** *(if game has online features, multiplayer, or player data)*: Conduct pre-release security audit. Review authentication, anti-cheat, data privacy compliance. Sign off on security posture.
- **ccgs-network-programmer** *(if game has multiplayer)*: Sign off on netcode stability. Verify lag compensation, reconnect handling, and bandwidth usage under load.

When either agent is in the active set, decide its condition from `platform.online` and `platform.multiplayer` in `project.yaml`, plus whether the game stores player data. A key that is absent is not a `false`: ask the user rather than assume an offline game. An agent skipped on these grounds says so by name in the Phase 3 output — e.g. `ccgs-security-engineer: not spawned — platform.online: false, platform.multiplayer: false, no player data`.

### Phase 4: Localization, Performance, and Analytics
Delegate (can run in parallel with Phase 3 if resources available):
- Verify all strings are translated (delegate to **ccgs-localization-lead** if available)
- Run performance benchmarks against targets (delegate to **ccgs-performance-analyst** if available)
- **ccgs-analytics-engineer**: Verify all telemetry events fire correctly on release build. Confirm dashboards are receiving data. Check that critical funnels (onboarding, progression, monetization if applicable) are instrumented.
- Output: localization, performance, and analytics sign-off — one file per agent (table above)

### Phase 5: Go/No-Go
Before delegating, get the **ccgs-technical-director** release sign-off. The ccgs-producer
cannot spawn agents, so the orchestrator does: spawn `ccgs-technical-director` at
`review_mode: full` only — this is a director review, not a PHASE-GATE, so `lean`
and `solo` skip it. Ask for GO, CONCERNS or NO-GO on the release candidate's
technical state, or NOT ASSESSED naming what it could not read. When it is not
spawned, the go/no-go record says `ccgs-technical-director sign-off: not run
(review_mode: <mode>)` instead of listing it as given; a NOT ASSESSED answer is
recorded as such and never counted as a sign-off.

Delegate to **ccgs-producer**, passing every sign-off collected so far:
- Collect sign-off from: ccgs-qa-lead, ccgs-release-manager, ccgs-devops-engineer, ccgs-security-engineer (if spawned in Phase 3), ccgs-network-programmer (if spawned in Phase 3), and ccgs-technical-director (if spawned above)
- Retain the actual readiness evidence and any explicitly accepted CONCERNS in the go/no-go record
- Evaluate any open issues — are they blocking or can they ship?
- Make the go/no-go call
- Output: release decision with rationale

**If the producer declares NO-GO:** retain FAIL and the current stage, fix the blocker and repeat the affected checks or defer the release. Produce a partial report with missing/failed sign-offs. A written override cannot turn FAIL or NOT ASSESSED into permission to advance. Only a CONCERNS assessment permits explicit acceptance of its listed risks.

### Phase 6: Verified Local Release Package (if GO)

The release manager and DevOps engineer build the accepted local targets and retain build logs, exact revision/version, package paths and hashes. Launch the exported game and run the critical input/runtime checks; a successful export command alone is not sufficient. Finalize the local changelog and patch-note drafts. The coordinator records the local release result.

Publishing, uploading builds, pushing release tags, store changes, notifications and external messages require a separate explicit user request for those actions. Do not perform them as part of local release acceptance.

### Phase 7: Operations Preparation

Prepare the original release report, known-issues draft and monitoring/rollback plan. Existing telemetry, security, network and performance claims require actual reports from the accepted environment; absent services/reports remain NOT ASSESSED. Do not fabricate live dashboards or claim the game was published. Future explicitly authorized public releases may use the retained communication and post-release procedures.

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
partial report.** Full procedure: `.agents/studio/docs/error-recovery-protocol.md`.

Common blockers:
- Input file missing (story not found, GDD absent) → redirect to the skill that creates it
- ADR status is Proposed → do not implement; accept it with `$ccgs-architecture-decision accept ADR-NNNN` once decided
- Scope too large → split into two stories via `$ccgs-create-stories`
- Conflicting instructions between ADR and story → surface the conflict, do not guess


## Output

A summary report covering: release version, scope, quality gate results, go/no-go decision, deployment status, and monitoring plan.

Verdict: **COMPLETE** — release executed and deployed.
Verdict: **BLOCKED** — release halted; the stage check stopped it, go/no-go was NO, or a hard blocker is unresolved.

## Next Steps

- Monitor post-release dashboards for 48 hours.
- Run `$ccgs-retrospective` if significant issues occurred during the release.
- `project.stage` reads `Release` unless the stage check was overridden: `$ccgs-gate-check release` is the Polish → Release readiness gate, run before this skill. After an override the stage still reads what it did. Only `$ccgs-gate-check` changes `project.stage` (on a PASS, or a CONCERNS whose risks the user accepted), so this skill never writes it or `production/stage.txt`. `Release` is the terminal stage in the `project.stage` enum — there is no post-launch stage value. Record live/post-launch status in the release report, not in `project.stage`.
