# Available Skills (Slash Commands)

74 slash commands organized by phase. Type `/` in Codex to access any of them.

## Onboarding & Navigation

| Command | Purpose |
|---------|---------|
| `$ccgs-start` | First-time onboarding — asks where you are, then guides you to the right workflow |
| `$ccgs-help` | Context-aware "what do I do next?" — reads current stage and surfaces the required next step |
| `$ccgs-project-stage-detect` | Full project audit — detect phase, identify existence gaps, recommend next steps |
| `$ccgs-setup-engine` | Configure engine + version, detect knowledge gaps, populate version-aware reference docs |
| `$ccgs-adopt` | Brownfield format audit — checks internal structure of existing GDDs/ADRs/stories, produces migration plan |
| `$ccgs-settings` | View or change project config — the effective merged values, or a local override in `project.local.yaml` |

## Game Design

| Command | Purpose |
|---------|---------|
| `$ccgs-brainstorm` | Guided ideation using professional studio methods (MDA, SDT, Bartle, verb-first) |
| `$ccgs-map-systems` | Decompose game concept into systems, map dependencies, prioritize design order |
| `$ccgs-design-system` | Guided, section-by-section GDD authoring for a single game system |
| `$ccgs-quick-design` | Lightweight design spec for small changes — tuning, tweaks, minor additions |
| `$ccgs-review-all-gdds` | Cross-GDD consistency and game design holism review across all design docs |
| `$ccgs-propagate-design-change` | When a GDD is revised, find affected ADRs and produce an impact report |

## Art & Assets

| Command | Purpose |
|---------|---------|
| `$ccgs-art-bible` | Guided, section-by-section Art Bible authoring — creates visual identity spec before asset production begins |
| `$ccgs-asset-spec` | Generate per-asset visual specifications and AI generation prompts from GDDs, level docs, or character profiles |
| `$ccgs-asset-audit` | Audit assets for naming conventions, file size budgets, and pipeline compliance |

## UX & Interface Design

| Command | Purpose |
|---------|---------|
| `$ccgs-ux-design` | Guided section-by-section UX spec authoring (screen/flow, HUD, or pattern library) |
| `$ccgs-ux-review` | Validate UX specs for GDD alignment, accessibility, and pattern compliance |

## Architecture

| Command | Purpose |
|---------|---------|
| `$ccgs-create-architecture` | Guided authoring of the master architecture document |
| `$ccgs-architecture-decision` | Create an Architecture Decision Record (ADR) |
| `$ccgs-architecture-review` | Validate all ADRs for completeness, dependency ordering, and GDD coverage |
| `$ccgs-create-control-manifest` | Generate flat programmer rules sheet from accepted ADRs |

## Stories & Sprints

| Command | Purpose |
|---------|---------|
| `$ccgs-create-epics` | Translate GDDs + ADRs into epics — one per architectural module |
| `$ccgs-create-stories` | Break a single epic into implementable story files |
| `$ccgs-dev-story` | Read a story and implement it — routes to the correct programmer agent |
| `$ccgs-sprint-plan` | Generate or update a sprint plan; initializes sprint-status.yaml |
| `$ccgs-sprint-status` | Fast 30-line sprint snapshot (reads sprint-status.yaml) |
| `$ccgs-story-readiness` | Validate a story is implementation-ready before pickup (READY/NEEDS WORK/BLOCKED) |
| `$ccgs-story-done` | 8-phase completion review after implementation; updates story file, surfaces next story |
| `$ccgs-estimate` | Structured effort estimate with complexity, dependencies, and risk breakdown |

## Reviews & Analysis

| Command | Purpose |
|---------|---------|
| `$ccgs-design-review` | Review a game design document for completeness and consistency |
| `$ccgs-code-review` | Architectural code review for a file or changeset |
| `$ccgs-balance-check` | Analyze game balance data, formulas, and config — flag outliers |
| `$ccgs-content-audit` | Audit GDD-specified content counts against implemented content |
| `$ccgs-scope-check` | Analyze feature or sprint scope against original plan, flag scope creep |
| `$ccgs-perf-profile` | Structured performance profiling with bottleneck identification |
| `$ccgs-tech-debt` | Scan, track, prioritize, and report on technical debt |
| `$ccgs-gate-check` | Validate readiness to advance between development phases (PASS/CONCERNS/NOT ASSESSED/FAIL) |
| `$ccgs-consistency-check` | Scan all GDDs against the entity registry to detect cross-document inconsistencies (stats, names, rules that contradict each other) |
| `$ccgs-security-audit` | Audit the game for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure, and input validation gaps |

## QA & Testing

| Command | Purpose |
|---------|---------|
| `$ccgs-qa-plan` | Generate a QA test plan for a sprint or feature |
| `$ccgs-smoke-check` | Run critical path smoke test gate before QA hand-off |
| `$ccgs-soak-test` | Generate a soak test protocol for extended play sessions |
| `$ccgs-regression-suite` | Map test coverage to GDD critical paths, identify fixed bugs without regression tests |
| `$ccgs-test-setup` | Scaffold the test framework and CI/CD pipeline for the project's engine |
| `$ccgs-test-helpers` | Generate engine-specific test helper libraries for the test suite |
| `$ccgs-test-evidence-review` | Quality review of test files and manual evidence documents |
| `$ccgs-test-flakiness` | Detect non-deterministic (flaky) tests from CI run logs |
| `$ccgs-skill-test` | Validate skill files for structural compliance and behavioral correctness |
| `$ccgs-skill-improve` | Improve a skill using a test-fix-retest loop — diagnose, propose fix, rewrite, verify |

## Production

| Command | Purpose |
|---------|---------|
| `$ccgs-milestone-review` | Review milestone progress and generate status report |
| `$ccgs-retrospective` | Run a structured sprint or milestone retrospective |
| `$ccgs-bug-report` | Create a structured bug report |
| `$ccgs-bug-triage` | Read all open bugs, re-evaluate priority vs. severity, assign owner and label |
| `$ccgs-reverse-document` | Generate design or architecture docs from existing implementation |
| `$ccgs-playtest-report` | Generate a structured playtest report or analyze existing playtest notes |

## Release

| Command | Purpose |
|---------|---------|
| `$ccgs-release-checklist` | Generate and validate a pre-release checklist for the current build |
| `$ccgs-launch-checklist` | Complete launch readiness validation across all departments |
| `$ccgs-changelog` | Auto-generate changelog from git commits and sprint data |
| `$ccgs-patch-notes` | Generate player-facing patch notes from git history and internal data |
| `$ccgs-hotfix` | Emergency fix workflow with audit trail, bypassing normal sprint process |
| `$ccgs-day-one-patch` | Prepare a focused day-one patch for known issues discovered after gold master but before or at public launch |

## Creative & Content

| Command | Purpose |
|---------|---------|
| `$ccgs-prototype` | Concept prototype — throwaway build right after brainstorm to validate core idea (Phase 1) |
| `$ccgs-vertical-slice` | Pre-Production validation — production-quality end-to-end build before committing to Production (Phase 4) |
| `$ccgs-onboard` | Generate contextual onboarding document for a new contributor or agent |
| `$ccgs-localize` | Localization workflow: string extraction, validation, translation readiness |

## Team Orchestration

Coordinate multiple agents on a single feature area:

| Command | Coordinates |
|---------|-------------|
| `$ccgs-team-combat` | game-designer + gameplay-programmer + ai-programmer + technical-artist + sound-designer + qa-tester |
| `$ccgs-team-narrative` | narrative-director + writer + world-builder + level-designer |
| `$ccgs-team-ui` | ux-designer + ui-programmer + art-director + accessibility-specialist |
| `$ccgs-team-release` | release-manager + qa-lead + devops-engineer + producer |
| `$ccgs-team-polish` | performance-analyst + technical-artist + sound-designer + qa-tester |
| `$ccgs-team-audio` | audio-director + sound-designer + technical-artist + gameplay-programmer |
| `$ccgs-team-level` | level-designer + narrative-director + world-builder + art-director + systems-designer + qa-tester |
| `$ccgs-team-live-ops` | live-ops-designer + economy-designer + community-manager + analytics-engineer |
| `$ccgs-team-qa` | qa-lead + qa-tester + gameplay-programmer + producer |

## Overlap with Codex's bundled skills

Codex ships its own skills, and one name collides with CCGS's.

| You type | You get | Use it for |
|---------|---------|-----------|
| `$ccgs-code-review` | **CCGS's** — project skills take the bare name | Architectural review against this project's coding standards, SOLID, testability and the control manifest. Knows about ADRs, stories and `docs/architecture/`. |
| `/review` | **Codex's bundled** review — the alias of its `$ccgs-code-review`, which CCGS's skill shadows | Reviewing a pull request or a plain diff for correctness bugs, with no knowledge of CCGS's design documents or gates. |

Both are useful; they answer different questions. Reach for the CCGS one during
`$ccgs-dev-story` and before `$ccgs-story-done`, because it checks the things the gates
later check. Reach for the bundled one when you want a general review of a diff
that has nothing to do with a story.

CCGS does **not** turn the bundled skills off. `disableBundledSkills` would
remove all of them, including `/debug`, `/security-review` and `/simplify`,
which are worth keeping. If you want a bundled skill hidden, use
Project-local skill selection belongs in the host's Codex controls; this repository
does not write global settings or a settings-local file.
the whole set.
