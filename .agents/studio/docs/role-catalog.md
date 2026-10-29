# Native role catalog

These 49 standalone Codex agents migrate the role contracts from the historical studio role set.
Each file is discoverable as `ccgs-<role>` and contains only the official required fields:
`name`, `description`, and `developer_instructions`. Agents inherit the parent session settings.

## Contract rules

- Role-specific instructions preserve the source expertise, artifacts, engine/language suitability, and boundaries.
- Review and audit assignments are read-only; an independent configured reviewer owns approval.
- Minimal workflow routes use the nine `ccgs-*` skills already shipped in `.agents/skills/`; other migrated skill references remain prefixed for the separately ported full workflow.
- Shared guidance lives under `.agents/studio/`; no role relies on legacy Claude paths or per-file approval prompts.

## Roles

### `ccgs-accessibility-specialist`

- Expertise: Accessibility standards and assistive features — remapping, text scaling, colorblind modes, screen reader support.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `accessibility-specialist` role contract migrated into `.codex/agents/ccgs-accessibility-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ai-programmer`

- Expertise: Implements game AI — behavior trees, state machines, pathfinding, perception, decision-making, NPC and enemy behavior, AI debugging.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ai-programmer` role contract migrated into `.codex/agents/ccgs-ai-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-analytics-engineer`

- Expertise: Telemetry and analytics — event tracking, player behavior, A/B test frameworks, dashboard specification, data pipelines.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `analytics-engineer` role contract migrated into `.codex/agents/ccgs-analytics-engineer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-art-director`

- Expertise: Owns visual identity — style guides, art bible, asset standards, color palettes, UI visual direction.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `art-director` role contract migrated into `.codex/agents/ccgs-art-director.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-audio-director`

- Expertise: Owns sonic identity — music direction, sound palette, audio implementation strategy, mix balance.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `audio-director` role contract migrated into `.codex/agents/ccgs-audio-director.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-community-manager`

- Expertise: Player-facing communication — patch notes, social posts, community updates, feedback collection, player bug triage, crisis communication.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `community-manager` role contract migrated into `.codex/agents/ccgs-community-manager.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-creative-director`

- Expertise: Highest creative authority — vision, tone, aesthetic direction. Use when a decision affects game identity or department leads deadlock.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `creative-director` role contract migrated into `.codex/agents/ccgs-creative-director.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-devops-engineer`

- Expertise: Build pipelines, CI/CD configuration, version control workflow, branching strategy, automated test pipelines, deployment infrastructure.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `devops-engineer` role contract migrated into `.codex/agents/ccgs-devops-engineer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-economy-designer`

- Expertise: Resource economies — loot tables, sink/faucet analysis, progression curve calibration, economic balance.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `economy-designer` role contract migrated into `.codex/agents/ccgs-economy-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-engine-programmer`

- Expertise: Core engine systems — rendering pipeline, physics, memory, resource loading, scene management, performance-critical framework code.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `engine-programmer` role contract migrated into `.codex/agents/ccgs-engine-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-game-designer`

- Expertise: Mechanical and systems design — core loops, progression, combat, economy, player-facing rules. Mechanics-level questions.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `game-designer` role contract migrated into `.codex/agents/ccgs-game-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-gameplay-programmer`

- Expertise: Implements designed mechanics as code — player systems, combat, interactive features, gameplay system code.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `gameplay-programmer` role contract migrated into `.codex/agents/ccgs-gameplay-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-godot-csharp-specialist`

- Expertise: Godot 4 C# quality — .NET patterns, attribute-based exports, signal delegates, async patterns, type-safe node access.
- Engine/language suitability: Godot; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `godot-csharp-specialist` role contract migrated into `.codex/agents/ccgs-godot-csharp-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-godot-gdextension-specialist`

- Expertise: Native code integration with Godot — GDExtension API, godot-cpp and godot-rust bindings, custom node types, the native boundary.
- Engine/language suitability: Godot; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `godot-gdextension-specialist` role contract migrated into `.codex/agents/ccgs-godot-gdextension-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-godot-gdscript-specialist`

- Expertise: GDScript code quality — static typing enforcement, signal architecture, coroutine patterns, GDScript idioms, typed and performant.
- Engine/language suitability: Godot; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `godot-gdscript-specialist` role contract migrated into `.codex/agents/ccgs-godot-gdscript-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-godot-shader-specialist`

- Expertise: Godot rendering customization — shading language, visual shaders, material setup, particle shaders, post-processing.
- Engine/language suitability: Godot; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `godot-shader-specialist` role contract migrated into `.codex/agents/ccgs-godot-shader-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-godot-specialist`

- Expertise: Authority on Godot-specific patterns and APIs — node/scene architecture, signals, resources; guides GDScript vs C# vs GDExtension.
- Engine/language suitability: Godot; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `godot-specialist` role contract migrated into `.codex/agents/ccgs-godot-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-lead-programmer`

- Expertise: Lead programmer — code-level architecture, coding standards, code review, API design, refactoring strategy, assigning work to specialist programmers.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `lead-programmer` role contract migrated into `.codex/agents/ccgs-lead-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-level-designer`

- Expertise: Spatial design for levels and areas — encounter layouts, pacing, difficulty, layout planning, environmental storytelling.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `level-designer` role contract migrated into `.codex/agents/ccgs-level-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-live-ops-designer`

- Expertise: Post-launch content — seasonal events, battle passes, content cadence, retention, engagement analytics. Keeps the game fresh.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `live-ops-designer` role contract migrated into `.codex/agents/ccgs-live-ops-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-localization-lead`

- Expertise: Internationalization architecture — i18n system design, string extraction workflows, locale testing, locale-specific issues, translation pipeline.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `localization-lead` role contract migrated into `.codex/agents/ccgs-localization-lead.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-narrative-director`

- Expertise: Story architecture, world-building, character design, dialogue strategy. Narrative structure and direction rather than writing individual lines.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `narrative-director` role contract migrated into `.codex/agents/ccgs-narrative-director.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-network-programmer`

- Expertise: Multiplayer networking — state replication, lag compensation, matchmaking, network protocol, netcode and bandwidth optimization.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `network-programmer` role contract migrated into `.codex/agents/ccgs-network-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-performance-analyst`

- Expertise: Performance analyst — profiling, bottlenecks, memory analysis, frame time investigation, recommends optimizations, tracks metrics over time.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `performance-analyst` role contract migrated into `.codex/agents/ccgs-performance-analyst.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-producer`

- Expertise: Production concerns — sprint planning, milestone tracking, risk, scope, cross-department coordination when multiple departments must synchronize.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `producer` role contract migrated into `.codex/agents/ccgs-producer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-prototyper`

- Expertise: Throwaway builds — concept prototypes after brainstorm to test an idea is fun before GDDs; vertical slices pre-production. Speed over standards.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `prototyper` role contract migrated into `.codex/agents/ccgs-prototyper.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-qa-lead`

- Expertise: Test strategy and process — test plan creation, bug severity assessment, regression planning, release quality gates, readiness evaluation.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `qa-lead` role contract migrated into `.codex/agents/ccgs-qa-lead.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-qa-tester`

- Expertise: Writes test cases, bug reports, and checklists — test case generation, regression checklist creation, execution documentation.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `qa-tester` role contract migrated into `.codex/agents/ccgs-qa-tester.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-release-manager`

- Expertise: Release pipeline — certification checklists, store submissions and page prep, platform requirements, version numbering, release-day coordination.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `release-manager` role contract migrated into `.codex/agents/ccgs-release-manager.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-security-engineer`

- Expertise: Protects against cheating, exploits, breaches — anti-cheat measures, secure save data and network comms, player privacy compliance.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `security-engineer` role contract migrated into `.codex/agents/ccgs-security-engineer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-sound-designer`

- Expertise: SFX specifications and spec sheets — audio event documentation, mixing parameters, sound category definitions.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `sound-designer` role contract migrated into `.codex/agents/ccgs-sound-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-systems-designer`

- Expertise: Detailed subsystem mechanics — combat formulas, progression curves, crafting recipes, status effect interactions, mathematical modeling of a mechanic.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `systems-designer` role contract migrated into `.codex/agents/ccgs-systems-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-technical-artist`

- Expertise: Technical artist bridging art and engineering — shaders, VFX, rendering optimization, art pipeline tools, art-to-engine issues.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `technical-artist` role contract migrated into `.codex/agents/ccgs-technical-artist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-technical-director`

- Expertise: High-level technical decisions — engine architecture, technology choices, performance strategy, technical risk, cross-system conflicts.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `technical-director` role contract migrated into `.codex/agents/ccgs-technical-director.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-tools-programmer`

- Expertise: Internal dev tools — editor extensions, content authoring tools, debug utilities, pipeline automation, editor workflow.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `tools-programmer` role contract migrated into `.codex/agents/ccgs-tools-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ue-blueprint-specialist`

- Expertise: Blueprint architecture and Blueprint/C++ boundary — optimization, maintainable graphs. Prevents Blueprint spaghetti, enforces clean BP patterns.
- Engine/language suitability: Unreal; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ue-blueprint-specialist` role contract migrated into `.codex/agents/ccgs-ue-blueprint-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ue-gas-specialist`

- Expertise: Gameplay Ability System — abilities, gameplay effects, attribute sets, tags, ability tasks, prediction. Prevents common GAS anti-patterns.
- Engine/language suitability: Unreal; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ue-gas-specialist` role contract migrated into `.codex/agents/ccgs-ue-gas-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ue-replication-specialist`

- Expertise: Unreal networking — property replication, RPCs, client prediction, relevancy, net serialization, bandwidth. Server-authoritative architecture.
- Engine/language suitability: Unreal; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ue-replication-specialist` role contract migrated into `.codex/agents/ccgs-ue-replication-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ue-umg-specialist`

- Expertise: Unreal UI implementation — UMG widget hierarchy, data binding, CommonUI input routing, widget styling, UI optimization.
- Engine/language suitability: Unreal; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ue-umg-specialist` role contract migrated into `.codex/agents/ccgs-ue-umg-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ui-programmer`

- Expertise: Implements user interface systems — menus, HUDs, inventory screens, dialogue boxes, UI framework code, screen flow.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ui-programmer` role contract migrated into `.codex/agents/ccgs-ui-programmer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unity-addressables-specialist`

- Expertise: Unity asset management — Addressable groups, loading/unloading, content catalogs, remote delivery, asset bundle optimization, fast load times.
- Engine/language suitability: Unity; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unity-addressables-specialist` role contract migrated into `.codex/agents/ccgs-unity-addressables-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unity-dots-specialist`

- Expertise: Unity Data-Oriented Technology Stack — Entity Component System, Jobs, Burst compiler optimization, hybrid renderer, correct ECS patterns.
- Engine/language suitability: Unity; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unity-dots-specialist` role contract migrated into `.codex/agents/ccgs-unity-dots-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unity-shader-specialist`

- Expertise: Unity rendering — Shader Graph, custom HLSL, VFX Graph, render pipeline customization (URP/HDRP), post-processing within performance budgets.
- Engine/language suitability: Unity; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unity-shader-specialist` role contract migrated into `.codex/agents/ccgs-unity-shader-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unity-specialist`

- Expertise: Authority on Unity-specific patterns and APIs — guides MonoBehaviour vs DOTS/ECS, Unity subsystems including Addressables and Input System.
- Engine/language suitability: Unity; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unity-specialist` role contract migrated into `.codex/agents/ccgs-unity-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unity-ui-specialist`

- Expertise: Unity UI implementation — UI Toolkit (UXML/USS), UGUI Canvas, data binding, runtime UI performance, cross-platform adaptation.
- Engine/language suitability: Unity; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unity-ui-specialist` role contract migrated into `.codex/agents/ccgs-unity-ui-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-unreal-specialist`

- Expertise: Authority on Unreal-specific patterns and APIs — guides Blueprint vs C++, UE subsystems (GAS, Enhanced Input, Niagara, etc.).
- Engine/language suitability: Unreal; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `unreal-specialist` role contract migrated into `.codex/agents/ccgs-unreal-specialist.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-ux-designer`

- Expertise: User experience flows, interaction design, information architecture — user flow mapping, interaction pattern design, onboarding, accessibility requirements.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `ux-designer` role contract migrated into `.codex/agents/ccgs-ux-designer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-world-builder`

- Expertise: World builder for lore — factions, cultures, history, geography, ecology, world rules. Faction design, lore consistency checks.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `world-builder` role contract migrated into `.codex/agents/ccgs-world-builder.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

### `ccgs-writer`

- Expertise: Writer of player-facing text — dialogue, lore entries, item and ability descriptions, environmental text.
- Engine/language suitability: Engine-agnostic; follow the configured engine and language in `project.yaml` when the role is not engine-specific.
- Contract source: the `writer` role contract migrated into `.codex/agents/ccgs-writer.toml`.
- Artifacts and responsibility boundaries: see the role's `Key Responsibilities`, artifact/report sections, and `What This Agent Must NOT Do` clauses.

## Native team routes

Full workflow team entrypoints are `ccgs-team-combat`, `ccgs-team-narrative`,
`ccgs-team-ui`, `ccgs-team-release`, `ccgs-team-polish`, `ccgs-team-audio`,
`ccgs-team-level`, `ccgs-team-live-ops`, and `ccgs-team-qa`. Each route keeps
the source team-size collapse (`individual`, `small`, `studio`) and review
modes (`full`, `lean`, `solo`), dispatches native Codex role runs within the
host limit, and records actual run identities. Team skills own working
artifacts only; the parent coordinator owns authorized story, QA, and
checkpoint updates. Independent review is a distinct run in `full` mode.
