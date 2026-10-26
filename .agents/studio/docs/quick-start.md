# Game Studio Agent Architecture -- Quick Start Guide

## What Is This?

This is a complete Codex agent architecture for game development. It
organizes 49 specialized AI agents into a studio hierarchy that mirrors
real game development teams, with defined responsibilities, delegation
rules, and coordination protocols. It includes engine-specialist agents
for Godot, Unity, and Unreal — each with dedicated sub-specialists for
major engine subsystems. All design agents and templates are grounded in
established game design theory (MDA Framework, Self-Determination Theory,
Flow State, Bartle Player Types). Use whichever engine set matches your project.

## The Default Path: Rigor Minimal

`modes.rigor` defaults to `minimal` (`$ccgs-start` infers it from what you describe and shows it
before saving; `$ccgs-settings` changes it any time). At `minimal` the path to code is four steps:

1. `$ccgs-setup-engine` -- configure the engine
2. `$ccgs-brainstorm` -- writes the one-page `design/game-brief.md`, in place of the
   concept doc, systems decomposition and per-system GDDs
3. `$ccgs-create-stories` -- turns the brief's MVP list into stories under
   `production/epics/<slug>/`; the brief's build order is the plan, so there is
   no `$ccgs-create-epics` or `$ccgs-sprint-plan`
4. `$ccgs-dev-story` then `$ccgs-story-done`, story by story -- `$ccgs-story-done` names the
   next story, and `$ccgs-help` knows this route

Nothing at `minimal` runs `$ccgs-gate-check`, so `project.stage` stays at Concept.
Every skill still runs at any tier. The trade: no GDDs catch design problems
before code. Raise rigor with `$ccgs-settings` when the game outgrows the brief;
`standard` and `full` are the longer pipelines under
[First Steps for a New Project](#first-steps-for-a-new-project).

## How to Use

### 1. Understand the Hierarchy

There are three tiers of agents:

- **Tier 1 — Directors** who make high-level decisions (they inherit the parent session model)
  - `creative-director` -- vision and creative conflict resolution
  - `technical-director` -- architecture and technology decisions
  - `producer` -- scheduling, coordination, and risk management

- **Tier 2 — Department leads** who own their domain
  - `game-designer`, `lead-programmer`, `art-director`, `audio-director`,
    `narrative-director`, `qa-lead`, `release-manager`, `localization-lead`

- **Tier 3 — Specialists** who execute within their domain
  - Designers, programmers, artists, writers, testers, engineers

The tiers are seniority of role. Most agents run on your session's model; the
role profile does not override the active session model
(`.agents/studio/docs/model-tiers.md`).

### 2. Pick the Right Agent for the Job

Ask yourself: "What department would handle this in a real studio?"

| I need to... | Use this agent |
|-------------|---------------|
| Design a new mechanic | `game-designer` |
| Write combat code | `gameplay-programmer` |
| Create a shader | `technical-artist` |
| Write dialogue | `writer` |
| Plan the next sprint | `producer` |
| Review code quality | `lead-programmer` |
| Write test cases | `qa-tester` |
| Design a level | `level-designer` |
| Fix a performance problem | `performance-analyst` |
| Set up CI/CD | `devops-engineer` |
| Design a loot table | `economy-designer` |
| Resolve a creative conflict | `creative-director` |
| Make an architecture decision | `technical-director` |
| Manage a release | `release-manager` |
| Prepare strings for translation | `localization-lead` |
| Test a mechanic idea quickly | `prototyper` |
| Review code for security issues | `security-engineer` |
| Check accessibility compliance | `accessibility-specialist` |
| Get Unreal Engine advice | `unreal-specialist` |
| Get Unity advice | `unity-specialist` |
| Get Godot advice | `godot-specialist` |
| Design GAS abilities/effects | `ue-gas-specialist` |
| Define BP/C++ boundaries | `ue-blueprint-specialist` |
| Implement UE replication | `ue-replication-specialist` |
| Build UMG/CommonUI widgets | `ue-umg-specialist` |
| Design DOTS/ECS architecture | `unity-dots-specialist` |
| Write Unity shaders/VFX | `unity-shader-specialist` |
| Manage Addressable assets | `unity-addressables-specialist` |
| Build UI Toolkit/UGUI screens | `unity-ui-specialist` |
| Write idiomatic GDScript | `godot-gdscript-specialist` |
| Write Godot C# code | `godot-csharp-specialist` |
| Create Godot shaders | `godot-shader-specialist` |
| Build GDExtension modules | `godot-gdextension-specialist` |
| Plan live events and seasons | `live-ops-designer` |
| Write patch notes for players | `community-manager` |
| Brainstorm a new game idea | Use `$ccgs-brainstorm` skill |

### 3. Use Slash Commands for Common Tasks

| Command | What it does |
|---------|-------------|
| `$ccgs-start` | First-time onboarding — asks where you are, guides you to the right workflow |
| `$ccgs-help` | Context-aware "what do I do next?" — reads your current phase and artifacts |
| `$ccgs-project-stage-detect` | Analyze project state, detect stage, identify gaps |
| `$ccgs-setup-engine` | Configure engine + version, populate reference docs |
| `$ccgs-adopt` | Brownfield audit and migration plan for existing projects |
| `$ccgs-brainstorm` | Guided game concept ideation from scratch |
| `$ccgs-map-systems` | Decompose concept into systems, map dependencies, guide per-system GDDs |
| `$ccgs-design-system` | Guided, section-by-section GDD authoring for a single game system |
| `$ccgs-quick-design` | Lightweight spec for small changes — tuning, tweaks, minor additions |
| `$ccgs-review-all-gdds` | Cross-GDD consistency and game design theory review |
| `$ccgs-propagate-design-change` | Find ADRs and stories affected by a GDD change |
| `$ccgs-art-bible` | Guided, section-by-section Art Bible authoring — creates visual identity spec before asset production |
| `$ccgs-asset-spec` | Generate per-asset visual specifications and AI generation prompts from GDDs or character profiles |
| `$ccgs-ux-design` | Author UX specs (screen/flow, HUD, interaction patterns) |
| `$ccgs-ux-review` | Validate UX specs for accessibility and GDD alignment |
| `$ccgs-create-architecture` | Master architecture document for the game |
| `$ccgs-architecture-decision` | Creates an ADR |
| `$ccgs-architecture-review` | Validate all ADRs, dependency ordering, GDD traceability — writes the index to `docs/architecture/requirements-traceability.md` |
| `$ccgs-create-control-manifest` | Flat programmer rules sheet from Accepted ADRs |
| `$ccgs-create-epics` | Translate GDDs + ADRs into epics (one per architectural module) |
| `$ccgs-create-stories` | Break a single epic into implementable story files |
| `$ccgs-dev-story` | Read a story and implement it — routes to the correct programmer agent |
| `$ccgs-sprint-plan` | Creates or updates sprint plans |
| `$ccgs-sprint-status` | Quick 30-line sprint snapshot |
| `$ccgs-story-readiness` | Validate a story is implementation-ready before pickup |
| `$ccgs-story-done` | End-of-story completion review — verifies acceptance criteria |
| `$ccgs-estimate` | Produces structured effort estimates |
| `$ccgs-design-review` | Reviews a design document |
| `$ccgs-code-review` | Reviews code for quality and architecture |
| `$ccgs-balance-check` | Analyzes game balance data |
| `$ccgs-asset-audit` | Audits assets for compliance |
| `$ccgs-content-audit` | GDD-specified content vs. implemented — find gaps |
| `$ccgs-scope-check` | Detect scope creep against plan |
| `$ccgs-perf-profile` | Performance profiling and bottleneck ID |
| `$ccgs-tech-debt` | Scan, track, and prioritize tech debt |
| `$ccgs-gate-check` | Validate phase readiness (PASS/CONCERNS/NOT ASSESSED/FAIL) |
| `$ccgs-consistency-check` | Scan all GDDs for cross-document inconsistencies (conflicting stats, names, rules) |
| `$ccgs-security-audit` | Audit for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure |
| `$ccgs-reverse-document` | Generate design/architecture docs from existing code |
| `$ccgs-milestone-review` | Reviews milestone progress |
| `$ccgs-retrospective` | Runs sprint/milestone retrospective |
| `$ccgs-bug-report` | Structured bug report creation |
| `$ccgs-playtest-report` | Creates or analyzes playtest feedback |
| `$ccgs-onboard` | Generates onboarding docs for a role |
| `$ccgs-release-checklist` | Validates pre-release checklist |
| `$ccgs-launch-checklist` | Complete launch readiness validation |
| `$ccgs-changelog` | Generates changelog from git history |
| `$ccgs-patch-notes` | Generate player-facing patch notes |
| `$ccgs-hotfix` | Emergency fix with audit trail |
| `$ccgs-day-one-patch` | Prepare a focused day-one patch for known issues discovered after gold master |
| `$ccgs-prototype` | Concept prototype — validate core idea before writing GDDs (Phase 1) |
| `$ccgs-vertical-slice` | Production-quality end-to-end build — validate full game loop (Phase 4) |
| `$ccgs-localize` | Localization scan, extract, validate |
| `$ccgs-team-combat` | Orchestrate full combat team pipeline |
| `$ccgs-team-narrative` | Orchestrate full narrative team pipeline |
| `$ccgs-team-ui` | Orchestrate full UI team pipeline |
| `$ccgs-team-release` | Orchestrate full release team pipeline |
| `$ccgs-team-polish` | Orchestrate full polish team pipeline |
| `$ccgs-team-audio` | Orchestrate full audio team pipeline |
| `$ccgs-team-level` | Orchestrate full level creation pipeline |
| `$ccgs-team-live-ops` | Orchestrate live-ops team for seasons, events, and post-launch content |
| `$ccgs-team-qa` | Orchestrate full QA team cycle — test plan, test cases, smoke check, sign-off |
| `$ccgs-qa-plan` | Generate a QA test plan for a sprint or feature |
| `$ccgs-bug-triage` | Re-prioritize open bugs, assign to sprints, surface systemic trends |
| `$ccgs-smoke-check` | Run critical path smoke test gate before QA hand-off (PASS/FAIL) |
| `$ccgs-soak-test` | Generate a soak test protocol for extended play sessions |
| `$ccgs-regression-suite` | Map coverage to GDD critical paths, flag gaps, maintain regression suite |
| `$ccgs-test-setup` | Scaffold test framework + CI pipeline for the project's engine (run once) |
| `$ccgs-test-helpers` | Generate engine-specific test helper libraries and factory functions |
| `$ccgs-test-flakiness` | Detect flaky tests from CI history, flag for quarantine or fix |
| `$ccgs-test-evidence-review` | Quality review of test files and manual evidence — ADEQUATE/INCOMPLETE/MISSING |
| `$ccgs-skill-test` | Validate skill files for compliance and correctness (static / spec / audit) |
| `$ccgs-skill-improve` | Improve a skill using a test-fix-retest loop — diagnose, propose fix, rewrite, verify |

### 4. Use Templates for New Documents

Templates are in `.agents/studio/docs/templates/`:

- `game-design-document.md` -- for new mechanics and systems
- `architecture-decision-record.md` -- for technical decisions
- `architecture-traceability.md` -- sample layout for a GDD requirement to ADR to
  story index (`$ccgs-architecture-review` writes its own index to
  `docs/architecture/requirements-traceability.md`)
- `risk-register-entry.md` -- for new risks
- `narrative-character-sheet.md` -- for new characters
- `test-plan.md` -- for feature test plans
- `sprint-plan.md` -- for sprint planning
- `milestone-definition.md` -- for new milestones
- `level-design-document.md` -- for new levels
- `game-pillars.md` -- for core design pillars
- `art-bible.md` -- for visual style reference
- `technical-design-document.md` -- for per-system technical designs
- `post-mortem.md` -- for project/milestone retrospectives
- `sound-bible.md` -- for audio style reference
- `release-checklist-template.md` -- for platform release checklists
- `changelog-template.md` -- for player-facing patch notes
- `release-notes.md` -- for player-facing release notes
- `incident-response.md` -- for live incident response playbooks
- `game-concept.md` -- for initial game concepts (MDA, SDT, Flow, Bartle)
- `game-brief.md` -- for the one-page brief that replaces the concept doc at `rigor: minimal`
- `pitch-document.md` -- for pitching the game to stakeholders
- `economy-model.md` -- for virtual economy design (sink/faucet model)
- `faction-design.md` -- for faction identity, lore, and gameplay role
- `systems-index.md` -- for systems decomposition and dependency mapping
- `project-stage-report.md` -- for project stage detection output
- `design-doc-from-implementation.md` -- for reverse-documenting existing code into GDDs
- `architecture-doc-from-code.md` -- for reverse-documenting code into architecture docs
- `concept-doc-from-prototype.md` -- for reverse-documenting prototypes into concept docs
- `ux-spec.md` -- for per-screen UX specifications (layout zones, states, events)
- `hud-design.md` -- for whole-game HUD philosophy, zones, and element specs
- `accessibility-requirements.md` -- for project-wide accessibility tier and feature matrix
- `interaction-pattern-library.md` -- for standard UI controls and game-specific patterns
- `player-journey.md` -- for 6-phase emotional arc and retention hooks by time scale
- `difficulty-curve.md` -- for difficulty axes, onboarding ramp, and cross-system interactions
- `test-evidence.md` -- template for recording manual test evidence (screenshots, walkthrough notes)

### 5. Follow the Coordination Rules

1. Work flows down the hierarchy: Directors -> Leads -> Specialists
2. Conflicts escalate up the hierarchy
3. Cross-department work is coordinated by the `producer`
4. Agents do not modify files outside their domain without delegation
5. All decisions are documented

## First Steps for a New Project

**Don't know where to begin?** Run `$ccgs-start`. It asks where you are and routes
you to the right workflow. No assumptions about your game, engine, or experience level.

The paths below walk the `standard`/`full` pipeline. At `rigor: minimal` (the
default), follow [The Default Path](#the-default-path-rigor-minimal) instead.

If you already know what you need, jump directly to the relevant path:

### Path A: "I have no idea what to build"

1. **Run `$ccgs-start`** (or `$ccgs-brainstorm open`) — guided creative exploration:
   what excites you, what you've played, your constraints
   - Generates 3 concepts, helps you pick one, defines core loop and pillars
   - Produces a game concept document and recommends an engine
2. **Set up the engine** — Run `$ccgs-setup-engine` (uses the brainstorm recommendation)
   - Configures AGENTS.md, detects knowledge gaps, populates reference docs
   - Writes engine, naming conventions, and performance budgets to `project.yaml`
     (the source of truth), mirrored to `.agents/studio/docs/technical-preferences.md`
   - If the engine version is newer than the LLM's training data, it fetches
     current docs from the web so agents suggest correct APIs
3. **Validate the concept** — Run `$ccgs-design-review design/gdd/game-concept.md`
   (or `design/game-brief.md`, if `$ccgs-brainstorm` wrote the one-page brief)
4. **Prototype the mechanic** — Run `$ccgs-prototype [core-mechanic]` (1 day at most) to
   test that the core idea is fun before you write GDDs
5. **Decompose into systems** — Run `$ccgs-map-systems` to map all systems and dependencies
6. **Design each system** — Run `$ccgs-design-system [system-name]` (or `$ccgs-map-systems next`)
   to write GDDs in dependency order, informed by the prototype findings
7. **Plan the first sprint** — After architecture and `$ccgs-vertical-slice`, run `$ccgs-sprint-plan new`
8. Start building

### Path B: "I know what I want to build"

If you already have a game concept and engine choice:

1. **Set up the engine** — Run `$ccgs-setup-engine [engine] [version]`
   (e.g., `$ccgs-setup-engine godot 4.7`) — also creates technical preferences
2. **Write the Game Pillars** — delegate to `creative-director`
3. **Decompose into systems** — Run `$ccgs-map-systems` to enumerate systems and dependencies
4. **Design each system** — Run `$ccgs-design-system [system-name]` for GDDs in dependency order
5. **Create the initial ADR** — Run `$ccgs-architecture-decision`
6. **Create the first milestone** in `production/milestones/`
7. **Plan the first sprint** — Run `$ccgs-sprint-plan new`
8. Start building

### Path C: "I know the game but not the engine"

If you have a concept but don't know which engine fits:

1. **Run `$ccgs-setup-engine`** with no arguments — it will ask about your game's
   needs (2D/3D, platforms, team size, language preferences) and recommend
   an engine based on your answers
2. Follow Path B from step 2 onward

### Path D: "I have an existing project"

If you have design docs, prototypes, or code already:

1. **Run `$ccgs-start`** (or `$ccgs-project-stage-detect`) — analyzes what exists,
   identifies gaps, and recommends next steps
2. **Run `$ccgs-adopt`** if you have existing GDDs, ADRs, or stories — audits
   internal format compliance and builds a numbered migration plan to fill gaps
   without overwriting your existing work
3. **Configure engine if needed** — Run `$ccgs-setup-engine` if not yet configured
4. **Validate phase readiness** — Run `$ccgs-gate-check` to see where you stand
5. **Plan the next sprint** — Run `$ccgs-sprint-plan new`

## File Structure Reference

```
AGENTS.md                          -- Master config (read this first, ~80 lines)
project.yaml                       -- Machine-readable project config (engine, modes, stage) — source of truth
.agents/ and .codex/
  .codex/hooks.json                -- project-local hook registration reference
  agents/                          -- 49 agent definitions (YAML frontmatter)
  skills/                          -- 74 slash command definitions (YAML frontmatter)
  hooks/                           -- 15 event hooks (.sh, wired by settings.json) + yaml-helper.sh, update-check.sh
  rules/                           -- 14 path-specific rule files
  docs/
    quick-start.md                 -- This file
    technical-preferences.md       -- Legacy fallback for project.yaml config (mirror; see project.yaml at repo root)
    coding-standards.md            -- Coding and design doc standards
    coordination-rules.md          -- Agent coordination rules
    context-management.md          -- Context budgets and compaction instructions
    directory-structure.md         -- Project directory layout
    workflow-catalog.yaml          -- 7-phase pipeline definition (read by $ccgs-help)
    setup-requirements.md          -- System prerequisites (Git Bash, jq, Python)
    settings-local-template.md     -- Host-controlled settings guidance
    AGENTS-local-template.md       -- Personal AGENTS.local.md guide (gitignored overrides)
    templates/                     -- 62 document templates (+ per-section guidance)
```
