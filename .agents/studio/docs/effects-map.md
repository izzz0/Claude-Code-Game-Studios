# Project configuration

Schema remains version 1. Scripts preserve the upstream YAML subset and
per-key resolution behavior. Existing keys are not reset during migration.
The root project.yaml template deliberately does not seed rigor's six knobs.
New onboarding writes only missing modes.rigor=minimal and
modes.automation=guided. Core skills support minimal workflows only.

## modes.rigor

minimal expands to workflow minimal, terse docs, minimal QA, coarse stories,
solo review and a team size of 1. standard/full values are understood by the
resolver for compatibility but their workflows are not implemented in this
release. Existing explicit knobs or legacy mirrors win over this expansion.

## modes.workflow and system_overrides

The workflow chooses the required design artifacts. Resolve system overrides
by the system slug; never infer workflow from QA level. Stop on an effective
non-minimal workflow instead of silently downgrading.

## modes.automation

guided is the default; collaborative requests review at major phases;
autonomous proceeds within the accepted scope. Existing values and explicit
user authorization are respected.

## modes.automation_always_ask

Default categories are scope_changes, file_deletions and schema_changes.
Respect the effective configured categories; routine authorized file edits do
not need separate prompts.

## modes.review_mode and team.size

Review depth and team preferences do not force unavailable agents to run.
Report self-review honestly. These settings are locally overridable.

## modes.story_granularity and docs.density

Existing settings are preserved. Minimal creates one coherent story per MVP
feature and keeps design records brief.

## qa.level and testing.strict

QA is separate from workflow. At minimal QA unconfigured automated tests may
be explicitly waived; failing tests cannot. A visible change still needs a
retained, opened screenshot and a real run. A configured stricter requirement
or a story's explicit test requirement must be satisfied.
testing.strict accepts a legacy boolean or a map of logic, integration, visual,
ui and config booleans. Missing evidence is never a test PASS.

## engine and naming and platform and commands and testing.framework

Project-wide facts belong in project.yaml, not local overrides. Engine paths
are editor executables (Godot/Unity) or installation roots (Unreal). Commands
may be strings or per-OS mappings. Do not guess the platform's command.

## project and framework and schema_version

Identity and stage are shared. Change project.stage through set-stage.sh;
it keeps production/stage.txt in step. Framework version comes from the
resource VERSION file; no automatic upstream update service is installed.

## performance and accessibility

Configured budgets and accessibility targets remain project requirements;
performance.enforce is a locally overridable warn/block/off preference.

## features.session_state

Default on. Checkpoints are explicitly read/written by skills; there are no
automatic session hooks. Set off to disable checkpoint updates.

## features.read_guard and features.token_budget_warn_at and updates.check

> ### RESERVED
> Retained configuration compatibility only. This release installs no automatic
> read guard, token meter or remote update hook. These keys do not enable one.

## Local overrides

Only keys on yaml-helper.sh's _yaml_helper_locally_overridable whitelist apply.
The helper reports other local keys; project.local.yaml requires project.yaml.
Resolution: allowed local key -> project key -> legacy mirror -> rigor expansion
where applicable -> terminal default. Nested keys resolve independently.
Use config-set.sh --local for supported scalar edits and inspect its warnings.

## Complete example `project.yaml`

This documents recognized keys; it is not a template to copy wholesale. In
particular, do not seed the six expanded knobs when selecting rigor.

```yaml
schema_version: 1
framework:
  version: 1.2.0-codex.1
project:
  name: My Game
  version: 0.1.0
  genre: arcade
  kind: game
  stage: Concept
engine:
  name: Godot
  version: choose-installed-version
  language: GDScript
  path: /path/to/editor
platform:
  targets: [PC]
  input_methods: [Keyboard/Mouse]
commands:
  test: project-test-command
  smoke: project-import-command
  run: project-windowed-run-command
modes:
  rigor: minimal
  automation: guided
naming:
  files: snake_case
performance:
  target_framerate: 60
  frame_budget_ms: 16.67
  draw_call_limit: 100
  memory_ceiling_mb: 512
testing:
  framework: project-test-framework
features:
  session_state: on
```
