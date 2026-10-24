# Codex Game Studios

A repository-local game-development workflow for Codex: nine skills, a short game
brief, implementation stories, and explicit runtime evidence.

This is a Codex-only fork of [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).
It retains the MIT license and reuses the upstream configuration and observation
helpers. The original Claude-specific skills, agents and lifecycle hooks are
available in Git history, not installed by this version.

## Start

1. Clone this fork and open its root folder in Codex.
2. Make Git, Bash and Python 3 available to the Codex process. Windows users need
   **Git Bash from Git for Windows**, not the Windows Store Bash/WSL launcher.
   Check `bash --version` and `python --version` in that environment.
3. Ask Codex to use **$ccgs-start**. Local skills live in .agents/skills/; if a
   client has not refreshed its skill list, reopen the project or start a new chat.
4. Choose your engine and version. An installed Godot, Unity or Unreal editor is
   needed for actual engine execution; configuration alone does not install one.

In the desktop app, add this checkout as a local project and start the chat in
that project with the checkout as its primary folder. Starting a new chat in
another project does not switch its working directory or load this repository's
skills. If `$ccgs-start` is not found, check the selected project folder first.

The template does not require a separate model API key, prescribe a model,
change global Codex settings, or start agents/hooks automatically.

## Core route

| Skill | Result |
| --- | --- |
| $ccgs-start | Inspect/resume the project and choose the next step |
| $ccgs-setup-engine | Pin engine, version, language and project commands |
| $ccgs-brainstorm | Write design/game-brief.md with an MVP and build order |
| $ccgs-prototype | Optionally test one idea in prototypes/ |
| $ccgs-create-stories | Add stable, non-overwriting stories from the brief |
| $ccgs-dev-story | Implement one story and retain verification evidence |
| $ccgs-smoke-check | Interpret actual tests and runtime observations |
| $ccgs-code-review | Read-only review of the implementation |
| $ccgs-story-done | Match acceptance criteria to evidence and close the story |

The supported release is the **minimal** workflow. New onboarding selects
minimal rigor and guided collaboration: routine edits/checks proceed within the
agreed task, with questions for consequential decisions. Existing configuration
is preserved. standard/full workflows and a stricter per-system workflow are
reported as unsupported, never silently downgraded.

## Files and configuration

- AGENTS.md supplies persistent project guidance.
- .agents/studio/ holds shared scripts, references and templates.
- project.yaml holds project facts; ignored project.local.yaml contains only
  permitted personal overrides.
- design/game-brief.md describes the game; production/epics/ holds stories.
- production/qa/ holds test results and retained screenshots.
- production/session-state/active.md is an ignored recovery checkpoint, read
  explicitly on restart. No automatic session hook loads it.
- docs/engine-reference/ holds version snapshots to verify against the engine
  selected for the current game.

Godot code belongs in src/, Unity code in Assets/, Unreal code in Source/.
The framework's own tests live in studio-tests/; game tests live in tests/ or
the engine's project test directory.

For supported configuration and helper usage, see
[the core workflow](.agents/studio/docs/core-workflow.md) and
[configuration reference](.agents/studio/docs/effects-map.md).

## Evidence and limitations

An import/compile check does not establish that a game works. Visible changes
require a real rendered run plus a retained screenshot that Codex actually opens.
Timing, responsiveness and sound require appropriate playtest evidence.

The test runner emits observations. Its own exit code 0 does **not** mean the
game tests passed: inspect the TSV ran/exit/timed_out/zero_tests/rule/results
rows. Missing engines, zero tests and missing results are reported, not passed.
Minimal can explicitly waive unconfigured automated tests; it cannot waive
observation of visible work.

Subagents are optional. A review by the current agent is identified as self-review.
This release does not port the original full studio hierarchy or all workflows.

## Framework checks

Run from the repository root:

    python -m unittest discover -s studio-tests/codex -v

The checks use Python's standard library and Bash. They validate both a fresh
template and the valid post-start configuration containing only
`modes.rigor: minimal` and `modes.automation: guided`; ignored scratch files
and known third-party addon instructions (addons/gdUnit4) are excluded from first-party resource
checks, while first-party legacy Claude instructions and seeded expanded rigor
keys remain failures. On Windows, if Bash is not
on PATH, set CCGS_BASH to the Git Bash executable for that process, for example:

    $env:CCGS_BASH = 'C:/Program Files/Git/bin/bash.exe'
    python -m unittest discover -s studio-tests/codex -v

Windows and Linux CI run the same checks. Stub engine tests verify runner
interpretation only; they are not evidence of real Godot/Unity/Unreal gameplay.
The structure checks do not replace a game's configured tests or runtime checks.
Run those separately.
