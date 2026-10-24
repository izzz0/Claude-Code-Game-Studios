---
name: ccgs-smoke-check
description: Run the configured engine smoke gate for one story and record precise test, runtime, and screenshot evidence without unsupported passes.
---

# Smoke check

Read .agents/studio/docs/core-workflow.md, resolve the root, and read docs/engine-reference/<engine>/VERSION.md.

## Inputs

Story path, resolved engine name, commands.test/commands.smoke/commands.run, and existing evidence directory.

## Actions

- Resolve config with bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,engine_values; stop on unsupported tiers.
- Create production/qa/. Run the configured compile/import check. For a built-in runner, run bash .agents/studio/scripts/test-run.sh <engine> --dry-run, then the same command without --dry-run and with --log production/qa/test.log; inspect actual facts. Follow core-workflow.md's custom-runner route when appropriate.
- Run the real player-visible path with commands.run; retain screenshots under production/qa/evidence/<story-slug>/ and a note with the exact Run result: stamp.
- PASS requires actual successful checks and required runtime/visual evidence. A genuine failed required check is FAIL; an unavailable check is NOT ASSESSED. At minimal QA only, unconfigured automated tests with no stricter/story requirement may be WAIVED: if all remaining required checks pass, report PASS WITH NOTES and keep the test result explicitly WAIVED. Zero tests from a configured suite or a failed test is not a waiver. Missing required screenshots still block.
- Use bash .agents/studio/scripts/story-facts.sh and bash .agents/studio/scripts/story-status.sh only for observation. Update bash .agents/studio/scripts/session-state.sh checkpoint with files, result, blockers.

## Output

Return separate test, compile and observation results plus overall PASS, PASS WITH NOTES, FAIL, NOT ASSESSED or INCOMPLETE. PASS/PASS WITH NOTES routes to ccgs-code-review; other results retain the open story and report the required next action.
