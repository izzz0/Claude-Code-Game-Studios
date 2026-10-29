# Codex studio workflow

The studio is repository-local. Read this contract at skill entry, then only the relevant workflow, role and artifact references. Skills are executed instructions, not a background service.

## Root, configuration and authorization

Locate the current project's project.yaml and Git/worktree identity. Use the nearest project configuration in a nested project. Resolve explicitly with:

    bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,review_mode,testing.strict,engine_values

Use the same helper for named system overrides; derive the system from its GDD filename stem before any TR alias. Whitelisted local -> project -> legacy mirror -> rigor expansion -> terminal default. Preserve existing values. Invalid configuration, orphan overrides or a local file without its base must be reported, never replaced with guessed defaults. On Windows, `runtime/context.py:bash_executable` discovers a real Git Bash; do not run a `WindowsApps` alias or mutate global `PATH`.

During a game/project workflow, treat `.agents/studio/` as read-only framework
and template content. Project-owned technical preferences live in
`docs/technical-preferences.md`; initialize it from
`.agents/studio/docs/technical-preferences.md` only when the project document is
absent, and preserve an existing project document. The original
`.agents/studio/docs/technical-preferences.md` remains a read-only per-key
fallback for legacy values. This workflow rule does not restrict explicit
maintenance of the studio framework source itself.

New projects initialize only absent modes.rigor=minimal and modes.automation=guided using config-set.sh (preview --dry-run, then the authorized write). Never seed the six expanded knobs merely to choose rigor. Schema remains 1. Configuration changes preserve unrelated keys. Reserved settings remain visibly reserved until implemented; in particular strict_gate_checks has no independent runtime effect.

Guided automatically performs ordinary authorized edits and checks, asking for material product, architecture or scope decisions. Collaborative reviews major phase drafts. Autonomous makes in-scope decisions and records them. Explicit human authorization wins; no mode grants new permission. A required unanswered question remains pending. Do not add an approval for every new file, status update or ordinary config edit.

## Workflow tiers

minimal: engine -> one-page design/game-brief.md -> optional isolated prototype -> stable stories -> implementation -> smoke -> review -> completion. Keep this path independent of the phase ladder. Do not reset an existing project's stage just to fit this route.

standard: concept, system map, five required GDD sections, simplified architecture, critical accepted ADRs, core-screen UX and applicable asset/test setup, epics/stories/sprints, phase gates and regression.

full: all eight GDD sections, complete architecture and ADR/requirement traceability, applicable art/UX/asset contracts, full review and QA requirements, regression and release evidence. Read workflow-modes.md and workflow-catalog.yaml for exact required artifacts. A project-level tier, per-system tier, review_mode and team.size are separate axes; changing one does not silently change the others.

Phase gates return PASS, CONCERNS, FAIL or NOT ASSESSED. Only PASS, or explicit recorded human acceptance of the stated CONCERNS, advances project.stage through set-stage.sh and its legacy mirror. FAIL and NOT ASSESSED retain the stage while work on blockers may continue. A receipt or file existing does not establish its quality.

## Engine and implementation

Determine engine, version and language before choosing code roots: Godot `src/`, Unity `Assets/`, Unreal `Source/`, or Cocos Creator 3.8.8 TypeScript roots returned by `resolve_code_roots` (including `client/assets/scripts`, `packages/core/src`, `packages/protocol/src`, and `server/src` when present). Generated shared trees are read-only. Resolve specialists from project settings; map known original role names to ccgs-prefixed native profiles without rewriting user configuration. null/empty specialists are unset. Check installed executables and version references; snapshots are not proof an API works.

Keep changes scoped to the accepted story. Do not impose interfaces, dependency injection or arbitrary architecture just to satisfy a review checklist. Follow accepted ADRs actually named by the story; minimal work naming none does not require invented ADRs.

## Stories and recovery

Read all existing stories before allocating IDs. Match the feature and preserve its filename, number and contents on repeated creation. New IDs use the next available number, never renumber or overwrite. Full/standard story detail follows configured granularity and accepted design; minimal keeps one coherent MVP feature per story.

Ready -> In Progress -> In Review -> Complete. Unresolved dependencies remain Blocked and cannot be bypassed by claiming consent or changing their status without evidence. An interrupted story remains In Progress. A completed story is not silently reopened. Keep matching sprint entries consistent and preserve unrelated entries.

The coordinator records actual branch, story, files, blockers and next action through session-state.sh at development phase boundaries. Honor features.session_state=off. Reconcile stale branches and native agent runs on recovery; an old agent ID is not evidence it is still running. Keep bounded checkpoint markers and narrative appends separate. Read-only review and plan activity do not alter checkpoints.

## Native roles and teams

Read coordination-rules.md for native ccgs-role routing and team records. Available native agents perform actual delegated work; writing several role viewpoints in one answer does not establish independent review. Default team selection remains individual at minimal/standard unless explicitly overridden; full expands to studio. Respect host concurrency and one writer per file. Do not pin or silently switch models/providers/permissions.

A required independent reviewer must be a distinct run that did not implement the reviewed change, with identity, inputs and result retained. Quota failure, unavailable agents or absent sign-off is NOT ASSESSED, never fabricated. Self-review remains labeled self-review where the configured route permits it.

Hooks are configured by default, but only a supported host that has trusted the current definition actually runs them. Report configured/observed/trust-unconfirmed separately. Do not bypass trust or modify global configuration. Native lifecycle logs are observational and not game QA evidence. Hooks do not edit code, stories, QA artifacts or existing checkpoints and do not launch models or Codex recursively.

## Tests and observation

For supported gdUnit4/Unity/Unreal runners, and for the Cocos adapter when its explicit Node/TAP command is configured, use test-run.sh with --dry-run and then a retained --log under production/qa. Read ran, precheck, import/build exit, test exit, timeout, zero_tests, counts, result file and actual logs. The Cocos runtime/report path is still under active verification; helper exit 0 only means observations were emitted.

PASS requires a recognized successful result with nonzero tests. FAIL includes actual failures or required-run timeout. NOT ASSESSED includes missing engine/runner/result, zero tests, absent evidence or unsupported format. At minimal QA, genuinely unconfigured automated tests with no stricter story requirement may be explicitly WAIVED; configured failing/zero-test suites are not a waiver. Required acceptance failures and visible evidence cannot be waived by a strictness flag.

At standard QA satisfy required Logic/Integration evidence. At full QA map every AC to current evidence and run regression. A numeric qa.coverage_minimum, when configured, needs an actual engine-recognized coverage report. Null imposes no numeric threshold. Never derive percentages from test counts, assertion counts or intuition.

Import/compile, game tests and rendered runtime are distinct. Import before the Godot parser, pass actual `res://` script paths after `--`, and retain its exit status. For Cocos, preserve the configured Node/TAP command and report/runner diagnostics; do not treat a zero exit without a fresh recognized TAP report as evidence. For any visible change launch the actual game, reach the relevant states, retain and open images in `production/qa/evidence/<story>/`, and record input/timing/audio checks separately. A title frame or unopened screenshot does not prove a deeper state or input behavior.

Preserve exactly one applicable implementation stamp:

    Run result: OBSERVED — actual observed state and retained image path
    Run result: NOT VERIFIED — missing requirement
    Run result: N/A — no player-visible surface

NOT VERIFIED blocks visible completion at every tier. Perf/soak metrics require actual measurements with environment and duration; no data means NOT ASSESSED.

## Review and completion

Review reads actual code, ACs and evidence, reports real blocking/advisory findings, and writes no code, story, QA stamp or checkpoint. The caller retains the returned response afterwards. Use review-receipts.sh hash/check for freshness, verify mandatory paths independently, and reassess affected ACs after behavior or inputs change.

Completion checks every AC against current observed/tested evidence or an applicable explicit minimal test waiver; resolves blocking findings and verifies required independent review. Only then set Status Complete via md-section.sh, synchronize sprint entries and update checkpoint. Missing evidence stays incomplete. Release preparation can produce a local build and checklist; external publication, messages and uploads require the user's corresponding authorization.
