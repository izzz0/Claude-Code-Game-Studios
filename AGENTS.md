# Codex Game Studios

This repository provides 74 local skills, 49 native role profiles and nine team
workflows. Start with $ccgs-start. New projects default to minimal + guided;
preserve existing minimal, standard or full settings and independent overrides.

## Before working

- Read optional AGENTS.local.md and production/session-state/active.md if present.
  Reconcile the checkpoint's branch, story and next action with actual files.
- Read .agents/studio/docs/core-workflow.md at studio skill entry. Resolve fresh
  configuration using the existing yaml-helper.sh; do not replace its parser.
- Read applicable shared guidance from .agents/studio/rules/ explicitly, using
  rules-reference.md and the actual engine/files. These resource files are not
  claimed to be automatically discovered host rules.
- Keep model, provider and permissions inherited. Normal authorized edits/checks
  do not require per-file prompts. Ask about material missing requirements or
  consequential product, scope or architecture changes.
- Hooks are configured in .codex/hooks.json and require host review/trust.
  Report configured, discovered, observed and trust-unconfirmed separately.

## Development and coordination

- Use the smallest change satisfying the accepted story. Do not impose interfaces,
  dependency injection or a studio hierarchy on a task that does not need them.
- Determine engine/version/language before game code: Godot `src/`, Unity
  `Assets/` (or engine-native `Packages/`), Unreal `Source/`, or Cocos
  Creator 3.8.8 TypeScript roots resolved by `resolve_code_roots` (for
  example `client/assets/scripts`, `packages/core/src`,
  `packages/protocol/src`, `server/src`). Read the matching
  `docs/engine-reference/` entry. Generated shared trees are read-only and
  must not be edited.
- On Windows, runtime helpers discover an actual Git Bash through
  `.agents/studio/runtime/context.py:bash_executable`; do not execute a
  `WindowsApps` alias and do not edit global `PATH`.
- Use actual task-relevant native profiles through the coordinator. Resolve
  team.size separately from workflow/review depth and obey host concurrency.
  Assign one writer per file; record actual IDs and returned work with team-run.py.
- Required independent review uses a separate non-implementing run. Unavailable
  agents or missing sign-off remain NOT ASSESSED; never fabricate a consultation.
- Review and plan assignments are read-only, including code, stories, QA evidence
  and checkpoints. The caller may retain returned findings afterwards.
- Only the coordinator updates developmental checkpoints during authorized work.
  Honor features.session_state=off; use atomic state helpers and reconcile conflicts.

## Evidence and gates

- PASS permits advancement. CONCERNS requires explicit acceptance of its listed
  risks. FAIL and NOT ASSESSED retain the stage while blockers are resolved.
- Helpers emit observations. test-run.sh exit 0 means the helper finished; inspect
  actual runner counts, exits, timeouts, result files and logs.
- Missing engine/results, zero tests or missing required evidence never pass.
  Minimal may explicitly waive genuinely unconfigured tests, not a configured
  failure or required runtime observation. Coverage requires an actual report.
- For player-visible changes, launch the real game, reach the relevant states,
  retain and open screenshots, and record actual input/runtime observations.
- Match every acceptance criterion to fresh evidence before Complete. Reassess
  affected criteria after behavior changes; do not reuse stale evidence.
- Release acceptance ends at a locally runnable exported package. External
  publication, uploads and messages require corresponding explicit authorization.

## Framework checks

Run python -m unittest discover -s studio-tests/codex -v with Python 3.11+ and
working Bash. Framework fixtures, real game tests and native host acceptance are
different evidence classes. Do not modify global Codex settings or other projects.
