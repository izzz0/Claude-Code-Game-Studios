# Native acceptance smoke catalog

This directory currently contains **twenty-seven authored native cases**:

- `ccgs-help`: read-only navigation from a minimal project with no engine;
  expected handoff is `$ccgs-setup-engine`.
- `ccgs-start`: returning-user onboarding with the same unconfigured-engine
  handoff; it must not write stage/configuration or start the next skill.
- `ccgs-setup-engine`: explicit Godot 4.6.1 + GDScript configuration using the
  real config tool, with readback checks and preservation of unrelated project
  values.
- `ccgs-code-review`: read-only native review of a real GDScript off-by-one bug
  (`index 2` is the third target), with story and QA evidence and a blocking
  `CHANGES REQUIRED` finding.
- `ccgs-bug-report`: create a new report with reproduction, severity and priority.
- `ccgs-architecture-decision`: document a chosen delivery-state owner and its alternatives.
- `ccgs-scope-check`: quantify the addition of networking and online leaderboards.
- `ccgs-consistency-check`: identify conflicting Player health values in two GDDs.
- `ccgs-qa-plan`: classify three story acceptance sets and required observations.
- `ccgs-bug-triage`: prioritize a crash and cosmetic issue within sprint capacity.
- `ccgs-tech-debt`: register a measured-risk TODO while preserving existing IDs.
- `ccgs-test-flakiness`: analyze supplied fixture reports with a 2/5 failure rate.
- Core pipeline: stable story creation, dependency readiness, a pure-logic
  development story, and refusal to close a story without its required evidence.
- Quality/release: failed evidence, curated regression selection, missing
  performance measurements and an incomplete release candidate.
- Design/production: a one-page brainstorm, systems map, two architecture epics,
  and a read-only sprint draft constrained by capacity and dependencies.
- Teams: combat timing, HUD/accessibility and a QA smoke-failure stop. These
  require actual native-agent and recovery evidence, currently unassessed.

`coverage.unauthored_manifest_skills` records the remaining 47 skills from
`studio-tests/migration-manifest.json` that intentionally have no placeholder
case yet.

Each case uses the full `ccgs-*` skill name and an independent fixture under
`fixtures/<name>/`. Fixtures contain schema-1 `project.yaml` with
`modes.rigor: minimal` and `modes.automation: guided`, plus the relevant
`production/epics/<slug>/story-*.md` and QA evidence layout. The setup fixture
leaves `engine` unset before the explicit request; the review fixture pins
Godot/GDScript and its specialist.

`fixture_stdout`, `actual_result_stub`, and `expected_native_until_run` make
execution status explicit: no fixture pretends to be a native result. The
catalog expects `fixture_stdout: null`, `actual_result_stub: null`, and a real
native run before PASS. Missing host tools, runtime, specialist identity, or
the review's `independent_review` evidence must be reported as `NA`, not PASS.

The review case is read-only and must not alter source, story, QA evidence,
project configuration, or checkpoints. The setup case may modify the expected
configuration outputs within its explicit case request; ordinary configuration
edits do not need per-file approval.

Run this driver from a normal terminal in an isolated ordinary Git clone after
reviewing its current project hooks. This avoids the linked-worktree discovery
issue and keeps the host's model, provider, permissions and login inherited:

```powershell
python -X utf8 studio-tests/native/run_acceptance.py --project . --codex '<path-to-codex.exe>' --case ccgs-help --resume
```

Use `--list` to inspect authored coverage without launching Codex, `--inspect`
to inspect current project hook discovery/trust without a model turn, and
`--case <skill-or-id>` to select cases. `--all` selects all currently authored
cases. Unwritten cases and the overall full-port acceptance remain unassessed.

Evidence is retained under `.scratch/native-acceptance`. Resume reuses a PASS
only while source, fixture, host version/binary, response and sandbox hashes
match. Failed or interrupted cases retain their attempt directory and are
retried in a separate fresh attempt. Story-level recovery is a separate case.
Host interaction requests stop the batch for human attention; this driver does
not approve them. Additional visual or independent-review evidence cannot be
satisfied by a claim in the returned text.
