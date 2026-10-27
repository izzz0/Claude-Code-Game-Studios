# Native acceptance smoke catalog

This directory currently contains **seventy-four authored native cases**:

- `ccgs-help`: read-only navigation from a minimal project with no engine;
  expected handoff is `$ccgs-setup-engine`. The case checks navigation, actual
  configuration facts and a single workflow command outside inventory bullets;
  it does not attest every catalog-enumeration or formatting responsibility.
- `ccgs-start`: returning-user onboarding with the same unconfigured-engine
  handoff; it must not write stage/configuration or start the next skill. Exact
  project identity and settings are checked through the original YAML parser,
  without requiring the project name to be repeated in the response prose.
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

`coverage.unauthored_manifest_skills` is now zero: each of the 74 manifest skills
has one authored case. This is catalog coverage, not 74 successful native runs.
The added design, quality, runtime and six team cases check concrete inputs,
outputs and missing-evidence outcomes; their actual results remain separate.

Utility/context cases add local-override inspection, programmer onboarding,
record-based retrospective analysis and read-only stage-gap detection. They
remain authored and unexecuted.

Each case uses the full `ccgs-*` skill name and an independent fixture under
`fixtures/<name>/`. Fixtures contain schema-1 `project.yaml` with test-specific workflow modes,
usually minimal/guided, plus the relevant
`production/epics/<slug>/story-*.md` and QA evidence layout. The setup fixture
leaves `engine` unset before the explicit request; the review fixture pins
Godot/GDScript and its specialist. Utility fixtures also cover standard/full
projects and an explicitly preserved autonomous local override; the runner
does not coerce those settings to the new-project defaults.

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
only with intact native event/thread receipts. `--inspect` writes a separate
`inspection.json` and preserves existing batch state and acceptance summary.
Resume otherwise reuses a PASS
only while source, fixture, host version/binary, response and sandbox hashes
match. Failed or interrupted cases retain their attempt directory and are
retried in a separate fresh attempt. Story-level recovery is a separate case.
Host interaction requests stop the batch for human attention; this driver does
not approve them. Additional visual or independent-review evidence cannot be
satisfied by a claim in the returned text.

The console prints compact case results. Full protected-file and artifact hashes
remain in state.json and each attempt/result.json. Historical failed attempts
are retained; a changed fixture or assertion requires a fresh native attempt.

The help command check recognizes ATX and standalone bold inventory headings.
It excludes inventory skill names only; command references in descriptions stay
checked. A subsequent heading or non-list body ends the inventory region.
The captured bold-heading response is a parser regression fixture, not a new
native execution. Offline reassessments retain the original FAIL and are stored
separately from native attempts and resume state.

An incomplete native turn does not grade response/artifact expectations. It
remains NOT ASSESSED, with the actual terminal host error retained in the result
and compact console output. Observed hook or read-only protection failures still
fail, even when the host turn fails. A host capacity error never switches models
or turns an unexecuted case into a skill failure or PASS.

Git-dependent fixtures use an explicit ignored `.scratch/case-history.git`, never
the parent framework history or a new `.git` trust boundary. Baselines are committed
with fixture-local identity and current input bytes restored before native execution.

Each new attempt retains `before.json`, full child thread/item pagination receipts,
and hashes of ignored review observations. A timed-out turn retains an unassessed
result and stops the batch. Team/review verification crossmatches native child IDs,
configured roles, actual completed turns, recovery ordering and retained artifact
hashes. Missing history or independent review never becomes a PASS from prose.

Acceptance parent threads retain local rollout history so native child agents
can fork their context; no model, provider or permission override is made.
Resume fingerprints include all shared runtime inputs plus the selected case
and its own fixture. Editing another case alone does not invalidate an unrelated
PASS; shared code, host, instructions or selected-case changes still do.

Child IDs are collected from actual legacy collaboration receipts and native
`subAgentActivity` items. Interrupted parent attempts retain read-only child
metadata and full history when the host provides them. Activity is lifecycle
evidence only: it does not prove assignment contents, returned work or review
completion. Missing or encrypted assignment evidence remains NOT ASSESSED.
