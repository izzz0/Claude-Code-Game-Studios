# Codex Game Studios

A repository-local game-development template for Codex with **74 skills,
49 professional roles and nine team workflows**. Migrated from
[Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)
at baseline 05ad7c8, extending the tested nine-skill core at bcc5607.
The upstream MIT license is retained.

## Start

1. Open this checkout as the Codex chat's project. A new chat in a different
   project does not load these repository-local skills.
2. Provide Git, Python 3.11+ and working Bash. Windows uses Git for Windows'
   Bash. The runtime discovers the actual executable via
   `.agents/studio/runtime/context.py:bash_executable`; do not run a
   `WindowsApps` alias or edit global `PATH`. Verify the tools in the actual
   Codex host environment.
3. Review and trust the project's hook definitions in the host. New or changed
   definitions require review; configured does not mean trusted or observed.
4. Invoke **$ccgs-start**, then follow its engine/configuration-aware next step.

No separate model API, global installation or model/provider/permission change
is required. See [setup and trust](.agents/studio/docs/setup-requirements.md).

On the tested Windows CLI `0.164.0-alpha.11.1`, linked Git worktrees can load
hooks from the primary checkout instead of the worktree. Confirm the source
path in `/hooks`; do not treat another source's Active count as this studio's
execution. An isolated ordinary Git clone discovered the project hooks after
project trust. This host limitation is tracked in
[openai/codex#27133](https://github.com/openai/codex/issues/27133).
Do not work around it by installing these hooks globally.

## Workflows

New projects initialize only missing minimal rigor and guided automation.
Existing settings and whitelisted local overrides remain intact.

| Workflow | Expected route |
| --- | --- |
| minimal | Engine → one-page brief → optional isolated prototype → stories → implementation → checks → review → closure |
| standard | Concept/system design → required GDD sections → architecture/ADRs/UX → epics/stories/sprints → gates and regression |
| full | Complete design and traceability → applicable specialist/director reviews → full QA/regression → verified local release |

Workflow strength, review depth and team size are separate configuration axes.
Guided proceeds with ordinary authorized edits and checks, asking about material
decisions. A stricter existing workflow is never silently downgraded.

The original nine core entries remain: ccgs-start, ccgs-setup-engine,
ccgs-brainstorm, ccgs-prototype, ccgs-create-stories, ccgs-dev-story,
ccgs-smoke-check, ccgs-code-review and ccgs-story-done. Use ccgs-help for the
complete design, development, quality, release and operations catalog.

## Native roles and teams

Profiles live in .codex/agents/ccgs-*.toml and inherit parent model/permissions.
The nine team entries cover combat, narrative, UI, release, polish, audio,
level, live operations and QA. They dispatch actual task-relevant native roles,
queue within host limits and retain identity, ownership, results and recovery.

A manifest or a role file does not prove a role ran. Required independent
review must be a distinct non-implementing execution; unavailable agents or
missing results remain NOT ASSESSED. See the
[coordination contract](.agents/studio/docs/coordination-rules.md).

## Configuration, hooks and evidence

project.yaml remains schema 1. Ignored project.local.yaml accepts only the
existing whitelist. Shared resources live under .agents/studio/; see
[configuration effects](.agents/studio/docs/effects-map.md).
Project-owned technical preferences live in `docs/technical-preferences.md`.
Game workflows keep framework resources read-only; old preferences in the shipped
template remain per-key fallbacks, and `project.yaml` keeps precedence.

Native hooks provide context, checks and ignored runtime receipts. They never
launch models/Codex recursively or update code, stories, QA evidence or
developmental checkpoints. The coordinator owns authorized progress updates.
See the [hook contract](.agents/studio/docs/hooks-reference.md).

PASS advances; CONCERNS needs explicit human acceptance; FAIL/NOT ASSESSED holds
the stage. A helper's exit code is not a game result. Missing engines/results,
zero tests, timeouts, stale evidence and absent numeric coverage reports cannot
be presented as passed. Minimal waiver applies only to genuinely unconfigured
tests without a stricter requirement.

Player-visible acceptance needs a real launch, saved and opened images, and
appropriate input/runtime evidence. Release acceptance stops at a locally
runnable package; publishing/uploading/messaging requires separate authorization.

## Validation and limits

Run:

    python -m unittest discover -s studio-tests/codex -v

Windows and Linux CI run structure, configuration, script and hook-protocol
regressions without commercial engine licenses or model APIs. Protocol fixtures
do not establish native host execution, and stub runners do not establish real
gameplay.

Source coverage, native host verification and engine verification are recorded
separately in [the migration manifest](studio-tests/migration-manifest.json)
and [the acceptance report](studio-tests/acceptance/full-port-20261025.md).
Godot 4.6.1/GDScript is the current acceptance
target. Unity and Unreal remain **UNVERIFIED** until exercised; Cocos Creator
3.8.8 is recognized with its explicit Node/TAP adapter and resolved TypeScript
roots. Isolated Node/TAP, type checks and Web builds have been observed;
complete native workflows and device-specific behavior remain unverified.
No incomplete or unverified case is promoted to PASS.
