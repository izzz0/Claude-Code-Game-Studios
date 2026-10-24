# Codex Game Studios

This repository is a game-development template with nine repository-local Codex
skills. Start with $ccgs-start. The supported workflow is minimal; do not silently
convert an existing standard/full project or a stricter system override.

## Before working

- Read production/session-state/active.md if present, especially after resuming.
  Confirm its branch and current task against the actual working tree.
- Read .agents/studio/docs/core-workflow.md when using a studio skill. It defines
  configuration resolution, collaboration, story state and evidence requirements.
- Use project.yaml as the project configuration; personal whitelisted overrides
  belong in the ignored project.local.yaml. Run helpers explicitly from the
  repository root. They are ordinary scripts, with no automatic lifecycle hooks.
- Preserve the user's selected model, environment permissions and authorizations.
  Normal edits and checks within an agreed task do not need per-file approval.
  Ask about consequential scope/architecture changes or genuinely missing input.
  A pending required question is not permission to proceed.

## Implementation

- Keep changes scoped to the accepted brief/story. Prefer the smallest working
  implementation; do not require interfaces, dependency injection or new
  architecture for their own sake.
- Determine the engine before writing game code: Godot uses src/, Unity uses
  Assets/, Unreal uses Source/. Resolve engine version and relevant references
  under docs/engine-reference/; verify uncertain APIs against official docs.
- Run meaningful checks for the change. For anything player-visible, launch the
  actual game, retain a relevant screenshot and open it. Parsing is not running.
- Helpers emit observations, never game-quality verdicts. In particular,
  test-run.sh exiting 0 means the helper finished; inspect its TSV result rows.
- Do not mark unfinished, unobserved or failed work Complete. Keep evidence and
  limitations explicit. Code review is read-only unless fixes are requested.
- Use the current agent by default; delegate bounded tasks only when useful.
  Identify independent review versus self-review accurately.

## Framework checks

Run: python -m unittest discover -s studio-tests/codex -v

These are framework tests, separate from a game's tests/. On Windows use Git
Bash and a working Python 3 on PATH; see README.md. Do not modify global Codex
settings or unrelated projects to use this template.
